#Импортируем из остальных файлов проекта необходимые зависимости - классы, функции и модули
from fetch import *
from global_import import *
from additional_classes import *
from graphs_window import GraphsWindow

#Создаем главное рабочее окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
#Создаем переменные и зависимости, используемые в рамках главного окна
        self.root_for_timer = None
        self.text_for_timer = None
        self.cpu_cores, self.cpu_threads = initialize_cpu_info()
        self.cpu_threads_info = []
        self.cpu_threads_flag = False
        self.mb_fans_control = []
        self.mb_voltage = []
        self.mb_temp = []
        self.mb_fans = []
        self.cpu_load = []
        self.cpu_temp = []
        self.cpu_clock = []
        self.cpu_power = []
        self.cpu_voltage = []
        self.gpu_temp = []
        self.gpu_clock = []
        self.gpu_load = []
        self.gpu_power = []
        self.gpu_memory = []
        self.ram_load = []
        self.ram_data = []
#Настраиваем вид главного окна
        self.setWindowTitle('AInPC')
        self.setFixedSize(QSize(830, 500))
        self.setWindowIcon(QIcon(getcwd() + '/recources//main_icon.png'))
#Создаем и настраиваем верхнее меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Вид')
        menubar_height = self.menuBar().height()
        open_graphs = QAction('Графики', self)
        create_report = QAction('Отчет', self)
        open_cmd = QAction('Командная строка', self)
        open_powershell = QAction('Windows PowerShell', self)
        open_graphs.triggered.connect(self.open_graphs_window)
        open_cmd.triggered.connect(self.open_cmd)
        open_powershell.triggered.connect(self.open_powershell)
        create_report.triggered.connect(self.create_report)
        file_menu.addAction(open_graphs)
        file_menu.addAction(open_cmd)
        file_menu.addAction(open_powershell)
        file_menu.addAction(create_report)
#Создаем и настраиваем левую часть окна - дерево, в котором содежится меню выбора части ПК
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setGeometry(10, menubar_height, 150, self.height() - menubar_height - 10)
        self.tree_widget.setHeaderHidden(True)
        self.setup_tree()
        self.tree_widget.itemSelectionChanged.connect(self.on_item_selected)
        self.tree_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
#Создаем и настраиваем правую часть окна - таблицу, где отображается информация о выбранном компоненте системы
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(self.tree_widget.width() + 20 + 10, menubar_height, self.width() - self.tree_widget.width() - 20 - 10 - 10, self.height() - menubar_height - 10)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(False)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.verticalHeader().setDefaultSectionSize(1)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setup_table(9)

#Создаем поток опроса датчков компонентов системы и "подключаем" его реакцию на готовность обновления
        self.stats_thread = StatsThread()
        self.stats_thread.start()
        self.stats_thread.sensors_signal.connect(self.on_change)
#Создаем таймер обновления и "подключаем" его действие, по истечению времени таймера
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_table_with_timer)
#Заполняем правую часть окна данными, которые отображаются самыми первыми
        self.initialize_table(None, 'Процессор')
#Отображаем главное окно
        self.show()

#Функция, служащая для выравнивания всех ячеек в таблице справа
    def fix_table(self):
        for row in range(self.table_widget.rowCount()):
            for col in range(self.table_widget.columnCount()):
                if (self.table_widget.rowSpan(row, col) > 1) or (self.table_widget.columnSpan(row, col) > 1):
                    self.table_widget.setSpan(row, col, 1, 1)
        self.table_widget.clearContents()

#Функция, подготавливающая таблицу для отображения справочных данных
    def setup_table(self, row_count):
        column_names = ['Поле', 'Описание']
        self.table_widget.setRowCount(row_count)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(column_names)

#Функция, заполняющая дерево в левой части экрана всеми "ветвями"
    def setup_tree(self):
        root_item_cpu = QTreeWidgetItem(self.tree_widget, ['Процессор'])               
        child_item1_cpu = QTreeWidgetItem(root_item_cpu, ['Температура'])
        child_item2_cpu = QTreeWidgetItem(root_item_cpu, ['Загрузка'])
        сhild_item3_cpu = QTreeWidgetItem(root_item_cpu, ['Частота'])
        child_item4_cpu = QTreeWidgetItem(root_item_cpu, ['Напряжение'])

        root_item_gpu = QTreeWidgetItem(self.tree_widget, ['Видеокарта'])
        child_item1_gpu = QTreeWidgetItem(root_item_gpu, ['Температура'])
        child_item2_gpu = QTreeWidgetItem(root_item_gpu, ['Загрузка'])
        сhild_item3_gpu = QTreeWidgetItem(root_item_gpu, ['Частота'])
        child_item4_gpu = QTreeWidgetItem(root_item_gpu, ['Напряжение'])
        child_item5_gpu = QTreeWidgetItem(root_item_gpu, ['Память'])

        root_item_ram = QTreeWidgetItem(self.tree_widget, ['Оперативная память'])
        child_item1_ram = QTreeWidgetItem(root_item_ram, ['Числовая информация'])

