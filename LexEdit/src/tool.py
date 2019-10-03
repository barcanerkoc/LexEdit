import re
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QEvent, QModelIndex
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout

from src.data import Data
from PyQt5 import QtCore

from src.user import User


class Tool(QMainWindow):

    def __init__(self):
        super().__init__()
        Tool.mainWindow(self)

    def mainWindow(self):

        win = QWidget(self)
        self.setCentralWidget(win)
        mainGrid = QGridLayout()

        # MenuBar Creation
        menuBar = self.menuBar()
        file = menuBar.addMenu("File")

        init = QAction("Preferences", self)
        file.addAction(init)
        init.triggered.connect(self.initialize)

        clearPrefs = QAction("Clear Preferences", self)
        file.addAction(clearPrefs)
        clearPrefs.triggered.connect(self.clearPreferences)

        filter = menuBar.addMenu("Filter")

        # Lemma ListView
        lemmaGrid = QGridLayout()
        lemmaGrid.setVerticalSpacing(10)
        mainGrid.addLayout(lemmaGrid, 0, 0)

        self.lemmas = QListWidget()
        self.lemmas.installEventFilter(self)
        self.lemmas.setAlternatingRowColors(True)
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

        self.selectedRootDef = QTreeWidget()

        self.selectedRootDef.setMaximumHeight(120)
        self.selectedRootDef.setMinimumWidth(150)
        self.selectedRootDef.setAlternatingRowColors(True)
        self.selectedRootDef.header().hide()
        self.selectedRootDef.setColumnWidth(20, 20)
        self.selectedRootDef.setEditTriggers(QAbstractItemView.NoEditTriggers)

        selectedRootDefLAbel = QLabel("<b>Selected Root's Definition</b>")
        rootsGrid.addWidget(selectedRootDefLAbel, 4, 0)
        rootsGrid.addWidget(self.selectedRootDef, 5, 0, 1, -1)

        self.morphAnalysis = QListWidget()
        self.morphAnalysis.installEventFilter(self)
        self.morphAnalysis.setAlternatingRowColors(True)
        self.morphAnalysis.setSpacing(5)
        self.morphAnalysis.currentRowChanged.connect(self.selectMorphAnalysis)
        morphAnalysisLAbel = QLabel("<b>Morphological Analysis of Current Root</b>")
        rootsGrid.addWidget(morphAnalysisLAbel, 8, 0)
        rootsGrid.addWidget(self.morphAnalysis, 9, 0, 1, -1)

        # Buttonlar ButtonBox ile değişebilir kontrol et

        buttonGrid = QGridLayout()
        mainGrid.addLayout(buttonGrid, 1, 0)

        self.addRootButton = QPushButton("Add Root")
        self.addRootButton.clicked.connect(self.addRootWindow)
        self.addRootShortcut = QAction("Add", self)
        self.addRootShortcut.setShortcut("Shift+A")
        self.addRootButton.addAction(self.addRootShortcut)
        self.addRootShortcut.triggered.connect(self.addRootWindow)

        self.deleteLemmaButton = QPushButton("Delete Lemma")
        self.deleteLemmaButton.clicked.connect(lambda: self.deleteLemma(self.lemmas.currentItem().text()))
        self.deleteLemmaShortcut = QAction("Delete", self)
        self.deleteLemmaShortcut.setShortcut("Shift+D")
        self.deleteLemmaButton.addAction(self.deleteLemmaShortcut)
        self.deleteLemmaShortcut.triggered.connect(lambda: self.deleteLemma(self.lemmas.currentItem().text()))

        buttonGrid.addWidget(self.addRootButton, 0, 0)
        buttonGrid.addWidget(self.deleteLemmaButton, 0, 1)

        self.undoButton = QPushButton("Undo")
        self.undoButton.setEnabled(False)
        self.undoButton.setMaximumWidth(100)

        self.undoShortcut = QAction("Undo", self)
        self.undoShortcut.setShortcut("Ctrl+Z")
        self.undoButton.addAction(self.undoShortcut)

        mainGrid.addWidget(self.undoButton, 1, 1, QtCore.Qt.AlignRight)

        self.currentLemmaDef = TestTree()

        self.currentLemmaDef.installEventFilter(self)
        self.currentLemmaDef.itemDropped.connect(self.actionOnItemDropped)

        self.currentLemmaDef.setDragEnabled(True)
        self.currentLemmaDef.setSelectionMode(QAbstractItemView.SingleSelection)
        self.currentLemmaDef.viewport().setAcceptDrops(True)
        self.currentLemmaDef.setDropIndicatorShown(True)
        self.currentLemmaDef.setDragDropMode(QAbstractItemView.InternalMove)

        self.currentLemmaDef.setMaximumHeight(420)
        self.currentLemmaDef.setMinimumWidth(150)
        self.currentLemmaDef.setAlternatingRowColors(True)
        self.currentLemmaDef.header().hide()
        self.currentLemmaDef.setColumnWidth(20, 20)
        # self.currentLemmaDef.setSelectionMode(3)
        self.currentLemmaDef.setEditTriggers(QAbstractItemView.NoEditTriggers)
        currentLemmaDefLabel = QLabel("<b>Current Lemma's Definition</b>")

        self.currentLemmaDef.installEventFilter(self)

        rootsGrid.addWidget(currentLemmaDefLabel, 0, 0)
        rootsGrid.addWidget(self.currentLemmaDef, 1, 0, 1, -1)

        moveUpAct = QAction("MoveUp", self)
        moveUpAct.setShortcut(QKeySequence("W"))
        self.addAction(moveUpAct)
        moveUpAct.triggered.connect(self.moveUp)

        moveDownAct = QAction("MoveDown", self)
        moveDownAct.setShortcut(QKeySequence("S"))
        self.addAction(moveDownAct)
        moveDownAct.triggered.connect(self.moveDown)

        changeFocusRight = QAction("Left", self)
        changeFocusRight.setShortcut("D")
        self.addAction(changeFocusRight)
        changeFocusRight.triggered.connect(lambda: self.changeFocus("D"))

        changeFocusLeft = QAction("Left", self)
        changeFocusLeft.setShortcut("A")
        self.addAction(changeFocusLeft)
        changeFocusLeft.triggered.connect(lambda: self.changeFocus("A"))

        noFilter = QAction("No Filter", self)
        filter.addAction(noFilter)
        noFilter.triggered.connect(self.noFilter)

        addedRootsCurrent = QAction("Roots Added in Current Session", self)
        filter.addAction(addedRootsCurrent)
        addedRootsCurrent.triggered.connect(self.filterAddedRoots)

        deletedLemmasCurrent = QAction("Lemmas Deleted in Current Session", self)
        filter.addAction(deletedLemmasCurrent)
        deletedLemmasCurrent.triggered.connect(self.filterDeletedLemmas)

        mainGrid.setHorizontalSpacing(20)
        win.setLayout(mainGrid)
        win.setWindowTitle("PyQt")
        win.setGeometry(100, 100, 1000, 750)

        x = app.desktop().screenGeometry().center().x()
        y = app.desktop().screenGeometry().center().y()
        win.move(int(x - win.geometry().width() / 2), int(y - win.geometry().height() / 2))

        self.setWindowTitle("LexEdit")
        self.show()
        self.loginPanel()

        if self.data.session.user.username != "admin":
            self.loadLastSession()
            wordWrap = ItemWordWrap(self)
            self.currentLemmaDef.setItemDelegate(wordWrap)
            self.selectedRootDef.setItemDelegate(wordWrap)

    def closeEvent(self, event):

        if self.data.session.user.username == "admin":
            return

        if len(self.lemmas.selectedItems()):
            self.data.session.endOfSession(self.regExTextBox.text(), self.lemmas.currentItem().text())
        else:
            self.data.session.endOfSession(self.regExTextBox.text(), "")
        event.accept()

    def loadLastSession(self):

        lastSession = self.data.session.loadLastSession()

        if not len(lastSession[0]):
            return

        self.regExTextBox.setText(lastSession[0])
        self.populateLemmas()

        if len(lastSession[1]):
            item = self.lemmas.findItems(lastSession[1], Qt.MatchExactly)[0]
            item.setSelected(True)
            self.lemmas.setCurrentRow(self.lemmas.row(item))
            self.lemmas.scrollToItem(item, QAbstractItemView.PositionAtCenter)

        self.lemmas.setFocus()

    def loginPanel(self):

        loginDialog = QDialog()
        grid = QGridLayout()
        loginDialog.setLayout(grid)

        usernameLabel = QLabel("Username:")
        usernameText = QLineEdit()
        grid.addWidget(usernameLabel, 0, 0)
        grid.addWidget(usernameText, 0, 1, 1, -1)

        passwordLabel = QLabel("Password:")
        passwordText = QLineEdit()
        passwordText.setEchoMode(QLineEdit.Password)
        grid.addWidget(passwordLabel, 1, 0)
        grid.addWidget(passwordText, 1, 1, 1, -1)

        userFolderPathButton = QPushButton("Users File Path")
        userFolderPathButton.clicked.connect(lambda: self.fileBrowser("Users Folder"))
        self.usersFolderPath = QLineEdit()
        grid.addWidget(userFolderPathButton, 2, 0)
        grid.addWidget(self.usersFolderPath, 2, 1, 1, -1)

        self.usersFolderPath.setText(Data.getUsersFolderPath())

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(loginDialog.accept)
        buttons.rejected.connect(loginDialog.reject)
        grid.addWidget(buttons, 3, 2)

        # grid.setHorizontalSpacing(20)

        loginDialog.accepted.connect(lambda: self.authenticate(usernameText.text(), passwordText.text()))
        loginDialog.rejected.connect(loginDialog.close)
        loginDialog.rejected.connect(sys.exit)

        loginDialog.setWindowModality(Qt.ApplicationModal)
        loginDialog.exec_()

    def adminPanel(self):

        adminDialog = QDialog()
        grid = QGridLayout()
        adminDialog.setLayout(grid)

        adminDialog.setMinimumSize(500, 300)
        adminDialog.setMaximumSize(825, 500)

        self.tabs = QTabWidget()
        usersData = self.data.session.user.getAllAnnotatorData()

        for x in range(len(usersData)):

            tab = QWidget()
            self.tabs.addTab(tab, usersData[x][0])
            self.createTabContent(tab, usersData[x])
            self.tabs.setTabText(x, usersData[x][0])

        adminTab = QWidget()
        self.tabs.addTab(adminTab, "Admin")

        adminGrid = QGridLayout()
        addedRootsWindow = QListWidget()
        addedRootsWindow.setSelectionMode(QAbstractItemView.NoSelection)
        addedRootsWindow.setMinimumSize(200, 200)
        addedRootsWindow.setMaximumSize(400, 400)

        deletedLemmasWindow = QListWidget()
        deletedLemmasWindow.setSelectionMode(QAbstractItemView.NoSelection)
        deletedLemmasWindow.setMinimumSize(200, 200)
        deletedLemmasWindow.setMaximumSize(400, 400)

        createDictButton = QPushButton("Create Dictionary")
        createDictButton.setMaximumWidth(100)
        createDictButton.clicked.connect(self.createDictAction)

        buttons = QDialogButtonBox(Qt.Horizontal)
        buttons.addButton(createDictButton, QDialogButtonBox.ActionRole)

        createNewUserButton = QPushButton("Create New User")
        createNewUserButton.setMaximumWidth(100)
        createNewUserButton.clicked.connect(self.createNewUserDialog)

        adminGrid.addWidget(createNewUserButton, 0, 1, QtCore.Qt.AlignRight)
        adminGrid.addWidget(addedRootsWindow, 1, 0)
        adminGrid.addWidget(deletedLemmasWindow, 1, 1)
        adminGrid.addWidget(buttons, 2, 1)

        adminTab.setLayout(adminGrid)

        self.tabs.setTabText(len(usersData), "Admin")

        grid.addWidget(self.tabs, 0, 0)

        adminDialog.rejected.connect(self.tabs.close)
        adminDialog.rejected.connect(sys.exit)

        adminDialog.setWindowModality(Qt.ApplicationModal)
        adminDialog.exec_()

    def createTabContent(self, tab, data):

        grid = QGridLayout()

        addedRootsWindow = QListWidget()
        addedRootsWindow.setSelectionMode(QAbstractItemView.ExtendedSelection)
        addedRootsWindow.setMinimumSize(200, 200)
        addedRootsWindow.setMaximumSize(400, 400)

        deletedLemmasWindow = QListWidget()
        deletedLemmasWindow.setSelectionMode(QAbstractItemView.ExtendedSelection)
        deletedLemmasWindow.setMinimumSize(200, 200)
        deletedLemmasWindow.setMaximumSize(400, 400)

        approveButton = QPushButton("Approve")
        approveButton.setMaximumWidth(100)
        approveButton.clicked.connect(self.approveAction)

        createDictButton = QPushButton("Create Dictionary")
        createDictButton.setMaximumWidth(100)
        createDictButton.clicked.connect(self.createDictAction)

        buttons = QDialogButtonBox(Qt.Horizontal)
        buttons.addButton(approveButton, QDialogButtonBox.ActionRole)
        buttons.addButton(createDictButton, QDialogButtonBox.ActionRole)

        createNewUserButton = QPushButton("Create New User")
        createNewUserButton.setMaximumWidth(100)
        createNewUserButton.clicked.connect(self.createNewUserDialog)

        grid.addWidget(createNewUserButton, 0, 1, QtCore.Qt.AlignRight)
        grid.addWidget(addedRootsWindow, 1, 0)
        grid.addWidget(deletedLemmasWindow, 1, 1)
        grid.addWidget(buttons, 2, 1)

        if len(data[1]):
            for tup in data[1]:
                addedRootsWindow.addItem(tup[0] + "\t" + tup[1])

        if len(data[2]):
            deletedLemmasWindow.addItems(data[2])

        tab.setLayout(grid)

    def approveAction(self):

        """
        Admin Function

        This function takes all approved items (both added roots and deleted lemmas) and
        pass them to both the admin's appropriate lists and admin's tab.

        By PyQT, children of the current tab ordered. The order is:
        0 - Layout of the tab
        1 - Create New User Button
        2 - Current User's added roots list
        3 - Current User's deleted lemmas list
        """

        approvedAddedItems = self.tabs.currentWidget().children()[2].selectedItems()
        for item in approvedAddedItems:
            self.data.session.user.approveAddedRoot(item.text())
            self.tabs.widget(self.tabs.count() - 1).children()[2].addItem(item)

        approvedDeletedItems = self.tabs.currentWidget().children()[3].selectedItems()
        for item in approvedDeletedItems:
            self.data.session.user.approveDeletedLemma(item.text())
            self.tabs.widget(self.tabs.count() - 1).children()[3].addItem(item)

        # self.tabs.widget(self.tabs.count() - 1).update()
        # self.tabs.widget(self.tabs.count() - 1).update()

    def createDictAction(self):

        """
        Admin Function

        This function takes desired dictionary name from the user and pass it to
        admin's appropriate function to initiate dictionary creation
        """

        dictNameDialog = QDialog()
        grid = QGridLayout()
        dictNameDialog.setLayout(grid)

        dictNameLabel = QLabel("Name of the Dictionary : ")
        dictNameText = QLineEdit()
        grid.addWidget(dictNameLabel, 0, 0)
        grid.addWidget(dictNameText, 0, 1, 1, -1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dictNameDialog.accept)
        buttons.rejected.connect(dictNameDialog.reject)
        grid.addWidget(buttons, 1, 1)

        dictNameDialog.accepted.connect(lambda: self.data.session.user.createDictionary(dictNameText.text()))
        dictNameDialog.rejected.connect(dictNameDialog.close)

        dictNameDialog.setWindowModality(Qt.ApplicationModal)
        dictNameDialog.exec_()

    def createNewUserDialog(self):

        newUserDialog = QDialog()
        grid = QGridLayout()
        newUserDialog.setLayout(grid)

        usernameTextLabel = QLabel("username : ")
        usernameText = QLineEdit()

        passwordTextLabel = QLabel("password : ")
        passwordText = QLineEdit()

        grid.addWidget(usernameTextLabel, 0, 0)
        grid.addWidget(usernameText, 0, 1)
        grid.addWidget(passwordTextLabel, 1, 0)
        grid.addWidget(passwordText, 1, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(newUserDialog.accept)
        buttons.rejected.connect(newUserDialog.reject)
        grid.addWidget(buttons, 2, 1)

        newUserDialog.accepted.connect(lambda: self.data.session.user.createUser(usernameText.text(), passwordText.text()))
        newUserDialog.rejected.connect(newUserDialog.close)

        newUserDialog.setWindowModality(Qt.ApplicationModal)
        newUserDialog.exec_()

    def authenticate(self, username, password):

        Data.setUsersFolderPath(self.usersFolderPath.text())

        if not User.login(username, password):
            self.loginPanel()

        self.data = Data(username)

        if username == "admin":
            self.adminPanel()

    def initialize(self):

        self.initDialog = QDialog()
        grid = QGridLayout()
        self.initDialog.setLayout(grid)

        selectJSONButton = QPushButton("Select Dictionary")
        selectJSONButton.clicked.connect(lambda: self.fileBrowser("JSON"))
        self.JSONPath = QLineEdit()
        self.JSONPath.setReadOnly(True)
        grid.addWidget(selectJSONButton, 0, 0)
        grid.addWidget(self.JSONPath, 0, 1, 1, -1)

        morpAnalyzerURL = QLabel("Morphological Analyzer URL:")
        self.analyzerURL = QLineEdit()
        grid.addWidget(morpAnalyzerURL, 1, 0)
        grid.addWidget(self.analyzerURL, 1, 1, 1, -1)

        selectPOSPyButton = QPushButton("Select getPOS.py")
        selectPOSPyButton.clicked.connect(lambda: self.fileBrowser("POS.PY"))
        self.getPOSPyPath = QLineEdit()
        self.getPOSPyPath.setReadOnly(True)
        grid.addWidget(selectPOSPyButton, 2, 0)
        grid.addWidget(self.getPOSPyPath, 2, 1, 1, -1)

        selectSuffixesPyButton = QPushButton("Select getSuffixes.py")
        selectSuffixesPyButton.clicked.connect(lambda: self.fileBrowser("suffix.PY"))
        self.getSuffixesPyPath = QLineEdit()
        self.getSuffixesPyPath.setReadOnly(True)
        grid.addWidget(selectSuffixesPyButton, 3, 0)
        grid.addWidget(self.getSuffixesPyPath, 3, 1, 1, -1)

        selectSessionStorePathButton = QPushButton("Select Session Store Path")
        selectSessionStorePathButton.clicked.connect(lambda: self.fileBrowser("Folder"))
        self.usersFilePath = QLineEdit()
        self.usersFilePath.setReadOnly(True)
        grid.addWidget(selectSessionStorePathButton, 4, 0)
        grid.addWidget(self.usersFilePath, 4, 1, 1, -1)

        # Buttonlar ButtonBox ile değişebilir kontrol et

        acceptButton = QPushButton("Accept")
        acceptButton.clicked.connect(lambda: self.closeInitialize("accept"))
        grid.addWidget(acceptButton, 5, 3)

        rejectButton = QPushButton("Reject")
        rejectButton.clicked.connect(lambda: self.closeInitialize("reject"))
        grid.addWidget(rejectButton, 5, 4)

        self.fillPreferences()

        self.initDialog.setWindowModality(Qt.ApplicationModal)
        self.initDialog.exec_()

    def fileBrowser(self, fileType):

        if fileType == "JSON":
            fileBrowser = QFileDialog()
            fileBrowser.setDefaultSuffix(".json")
            filename = fileBrowser.getOpenFileName(None, "Select JSON", "C:\\", "JSON (*.json)")

            if len(filename[0]) > 0:
                self.JSONPath.setText(filename[0])

        elif fileType == "POS.PY":
            fileBrowser = QFileDialog()
            fileBrowser.setDefaultSuffix(".py")
            filename = fileBrowser.getOpenFileName(None, "Select POS.PY", "C:\\", "PY (*.py)")

            if len(filename[0]) > 0:
                self.getPOSPyPath.setText(filename[0])

        elif fileType == "suffix.PY":
            fileBrowser = QFileDialog()
            fileBrowser.setDefaultSuffix(".py")
            filename = fileBrowser.getOpenFileName(None, "Select suffix.PY", "C:\\", "PY (*.py)")

            if len(filename[0]) > 0:
                self.getSuffixesPyPath.setText(filename[0])

        elif fileType == "Folder":
            fileBrowser = QFileDialog()
            fileBrowser.setFileMode(QFileDialog.DirectoryOnly)
            filename = QFileDialog.getExistingDirectory(None, "Select Folder", "C:\\")

            if len(filename) > 0:
                self.usersFilePath.setText(filename)

        elif fileType == "Users Folder":
            fileBrowser = QFileDialog()
            fileBrowser.setFileMode(QFileDialog.DirectoryOnly)
            filename = QFileDialog.getExistingDirectory(None, "Select Folder", "C:\\")

            if filename.split("/")[-1] == "Users":
                self.usersFolderPath.setText(filename)

    def closeInitialize(self, option):

        if option == "accept":
            self.initDialog.accept()

            if len(self.JSONPath.text()) > 0:
                self.data.dictPath = self.JSONPath.text()
                self.data.loadData()

            if len(self.analyzerURL.text()) > 0:
                self.data.analyzerURL = self.analyzerURL.text()

            if len(self.getPOSPyPath.text()) > 0:
                self.data.POSPyPath = self.getPOSPyPath.text()

            if len(self.getSuffixesPyPath.text()) > 0:
                self.data.suffixesPyPath = self.getSuffixesPyPath.text()

            if len(self.usersFilePath.text()) > 0:
                self.data.session.initFilePath = self.usersFilePath.text()

        else:
            self.initDialog.reject()

    def fillPreferences(self):

        if len(self.data.dictPath) > 0:
            self.JSONPath.setText(self.data.dictPath)

        if len(self.data.analyzerURL) > 0:
            self.analyzerURL.setText(self.data.analyzerURL)

        if len(self.data.POSPyPath) > 0:
            self.getPOSPyPath.setText(self.data.POSPyPath)

        if len(self.data.suffixesPyPath) > 0:
            self.getSuffixesPyPath.setText(self.data.suffixesPyPath)

    def clearPreferences(self):

        self.data.setDefaultPreferences()

    def addRootWindow(self):

        addRootDialog = QDialog()
        grid = QGridLayout()
        addRootDialog.setLayout(grid)

        rootTextField = QLineEdit()
        grid.addWidget(rootTextField, 0, 0, 1, 3)

        POSComboBox = QComboBox()
        POSComboBox.addItems(["NOM", "VS", "PRED", "NUM", "POSTP", "INTERJ"])
        grid.addWidget(POSComboBox, 1, 0, 1, 3)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(addRootDialog.accept)
        buttons.rejected.connect(addRootDialog.reject)
        grid.addWidget(buttons, 5, 2)

        grid.setHorizontalSpacing(20)

        addRootDialog.accepted.connect(lambda: self.addRoot(rootTextField.text(), POSComboBox.currentText()))
        addRootDialog.rejected.connect(addRootDialog.close)

        addRootDialog.setWindowModality(Qt.ApplicationModal)
        addRootDialog.exec_()

    def populateLemmas(self):

        if not len(self.regExTextBox.text()):
            return

        self.lemmas.clear()

        regData = self.data.search(self.regExTextBox.text())

        if not len(regData[0]) or regData[0][0] == "error":
            palette = QPalette()
            palette.setColor(QPalette.Base, Qt.red)
            self.regExTextBox.setPalette(palette)
            return
        else:
            palette = QPalette()
            palette.setColor(QPalette.Base, Qt.green)
            self.regExTextBox.setPalette(palette)

        self.lemmas.addItems(regData[0])

        for x in range(len(regData[1])):

            self.reorganizeLemma(regData[1][x])

        for x in range(len(regData[2])):

            item = self.lemmas.findItems(regData[2][x], Qt.MatchExactly)
            if len(item):

                item[0].setBackground(Qt.red)

    def reorganizeLemma(self, root):

        charIndex = 0
        lemmaIndex = 0
        limit = self.lemmas.count()
        while lemmaIndex < limit:

            if charIndex == len(root):
                break

            if len(self.lemmas.item(lemmaIndex).text()) < len(root) or ord(self.lemmas.item(lemmaIndex).text()[charIndex]) == 32 or ord(root[charIndex]) == 32:

                lemmaIndex += 1

                if self.lemmas.count() == lemmaIndex:
                    charIndex += 1
                    lemmaIndex = 0

                continue

            if ord(self.lemmas.item(lemmaIndex).text()[charIndex]) > ord(root[charIndex]):

                limit = lemmaIndex
                lemmaIndex = 0

            else:

                lemmaIndex += 1

                if self.lemmas.count() == lemmaIndex:
                    charIndex += 1
                    lemmaIndex = 0

        for x in range(lemmaIndex - 1, -1, -1):

            if len(self.lemmas.item(x).text()) < len(root) or self.lemmas.item(x).text()[charIndex] is not root[charIndex]:
                break

            if len(self.lemmas.item(x).text()) > len(root):
                lemmaIndex -= 1

        item = QListWidgetItem(root)
        item.setBackground(Qt.green)
        self.lemmas.insertItem(lemmaIndex, item)

    def lemmaListViewRowChanged(self, rowIndex):

        if rowIndex == -1:
            return

        self.lemmasRowIndex = rowIndex

        if not (self.lemmas.item(rowIndex).background() == Qt.red or self.lemmas.item(rowIndex).background() == Qt.green):

            self.addRootButton.setEnabled(True)
            self.deleteLemmaButton.setEnabled(True)

            self.undoButton.setEnabled(False)
            self.undoButton.setText("Undo")

        else:

            self.addRootButton.setEnabled(False)
            self.deleteLemmaButton.setEnabled(False)

            self.undoTypeCheck(rowIndex)

        self.currentLemmaDef.clear()
        self.morphAnalysis.clear()
        self.selectedRootDef.clear()

        defData = self.data.getCurrentLemmaDef(str(self.lemmas.item(rowIndex).text()))

        for x in range(len(defData)):

            self.currentLemmaDef.insertTopLevelItem(x, QTreeWidgetItem(["(" + Data.intToRomanNumeral(x + 1) + ")" + "%15s" % str(defData[x][0])]))

            for y in range(len(defData[x][1])):

                # inferred_pos, gloss
                self.currentLemmaDef.topLevelItem(x).addChild(QTreeWidgetItem([str(y + 1) + "%11s" % (defData[x][1][y][0]) + "\t" + defData[x][1][y][1]]))

        self.currentLemmaDef.expandAll()

        if str(self.lemmas.item(rowIndex).text()) in self.data.session.collapsedSenses:

            collapseData = self.data.session.collapsedSenses[str(self.lemmas.item(rowIndex).text())].split(" ")
            childrenRowsCombined = {}

            for index in range(len(collapseData)):

                parentIndex = collapseData[index][1:-1].split("|")[0]

                parentWidget = self.currentLemmaDef.topLevelItem(int(parentIndex) - 1)
                childrenIndexes = list(map(int, collapseData[index][1:-1].split("|")[1].split(",")))

                if parentIndex in childrenRowsCombined:
                    childrenRowsCombined[parentIndex][0].extend(childrenIndexes)
                else:
                    childrenRowsCombined[parentIndex] = [childrenIndexes, []]

                collapsedWidget = QTreeWidgetItem(["[" + collapseData[index][1:-1].split("|")[1] + "]"])

                for childIndex in range(len(childrenIndexes)):
                    adjustment = childrenIndexes[childIndex] - self.adjustCollapsedRow(childrenRowsCombined[parentIndex], childrenIndexes[childIndex]) - 1
                    child = parentWidget.takeChild(childrenIndexes[childIndex] - self.adjustCollapsedRow(childrenRowsCombined[parentIndex], childrenIndexes[childIndex]) - 1)
                    collapsedWidget.addChild(child)

                # parentWidget.insertChild(childrenIndexes[0] - 1, collapsedWidget)
                k = childrenIndexes[0] - self.adjustCollapsedRow(childrenRowsCombined[parentIndex], childrenIndexes[0])
                parentWidget.insertChild(childrenIndexes[0] - self.adjustCollapsedRow(childrenRowsCombined[parentIndex], childrenIndexes[0]) - 1, collapsedWidget)

                childrenRowsCombined[parentIndex][1].append(childrenIndexes[0])

        self.currentLemmaDef.expandAll()

        morphs = self.data.getMorphologicalAnalysis(str(self.lemmas.item(rowIndex).text()))

        if not len(morphs):
            self.morphAnalysis.addItem("Can not connect to http://ddil.isikun.edu.tr/mortur/ check your internet connection")
            return

        for x in range(len(morphs)):

            # self.morphAnalysis.addItem(QListWidgetItem("\t\t" + morphs[x][0] + "\n" + morphs[x][1]))
            self.morphAnalysis.addItem(QListWidgetItem(morphs[x][1]))
            # self.morphAnalysis.addItem(QListWidgetItem("%100s" % (morphs[x][0]) + "\n" + "%-50s" % (morphs[x][1].split("\t")[0]) + "%-20s" % (morphs[x][1].split("\t")[1]) + (morphs[x][1].split("\t")[2])))

    def adjustCollapsedRow(self, indexes, curIndex):

        adjustment = 0
        for ind in range(len(indexes[0])):
            if indexes[0][ind] < curIndex:
                adjustment += 1

        for ind in range(len(indexes[1])):
            if indexes[1][ind] < curIndex:
                adjustment -= 1

        return adjustment

    def selectMorphAnalysis(self, rowIndex):

        if rowIndex == -1:
            return

        self.morpRowIndex = rowIndex

        self.selectedRootDef.clear()

        selectedRootDef = self.data.getSelectedRootDef(str(self.morphAnalysis.item(rowIndex).text()))

        for x in range(len(selectedRootDef)):

            # Roma rakamları ile değiştirilecek. Fonksiyon değil Library yazmak daha mantıklı
            self.selectedRootDef.insertTopLevelItem(x, QTreeWidgetItem(["(" + str(x + 1) + ")" + "%8s" % str(selectedRootDef[x][0])]))

            for y in range(len(selectedRootDef[x][1])):

                # inferred_pos, gloss
                self.selectedRootDef.topLevelItem(x).addChild(QTreeWidgetItem(["%7s" % (selectedRootDef[x][1][y][0]) + "\t" + selectedRootDef[x][1][y][1]]))

        self.selectedRootDef.expandAll()

    def addRoot(self, root, POSTag):

        self.data.session.addRoot(root, POSTag)
        self.reorganizeLemma(root)
        self.addRootButton.setEnabled(False)
        self.deleteLemmaButton.setEnabled(False)
        self.undoTypeCheck(self.lemmas.currentRow())

    def deleteLemma(self, deletedLemma):

        deletedLemmasJSON = self.data.getDeletedLemmasJSON(self.lemmas.currentItem().text())
        self.lemmas.currentItem().setBackground(Qt.red)
        self.data.session.deletedLemmas.append(deletedLemmasJSON)
        self.data.session.deleteLemma(deletedLemma)
        self.addRootButton.setEnabled(False)
        self.deleteLemmaButton.setEnabled(False)
        self.undoTypeCheck(self.lemmas.currentRow())

    def undoTypeCheck(self, rowIndex):

        if self.lemmas.item(rowIndex).background() == Qt.red:

            self.undoButton.setEnabled(True)
            self.undoButton.setText("Undo Delete")
            self.undoButton.clicked.connect(self.undoDelete)
            self.undoShortcut.triggered.connect(self.undoDelete)

        elif self.lemmas.item(rowIndex).background() == Qt.green:

            self.undoButton.setEnabled(True)
            self.undoButton.setText("Undo Add")
            self.undoButton.clicked.connect(self.undoAdd)
            self.undoShortcut.triggered.connect(self.undoAdd)

    def undoAdd(self):

        self.data.session.undoAdd(self.lemmas.currentItem().text())
        row = self.lemmas.currentRow()
        self.lemmas.takeItem(row)

        if self.lemmas.count() - 1 == row and row - 1 != -1:
            row -= 1

        self.lemmas.setCurrentRow(row)
        self.undoButton.clicked.disconnect()
        self.undoShortcut.triggered.disconnect()

        self.undoButton.setEnabled(False)
        self.undoButton.setText("Undo")
        self.lemmas.setFocus()

    def undoDelete(self):

        self.data.session.undoDelete(self.lemmas.currentItem().text())
        self.lemmas.currentItem().setBackground(Qt.white)
        self.undoButton.clicked.disconnect()
        self.undoShortcut.triggered.disconnect()

        self.undoButton.setEnabled(False)
        self.undoButton.setText("Undo")
        self.lemmas.setFocus()

    def noFilter(self):

        self.regExTextBox.setEnabled(True)
        self.populateLemmas()

    def filterAddedRoots(self):

        self.regExTextBox.setEnabled(False)
        self.lemmas.clear()

        for x in range(len(self.data.session.addedRoots)):
            self.lemmas.addItem(self.data.session.addedRoots[x][0])

    def filterDeletedLemmas(self):

        self.regExTextBox.setEnabled(False)
        self.lemmas.clear()
        self.lemmas.addItems(self.data.session.deletedLemmasOnlyLemma)

    def eventFilter(self, obj, event):

        if (obj == self.lemmas or obj == self.morphAnalysis) and event.type() == QEvent.FocusIn:

            if obj == self.lemmas:
                # print("lemmas")
                self.focusedTab = "lemmas"
            elif obj == self.morphAnalysis:
                # print("morp")
                self.focusedTab = "morp"
            else:
                # print("else")
                self.focusedTab = "else"

        return super(Tool, self).eventFilter(obj, event)

    def changeFocus(self, direction):

        if self.focusedTab == "lemmas" and direction == "D":
            self.lemmas.clearSelection()
            self.morphAnalysis.setFocus()
            self.morphAnalysis.setCurrentRow(0)

        elif self.focusedTab == "morp" and direction == "A":
            self.morphAnalysis.clearSelection()
            self.lemmas.setFocus()
            self.lemmas.setCurrentRow(self.lemmasRowIndex)

    def moveUp(self):

        if self.focusedTab == "lemmas":

            if self.lemmasRowIndex == 0:
                return

            self.lemmasRowIndex -= 1
            self.lemmas.setCurrentRow(self.lemmasRowIndex)

        elif self.focusedTab == "morp":

            if self.morpRowIndex == 0:
                return

            self.morpRowIndex -= 1
            self.morphAnalysis.setCurrentRow(self.morpRowIndex)

    def moveDown(self):

        if self.focusedTab == "lemmas":

            if self.lemmasRowIndex == self.lemmas.count() - 1:
                return

            self.lemmasRowIndex += 1
            self.lemmas.setCurrentRow(self.lemmasRowIndex)

        elif self.focusedTab == "morp":

            if self.morpRowIndex == self.morphAnalysis.count() - 1:
                return

            self.morpRowIndex += 1
            self.morphAnalysis.setCurrentRow(self.morpRowIndex)

    def actionOnItemDropped(self, action, signalContent):

        if action:
            if self.lemmas.currentItem().text() in self.data.session.collapsedSenses:

                if signalContent[1:-1].split("|")[1] in self.data.session.collapsedSenses[self.lemmas.currentItem().text()]:
                    self.data.session.collapsedSenses[self.lemmas.currentItem().text()] = self.data.session.collapsedSenses[self.lemmas.currentItem().text()].replace(signalContent[:signalContent.rfind("|")] + "]", signalContent[:2] + signalContent[signalContent.rfind("|"):])
                else:
                    self.data.session.collapsedSenses[self.lemmas.currentItem().text()] += " " + signalContent

            else:
                self.data.session.collapsedSenses[self.lemmas.currentItem().text()] = signalContent
        else:

            splittedData = self.data.session.collapsedSenses[self.lemmas.currentItem().text()].split(" ")
            if len(splittedData) == 1:

                del self.data.session.collapsedSenses[self.lemmas.currentItem().text()]

            elif len(splittedData) > 1:

                temp = ""

                index = 0
                while index < len(splittedData):

                    if int(signalContent.split("|")[0]) != int(splittedData[index][1:-1].split("|")[0]):
                        index += 1
                        continue

                    if signalContent.split("|")[1] in splittedData[index][1:-1].split("|")[1]:
                        index += 1
                        continue

                    if index == len(splittedData) - 1:
                        temp += splittedData[index]
                    else:
                        temp += splittedData[index] + " "

                    index += 1

                self.data.session.collapsedSenses[self.lemmas.currentItem().text()] = temp


class TestTree(QTreeWidget):

    itemDropped = QtCore.pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super(QTreeWidget, self).__init__(parent)
        self.dragEventPos = None

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):

            # encoded = QByteArray(event.mimeData().data("application/x-qabstractitemmodeldatalist"))
            # stream = QDataStream(encoded, QIODevice.ReadOnly)

            """
            data = event.mimeData()
            source_item = QStandardItemModel()
            source_item.dropMimeData(data, QtCore.Qt.CopyAction, 0, 0, QtCore.QModelIndex())
            print(source_item.item(0, 0).text())
            """
            print(event.pos())
            dropIndex = QModelIndex(self.indexAt(event.pos()))
            dragEnterIndex = QModelIndex(self.indexAt(self.dragEventPos))
            # dropIndicator = QAbstractItemView.dropIndicatorPosition(self)

            # k = dropIndex.data(0).split(" ")[0]
            # c = self.checkDepth(dropIndex)

            if self.checkParents(dropIndex, dragEnterIndex) and not self.checkDepth(dropIndex):

                if not dragEnterIndex.data(0).find("[") == 0 and self.checkDepth(dragEnterIndex) == 0:
                    # super(QTreeWidget, self).dropEvent(event)

                    if dropIndex.data(0).find("[") == 0:

                        temp = self.itemFromIndex(dropIndex).data(0, 0)[1:-1]
                        oldText = temp
                        nums = self.itemFromIndex(dropIndex).data(0, 0)[1:-1].split(",")

                        parent = self.itemFromIndex(QModelIndex(dropIndex))
                        newChild = self.itemFromIndex(QModelIndex(dragEnterIndex)).parent().takeChild(dragEnterIndex.row())

                        check = True
                        for index in range(len(nums)):

                            if int(dragEnterIndex.data(0).split(" ")[0]) < int(nums[index]):
                                temp = "[" + temp[0:(2 * index)] + str(dragEnterIndex.data(0).split(" ")[0]) + "," + temp[(2 * index):] + "]" # düzeltmeeeeeeeeeeeeeeeeeeeeeeee
                                parent.insertChild(index, newChild)
                                if index == 0:
                                    parent.parent().insertChild(dragEnterIndex.row(), parent.parent().takeChild(dropIndex.row() - 1))
                                check = False
                                break

                        if check:
                            temp = "[" + temp + "," + str(dragEnterIndex.data(0).split(" ")[0]) + "]"
                            parent.addChild(newChild)

                        parent.setData(0, 0, temp)
                        k = "[" + str(self.indexOfTopLevelItem(parent.parent()) + 1) + "|" + oldText + "|" + temp[1:]
                        self.itemDropped.emit(True, "[" + str(self.indexOfTopLevelItem(parent.parent()) + 1) + "|" + oldText + "|" + temp[1:])

                    else:

                        if dropIndex.row() < dragEnterIndex.row():

                            firstChildModelIndex = QModelIndex(dropIndex)
                            secondChildModelIndex = QModelIndex(dragEnterIndex)

                        elif dropIndex.row() > dragEnterIndex.row():

                            firstChildModelIndex = QModelIndex(dragEnterIndex)
                            secondChildModelIndex = QModelIndex(dropIndex)

                        collapsedNums = QTreeWidgetItem(["[" + firstChildModelIndex.data(0).split(" ")[0] + "," + secondChildModelIndex.data(0).split(" ")[0] + "]"])
                        parent = self.itemFromIndex(firstChildModelIndex).parent()
                        fn = firstChildModelIndex.row()
                        sn = secondChildModelIndex.row()
                        secondChild = self.itemFromIndex(secondChildModelIndex).parent().takeChild(secondChildModelIndex.row())
                        firstChild = self.itemFromIndex(firstChildModelIndex).parent().takeChild(firstChildModelIndex.row())

                        parent.insertChild(firstChildModelIndex.row(), collapsedNums)

                        collapsedNums.addChild(firstChild)
                        collapsedNums.addChild(secondChild)

                        collapsedNums.setExpanded(True)
                        k = "[" + str(self.indexOfTopLevelItem(parent) + 1) + "|" + str(firstChildModelIndex.row() + 1) + "," + str(secondChildModelIndex.row() + 1) + "]"
                        self.itemDropped.emit(True, "[" + str(self.indexOfTopLevelItem(parent) + 1) + "|" + str(firstChildModelIndex.row() + 1) + "," + str(secondChildModelIndex.row() + 1) + "]")

                elif self.checkDepth(dragEnterIndex) == 1:

                    draggedDataRowNum = dragEnterIndex.data(0).split(" ")[0]
                    temp = self.itemFromIndex(dragEnterIndex).parent().data(0, 0)[1:-1]
                    oldText = temp
                    nums = self.itemFromIndex(dragEnterIndex).parent().data(0, 0)[1:-1].split(",")

                    index = nums.index(dragEnterIndex.data(0).split(" ")[0])
                    if index:
                        temp = "[" + temp[0:temp.find(draggedDataRowNum) - 1] + temp[temp.find(draggedDataRowNum) + len(draggedDataRowNum):] + "]"
                    else:
                        temp = "[" + temp[(temp.find(",") + 1):] + "]"

                    parent = self.itemFromIndex(dragEnterIndex).parent()
                    child = parent.takeChild(dragEnterIndex.row())

                    parent.setData(0, 0, temp)

                    self.insertPartedChild(draggedDataRowNum, parent, child)

                    if len(nums) == 2:
                        lastChild = parent.takeChild(0)
                        self.insertPartedChild(lastChild.text(0).split(" ")[0], parent, lastChild)
                        self.itemDropped.emit(False, str(self.indexOfTopLevelItem(parent.parent()) + 1) + "|" + temp[1:-1])
                        parent.parent().removeChild(parent)
                    else:
                        k = "[" + str(self.indexOfTopLevelItem(parent.parent()) + 1) + "|" + oldText + "|" + temp[1:]
                        self.itemDropped.emit(True, "[" + str(self.indexOfTopLevelItem(parent.parent()) + 1) + "|" + oldText + "|" + temp[1:])

        #self.dragEventPos = None
        # super(QTreeWidget, self).dropEvent(event)

    def insertPartedChild(self, draggedDataRowNum, parent, child):

        check = True
        for index in range(parent.parent().childCount()):
            k = self.findFirstNum(parent.parent().child(index).text(0).split(" ")[0])
            if int(draggedDataRowNum) < self.findFirstNum(parent.parent().child(index).text(0).split(" ")[0]):
                parent.parent().insertChild(index, child)
                check = False
                break

        if check:
            parent.parent().addChild(child)

    def changeParentRowAccordingToAddedChild(self, draggedDataRowNum, parent, dropIndex):

        for index in range(parent.parent().childCount()):
            k = self.findFirstNum(parent.parent().child(index).text(0).split(" ")[0])
            if int(draggedDataRowNum) < self.findFirstNum(parent.parent().child(index).text(0).split(" ")[0]):
                parent.parent().insertChild(index, parent.parent().takeChild(dropIndex))
                break

    def findFirstNum(self, text):

        return int(re.search("\d+", text).group())

    def dragLeaveEvent(self, event):

        #self.dragEventPos = None
        super(QTreeWidget, self).dragLeaveEvent(event)

    def dragEnterEvent(self, event):

        #if self.dragEventPos is not None:
            #return

        self.dragEventPos = event.pos()
        k = self.itemAt(event.pos()).text(0)
        print(event.pos())
        # print(QModelIndex(self.indexAt(event.pos())).row())
        super(QTreeWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        self.setDropIndicatorShown(True)
        super(QTreeWidget, self).dragMoveEvent(event)

    def checkParents(self, child1, child2):

        while child2.parent().row() != -1:

            if child1.parent().row() == child2.parent().row():
                return True
            else:
                child2 = child2.parent()

        return False

    def checkDepth(self, item):

        depth = 0

        while item.parent().row() != -1:
            item = item.parent()
            depth += 1

        return depth - 1


class ItemWordWrap(QAbstractItemDelegate):

    def __init__(self, parent=None):
        super(QAbstractItemDelegate, self).__init__(parent)
        self.parent = parent

    def paint(self, painter, option, index):
        text = index.model().data(index)
        document = QTextDocument()
        document.setPlainText(text)
        document.setTextWidth(option.rect.width())
        index.model().setData(index, option.rect.width(), QtCore.Qt.UserRole+1)
        painter.save()
        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):

        text = index.model().data(index)
        document = QTextDocument()
        document.setHtml(text)
        width = index.model().data(index, QtCore.Qt.UserRole+1)
        if not width:
            width = 20
        document.setTextWidth(width)
        return QtCore.QSize(int(document.idealWidth() + 10),  int(document.size().height()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    k = Tool()
    sys.exit(app.exec_())
