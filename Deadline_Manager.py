import sys, random
import time
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtMultimedia
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from main_window import MainWindow
from chart import gantt
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import configparser
from db_controller import *
import pygame
import sqlite3

'''Global Variable'''
DW_visible = True
global visible_action, login_action, task_action, matrix_action, logged, sizeX, loggedUser
global window_x, window_y, pickles, pickleNow, pickleCycle, resize_action, animation_action, pickle_animation
global sadNow, sadCycle, sad_animation, sads

class Desktop_Wizard_Window(QWidget):

    def __init__(self, parent=None):
        super(Desktop_Wizard_Window, self).__init__()
        global logged, login_action, visible_action, task_action, matrix_action, sizeX, loggedUser
        global resize_action, pickle_animation, sad_animation, sads

        '''Load config'''
        loadConfig()
        sads = []
        for i in range(1, 66):
            sads.append(QPixmap("images/sad/sad_" + str(i) + ".png"))

        '''Auto login or not'''
        if loggedUser is None:
            logged = False
        else:
            logged = True

        '''InitializeShow|HideAction'''
        visible_action = QAction("Show", self)
        visible_action.setCheckable(True)
        visible_action.setChecked(DW_visible)
        visible_action.triggered.connect(self.visible)

        '''Initialize other Actions'''
        resize_action = QAction("Resize", self)
        pickle_animation = QAction("Pickle", self)
        sad_animation = QAction("Sad", self)
        login_action = QAction("Login or Sign up", self)
        task_action = QAction("Task Manager", self)
        task_action.triggered.connect(self.showManager)
        matrix_action = QAction("Focus Matrix", self)

        if logged:
            login_action.setText("Sign Out[" + loggedUser + "]")
            task_action.setEnabled(True)
            matrix_action.setEnabled(True)

            widget.addWidget(main_window)
            widget.setCurrentIndex(widget.currentIndex() + 1)

        else:
            task_action.setDisabled(True)
            matrix_action.setDisabled(True)

        '''Window drawing'''


        self.mask = QBitmap.fromImage(
            QImage("images/Circle-Mask.png").scaled(QSize(100 + 50 * sizeX, 100 + 50 * sizeX)))
        self.resize(self.mask.size())
        self.setMask(self.mask)
        self.setWindowFlags(Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.trayEvent()
        self.resetPosition()

        self.label = QLabel(self)
        self.qpixmap = QPixmap("images/Circle.png").scaled(self.mask.width(), self.mask.height())
        self.label.setScaledContents(True)
        self.label.setPixmap(self.qpixmap)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.timer = QTimer()

        '''Right click menu'''
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.setRightClickMenu)
        self.setRightClickMenu()


    """Show Rick01"""
    @pyqtSlot()
    def showRick01(self):
        global sizeX
        self.mask = QBitmap.fromImage(
            QImage("images/Circle-Mask.png").scaled(QSize(100 + 50 * int(sizeX), 100 + 50 * int(sizeX))))
        self.setMask(self.mask)
        self.resize(self.mask.size())
        self.label.resize(QSize(100 + 50 * int(sizeX), 100 + 50 * int(sizeX)))
        self.label.setPixmap(QPixmap("images/Circle.png").scaled(QSize(100 + 50 * int(sizeX), 100 + 50 * int(sizeX))))
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    """Show Pickle"""

    @pyqtSlot()
    def showPickles(self):
        global sizeX, pickles, pickleNow, pickleCycle, resize_action, pickle_animation, sad_animation
        pickles = []
        for i in range(1, 10):
            pickles.append(QPixmap("images/pickle/" + str(i) + ".png"))

        pickleNow = 0
        pickleCycle = 0

        resize_action.setEnabled(False)
        pickle_animation.setEnabled(False)
        sad_animation.setEnabled(False)
        self.timer.timeout.connect(self.updatePickle)

        self.mask = QBitmap.fromImage(
            QImage("images/pickle/Full-Mask.png").scaled(QSize(100 + 50 * int(sizeX), 100 + 50 * int(sizeX))))
        self.resize(self.mask.size())
        self.label.resize(QSize(100 + 50 * int(sizeX), 100 + 50 * int(sizeX)))

        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.timer.start(100)
        pickle_animation.triggered.disconnect()
        pickle_animation.triggered.connect(self.showPickles)
        # #
        # main_window.pushButton_complete.clicked.disconnect(self.show_Pickles)
        # main_window.pushButton_complete.clicked.disconnect(main_window.mark_task)
        # main_window.pushButton_complete.clicked.connect(main_window.mark_task)
        # main_window.pushButton_complete.clicked.connect(self.show_Pickles)

    @pyqtSlot()
    def updatePickle(self):

        global pickles, pickleNow, pickleCycle, resize_action, animation_action, sad_animation, pickle_animation

        self.label.setPixmap(pickles[pickleNow])
        if pickleCycle == 0 and pickleNow == 1:
            self.setMask(self.mask)

        if pickleCycle == 6:

            self.timer.timeout.disconnect()
            self.showRick01()
            resize_action.setEnabled(True)
            pickle_animation.setEnabled(True)
            sad_animation.setEnabled(True)
        else:
            if pickleNow < len(pickles) - 1:
                pickleNow += 1
            else:
                pickleNow = 0
                pickleCycle += 1

    """Show Sad Rick"""
    @pyqtSlot()
    def showSad(self):
        global sizeX, sads, sadNow, sadCycle, resize_action, sad_animation

        sadNow = 0
        sadCycle = 0

        resize_action.setEnabled(False)
        sad_animation.setEnabled(False)
        pickle_animation.setEnabled(False)
        self.timer.timeout.connect(self.updateSad)

        self.mask = QBitmap.fromImage(
            QImage("images/sad/Full-Mask.png").scaled(QSize(120 * int(sizeX), 90 * int(sizeX))))
        self.setMask(self.mask)
        self.resize(self.mask.size())
        self.label.setPixmap(sads[0])
        self.label.resize(QSize(120 * int(sizeX), 90 * int(sizeX)))

        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.timer.start(100)
        sad_animation.triggered.disconnect()
        sad_animation.triggered.connect(self.showSad)
        # #
        # main_window.pushButton_complete.clicked.disconnect(self.show_Pickles)
        # main_window.pushButton_complete.clicked.disconnect(main_window.mark_task)
        # main_window.pushButton_complete.clicked.connect(main_window.mark_task)
        # main_window.pushButton_complete.clicked.connect(self.show_Pickles)

    @pyqtSlot()
    def updateSad(self):

        global sads, sadNow, sadCycle, resize_action, animation_action, pickle_animation

        self.label.setPixmap(sads[sadNow])

        if sadCycle == 1:

            self.timer.timeout.disconnect()
            self.showRick01()
            resize_action.setEnabled(True)
            pickle_animation.setEnabled(True)
            sad_animation.setEnabled(True)
        else:
            if sadNow < len(sads) - 1:
                sadNow += 1
            else:
                sadNow = 0
                sadCycle += 1

    """Window move"""
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(QMouseEvent.globalPos() - self.mouse_drag_pos)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        writeConfig('config', 'window_x', str(self.x()))
        writeConfig('config', 'window_y', str(self.y()))

    """Reset Position"""
    def resetPosition(self):
        global window_x, window_y
        screen_geo = QDesktopWidget().screenGeometry()
        pet_geo = self.geometry()
        if window_x is not None and window_y is not None:
            self.move(window_x, window_y)

    """Right-click menu event"""
    def setRightClickMenu(self):
        global resize_action, animation_action, pickle_animation, sad_animation
        self.right_menu = QMenu(self)

        '''Animation menu'''
        animation_action = QAction("Animation", self)
        self.animation_menu = QMenu(self)
        animation_action.setMenu(self.animation_menu)
        pickle_animation.triggered.connect(self.showPickles)
        sad_animation.triggered.connect(self.showSad)
        self.animation_menu.addAction(pickle_animation)
        self.animation_menu.addAction(sad_animation)

        '''Exit'''
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        login_action.triggered.connect(self.loginActivity)
        resize_action.triggered.connect(self.resize0)



        self.right_menu.addAction(login_action)
        self.right_menu.addAction(task_action)
        self.right_menu.addAction(matrix_action)
        self.right_menu.addAction(animation_action)
        self.right_menu.addAction(resize_action)

        self.right_menu.addAction(visible_action)
        self.right_menu.addAction(quit_action)

        self.right_menu.popup(QCursor.pos())

    """Add system tray and events"""
    def trayEvent(self):
        tray = QSystemTrayIcon(self)
        tray.setIcon(QIcon('images/Rick-Icon.png'))
        tray_menu = QMenu()

        tray_menu.addAction(visible_action)

        '''Quit'''
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        tray_menu.addAction(quit_action)

        tray.setContextMenu(tray_menu)
        tray.show()

    """Show or hide window"""
    def visible(self, state):
        if state:
            self.setVisible(True)
            visible_action.setChecked(True)
        else:
            self.setVisible(False)
            visible_action.setChecked(False)

    """Resize window"""
    @pyqtSlot()
    def resize0(self):
        global sizeX, resize_action
        sizes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        size2, ok = QInputDialog.getItem(self, "Resize", "Resize (Current:" + str(sizeX) + ")", sizes, int(sizeX) - 1, False)
        if ok:
            sizeX = size2
            writeConfig("config", "window_size", str(size2))
            self.showRick01()
        resize_action.triggered.disconnect()

    """Exit Event"""
    def quit(self):
        app.exit()

    '''Right click login'''
    @pyqtSlot()
    def loginActivity(self):
        global logged, login_action

        if logged:
            logged = False
            writeConfig('Auto login', 'username', 'null')
            login_action.setText("Login or Sign up")
            task_action.setDisabled(True)
            matrix_action.setDisabled(True)
            widget.setVisible(False)

            welcome1 = WelcomeScreen()
            widget.addWidget(welcome1)

            widget.setCurrentIndex(widget.currentIndex() + 1)


        else:
            widget.show()

        login_action.triggered.disconnect(self.loginActivity)

    '''Show Admin Window'''

    @pyqtSlot()
    def showManager(self):
        global matrix_action
        widget.show()

        # matrix_action.triggered.disconnect(self.showManager)