#Условие, в рамках которого система немного адаптируется под ноутбуки, 
#однако, чтобы система могла полноценно работать на портативных устройствах требуются обширные правки
        root_item_mb = QTreeWidgetItem(self.tree_widget, ['Материнская плата'])
        mb_manufacturer_cmd = str(popen('wmic baseboard get manufacturer').read().encode()).split('\\n\\n')
        if mb_manufacturer_cmd[1].rstrip() != 'Notebook':
            child_item1_mb = QTreeWidgetItem(root_item_mb, ['Температура'])
            child_item2_mb = QTreeWidgetItem(root_item_mb, ['Вольтаж'])
            child_item3_mb = QTreeWidgetItem(root_item_mb, ['Вентиляторы'])
        else:
            child_item1_mb = QTreeWidgetItem(root_item_mb, ['Вольтаж'])
        
        root_item_logical_disks = QTreeWidgetItem(self.tree_widget, ['Логические диски'])
        root_item_physical_disks = QTreeWidgetItem(self.tree_widget, ['Физические диски'])
        
#Открытие всех элементов дерева
        self.tree_widget.expandAll()

#Функция, работающая по сообщению от потока, она обновляет все массивы, в которых хранятся значения датчиков
    def on_change(self, data):
        for item in data:
            if item[0][4] == 'CPU':
                if item[0][3] == 'Temperature':
                    self.cpu_temp = item
                elif item[0][3] == 'Load':
                    self.cpu_load = item
                elif item[0][3] == 'Clock':
                    self.cpu_clock = item
                elif item[0][3] == 'Power':
                    self.cpu_power = item
            elif item[0][4] == 'GpuNvidia':
                if item[0][3] == 'Temperature':
                    self.gpu_temp = item
                elif item[0][3] == 'Load':
                    self.gpu_load = item
                elif item[0][3] == 'Clock':
                    self.gpu_clock = item
                elif item[0][3] == 'Power':
                    self.gpu_power = item
                elif item[0][3] == 'SmallData':
                    self.gpu_memory = item
            elif item[0][4] == 'RAM':
                if item[0][3] == 'Load':
                    self.ram_load = item
                if item[0][3] == 'Data':
                    self.ram_data = item
            elif item[0][4] == 'SuperIO':
                if item[0][3] == 'Temperature':
                    self.mb_temp = item
                elif item[0][3] == 'Voltage':
                    self.mb_voltage = item
                elif item[0][3] == 'Control':
                    self.mb_fans_control = item
                elif item[0][3] == 'Fan':
                    self.mb_fans = item

#Функция, принудительно останавливающая поток при закрытии программы
    def stop_thread(self):
        self.stats_thread.stop()

#Функция, работающая по сообщению от таймера, запускает функцию в зависимости от того, какое "ветвь" сейчас активна
    def update_table_with_timer(self):
        if self.root_for_timer == 'CPU':
            if self.text_for_timer == 'Temperature':                               
                self.fill_table_cpu_temp()
            elif self.text_for_timer == 'Load':
                self.fill_table_cpu_load()
            elif self.text_for_timer == 'Clock':
                self.fill_table_cpu_clock()    
            elif self.text_for_timer == 'Power':
                self.fill_table_cpu_power()
        elif self.root_for_timer == 'GPU':
            if self.text_for_timer == 'Temperature':
                self.fill_table_gpu_temp()
            elif self.text_for_timer == 'Load':
                self.fill_table_gpu_load()
            elif self.text_for_timer == 'Clock':
                self.fill_table_gpu_clock()
            elif self.text_for_timer == 'Power':
                self.fill_table_gpu_power()
            elif self.text_for_timer == 'SmallData':
                self.fill_table_gpu_memory()
        elif self.root_for_timer == 'RAM':
            if self.text_for_timer == 'Load':
                self.fill_table_ram_load()
        elif self.root_for_timer == 'SuperIO': 
            if self.text_for_timer == 'Temperature':
                self.fill_table_mb_temp()
            elif self.text_for_timer == 'Voltage':
                self.fill_table_mb_voltage()
            elif self.text_for_timer == 'Control':
                self.fill_table_mb_fans()
       
#Функция, считывающая какую, именно "ветвь" выбрал пользователь
    def on_item_selected(self):
        self.root_for_timer = None
        self.text_for_timer = None
        selected_item = self.tree_widget.selectedItems()[0]
        selected_text = selected_item.text(0)
        root_item = selected_item.parent()
        if root_item is not None:
            root_text = root_item.text(0)
        else:
            root_text = None        
        if selected_item:
            self.initialize_table(root_text, selected_text)

#Функция, считывающая справочную информацию о процессоре из базы данных
    def get_cpu_info(self, name):
            try:
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cpu_info WHERE cpu_name = ?', (name,))
                return cursor.fetchone()
            except sqlite3.Error as error:
                message_box = QMessageBox()
                message_box.setWindowTitle('Ошибка')
                message_box.setText(f'Возникла ошибка в ходе получения информации о процессоре {name}, пожалуйста, попробуйте открыть вкладку повторно или перезапустите программу.')
                message_box.setIcon(QMessageBox.Icon.Warning)
                message_box.exec()
            finally:
                if conn:
                    conn.close()

#Функция, заполняющая таблицу температурными показателями ядер процессора
    def fill_table_cpu_temp(self):
        data = self.cpu_temp
        data = data[:self.cpu_cores + 1]
        for row in range(self.cpu_cores):
            data[row][1] = data[row][1].replace('CPU Core', 'Ядро процессора')
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(data[row][1]) + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(data[row][2]) + '\u00B0C'))
        
        self.table_widget.setSpan(self.cpu_cores, 0, 1, 2)
        data[self.cpu_cores][1] = data[self.cpu_cores][1].replace('CPU Package', 'Температурный пакет процессора')
        self.table_widget.setItem(self.cpu_cores + 1, 0, QTableWidgetItem(str(data[self.cpu_cores][1]) + '\t'))
        self.table_widget.setItem(self.cpu_cores + 1, 1, QTableWidgetItem(str(data[self.cpu_cores][2]) + '\u00B0C'))

