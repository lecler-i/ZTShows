#!/usr/bin/env python3

import re
import os
import time
import sys
import yaml
import uuid

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui.mainWindow import Ui_MainWindow

import libtorrent as lt
from pytvdbapi import api as TVDB
from tpb import TPB, CATEGORIES as TPB_CATEGORIES, ORDERS as TPB_ORDERS

from threading import Thread
from libs.progress import Progress

class ZTorrent:
    def __init__(self, handler):
        self.handler = handler
        self.data = {}
    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.data[key] = value
    def get(self, key):
        return self.data[key]

class DownloadManager:
    lt_states_str = ['queued', 'checking', 'downloading metadata', \
                     'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
    def __init__(self, instance):
        self.instance = instance
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.session.add_dht_router("router.utorrent.com", 6881)
        self.session.start_dht()

        self.torrents = {}

    def add_magnet(self, magnet, completion_callback = None, play_callback = None):
        uid = uuid.uuid4().hex
        self.torrents[uid] = ZTorrent(lt.add_magnet_uri(self.session, magnet, {'save_path': self.instance.settings.get('save_path')}))
        self.torrents[uid].handler.set_sequential_download(True)
        download_speed_limit = self.instance.settings.get('download_speed_limit')
        if download_speed_limit is not None and download_speed_limit > 0:
            self.torrents[uid].handler.set_download_limit(download_speed_limit * 1000)
        Thread(target=self.download_worker, args=(self.torrents[uid], completion_callback, play_callback,)).start()
        return self.torrents[uid]

    def get_torrents(self):
        return self.session.get_torrents()

    def download_worker(self, torrent, completion_callback = None, play_callback = None):
        while (not torrent.handler.has_metadata()):
            time.sleep(.1)
        info = torrent.handler.get_torrent_info()
        eta = Progress(info.total_size())
        launch_at = self.instance.settings.get('launch_video_percent')
        launched = False
        while (not torrent.handler.is_seed()):
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
            if (not launched and launch_at > 0 and
                status.progress >= launch_at / 100 and
                status.state in [3, 4, 5]):
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
    def __init__(self, path = None):
        if path is None:
            print('[WARNING] Settings: path is not set, the configuration will not be saved')
        self.path = path;
        self.store = None
    def load(self):
        self.store = yaml.load(open(self.path))
    def save(self):
        yaml.dump(self.store, open(self.path, 'w'), default_flow_style=False)
    def get(self, key):
        if self.store is None:
            self.store = {}
        try: return self.store[key]
        except: return None
    def set(self, key, value):
        if self.store is None:
            self.store = {}
        self.store[key] = value

class ZTShows:
    def __init__(self):
        self.settings = Settings('config.yml')
        self.download_manager = DownloadManager(self)

    def load(self):
        self.settings.load()

        tpb_base_url = self.settings.get('tpb_base_url')
        self.api_tpb = TPB('https://thepiratebay.se' if not tpb_base_url else tpb_base_url)
        tvdb_api_key = self.settings.get('tvdb_api_key')
        self.api_tvdb = TVDB.TVDB('81DD35DB106172E7' if not tvdb_api_key else tvdb_api_key)

    def unload(self):
        self.settings.save()

    def search(self, query, callback):
        def work(callback):
            callback(self.api_tvdb.search(query, 'en'))
        Thread(target=work, args=(callback,)).start()
        print(self.download_manager.get_torrents())

    def search_episode(self, episode, callback):
        def work(callback):
            results = self.api_tpb.search(query).order(TPB_ORDERS.SEEDERS.DES)
            callback(results)
        query = '{} s{:02d}e{:02d}'.format(episode.season.show.SeriesName,
                                           episode.season.season_number,
                                           episode.EpisodeNumber)
        Thread(target=work, args=(callback,)).start()

    def download(self, torrent, completion_callback = None, play_callback = None):
        self.download_manager.add_magnet(torrent.magnet_link, completion_callback, play_callback)

    def open_player(torrent):
        def work(player_path):
            os.system(player_path)
        player_path = self.settings.get('player_path').format(video='"' + self.settings.get('save_path') + torrent.handler.name() + '"', subtitles='')
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
    def start(self, maxValue):
        self.setTextVisible(True)
        self.setValue(0)
        self.setRange(0, maxValue)
    def progress(self, currentValue):
        self.setTextVisible(True)
        self.setValue(self.maximum())

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app, instance):
        super(MainWindow, self).__init__()
        self.app = app
        self.instance = instance
        self.instance.load()

        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.initMenu()
        self.initTabs()
        self.setCentralWidget(self.tabWidget)
        self.setMinimumSize(600, 400)
        self.initStatusBar()
        self.setWindowTitle('ZTShows - Be simple')
        self.show()

    def initStatusBar(self):
        self.progress = CustomProgressBar()
        self.statusBar().showMessage('Ready')
        self.statusBar().addPermanentWidget(self.progress)

    def initMenu(self):
        def exit_now():
            self.instance.unload()
            app.quit()

        self.actionExit.triggered.connect(exit_now)
        self.actionSoftExit.triggered.connect(exit_now)

    def initTabs(self):
        self.searchSerieTabInit()
        self.settingsTabInit()

    def searchSerieTabInit(self):
        def populateShows(shows):
            self.resultList.clear()
            for show in shows:
                showRow = QTreeWidgetItem(self.resultList)
                showRow.setText(0, show.SeriesName)
                for season in show:
                    seasonRow = QTreeWidgetItem(showRow)
                    if season.season_number == 0:
                        seasonRow.setText(0, 'Special')
                    else:
                        seasonRow.setText(0, 'Season {:02d}'.format(season.season_number))
                    seasonRow.setData(0, Qt.UserRole + 1, season)
                    showRow.addChild(seasonRow)
                    for episode in season:
                        episodeRow = QTreeWidgetItem(seasonRow)
                        episodeRow.setText(0, '{:02d} - {}'.format(episode.EpisodeNumber, episode.EpisodeName))
                        episodeRow.setData(0, Qt.UserRole + 1, episode)
                        seasonRow.addChild(episodeRow)
                self.resultList.addTopLevelItem(showRow)
                if len(shows) == 1:
                    self.resultList.expandItem(self.resultList.topLevelItem(0))

        def populateTorrents(item, torrents):
            for torrent in torrents:
                row = QTreeWidgetItem(item)
                row.setText(0, '{} : {}'.format(torrent.title, torrent.seeders))
                row.setData(0, Qt.UserRole + 1, torrent)
                item.addChild(row)

        def launchDownload(item, completion_callback = None, play_callback = None):
            torrent = item.data(0, Qt.UserRole + 1)
            if not hasattr(torrent, 'title'):
                return
            print('[INFO] Starting downloading')
            self.instance.download(torrent, completion_callback, play_callback)

        def getShowsResults():
            def searchDone(shows):
                self.progress.restore()
                populateShows(shows)
            self.progress.indeterminate()
            self.instance.search(self.searchField.text(), searchDone)

        def getTorrentsResults(item):
            def searchDone(torrents):
                self.progress.restore()
                populateTorrents(item, torrents)
                self.resultList.expandItem(item)
            episode = item.data(0, Qt.UserRole + 1)
            if not hasattr(episode, 'season'):
                return
            self.progress.indeterminate()
            self.instance.search_episode(episode, searchDone)

        def openMenu(position):
            def triggerPlay():
                item = self.resultList.selectedItems()[0]
                launchDownload(item, None, self.instance.open_player)
            def triggerDownload():
                item = self.resultList.selectedItems()[0]
                launchDownload(item, None, None)
            def triggerLoad():
                item = self.resultList.selectedItems()[0]
                getTorrentsResults(item)
            indexes = self.resultList.selectedIndexes()
            if len(indexes) > 0:
                level = 0
                index = indexes[0]
                while index.parent().isValid():
                    index = index.parent()
                    level += 1
            menu = QMenu()
            if level == 2:
                loadAction = QAction("Load torrents", self)
                loadAction.triggered.connect(triggerLoad)
                menu.addAction(loadAction)
            if level == 3:
                playAction = QAction("Play", self)
                playAction.triggered.connect(triggerPlay)
                menu.addAction(playAction)
                downloadAction = QAction("Download", self)
                downloadAction.triggered.connect(triggerDownload)
                menu.addAction(downloadAction)
            menu.exec_(self.resultList.viewport().mapToGlobal(position))

        self.searchField.returnPressed.connect(getShowsResults)
        QTimer.singleShot(0, self.searchField.setFocus)

        self.searchButton.clicked.connect(getShowsResults)

        self.resultList.header().close()
        self.resultList.itemClicked.connect(getTorrentsResults)
        self.resultList.itemDoubleClicked.connect(launchDownload)
        self.resultList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.resultList.customContextMenuRequested.connect(openMenu)

    def settingsTabInit(self):
        def textItem(node, key, dataType):
            def update(value):
                self.instance.settings.set(key, dataType(value))
            value = self.instance.settings.get(key)
            if value is not None:
                node.setText(str(value))
            node.textChanged.connect(update)

        def numericItem(node, key):
            def update(value):
                self.instance.settings.set(key, float(value))
            value = self.instance.settings.get(key)
            if value is not None:
                node.setValue(float(value))
            node.valueChanged.connect(update)

        def checkItem(node, key):
            def update(value):
                value = True if Qt.Checked else False
                self.instance.settings.set(key, value)
            value = self.instance.settings.get(key)
            if value is not None and value is True:
                node.setCheckState(Qt.Checked)
            node.stateChanged.connect(update)

        def comboItem(node, key):
            def update(value):
                self.instance.settings.set(key, str(value))
            value = self.instance.settings.get(key)
            if value is not None:
                idx = node.findText(key)
                if idx > -1:
                    node.setCurrentIndex(idx)
            node.currentIndexChanged.connect(update)

        textItem(self.launchCommandValue, "player_path", str)
        textItem(self.savePathValue, "save_path", str)
        comboItem(self.subtitlesLanguageValue, "subtitle_language")
        textItem(self.tpbUrlValue, "tpb_base_url", str)
        textItem(self.tvdbApiKeyValue, "tvdb_api_key", str)
        numericItem(self.speedLimitValue, "download_speed_limit")
        numericItem(self.launchAfterValue, "launch_video_percent")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ztshows = ZTShows()
    window = MainWindow(app, ztshows)
    window.show()
    sys.exit(app.exec_())