# create welcome screen class
class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        # load ui file
        loadUi("welcomescreen.ui", self)
        # connect login button to "direct to login" function
        self.login.clicked.connect(self.gotologin)
        # connect create a new account button to "direct to sign up" function
        self.create.clicked.connect(self.gotocreate)

    # direct to the login screen
    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    # direct to the sign up screen
    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# create a login screen class
class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui", self)
        # set password mode for the password input area
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        # judge whether the user has input all required fields
        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please input all fields.")

        else:
            # connect to the user information database where there are all account and password records
            conn = sqlite3.connect("user_info.db")
            cur = conn.cursor()
            query = 'SELECT password FROM login_info WHERE username =\'' + user + "\'"

            cur.execute(query)
            result_pass = cur.fetchone()[0]
            # judge whether the password is correct
            if result_pass == password:
                PaintVar.userLogin = True
                # record user
                with open("./user.txt", "wb") as f:
                    f.write(user.encode("utf-8"))
                # clear existing records on the main window
                main_window.clear()
                # add main window to the stacked widget
                widget.addWidget(main_window)
                # display users' existing to-do-list
                main_window.show_data()
                # draw a gantt chart according to the users' uncompleted tasks
                gantt()
                pixmap = QPixmap('./images/gantt.jpeg')
                # show gantt chart
                main_window.label_gantt_chart.setPixmap(pixmap)
                main_window.label_gantt_chart.setScaledContents(True)
                widget.setCurrentIndex(widget.currentIndex() + 1)

                '''Set automatic login'''
                global logged, login_action, task_action, matrix_action
                logged = True
                writeConfig('Auto login', 'username', str(user))
                login_action.setText("Sign Out[" + user + "]")
                task_action.setEnabled(True)
                matrix_action.setEnabled(True)

            else:
                self.error.setText("Invalid username or password")