#Функция, заполняющая таблицу показателями загрузки ядер и потоков процессора, а также общей загрузкой процессора
    def fill_table_cpu_load(self):
        data = self.cpu_load
        data = data[:self.cpu_threads + 1]
        if len(self.cpu_threads_info) < (self.cpu_threads + 1):
            existing_values = {item[1] for item in self.cpu_threads_info}
            for item in data:
                if item[1] not in existing_values and (item[0] in range(2, self.cpu_threads + 2) or item[0] == 0):
                    self.cpu_threads_info.append(item[:2])
        else:
            self.cpu_threads_flag = True
            for item in self.cpu_threads_info:
                if item[0] != 0:    
                    item[1] = item[1].replace('CPU Core', 'Ядро процессора').replace('Thread', '\u00A0Поток')
                    self.table_widget.setItem(item[0] - 2, 0, QTableWidgetItem(str(item[1]) + '\t'))
                else:
                    item[1] = item[1].replace('CPU Total', 'Общая загрузка процессора\t')
                    self.table_widget.setItem(self.cpu_threads + 1, 0, QTableWidgetItem(str(item[1]) + '\t'))
        self.table_widget.setSpan(self.cpu_threads, 0, 1, 2)
        if not self.cpu_threads_flag:
            for item in self.cpu_threads_info:
                if item[0] != 0:    
                    item[1] = item[1].replace('CPU Core', 'Ядро процессора').replace('Thread', '\u00A0Поток')
                    self.table_widget.setItem(item[0] - 2, 0, QTableWidgetItem(str(item[1]) + '\t'))
                else:
                    item[1] = item[1].replace('CPU Total', 'Общая загрузка процессора\t')
                    self.table_widget.setItem(self.cpu_threads + 1, 0, QTableWidgetItem(str(item[1]) + '\t'))
        else:
            for item in self.cpu_threads_info:
                if item[0] != 0:    
                    self.table_widget.setItem(item[0] - 2, 0, QTableWidgetItem(str(item[1]) + '\t'))
                else:
                    self.table_widget.setItem(self.cpu_threads + 1, 0, QTableWidgetItem(str(item[1]) + '\t'))
        for i in range(len(data)):
            if data[i][0] in range(2, self.cpu_threads + 2):
                self.table_widget.setItem(data[i][0] - 2, 1, QTableWidgetItem(str(round(data[i][2], 2)) + '%'))
            elif data[i][0] == 0:
                self.table_widget.setItem(self.cpu_threads + 1, 1, QTableWidgetItem(str(round(data[i][2], 2)) + '%'))

#Функция, заполняющая таблицу показателями частоты работы ядер и шины процессора
    def fill_table_cpu_clock(self):
        data = self.cpu_clock
        self.table_widget.setSpan(self.cpu_cores, 0, 1, 2)
        for item in data:
            if item[0] in range(1, self.cpu_cores + 1):
                item[1] = item[1].replace('CPU Core', 'Ядро процессора')
                self.table_widget.setItem(item[0] - 1, 0, QTableWidgetItem(str(item[1]) + '\t'))
                self.table_widget.setItem(item[0] - 1, 1, QTableWidgetItem(str(round(item[2], 2)) + ' ГГц'))
            elif item[0] == 0:
                item[1] = item[1].replace('Bus Speed', 'Шина процессора')
                self.table_widget.setItem(self.cpu_cores + 1, 0, QTableWidgetItem(str(item[1]) + '\t'))
                self.table_widget.setItem(self.cpu_cores + 1, 1, QTableWidgetItem(str(round(item[2], 2)) + ' МГц'))
    
#Функция, заполняющая таблицу показателями напряжения, подающимися на процессор
    def fill_table_cpu_power(self):
        data = self.cpu_power
        for row in range(len(data)):
            data[row][1] = data[row][1].replace('CPU Package', 'Пакет процессора').replace('CPU Cores', 'Ядра процессора').replace('CPU Memory', 'Память процессора')
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(data[row][1]) + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(round(data[row][2], 2)) + ' Вт'))

#Функция, получающая справочную информацию о видеокарте из базы данных
    def get_gpu_info(self, name):
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM gpu_info WHERE gpu_name = ?', (name,))
            return cursor.fetchone()
        except sqlite3.Error as error:
            message_box = QMessageBox()
            message_box.setWindowTitle('Ошибка')
            message_box.setText(f'Возникла ошибка в ходе получения информации о видеокарте {name}, пожалуйста, попробуйте открыть вкладку повторно или перезапустите программу.')
            message_box.setIcon(QMessageBox.Icon.Warning)
            message_box.exec()
        finally:
            if conn:
                conn.close()

#Функция, заполняющая таблицу температурными показателями видеокарты
    def fill_table_gpu_temp(self):
        data = self.gpu_temp
        if len(data) == 2:
            self.table_widget.setItem(2, 0, QTableWidgetItem('Память видеокарты\t'))
            gpu_memory_temp = QTableWidgetItem(str('Отсутствует датчик температуры на видеокарте'))
            gpu_memory_temp.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.table_widget.setItem(2, 1, gpu_memory_temp)
        for row in range(len(data)):
            data[row][1] = data[row][1].replace('GPU Core', 'Ядро видеокарты').replace('GPU Hot Spot', 'Hot Spot видеокарты')
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(data[row][1]) + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(round(data[row][2], 2)) + '\u00B0C'))
    
