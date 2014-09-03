#!/usr/bin/env python3

from pytvdbapi import api
from tpb import TPB
from tpb import CATEGORIES, ORDERS

import re
import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

import libtorrent as lt
import time
import sys
import json

from threading import Thread

tpb = TPB('https://thepiratebay.se')
tvdb = api.TVDB('81DD35DB106172E7')

def launchPlayer(h):
    config = json.load(open('config.json'))
    os.system(config['PLAYER_PATH'].format(video='"' + config['SAVE_PATH'] + h.name() + '"',subtitles=''))

def magnetDownload(link):
    config = json.load(open('config.json'))
    ses = lt.session()
    ses.listen_on(6881, 6891)

    # info = lt.torrent_info(sys.argv[1])
    # h = ses.add_torrent({'ti': info, 'save_path': '/tmp/'})

    h = lt.add_magnet_uri(ses, link, { 'save_path': config['SAVE_PATH'] })
    h.set_sequential_download(True)

    if config['DOWNLOAD_SPEED_LIMIT'] > 0:
        h.set_download_limit(config['DOWNLOAD_SPEED_LIMIT'] * 1000)

    print ('downloading metadata...')
    while (not h.has_metadata()): time.sleep(.5)

    print ('starting', h.name())

    launched = False
    while (not h.is_seed()):
        s = h.status()
        state_str = ['queued', 'checking', 'downloading metadata', \
                     'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
        print ('\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % \
               (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                s.num_peers, state_str[s.state]),)
        sys.stdout.flush()

        if not launched and config['LAUNCH_VIDEO_PERCENT'] > 0 and s.progress >= config['LAUNCH_VIDEO_PERCENT'] / 100 and s.state in [3, 4, 5]:
            t = Thread(target=launchPlayer, args=(h,))
            t.daemon = True
            t.start()
            launched = True
        time.sleep(1)

    print (h.name(), 'complete')


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # TODO : see pickle module to dump object
        self.settings = json.load(open('config.json'))

        self.initUI()

    def saveSettings(self):
        json.dump(self.settings, open('config.json', 'w'), indent=True)

    def initUI(self):
        self.initMenu()
        self.initTabs()

        self.setCentralWidget(self.tabWidget)

        self.setMinimumSize(600, 400)
        self.statusBar().showMessage('Ready')
        self.setWindowTitle('ZTShows - Be simple')
        self.show()

    def initMenu(self):
        #exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        aboutAction = QtGui.QAction('&About', self)
        aboutAction.setStatusTip('About ZTShows')
        #settingsAction = QtGui.QAction('&Settings', self)
        #aboutAction.setStatusTip('Configure things')

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        #fileMenu.addAction(settingsAction)
        fileMenu.addAction(exitAction)
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(aboutAction)

    def initTabs(self):
        self.tabWidget = QtGui.QTabWidget(self)

        searchSerieTab = self.searchSerieTab()
        searchMovieTab = QtGui.QWidget()
        downloadTab = QtGui.QWidget()
        settingsTab = self.settingsTab()

        self.tabWidget.addTab(searchSerieTab, "Search Serie")
        self.tabWidget.addTab(searchMovieTab, "Search Movie")
        self.tabWidget.addTab(downloadTab, "Downloads")
        self.tabWidget.addTab(settingsTab, "Settings")


    def searchSerieTab(self):

        searchResult = SearchResult()
        searchResult.setSelectionBehavior(QAbstractItemView.SelectRows)

        searchField = QtGui.QLineEdit()
        searchButton = QtGui.QPushButton("Search")

        def getResults():
            searchResult.populate(tvdb.search(searchField.text(), 'en'))

        searchField.returnPressed.connect(getResults)
        searchButton.clicked.connect(getResults)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(searchField)
        hbox.addWidget(searchButton)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(searchResult)

        widget = QtGui.QWidget()
        widget.setLayout(vbox)

        return widget


    def settingsTab(self):

        def textItemWidget(text, settingKey, dataType):
            def update(value):
                self.settings[settingKey] = dataType(value)
                self.saveSettings()

            labelField = QtGui.QLabel()
            labelField.setText(text)
            valueField = QtGui.QLineEdit()
            if settingKey in self.settings:
                valueField.setText(str(self.settings[settingKey]))
            valueField.textChanged.connect(update)
            hbox = QtGui.QHBoxLayout()
            hbox.addWidget(labelField)
            hbox.addWidget(valueField)
            widget = QtGui.QWidget()
            widget.setLayout(hbox)
            return widget

        def checkboxItemWidget(text, settingKey):
            def update(value):
                if value == QtCore.Qt.Checked:
                    self.settings[settingKey] = True
                else:
                    self.settings[settingKey] = False
                self.saveSettings()

            labelField = QtGui.QLabel()
            labelField.setText(text)
            valueField = QtGui.QCheckBox()
            if self.settings[settingKey] == True:
                valueField.setCheckState(QtCore.Qt.Checked)
            valueField.stateChanged.connect(update)
            hbox = QtGui.QHBoxLayout()
            hbox.addWidget(labelField)
            hbox.addWidget(valueField)
            widget = QtGui.QWidget()
            widget.setLayout(hbox)
            return widget

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(textItemWidget("Command line ({video}, {subtitles})", "PLAYER_PATH", str))
        vbox.addWidget(textItemWidget("Save path", "SAVE_PATH", str))
        vbox.addWidget(textItemWidget("Default subtitle language", "SUBTITLE_LANGUAGE", str))
        vbox.addWidget(textItemWidget("ThePirateBay url", "TPB_URL", str))
        vbox.addWidget(textItemWidget("Download speed limit (kB/s)", "DOWNLOAD_SPEED_LIMIT", int))
        vbox.addWidget(textItemWidget("Launch video when download reach X % (0 to disable)", "LAUNCH_VIDEO_PERCENT", float))

        widget = QtGui.QWidget()
        widget.setLayout(vbox)

        return widget


class SearchResult(QTreeView):
    def __init__(self):
        QTreeView.__init__(self)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Results'])
        self.setModel(self.model)
        self.setIconSize(QSize(500, 500))
        self.setUniformRowHeights(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.clicked.connect(self.populateTorrents)
        self.doubleClicked.connect(self.launchDownload)

    def populate(self, shows):
        self.model.clear()
        for show in shows:
            showRow = QStandardItem('{}'.format(show.SeriesName))
            showRow.setData(show)
            dshowRow = QStandardItem('{}'.format(show.SeriesName))
            for season in show:
                if season.season_number == 0:
                    seasonRow = QStandardItem("Special")
                else:
                    seasonRow = QStandardItem("Season {:02d}".format(season.season_number))
                seasonRow.setData(season)
                showRow.appendRow(seasonRow)
                for episode in season:
                    episodeRow = QStandardItem("{:02d} - {}".format(episode.EpisodeNumber, episode.EpisodeName))
                    episodeRow.setData(episode)
                    seasonRow.appendRow(episodeRow)
            self.model.appendRow(showRow)
        if len(shows) == 1:
            self.expand(self.model.indexFromItem(showRow))

    def populateTorrents(self, idx):
        episode = idx.data(Qt.UserRole + 1)
        if not hasattr(episode, 'season'):
            return
        search = tpb.search('{} S{:02d}E{:02d}'.format(episode.season.show.SeriesName, episode.season.season_number, episode.EpisodeNumber)).order(ORDERS.SEEDERS.DES)
        for torrent in search:
            child2 = QStandardItem("{} : {}".format(torrent.title, torrent.seeders))
            child2.setData(torrent)
            idx.model().itemFromIndex(idx).appendRow(child2)
            #print("{} : {}".format(torrent.title, torrent.seeders))

    def launchDownload(self, idx):
        torrent = idx.data(Qt.UserRole + 1)
        if not hasattr(torrent, 'title'):
            return
        Thread(target=magnetDownload, args=(torrent.magnet_link,)).start()
#        magnetDownload(torrent.magnet_link)


""""
class DownloadProgressDialog(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):      

        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        self.btn = QtGui.QPushButton('Start', self)
        self.btn.move(40, 80)
        self.btn.clicked.connect(self.doAction)

        self.timer = QtCore.QBasicTimer()
        self.step = 0
        
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('QtGui.QProgressBar')
        self.show()
        
    def timerEvent(self, e):
      
        if self.step >= 100:
        
            self.timer.stop()
            self.btn.setText('Finished')
            return
            
        self.step = self.step + 1
        self.pbar.setValue(self.step)

    def doAction(self):
      
        if self.timer.isActive():
            self.timer.stop()
            self.btn.setText('Start')
            
        else:
            self.timer.start(100, self)
            self.btn.setText('Stop')

"""

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())