# create a sign up screen class
class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("createacc.ui", self)
        # set password mode for the password input area
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        # link the button to the sign up function
        self.signup.clicked.connect(self.signupfunction)

    def signupfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()
        # judge whether the user has input all required fields
        if len(user) == 0 or len(password) == 0 or len(confirmpassword) == 0:
            self.error.setText("Please fill in all inputs.")

        elif password != confirmpassword:
            self.error.setText("Passwords do not match.")
        else:
            # write new user's info into the database
            conn = sqlite3.connect("user_info.db")
            cur = conn.cursor()

            user_info = [user, password]
            cur.execute('INSERT INTO login_info (username, password) VALUES (?,?)', user_info)
            conn.commit()
            conn.close()
            login = LoginScreen()
            widget.addWidget(login)
            widget.setCurrentIndex(widget.currentIndex() + 1)

# create a window class to display help information for the focus matrix
class FocusMatrix(QDialog):
    def __init__(self):
        super(FocusMatrix, self).__init__()
        loadUi("focus_matrix.ui", self)

# create a window class to display help information for the overview section
class Overview(QDialog):
    def __init__(self):
        super(Overview, self).__init__()
        loadUi("overview.ui", self)

# create a window class to display help information for the desktop assistant
class Assistant(QDialog):
    def __init__(self):
        super(Assistant, self).__init__()
        loadUi("assistant.ui", self)





'''Load config'''


def loadConfig():
    global sizeX, window_x, window_y, loggedUser, logged
    config = configparser.ConfigParser()
    config.read('config.ini')
    sizeX = int(config.get('config', 'window_size'))
    if config.get('config', 'window_x') == 'null' or config.get('config', 'window_y') == 'null':
        window_x = None
        window_y = None
    else:
        window_x = int(config.get('config', 'window_x'))
        window_y = int(config.get('config', 'window_y'))

    if config.get('Auto login', 'username') == "null":
        loggedUser = None
    else:
        loggedUser = str(config.get('Auto login', 'username'))
        logged = True





def writeConfig(section, option, key):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set(section, option, key)
    config.write(open('config.ini', "r+"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # create a stacked widget
    widget = QtWidgets.QStackedWidget()
    # create and add the welcome screen to the widget
    welcome = WelcomeScreen()
    widget.addWidget(welcome)
    widget.setFixedHeight(716)
    widget.setFixedWidth(1200)
    # create the welcome screen and help info screens
    main_window = MainWindow()
    focus_matrix = FocusMatrix()
    overview = Overview()
    assistant = Assistant()
    # link the actions under the help menu bar to their screens
    main_window.actionFocus_Matrix.triggered.connect(focus_matrix.show)
    main_window.actionOverview.triggered.connect(overview.show)
    main_window.actionTime_Mgt_Assistant.triggered.connect(assistant.show)
    # create  and the desktop assistant widget
    desktop_wizard_window = Desktop_Wizard_Window()
    desktop_wizard_window.show()

    main_window.showSadAction.triggered.connect(desktop_wizard_window.showSad)
    main_window.pushButton_complete.clicked.connect(desktop_wizard_window.showPickles)
    # widget.setVisible(False)
    # widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