#Функция, заполняющая таблицу показателями загрузки ядра, памяти и фрейм-буфера видеокарты
    def fill_table_gpu_load(self):
        data = self.gpu_load
        temp = []
        for item in data:
            if item[1] == 'GPU Core':
                item[0] = 0
                temp.append(item)
            elif item[1] == 'GPU Memory':
                item[0] = 1
                temp.append(item)
            elif item[1] == 'GPU Memory Controller':
                item[0] = 2
                temp.append(item)
        data = temp
        self.table_widget.setItem(0, 0, QTableWidgetItem('Ядро видеокарты\t'))
        self.table_widget.setItem(1, 0, QTableWidgetItem('Память видеокарты\t'))
        self.table_widget.setItem(2, 0, QTableWidgetItem('Фрейм-буфер видеокарты\t'))
        for i in range(3):
            self.table_widget.setItem(i, 1, QTableWidgetItem(str('0.00%')))
        for item in data:
            self.table_widget.setItem(item[0], 1, QTableWidgetItem(str(round(item[2], 2)) + '%'))
        
#Функция, заполняющая таблицу показателями частоты работы графического ядра и видеопамяти
    def fill_table_gpu_clock(self):
        data = self.gpu_clock
        temp = []
        for item in data:
            if item[1] == 'GPU Core':
                item[0] = 0
                temp.append(item)
            elif item[1] == 'GPU Memory':
                item[0] = 1
                temp.append(item)
        data = temp
        self.table_widget.setItem(0, 0, QTableWidgetItem('Ядро видеокарты\t'))
        self.table_widget.setItem(1, 0, QTableWidgetItem('Память видеокарты\t'))
        for i in range(2):
            self.table_widget.setItem(i, 1, QTableWidgetItem(str('0.0 МГц')))
        for item in data:
            self.table_widget.setItem(item[0], 1, QTableWidgetItem(str(round(item[2], 2)) + ' МГц'))

#Функция, заполняющая таблицу показателями напряжения, подающихся на видеокарту
    def fill_table_gpu_power(self):
        data = self.gpu_power
        self.table_widget.setItem(0, 0, QTableWidgetItem('Ядро видеокарты\t'))
        self.table_widget.setItem(0, 1, QTableWidgetItem(str(round(data[0][2], 2)) + ' Вт'))

#Функция, заполняющая таблицу информацией об использовании видеопамяти
    def fill_table_gpu_memory(self):
        data = self.gpu_memory
        temp = []
        for item in data:
            if item[0] in range(3):
                item[1] = item[1].replace('GPU Memory Free', 'Свободный объем памяти видеокарты').replace('GPU Memory Total', 'Общий объем памяти видеокарты').replace('GPU Memory Used', 'Занятый объем памяти видеокарты')
                temp.append(item)
        data = temp
        for item in data:
            self.table_widget.setItem(item[0], 0, QTableWidgetItem(str(item[1]) + '\t'))
            self.table_widget.setItem(item[0], 1, QTableWidgetItem(str(round(item[2], 2)) + ' Мб'))
        
#Функция, заполняющая таблицу показателями о загрузке оперативной памяти, как физической, так и виртуальной
    def fill_table_ram_load(self):
        data = self.ram_data
        for row in range(4):
            data[row][1] = data[row][1].replace('Virtual Memory Available', 'Доступно виртуальной памяти').replace('Virtual Memory Used', 'Использовано виртуальной памяти').replace('Memory Available', 'Доступно физической памяти').replace('Memory Used', 'Использовано физической памяти')
            self.table_widget.setItem(data[row][0], 0, QTableWidgetItem(str(data[row][1]) + '\t'))
            self.table_widget.setItem(data[row][0], 1, QTableWidgetItem(str(round(data[row][2], 2)) + ' Гб'))

        self.table_widget.setSpan(4, 0, 1, 2)
        
        data = self.ram_load
        for row in range(5, 7):
            data[row - 5][1] = data[row - 5][1].replace('Virtual Memory', 'Загрузка виртуальной памяти').replace('Memory', 'Загрузка физической памяти')
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(data[row - 5][1]) + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(round(data[row - 5][2], 2)) + '%'))

#Функция, получающая справочную информацию о материнской плате из базы данных
    def get_mb_info(self):
        mb_name = str(popen('wmic baseboard get product').read().encode()).split('\\n\\n')
        mb_name.pop(0)
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM mb_info WHERE mb_name = ?', (mb_name[0].rstrip(),))
            return cursor.fetchone()
        except sqlite3.Error as error:
            message_box = QMessageBox()
            message_box.setWindowTitle('Ошибка')
            message_box.setText('Возникла ошибка в ходе получения информации о материнской плате, пожалуйста, попробуйте открыть вкладку повторно или перезапустите программу.')
            message_box.setIcon(QMessageBox.Icon.Warning)
            message_box.exec()
        finally:
            if conn:
                conn.close()

#Функция, заполняющая таблицу температурными показателями материнской платы
    def fill_table_mb_temp(self):
        data = self.mb_temp
        for row in range(len(data)):
            data[row][1] = data[row][1].replace('Temperature', 'Датчик температуры')
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(data[row][1]) + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(round(data[row][2], 2)) + '\u00B0C'))

