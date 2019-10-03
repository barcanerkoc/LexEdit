import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtWidgets import QGridLayout, QWidget, QDesktopWidget
from qtpy import QtGui

from src.data import Data
from src.session import Session
from PyQt5 import QtCore


class View(QMainWindow):

    def mainWindow(self):
        win = QWidget(self)
        self.setCentralWidget(win)
        mainGrid = QGridLayout()

        # MenuBar Creation
        menuBar = self.menuBar()
        file = menuBar.addMenu("File")

        init = QAction("Initialize", self)
        file.addAction(init)
        init.triggered.connect(self.initialize)

        clearPrefs = QAction("Clear Preferences", self)
        file.addAction(clearPrefs)
        clearPrefs.triggered.connect(self.clearPreferences)

        session = menuBar.addMenu("Session")

        addedRootsCurrent = QAction("Roots Added in Current Session", self)
        session.addAction(addedRootsCurrent)
        addedRootsCurrent.triggered.connect(self.addedRootsWindow)

        deletedLemmasCurrent = QAction("Lemmas Deleted in Current Session", self)
        session.addAction(deletedLemmasCurrent)
        deletedLemmasCurrent.triggered.connect(self.deletedLemmasWindow)

        # Lemma ListView
        lemmaGrid = QGridLayout()
        lemmaGrid.setVerticalSpacing(10)
        mainGrid.addLayout(lemmaGrid, 0, 0)

        self.lemmas = QListWidget()
        self.lemmas.setMaximumWidth(300)
        self.lemmas.currentRowChanged.connect(self.lemmaListViewRowChanged)
        lemmasLabel = QLabel("<b>Lemmas</b>")

        self.regExTextBox = QLineEdit()
        self.regExTextBox.setMaximumWidth(300)
        self.regExTextBox.returnPressed.connect(self.populateLemmas)

        lemmaGrid.addWidget(lemmasLabel, 0, 0)
        lemmaGrid.addWidget(self.regExTextBox, 1, 0)
        lemmaGrid.addWidget(self.lemmas, 2, 0, -1, 1)

        # Roots side
        rootsGrid = QGridLayout()
        rootsGrid.setVerticalSpacing(10)
        mainGrid.addLayout(rootsGrid, 0, 1)

        self.selectedRootDef = QListWidget()
        self.selectedRootDef.setMaximumHeight(120)
        selectedRootDefLAbel = QLabel("<b>Selected Root's Definition</b>")
        rootsGrid.addWidget(selectedRootDefLAbel, 4, 0)
        rootsGrid.addWidget(self.selectedRootDef, 5, 0, 1, -1)

        self.morphAnalysis = QListWidget()
        self.morphAnalysis.setSpacing(5)
        self.morphAnalysis.currentRowChanged.connect(self.selectMorphAnalysis)
        morphAnalysisLAbel = QLabel("<b>Morphological Analysis of Current Root</b>")
        rootsGrid.addWidget(morphAnalysisLAbel, 8, 0)
        rootsGrid.addWidget(self.morphAnalysis, 9, 0, 1, -1)

        # Buttonlar ButtonBox ile değişebilir kontrol et

        buttonGrid = QGridLayout()
        mainGrid.addLayout(buttonGrid, 1, 0)

        addRootButton = QPushButton("Add Root")
        addRootButton.clicked.connect(self.addRootWindow)

        deleteRootButton = QPushButton("Delete Lemma")
        deleteRootButton.clicked.connect(self.deleteLemma)

        buttonGrid.addWidget(addRootButton, 0, 0)
        buttonGrid.addWidget(deleteRootButton, 0, 1)

        resetButton = QPushButton("Reset")
        resetButton.setMaximumWidth(100)
        mainGrid.addWidget(resetButton, 1, 1, QtCore.Qt.AlignRight)

        self.currentLemmaDef = QTreeWidget()
        self.currentLemmaDef.setMaximumHeight(120)
        self.currentLemmaDef.setMinimumWidth(150)
        self.currentLemmaDef.header().hide()
        self.currentLemmaDef.setColumnWidth(0, 20)
        self.currentLemmaDef.setSelectionMode(3)
        self.currentLemmaDef.setEditTriggers(QAbstractItemView.NoEditTriggers)
        currentLemmaDefLabel = QLabel("<b>Current Lemma's Definition</b>")

        rootsGrid.addWidget(currentLemmaDefLabel, 0, 0)
        rootsGrid.addWidget(self.currentLemmaDef, 1, 0, 1, -1)

        mainGrid.setHorizontalSpacing(20)
        win.setLayout(mainGrid)
        win.setWindowTitle("PyQt")
        win.setGeometry(100, 100, 1000, 750)

        x = app.desktop().screenGeometry().center().x()
        y = app.desktop().screenGeometry().center().y()
        win.move(int(x - win.geometry().width() / 2), int(y - win.geometry().height() / 2))

        self.data = Data()
        self.show()
        self.login()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    k = View()
    sys.exit(app.exec_())
