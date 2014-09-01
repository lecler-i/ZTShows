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

import subprocess

import libtorrent as lt
import time
import sys


tpb = TPB('https://thepiratebay.se')
tvdb = api.TVDB('81DD35DB106172E7')

SAVE_PATH = '/tmp/'


def magnetDownload(link):
    ses = lt.session()
    ses.listen_on(6881, 6891)

    # info = lt.torrent_info(sys.argv[1])
    # h = ses.add_torrent({'ti': info, 'save_path': '/tmp/'})

    h = lt.add_magnet_uri(ses, link, { 'save_path': SAVE_PATH })
    h.set_sequential_download(True)
    # h.set_download_limit(750000)

    print ('downloading metadata...')
    while (not h.has_metadata()): time.sleep(.5)

    print ('starting', h.name())
    print ('episode will be launched when the download reach 10%')

    launched = False
    while (not h.is_seed()):
        s = h.status()
        state_str = ['queued', 'checking', 'downloading metadata', \
                     'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
        print ('\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % \
               (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                s.num_peers, state_str[s.state]),)
        sys.stdout.flush()

        if not launched and s.progress >= 0.075 and s.state in [3, 4, 5]:
            os.system('vlc "/tmp/' + h.name() + '"')
            launched = True
        time.sleep(1)

    print (h.name(), 'complete')


class ShowView(QTreeView):
    def __init__(self):
        QTreeView.__init__(self)
        self.setIconSize(QSize(500, 500))
        self.setUniformRowHeights(True)
        self.clicked.connect(self.populateTorrents)
        self.doubleClicked.connect(self.download)

    def populate(self, shows):
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
            model.appendRow(showRow)

    def populateTorrents(self, idx):
        episode = idx.data(Qt.UserRole + 1)
        # if type(episode) is tpb.Torrent:
        #     return
        search = tpb.search('{} S{:02d}E{:02d}'.format(episode.season.show.SeriesName, episode.season.season_number, episode.EpisodeNumber)).order(ORDERS.SEEDERS.DES)
        for torrent in search:
            child2 = QStandardItem("{} : {}".format(torrent.title, torrent.seeders))
            child2.setData(torrent)
            idx.model().itemFromIndex(idx).appendRow(child2)
            print("{} : {}".format(torrent.title, torrent.seeders))

    def download(self, idx):
        torrent = idx.data(Qt.UserRole + 1)
        magnetDownload(torrent.magnet_link)


if __name__ == '__main__':
    app = QApplication([])

    win = QWidget()
    win.setWindowTitle('MY TORRENT WATCHER LOLZ')
    win.setMinimumSize(600, 400)

    layout = QVBoxLayout()
    win.setLayout(layout)

    view = ShowView()
    view.setSelectionBehavior(QAbstractItemView.SelectRows)
    layout.addWidget(view)

    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(['Series'])

    view.setModel(model)
    view.setUniformRowHeights(True)


    entry = QLineEdit(win)
    layout.addWidget(entry)

    def on_item_changed(curr, prev):
        print (curr.text())

    def on_text_changed():
        view.populate(tvdb.search(entry.text(), 'en'))

    entry.editingFinished.connect(on_text_changed)

    win.show()
    app.exec_()