#Функция, заполняющая таблицу показателями вольтажей, выдаваемых и подаваемых на материнскую плату
    def fill_table_mb_voltage(self):
        data = self.mb_voltage

        for row in range(len(data)):
            data[row][1] = data[row][1].replace('Voltage', 'Вольтаж')
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(data[row][1]) + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(round(data[row][2], 2)) + ' В'))

#Функция, заполняющая таблицу информацией о загруженности контроллеров вентиляторов и скорости работы вентиляторов
    def fill_table_mb_fans(self):
        data = self.mb_fans_control
        for row in range(len(data)):
            data[row][1] = data[row][1].replace('Fan', 'Контроллер вентилятора')
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(data[row][1]) + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(round(data[row][2], 2)) + '%'))
        
        self.table_widget.setSpan(len(data), 0, 1, 2)

        data = self.mb_fans
        for row in range(len(self.mb_fans_control) + 1, len(self.mb_fans_control) + 1 + len(data)):
            data[row - len(self.mb_fans_control) - 1][1] = data[row - len(self.mb_fans_control) - 1][1].replace('Fan', 'Вентилятор')
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(data[row - len(self.mb_fans_control) - 1][1]) + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(round(data[row - len(self.mb_fans_control) - 1][2], 2)) + ' об\мин'))

#Функция, инициализирующая таблицу в зависимости от того, какую "ветвь" выбрал пользователь
    def initialize_table(self, root, text):
        self.fix_table()
#Если пользователь выбрал "ветвь" первого уровня, тогда нам необходимо получить базовую –
#неизменяющуюся – информацию, поэтому мы можем сразу заполнить таблицу      
        if not root:
