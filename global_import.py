from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTreeWidget, QTableWidget, QAbstractItemView, QHeaderView, QTreeWidgetItem, QTableWidgetItem, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QSplashScreen
from PyQt6.QtGui import QAction, QPixmap, QIcon
from pyuac import main_requires_admin
import sys, hwtypes, clr, sqlite3, pyqtgraph, re
from os import getcwd, popen, system
from pywintypes import error as PyWinError

db = getcwd() + '\\aipcdb.db'

