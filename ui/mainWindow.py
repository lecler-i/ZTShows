# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(640, 480)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.searchTab = QtGui.QWidget()
        self.searchTab.setObjectName(_fromUtf8("searchTab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.searchTab)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.searchLayout = QtGui.QVBoxLayout()
        self.searchLayout.setObjectName(_fromUtf8("searchLayout"))
        self.searchActionBar = QtGui.QHBoxLayout()
        self.searchActionBar.setObjectName(_fromUtf8("searchActionBar"))
        self.searchField = QtGui.QLineEdit(self.searchTab)
        self.searchField.setObjectName(_fromUtf8("searchField"))
        self.searchActionBar.addWidget(self.searchField)
        self.searchButton = QtGui.QPushButton(self.searchTab)
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.searchActionBar.addWidget(self.searchButton)
        self.searchLayout.addLayout(self.searchActionBar)
        self.resultList = QtGui.QTreeWidget(self.searchTab)
        self.resultList.setObjectName(_fromUtf8("resultList"))
        self.searchLayout.addWidget(self.resultList)
        self.verticalLayout_3.addLayout(self.searchLayout)
        self.tabWidget.addTab(self.searchTab, _fromUtf8(""))
        self.downloadsTab = QtGui.QWidget()
        self.downloadsTab.setObjectName(_fromUtf8("downloadsTab"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.downloadsTab)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.downloadsLayout = QtGui.QVBoxLayout()
        self.downloadsLayout.setObjectName(_fromUtf8("downloadsLayout"))
        self.downloadsActionBar = QtGui.QHBoxLayout()
        self.downloadsActionBar.setObjectName(_fromUtf8("downloadsActionBar"))
        self.playButton = QtGui.QPushButton(self.downloadsTab)
        self.playButton.setObjectName(_fromUtf8("playButton"))
        self.downloadsActionBar.addWidget(self.playButton)
        self.pauseButton = QtGui.QPushButton(self.downloadsTab)
        self.pauseButton.setObjectName(_fromUtf8("pauseButton"))
        self.downloadsActionBar.addWidget(self.pauseButton)
        self.deleteButton = QtGui.QPushButton(self.downloadsTab)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.downloadsActionBar.addWidget(self.deleteButton)
        self.launchButton = QtGui.QPushButton(self.downloadsTab)
        self.launchButton.setObjectName(_fromUtf8("launchButton"))
        self.downloadsActionBar.addWidget(self.launchButton)
        self.limitButton = QtGui.QPushButton(self.downloadsTab)
        self.limitButton.setObjectName(_fromUtf8("limitButton"))
        self.downloadsActionBar.addWidget(self.limitButton)
        self.downloadsLayout.addLayout(self.downloadsActionBar)
        self.downloadsList = QtGui.QTableView(self.downloadsTab)
        self.downloadsList.setObjectName(_fromUtf8("downloadsList"))
        self.downloadsLayout.addWidget(self.downloadsList)
        self.horizontalLayout_3.addLayout(self.downloadsLayout)
        self.tabWidget.addTab(self.downloadsTab, _fromUtf8(""))
        self.settingsTab = QtGui.QWidget()
        self.settingsTab.setObjectName(_fromUtf8("settingsTab"))
        self.formLayout = QtGui.QFormLayout(self.settingsTab)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.launchCommandLabel = QtGui.QLabel(self.settingsTab)
        self.launchCommandLabel.setObjectName(_fromUtf8("launchCommandLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.launchCommandLabel)
        self.launchCommandValue = QtGui.QLineEdit(self.settingsTab)
        self.launchCommandValue.setObjectName(_fromUtf8("launchCommandValue"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.launchCommandValue)
        self.savePathLabel = QtGui.QLabel(self.settingsTab)
        self.savePathLabel.setObjectName(_fromUtf8("savePathLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.savePathLabel)
        self.savePathValue = QtGui.QLineEdit(self.settingsTab)
        self.savePathValue.setObjectName(_fromUtf8("savePathValue"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.savePathValue)
        self.subtitlesLanguageLabel = QtGui.QLabel(self.settingsTab)
        self.subtitlesLanguageLabel.setObjectName(_fromUtf8("subtitlesLanguageLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.subtitlesLanguageLabel)
        self.tpbUrlLabel = QtGui.QLabel(self.settingsTab)
        self.tpbUrlLabel.setObjectName(_fromUtf8("tpbUrlLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.tpbUrlLabel)
        self.tpbUrlValue = QtGui.QLineEdit(self.settingsTab)
        self.tpbUrlValue.setObjectName(_fromUtf8("tpbUrlValue"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.tpbUrlValue)
        self.speedLimitLabel = QtGui.QLabel(self.settingsTab)
        self.speedLimitLabel.setObjectName(_fromUtf8("speedLimitLabel"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.speedLimitLabel)
        self.launchAfterLabel = QtGui.QLabel(self.settingsTab)
        self.launchAfterLabel.setObjectName(_fromUtf8("launchAfterLabel"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.launchAfterLabel)
        self.subtitlesLanguageValue = QtGui.QComboBox(self.settingsTab)
        self.subtitlesLanguageValue.setObjectName(_fromUtf8("subtitlesLanguageValue"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.subtitlesLanguageValue)
        self.speedLimitValue = QtGui.QSpinBox(self.settingsTab)
        self.speedLimitValue.setObjectName(_fromUtf8("speedLimitValue"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.speedLimitValue)
        self.launchAfterValue = QtGui.QDoubleSpinBox(self.settingsTab)
        self.launchAfterValue.setObjectName(_fromUtf8("launchAfterValue"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.launchAfterValue)
        self.tabWidget.addTab(self.settingsTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 29))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionAboutSoft = QtGui.QAction(MainWindow)
        self.actionAboutSoft.setObjectName(_fromUtf8("actionAboutSoft"))
        self.actionAboutUs = QtGui.QAction(MainWindow)
        self.actionAboutUs.setObjectName(_fromUtf8("actionAboutUs"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionSoftExit = QtGui.QAction(MainWindow)
        self.actionSoftExit.setObjectName(_fromUtf8("actionSoftExit"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSoftExit)
        self.menuHelp.addAction(self.actionAboutSoft)
        self.menuHelp.addAction(self.actionAboutUs)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.searchButton.setText(_translate("MainWindow", "Search", None))
        self.resultList.headerItem().setText(0, _translate("MainWindow", " ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.searchTab), _translate("MainWindow", "Search", None))
        self.playButton.setText(_translate("MainWindow", "Play", None))
        self.pauseButton.setText(_translate("MainWindow", "Pause", None))
        self.deleteButton.setText(_translate("MainWindow", "Delete", None))
        self.launchButton.setText(_translate("MainWindow", "Launch", None))
        self.limitButton.setText(_translate("MainWindow", "Limit", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.downloadsTab), _translate("MainWindow", "Downloads", None))
        self.launchCommandLabel.setText(_translate("MainWindow", "Launch command line (?)", None))
        self.savePathLabel.setText(_translate("MainWindow", "Save path", None))
        self.subtitlesLanguageLabel.setText(_translate("MainWindow", "Default subtitles language", None))
        self.tpbUrlLabel.setText(_translate("MainWindow", "The Pirate Bay URL (?)", None))
        self.speedLimitLabel.setText(_translate("MainWindow", "Default download speed limit (kB/s)", None))
        self.launchAfterLabel.setText(_translate("MainWindow", "Launch video after X % (?)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settingsTab), _translate("MainWindow", "Settings", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionAboutSoft.setText(_translate("MainWindow", "About ZTShows", None))
        self.actionAboutUs.setText(_translate("MainWindow", "About Us", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionSoftExit.setText(_translate("MainWindow", "Exit", None))