#Если пользователь выбрал "ветвь" первого уровня - останавливаем таймер, чтобы не создавать лишнюю нагрузку на систему
            self.timer.stop()
            if text == 'Процессор':
                cpu_specs = ['Наименование процессора', 'Сокет', 'Базовая частота', 'Количество ядер', 'Количество потоков', 'Кэш L1', 'Кэш L2', 'Кэш L3', 'Кэш L4', 'Фирма-производитель', 'Информация от производителя']
                cpu_names = str(popen('wmic cpu get name').read().encode()).split('\\n\\n')
                cpu_names.pop(0)
                for _ in range(2):
                    cpu_names.pop(-1)
                cpu_names = [item.rstrip() for item in cpu_names]
                cpu_count = len(cpu_names)
                self.setup_table((cpu_count * 11) + (cpu_count - 1))
                row = 0
                if cpu_count != 1:
                    for i in range(cpu_count):
                        info = self.get_cpu_info(cpu_names[i])
                        self.table_widget.setItem(row, 0, QTableWidgetItem(str(cpu_specs[0]) + f'#{j + 1}\t'))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(str(cpu_names[i])))
                        if info:
                            for j in range(row + 1, row + len(info) - 1):
                                self.table_widget.setItem(j, 0, QTableWidgetItem(str(cpu_specs[j - row]) + f'#{j + 1}\t'))
                                self.table_widget.setItem(j, 1, QTableWidgetItem(str(info[j - row])))
                            self.table_widget.setItem(row + 8, 0, QTableWidgetItem(str(cpu_specs[j - row]) + f'#{j + 1}\t'))
                            self.table_widget.setCellWidget(row + 8, 1, HyperlinkLabel(f'{info[j - row]}', f'{info[j - row]}'))
                        else:
                            for j in range(row + 1, row + 11):
                                self.table_widget.setItem(j, 0, QTableWidgetItem(str(cpu_specs[j - row]) + f'#{j + 1}\t'))
                                self.table_widget.setItem(j, 1, QTableWidgetItem(str('-')))
                        row += 10
                else:
                    info = self.get_cpu_info(cpu_names[0])
                    self.table_widget.setItem(0, 0, QTableWidgetItem(str(cpu_specs[0]) + '\t'))
                    self.table_widget.setItem(0, 1, QTableWidgetItem(str(cpu_names[0])))
                    if info:
                        for i in range(1, len(info) - 1):
                            self.table_widget.setItem(i, 0, QTableWidgetItem(str(cpu_specs[i]) + '\t'))
                            self.table_widget.setItem(i, 1, QTableWidgetItem(str(info[i])))
                        self.table_widget.setItem(10, 0, QTableWidgetItem(str(cpu_specs[10]) + '\t'))
                        self.table_widget.setCellWidget(10, 1, HyperlinkLabel(f'{info[10]}', f'{info[10]}'))
                    else:
                        for i in range(1, 11):
                            self.table_widget.setItem(i, 0, QTableWidgetItem(str(cpu_specs[i]) + '\t'))
                            self.table_widget.setItem(i, 1, QTableWidgetItem(str('-')))
            elif text == 'Видеокарта':
                gpu_specs = ['Наименование графического ускорителя', 'Базовая частота работы видеоядра', 'Фирма-производитель видеокарты', 'Информация от производителя видеокарты', 'Официальный драйвер видеокарты', 'Текущая версия драйвера видеокарты'] 
                gpu_names = str(popen('wmic path win32_VideoController get name').read().encode()).split('\\n\\n')
                gpu_names.pop(0)
                for _ in range(2):
                    gpu_names.pop(-1)
                gpu_names = [item.rstrip() for item in gpu_names]
                gpu_count = len(gpu_names)
                self.setup_table((gpu_count * 6) + (gpu_count - 1))
                row = 0
                if gpu_count != 1:
                    for i in range(len(gpu_count)):
                        info = self.get_gpu_info(gpu_names[i])
                        gpu_driver_info = str(popen('wmic path win32_VideoController get DriverVersion').read().encode()).split('\\n\\n')
                        gpu_driver_info.pop(0)
                        gpu_driver_info_short = gpu_driver_info[0].rstrip().replace('.', '')
                        self.table_widget.setItem(row, 0, QTableWidgetItem(str(gpu_specs[0]) + f'#{j + 1}\t'))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(str(gpu_names[i])))
                        if info:
                            for j in range(row + 1, len(info) - 2):
                                self.table_widget.setItem(j, 0, QTableWidgetItem(str(gpu_specs[j - row]) + f'#{j + 1}\t'))
                                self.table_widget.setItem(j, 1, QTableWidgetItem(str(info[j - row])))
                            for j in range(row + 3, row + 5):
                                self.table_widget.setItem(j, 0, QTableWidgetItem(str(gpu_specs[j - row]) + f'#{j + 1}\t'))
                                hyperlink = HyperlinkLabel(f'{info[j - row]}', f'{info[j - row]}')
                                self.table_widget.setCellWidget(j, 1, hyperlink)
                        else:
                            for j in range(row + 1, row + 5):
                                self.table_widget.setItem(j, 0, QTableWidgetItem(str(gpu_specs[j - row]) + f'#{j + 1}\t'))
                                self.table_widget.setItem(j, 1, QTableWidgetItem(str('-')))
                        self.table_widget.setItem(j + 1, 0, QTableWidgetItem(str(gpu_specs[5]) + f'#{j + 1}\t'))
                        self.table_widget.setItem(j + 1, 1, QTableWidgetItem(str(gpu_driver_info[0].rstrip() + ' \ ' + gpu_driver_info_short[-5:-2] + '.' + gpu_driver_info_short[-2:])))
                        row += 7
                else:
                    info = self.get_gpu_info(gpu_names[0])
                    self.table_widget.setItem(0, 0, QTableWidgetItem(str(gpu_specs[0]) + '\t'))
                    self.table_widget.setItem(0, 1, QTableWidgetItem(str(gpu_names[0])))
                    gpu_driver_info = str(popen('wmic path win32_VideoController get DriverVersion').read().encode()).split('\\n\\n')
                    gpu_driver_info.pop(0)
                    gpu_driver_info_short = gpu_driver_info[0].rstrip().replace('.', '')
                    self.table_widget.setItem(5, 0, QTableWidgetItem(str(gpu_specs[5]) + '\t'))
                    self.table_widget.setItem(5, 1, QTableWidgetItem(str(gpu_driver_info[0].rstrip() + ' \ ' + gpu_driver_info_short[-5:-2] + '.' + gpu_driver_info_short[-2:])))
                    if info: 
                        for i in range(1, len(info) - 2):
                            self.table_widget.setItem(i, 0, QTableWidgetItem(str(gpu_specs[i]) + '\t'))
                            self.table_widget.setItem(i, 1, QTableWidgetItem(str(info[i])))
                        for i in range(3, 5):
                            self.table_widget.setItem(i, 0, QTableWidgetItem(str(gpu_specs[i]) + '\t'))
                            hyperlink = HyperlinkLabel(f'{info[i]}', f'{info[i]}')
                            self.table_widget.setCellWidget(i, 1, hyperlink)
                    else:
                        for i in range(1, 5):
                            self.table_widget.setItem(i, 0, QTableWidgetItem(str(gpu_specs[i]) + '\t'))
                            self.table_widget.setItem(i, 1, QTableWidgetItem(str('-')))
            elif text == 'Оперативная память':
                ram_manufacturer = str(popen('wmic memorychip get Manufacturer').read().encode()).split('\\n\\n')
                ram_speed = str(popen('wmic memorychip get Speed').read().encode()).split('\\n\\n')
                pagefile = str(popen('wmic pagefileset get InitialSize, MaximumSize, Name').read().encode()).split('\\n\\n')
                ram_manufacturer.pop(0)
                ram_speed.pop(0)
                pagefile.pop(0)
                row = 0
                for _ in range(2):
                    ram_manufacturer.pop(-1)
                    ram_speed.pop(-1)
                    pagefile.pop(-1)
                self.setup_table((len(ram_manufacturer) * 2) + (len(pagefile) * 3) + 1)
                if len(ram_manufacturer) != 1:
                    for i in range(len(ram_manufacturer)):
                        self.table_widget.setItem(row, 0, QTableWidgetItem(str(f'Фирма-производитель модуля памяти #{i + 1}\t')))
                        if ram_manufacturer[i].isdigit():
                            ram_manufacturer[i] = ram_manufacturer[i].rstrip() + '- производитель незарегистрирован'
                        self.table_widget.setItem(row, 1, QTableWidgetItem(str(ram_manufacturer[i].rstrip())))
                        self.table_widget.setItem(row + 1, 0, QTableWidgetItem(str(f'Частота работы модуля памяти #{i + 1}\t')))
                        self.table_widget.setItem(row + 1, 1, QTableWidgetItem(str(ram_speed[i].rstrip() + ' МГц')))
                        row += 2
                else:
                    self.table_widget.setItem(row, 0, QTableWidgetItem(str('Фирма-производитель модуля памяти\t')))
                    if ram_manufacturer[0].isdigit():
                        ram_manufacturer[0] = ram_manufacturer[0].rstrip() + '- производитель незарегистрирован'
                    self.table_widget.setItem(row, 1, QTableWidgetItem(str(ram_manufacturer[0].rstrip())))
                    self.table_widget.setItem(row + 1, 0, QTableWidgetItem(str('Частота работы модуля памяти\t')))
                    self.table_widget.setItem(row + 1, 1, QTableWidgetItem(str(ram_speed[0].rstrip() + ' МГц')))             
                row += 1
                for i in range(len(pagefile)):
                    pagefile[i] = pagefile[i].split()
                if len(pagefile) != 1:
                    for i in range(len(pagefile)):
                        self.table_widget.setItem(row, 0, QTableWidgetItem(str(f'Адрес файла подкачки #{i + 1}\t')))
                        self.table_widget.setItem(row, 1, QTableWidgetItem(str(pagefile[i][2].replace('\\\\', '\\'))))
                        self.table_widget.setItem(row + 1, 0, QTableWidgetItem(str(f'Начальный размер файла подкачки #{i + 1}\t')))
                        self.table_widget.setItem(row + 1, 1, QTableWidgetItem(str(round(float(pagefile[i][0]) / 1024, 2)) + ' Гб'))
                        self.table_widget.setItem(row + 2, 0, QTableWidgetItem(str(f'Текущий размер файла подкачки #{i + 1}\t')))
                        self.table_widget.setItem(row + 2, 1, QTableWidgetItem(str(round(float(pagefile[i][1]) / 1024, 2)) + ' Гб'))
                        row += 3
                else:
                    self.table_widget.setItem(row, 0, QTableWidgetItem(str('Адрес файла подкачки\t')))
                    self.table_widget.setItem(row, 1, QTableWidgetItem(str(pagefile[0][2].replace('\\\\', '\\'))))
                    self.table_widget.setItem(row + 1, 0, QTableWidgetItem(str('Начальный размер файла подкачки\t')))
                    self.table_widget.setItem(row + 1, 1, QTableWidgetItem(str(round(float(pagefile[0][0]) / 1024, 2)) + ' Гб'))
                    self.table_widget.setItem(row + 2, 0, QTableWidgetItem(str('Текущий размер файла подкачки\t')))
                    self.table_widget.setItem(row + 2, 1, QTableWidgetItem(str(round(float(pagefile[0][1]) / 1024, 2)) + ' Гб'))
            elif text == 'Материнская плата':
                self.setup_table(5)
                self.table_widget.setItem(0, 0, QTableWidgetItem(str('Наименование материнской платы\t')))
                self.table_widget.setItem(1, 0, QTableWidgetItem(str('Фирма-производитель\t')))
                self.table_widget.setItem(2, 0, QTableWidgetItem(str('Информация от производителя\t')))
                self.table_widget.setItem(3, 0, QTableWidgetItem(str('Официальный драйвер\t')))
                self.table_widget.setItem(4, 0, QTableWidgetItem(str('Версия BIOS\t')))             
                info = self.get_mb_info()
                if info:
                    self.table_widget.setItem(0, 1, QTableWidgetItem(str(info[0])))
                    hyperlink_man = HyperlinkLabel(f'{info[1]}', f'{info[1]}')
                    self.table_widget.setCellWidget(2, 1, hyperlink_man)
                    hyperlink_driver = HyperlinkLabel(f'{info[2]}', f'{info[2]}')
                    self.table_widget.setCellWidget(3, 1, hyperlink_driver)
                else:
                    self.table_widget.setItem(0, 1, QTableWidgetItem(str('-')))
                    self.table_widget.setItem(2, 1, QTableWidgetItem(str('-')))
                    self.table_widget.setItem(3, 1, QTableWidgetItem(str('-')))                   
                mb_info_cmd = str(popen('wmic baseboard get manufacturer').read().encode()).split('\\n\\n')
                mb_bios_cmd = str(popen('wmic bios get smbiosbiosversion').read().encode()).split('\\n\\n')
                mb_info_cmd.pop(0)
                mb_bios_cmd.pop(0)
                self.table_widget.setItem(1, 1, QTableWidgetItem(str(mb_info_cmd[0].rstrip())))
                self.table_widget.setItem(4, 1, QTableWidgetItem(str(mb_bios_cmd[0].rstrip())))
            elif text == 'Логические диски':
                column_names = ['Том системы', 'Свободное место', 'Размер тома', 'Загруженность', 'Тип файловой системы']
                disks_info = str(popen('wmic logicaldisk get deviceid, freespace, size, filesystem').read().encode()).split('\\n\\n')
                disks_info.pop(0)
                for _ in range(2):
                    disks_info.pop(-1)            
                self.table_widget.setRowCount(len(disks_info))
                self.table_widget.setColumnCount(5)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                for i in range(len(disks_info)):
                    current_disk = disks_info[i].split()
                    self.table_widget.setItem(i, 0, QTableWidgetItem(str(current_disk[0])))
                    self.table_widget.setItem(i, 1, QTableWidgetItem(str(round(float(current_disk[2]) / pow(1024, 3), 2)) + ' Гб'))
                    self.table_widget.setItem(i, 2, QTableWidgetItem(str(round(float(current_disk[3]) / pow(1024, 3), 2)) + ' Гб'))
                    self.table_widget.setItem(i, 3, QTableWidgetItem(str(round((float(current_disk[2]) / float(current_disk[3])) * 100, 2)) + '%'))
                    self.table_widget.setItem(i, 4, QTableWidgetItem(str(current_disk[1])))                          
            elif text == 'Физические диски':
                column_names = ['Имя диска', 'Всего места']
                disks_info = str(popen('wmic diskdrive get model, size').read().encode()).split('\\n\\n')
                disks_info.pop(0)
                row = 0
                for _ in range(2):
                    disks_info.pop(-1)  
                self.table_widget.setRowCount(len(disks_info))
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                for item in disks_info:
                    item = item.rstrip()
                    for i in range(len(item) - 1, 0, -1):
                        if not item[i].isdigit():
                            self.table_widget.setItem(row, 0, QTableWidgetItem(str(item[0: i - 1].rstrip()) + '\t'))
                            self.table_widget.setItem(row, 1, QTableWidgetItem(str(round(float(item[i + 1:]) / pow(1024, 3), 2)) + ' Гб'))
                            row += 1
                            break 
