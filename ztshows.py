#!/usr/bin/env python3

import os
import time
import sys
import uuid
from threading import Thread

import yaml
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import libtorrent as lt
from pytvdbapi import api as TVDB

from tpb import TPB, ORDERS as TPB_ORDERS

from ui.mainWindow import Ui_MainWindow
from libs.progress import Progress


class ZTorrent:
    def __init__(self, handler):
        self.handler = handler
        self.data = {}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.data[key] = value

    def get(self, key):
        try:
            return self.data[key]
        except KeyError:
            return None


class DownloadManager:
    lt_states_str = ['queued', 'checking', 'downloading metadata',
                     'downloading', 'finished', 'seeding',
                     'allocating', 'checking fast-resume']

    def __init__(self, instance):
        self.instance = instance
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.session.add_dht_router("router.utorrent.com", 6881)
        self.session.start_dht(self.session)

        self.torrents = {}

    def add_magnet(self, magnet, completion_callback=None, play_callback=None):
        uid = uuid.uuid4().hex
        self.torrents[uid] = ZTorrent(
            lt.add_magnet_uri(self.session, magnet, {'save_path': self.instance.settings.get('save_path')}))
        self.torrents[uid].handler.set_sequential_download(True)
        download_speed_limit = self.instance.settings.get('download_speed_limit')
        if download_speed_limit is not None and download_speed_limit > 0:
            self.torrents[uid].handler.set_download_limit(download_speed_limit * 1000)
        Thread(target=self.download_worker, args=(self.torrents[uid], completion_callback, play_callback,)).start()
        return self.torrents[uid]

    def get_torrents(self):
        return self.session.get_torrents(self.session)

    def download_worker(self, torrent, completion_callback=None, play_callback=None):
        while not torrent.handler.has_metadata():
            time.sleep(.1)
        info = torrent.handler.get_torrent_info()
        eta = Progress(info.total_size())
        launch_at = self.instance.settings.get('launch_video_percent')
        launched = False
        while not torrent.handler.is_seed():
            eta.increment()
            status = torrent.handler.status()
            torrent.update(
                progress=status.progress * 100,
                download_rate=status.download_rate / 1000,
                upload_rate=status.upload_rate / 1000,
                num_peers=status.num_peers,
                state=self.lt_states_str[status.state],
                eta=str(eta.time_remaining())
            )
            if (not launched and launch_at > 0 and status.progress >= launch_at / 100
                and status.state in [3, 4, 5]):
                if play_callback:
                    play_callback(torrent)
                launched = True
            time.sleep(1)
        torrent.update(progress=100)
        if completion_callback:
            completion_callback(torrent)


class Settings:
    class SettingsException(Exception):
        pass

    def __init__(self, path=None):
        if path is None:
            print('[WARNING] Settings: path is not set, the configuration will not be saved')
        self.path = path
        self.store = None

    def load(self):
        self.store = yaml.load(open(self.path))

    def save(self):
        yaml.dump(self.store, open(self.path, 'w'), default_flow_style=False)

    def get(self, key):
        if self.store is None:
            self.store = {}
        try:
            return self.store[key]
        except KeyError:
            return None

    def set(self, key, value):
        if self.store is None:
            self.store = {}
        self.store[key] = value


class ZTShows:
    def __init__(self):
        self.settings = Settings('config.yml')
        self.download_manager = DownloadManager(self)
        self.api_tpb = None
        self.api_tvdb = None

    def load(self):
        self.settings.load()

        tpb_base_url = self.settings.get('tpb_base_url')
        self.api_tpb = TPB('https://thepiratebay.se' if not tpb_base_url else tpb_base_url)
        tvdb_api_key = self.settings.get('tvdb_api_key')
        self.api_tvdb = TVDB.TVDB('81DD35DB106172E7' if not tvdb_api_key else tvdb_api_key)

    def unload(self):
        self.settings.save()

    def search(self, query, callback):
        def work(w_callback):
            w_callback(self.api_tvdb.search(query, 'en'))

        Thread(target=work, args=(callback,)).start()
        print(self.download_manager.get_torrents())

    def search_episode(self, episode, callback):
        def work(w_callback):
            results = self.api_tpb.search(query).order(TPB_ORDERS.SEEDERS.DES)
            w_callback(results)

        query = '{} s{:02d}e{:02d}'.format(episode.season.show.SeriesName,
                                           episode.season.season_number,
                                           episode.EpisodeNumber)
        Thread(target=work, args=(callback,)).start()

    def download(self, torrent, completion_callback=None, play_callback=None):
        self.download_manager.add_magnet(torrent.magnet_link, completion_callback, play_callback)

    def open_player(self, torrent):
        def work(path):
            os.system(path)

        player_path = self.settings.get('player_path').format(
            video='"' + self.settings.get('save_path') + torrent.handler.name() + '"', subtitles='')
        t = Thread(target=work, args=(player_path,)).start()
        t.daemon = True


class CustomProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super(CustomProgressBar, self).__init__(parent)
        self.restore()

    def restore(self):
        self.setTextVisible(False)
        self.setValue(0)
        self.setRange(0, 1)

    def indeterminate(self):
        self.setTextVisible(False)
        self.setValue(0)
        self.setRange(0, 0)

    def start(self, max_value):
        self.setTextVisible(True)
        self.setValue(0)
        self.setRange(0, max_value)

    def progress(self, current_value):
        self.setTextVisible(True)
        self.setValue(current_value)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, instance):
        super(MainWindow, self).__init__()
        self.instance = instance
        self.instance.load()
        self.progress = None

        self.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.init_menu()
        self.init_tabs()
        self.setCentralWidget(self.tabWidget)
        self.setMinimumSize(600, 400)
        self.init_status_bar()
        self.setWindowTitle('ZTShows - Be simple')
        self.show()

    def init_status_bar(self):
        self.progress = CustomProgressBar()
        self.statusBar().showMessage('Ready')
        self.statusBar().addPermanentWidget(self.progress)

    def init_menu(self):
        def exit_now():
            self.instance.unload()
            qApp.quit()

        self.actionExit.triggered.connect(exit_now)
        self.actionSoftExit.triggered.connect(exit_now)

    def init_tabs(self):
        self.search_series_tab_init()
        self.settings_tab_init()

    def search_series_tab_init(self):
        def populate_shows(shows):
            self.resultList.clear()
            for show in shows:
                show_row = QTreeWidgetItem(self.resultList)
                show_row.setText(0, show.SeriesName)
                for season in show:
                    season_row = QTreeWidgetItem(show_row)
                    if season.season_number == 0:
                        season_row.setText(0, 'Special')
                    else:
                        season_row.setText(0, 'Season {:02d}'.format(season.season_number))
                    season_row.setData(0, Qt.UserRole + 1, season)
                    show_row.addChild(season_row)
                    for episode in season:
                        episode_row = QTreeWidgetItem(season_row)
                        episode_row.setText(0, '{:02d} - {}'.format(episode.EpisodeNumber, episode.EpisodeName))
                        episode_row.setData(0, Qt.UserRole + 1, episode)
                        season_row.addChild(episode_row)
                self.resultList.addTopLevelItem(show_row)
                if len(shows) == 1:
                    self.resultList.expandItem(self.resultList.topLevelItem(0))

        def populate_torrents(item, torrents):
            for torrent in torrents:
                row = QTreeWidgetItem(item)
                row.setText(0, '{} : {}'.format(torrent.title, torrent.seeders))
                row.setData(0, Qt.UserRole + 1, torrent)
                item.addChild(row)

        def launch_download(item, completion_callback=None, play_callback=None):
            torrent = item.data(0, Qt.UserRole + 1)
            if not hasattr(torrent, 'title'):
                return
            print('[INFO] Starting downloading')
            self.instance.download(torrent, completion_callback, play_callback)

        def get_shows_results():
            def done(shows):
                self.progress.restore()
                populate_shows(shows)

            self.progress.indeterminate()
            self.instance.search(self.searchField.text(), done)

        def get_torrents_results(item):
            def done(torrents):
                self.progress.restore()
                populate_torrents(item, torrents)
                self.resultList.expandItem(item)

            episode = item.data(0, Qt.UserRole + 1)
            if not hasattr(episode, 'season'):
                return
            self.progress.indeterminate()
            self.instance.search_episode(episode, done)

        def open_menu(position):
            def trigger_play():
                item = self.resultList.selectedItems()[0]
                launch_download(item, None, self.instance.open_player)

            def trigger_download():
                item = self.resultList.selectedItems()[0]
                launch_download(item, None, None)

            def trigger_load():
                item = self.resultList.selectedItems()[0]
                get_torrents_results(item)

            indexes = self.resultList.selectedIndexes()
            level = 0
            if len(indexes) > 0:
                index = indexes[0]
                while index.parent().isValid():
                    index = index.parent()
                    level += 1
            menu = QMenu()
            if level == 2:
                load_action = QAction("Load torrents", self)
                load_action.triggered.connect(trigger_load)
                menu.addAction(load_action)
            elif level == 3:
                play_action = QAction("Play", self)
                play_action.triggered.connect(trigger_play)
                menu.addAction(play_action)
                download_action = QAction("Download", self)
                download_action.triggered.connect(trigger_download)
                menu.addAction(download_action)
            menu.exec_(self.resultList.viewport().mapToGlobal(position))

        self.searchField.returnPressed.connect(get_shows_results)
        QTimer.singleShot(0, self.searchField.setFocus)

        self.searchButton.clicked.connect(get_shows_results)

        self.resultList.header().close()
        self.resultList.itemClicked.connect(get_torrents_results)
        self.resultList.itemDoubleClicked.connect(launch_download)
        self.resultList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.resultList.customContextMenuRequested.connect(open_menu)

    def settings_tab_init(self):
        def text_item(node, key, data_type):
            def update(u_value):
                self.instance.settings.set(key, data_type(u_value))

            value = self.instance.settings.get(key)
            if value is not None:
                node.setText(str(value))
            node.textChanged.connect(update)

        def numeric_item(node, key):
            def update(u_value):
                self.instance.settings.set(key, float(u_value))

            value = self.instance.settings.get(key)
            if value is not None:
                node.setValue(float(value))
            node.valueChanged.connect(update)

        def check_item(node, key):
            def update(u_value):
                u_value = True if u_value == Qt.Checked else False
                self.instance.settings.set(key, u_value)

            value = self.instance.settings.get(key)
            if value is not None and value is True:
                node.setCheckState(Qt.Checked)
            node.stateChanged.connect(update)

        def combo_item(node, key):
            def update(u_value):
                self.instance.settings.set(key, str(u_value))

            value = self.instance.settings.get(key)
            if value is not None:
                idx = node.findText(key)
                if idx > -1:
                    node.setCurrentIndex(idx)
            node.currentIndexChanged.connect(update)

        text_item(self.launchCommandValue, "player_path", str)
        text_item(self.savePathValue, "save_path", str)
        combo_item(self.subtitlesLanguageValue, "subtitle_language")
        text_item(self.tpbUrlValue, "tpb_base_url", str)
        text_item(self.tvdbApiKeyValue, "tvdb_api_key", str)
        numeric_item(self.speedLimitValue, "download_speed_limit")
        numeric_item(self.launchAfterValue, "launch_video_percent")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ztshows = ZTShows()
    window = MainWindow(ztshows)
    window.show()
    sys.exit(app.exec_())
