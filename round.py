import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtCore,QtGui

# set the brush parameter
# it will only be called when the user has logged in successfully
class PaintVar:
    userLogin=False
    percent=0
    percent2=0
    winw=300
    winh=0
    top=20
    left=30
    progressR=180
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.exit(app.exec_())