#Если пользователь выбрал "ветвь" второго уровня, тогда мы сначала смотрим на то, какое значение
#имеет "ветвь" первого уровня, а затем смотрим значение "ветви" второго уровня, и в зависимости от этого форматируем таблицу
#нужным образом   
        elif root:
            if root == 'Процессор':
                self.root_for_timer = 'CPU'
                if text == 'Температура':
                    self.text_for_timer = 'Temperature'
                    column_names = ['Устройство', 'Температура']
                    self.table_widget.setRowCount(self.cpu_cores + 2)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_cpu_temp()
                elif text == 'Загрузка':
                    self.text_for_timer = 'Load'
                    column_names = ['Устройство', 'Загрузка']
                    self.table_widget.setRowCount(self.cpu_threads + 2)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_cpu_load()
                elif text == 'Частота':
                    self.text_for_timer = 'Clock'
                    column_names = ['Устройство', 'Частота']
                    self.table_widget.setRowCount(self.cpu_cores + 2)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_cpu_clock()
                elif text == 'Напряжение':
                    self.text_for_timer = 'Power'
                    column_names = ['Устройство', 'Напряжение']
                    self.table_widget.setRowCount(3)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_cpu_power()
            elif root == 'Видеокарта':
                self.root_for_timer = 'GPU'
                if text == 'Температура':
                    self.text_for_timer = 'Temperature'
                    column_names = ['Устройство', 'Температура']
                    self.table_widget.setRowCount(3)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_gpu_temp()
                elif text == 'Загрузка':
                    self.text_for_timer = 'Load'
                    column_names = ['Устройство', 'Загрузка']
                    self.table_widget.setRowCount(3)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_gpu_load()
                elif text == 'Частота':
                    self.text_for_timer = 'Clock'
                    column_names = ['Устройство', 'Частота']
                    self.table_widget.setRowCount(2)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_gpu_clock()
                elif text == 'Напряжение':
                    self.text_for_timer = 'Power'
                    column_names = ['Устройство', 'Напряжение']
                    self.table_widget.setRowCount(1)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_gpu_power()
                elif text == 'Память':
                    self.text_for_timer = 'SmallData'
                    column_names = ['Устройство', 'Память']
                    self.table_widget.setRowCount(3)
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_gpu_memory()
            elif root == 'Оперативная память':
                self.root_for_timer = 'RAM'
                if text == 'Числовая информация':
                    self.text_for_timer = 'Load'
                    column_names = ['Поле', 'Значение']
                    self.table_widget.setRowCount(len(self.ram_data) + 1 + len(self.ram_load))
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_ram_load()
            elif root == 'Материнская плата':
                self.root_for_timer = 'SuperIO'
                if text == 'Температура':
                    self.text_for_timer = 'Temperature'
                    column_names = ['Устройство', 'Температура']
                    self.table_widget.setRowCount(len(self.mb_temp))
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_mb_temp()
                elif text == 'Вольтаж':
                    self.text_for_timer = 'Voltage'
                    column_names = ['Устройство', 'Вольтаж']
                    self.table_widget.setRowCount(len(self.mb_voltage))
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_mb_voltage()
                elif text == 'Вентиляторы':
                    self.text_for_timer = 'Control'
                    column_names = ['Поле', 'Значение']
                    self.table_widget.setRowCount(len(self.mb_fans) + 1 + len(self.mb_fans_control))
                    self.table_widget.setColumnCount(2)
                    self.table_widget.setHorizontalHeaderLabels(column_names)
                    self.fill_table_mb_fans()
