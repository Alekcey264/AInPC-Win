from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTreeWidget, QTableWidget, QAbstractItemView, QHeaderView, QTreeWidgetItem, QTableWidgetItem
from PyQt6.QtGui import QAction
from pyuac import main_requires_admin
import sys, hwtypes, clr, sqlite3
from os import getcwd, popen, system

db = getcwd() + '\\aipcdb.db'

