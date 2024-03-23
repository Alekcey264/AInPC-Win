#Импортируем все необходимые модули из библиотеки для работы с графическим интерфейсом
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTreeWidget, QTableWidget, QAbstractItemView, QHeaderView, QTreeWidgetItem, QTableWidgetItem, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QSplashScreen
from PyQt6.QtGui import QAction, QPixmap, QIcon
#Импортируем модуль для запуска программы от имени администратора
from pyuac import main_requires_admin
#Импортируем библиотеки для работы системой, типами датчиков, специальными dll файлами, базами данных, построения графиков и сортировки данных
import sys, hwtypes, clr, sqlite3, pyqtgraph, re
#Импортируем модули для работы с операционной системой
from os import getcwd, popen, system
#Импортируем модуль для чтения отказа пользователя
from pywintypes import error as PyWinError
#Импортируем модуль для получения текущего времени системы
from datetime import datetime
from subprocess import Popen

#Записываем метсоположение базы данных в отдельную переменную, чтобы доступ к ней
#можно было получить из всех частей кода
db = getcwd() + '\\aipcdb.db'