#В случае, если поток еще неактивен, то запускаем его
            if not self.stats_thread.running:
                self.stats_thread.running = True
#После выбора новой "ветки" запускаем таймер заново, чтобы обновление происходило стабильно раз в секунду без смещений
            self.timer.start(1000)

#Функция, открывающая окна с графиками
    def open_graphs_window(self):
        self.graphs_window = GraphsWindow()
    
#Функция, открывающая командную строку Windows
    def open_cmd(self):
        system('start cmd.exe')

#Функция, открывающая Windows PowerShell
    def open_powershell(self):
        system('start powershell.exe')
    
#Функция, открывающая окно формирования отчета о системе
    def create_report(self):
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        path = getcwd()
        system(f'start cmd.exe /C msinfo32 /report "{path}\\AInPC Report {current_time}.txt"')

#Функция, отвечающая за безопасное выключение программы
    def closeEvent(self, event):
        self.hide()
        self.stats_thread.running = False
        self.timer.stop()
        self.stop_thread()
        super().closeEvent(event)

#Функция, создающая главное окно и запускающая его
@main_requires_admin
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

#Вызываем функцию, которая создает главное окно, 
#и обрабатываем случай, если пользователь передумал запускать программу
if __name__ == '__main__':
    try:
        main()
    except PyWinError:
        exit()