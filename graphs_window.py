from fetch import *
from global_import import *


class GraphsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.values_list = []
        self.names_list = []
        self.graphs_list = []

        splash_for_graphs = self.show_graphs_splash_screen()
        self.initializing_graphs = InitializingGraphsThread(splash_for_graphs)
        self.initializing_graphs.start()
        self.initializing_graphs.iniatilizing_graphs_signal.connect(self.on_change_init)

        self.graphs_thread = GraphsThread()
        self.graphs_thread.graphs_signal.connect(self.on_change)

    def show_graphs_splash_screen(self):
        splash_pix = QPixmap(getcwd() + "/recources//graph_icon.png").scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
        splash.setFixedSize(500, 500)
        splash.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        splash.setEnabled(False)

        splash.show()
        return splash
        
    def create_graphs_window(self, splash):
        splash.close()

        self.setWindowTitle("AInPC Графики")
        self.setFixedSize(QSize(900, 500))
        central_widget = QWidget()
        layout = QVBoxLayout()

        scroll_area = QScrollArea(self)
        scroll_widget = QWidget(scroll_area)
        scroll_layout = QVBoxLayout(scroll_widget)

        self.plot_widgets = []
        n = 0
        if len(self.graphs_list) // 2:
            row_count = len(self.graphs_list) // 2 + 1
        else:
            row_count = len(self.graphs_list) // 2
        for _ in range(0, row_count):
            if n == len(self.graphs_list):
                break
            graph_row_widget = QWidget()
            row_layout = QHBoxLayout()
            for _ in range(2):
                name = self.graphs_list[n][0]
                plot_widget = pyqtgraph.PlotWidget()
                plot_widget.setMouseEnabled(x = False, y = False)
                plot_widget.setBackground("w")
                plot_widget.showGrid(x = True, y = True)
                plot_widget.setFixedWidth(405)
                plot_widget.plotItem.setFixedWidth(395)
                plot_widget.setFixedHeight(220)
                plot_widget.plotItem.setFixedHeight(215)
                plot_widget.plotItem.setTitle(name, color = (0, 0, 0)) 
                x_axis = plot_widget.getAxis("bottom")
                #x_axis.setStyle(showValues = False)
                if "Температура" in name:
                    plot_widget.plotItem.setLabel('left', '<b>Значение (\u00B0C)<\b>', color = (0, 0, 0))
                    pen = pyqtgraph.mkPen(color = (255, 0, 0), width = 4.5)
                elif "Частота" in name:
                    if "ядра" in name:
                        plot_widget.plotItem.setLabel('left', '<b>Значение (GHz)<\b>', color = (0, 0, 0))
                    else:
                        plot_widget.plotItem.setLabel('left', '<b>Значение (MHz)<\b>', color = (0, 0, 0))
                    pen = pyqtgraph.mkPen(color = (0, 0, 0), width = 4.5)
                elif "Загруженность" in name:
                    plot_widget.plotItem.setLabel('left', '<b>Значение (%)<\b>', color = (0, 0, 0))
                    pen = pyqtgraph.mkPen(color = (0, 255, 0), width = 4.5)
                elif "Скорость вращения" in name:
                    plot_widget.plotItem.setLabel('left', '<b>Значение (об\мин)<\b>', color = (0, 0, 0))
                    pen = pyqtgraph.mkPen(color = (0, 0, 255), width = 4.5)
                plot_widget.plotItem.setLabel('bottom', '<b>Время (сек.)<\b>', color = (0, 0, 0))
                plotx = plot_widget.plot([], [], pen = pen)
                self.plot_widgets.append((plot_widget, plotx))
                row_layout.addWidget(plot_widget)
                n = n + 1
                if n == len(self.graphs_list):
                    break
            graph_row_widget.setLayout(row_layout)
            scroll_layout.addWidget(graph_row_widget)
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)       

        self.show()    

        self.graphs_thread.start()
 

    def on_change_init(self, data):
        self.values_list = data[0]
        self.names_list = data[1]

        self.graphs_list = self.sort_values(self.values_list, self.names_list)
        self.create_graphs_window(data[2])

    def on_change(self, data):
        self.values_list = data[0]
        self.names_list = data[1]
        self.update_graphs()

    def update_graphs(self):
        self.correlate_values(self.graphs_list, self.values_list, self.names_list)
        j = 0
        for self.plot_widget, plot in self.plot_widgets:
            x_ax = [i for i in range(1, len(self.graphs_list[j]))]
            plot.setData(x_ax, self.graphs_list[j][1:])
            j += 1

    def stop_thread(self):
        self.graphs_thread.stop()

    def sort_values(self, values_list, names_list):

        temp_list = []
        temp_list += (sorted([sublist for sublist in values_list if 'Температура ядра процессора' in sublist[0]], key=lambda x: int(x[0].split("#")[1])))
        temp_list += (sorted([sublist for sublist in values_list if 'Загруженность ядра' in sublist[0]], key=lambda x: int(re.search(r'#(\d+)', x[0]).group(1))))
        temp_list += (sorted([sublist for sublist in values_list if 'Частота работы ядра процессора' in sublist[0]], key=lambda x: int(x[0].split("#")[1])))
        temp_list += [values_list[names_list.index('Частота работы шины процессора')]]
        if names_list.count('Температура ядра видеокарты') > 1:
            indexes = [index for index, item in enumerate(names_list) if item == 'Температура ядра видеокарты']
            temp_list += [values_list[index] for index in indexes]
        else:
            temp_list += [values_list[names_list.index('Температура ядра видеокарты')]]
        if 'Температура памяти видеокарты' in names_list:
            if names_list.count('Температура памяти видеокарты') > 1:
                indexes = [index for index, item in enumerate(names_list) if item == 'Температура памяти видеокарты']
                temp_list += [values_list[index] for index in indexes]
            else:
                temp_list += [values_list[names_list.index('Температура памяти видеокарты')]]
        if 'Температура Hot Spot видеокарты' in names_list:
            if names_list.count('Температура Hot Spot видеокарты') > 1:
                indexes = [index for index, item in enumerate(names_list) if item == 'Температура Hot Spot видеокарты']
                temp_list += [values_list[index] for index in indexes]
            else:
                temp_list += [values_list[names_list.index('Температура Hot Spot видеокарты')]]
        if names_list.count('Частота работы ядра видеокарты') > 1:
            indexes = [index for index, item in enumerate(names_list) if item == 'Частота работы ядра видеокарты']
            temp_list += [values_list[index] for index in indexes]
        else:
            temp_list += [values_list[names_list.index('Частота работы ядра видеокарты')]]
        if 'Частота работы памяти видеокарты' in names_list:
            if names_list.count('Частота работы памяти видеокарты') > 1:
                indexes = [index for index, item in enumerate(names_list) if item == 'Частота работы памяти видеокарты']
                temp_list += [values_list[index] for index in indexes]
            else:
                temp_list += [values_list[names_list.index('Частота работы памяти видеокарты')]]    
        temp_list += [values_list[names_list.index('Загруженность оперативной памяти')]]  
        temp_list += (sorted([sublist for sublist in values_list if 'Температура сенсора материнской платы' in sublist[0]], key=lambda x: int(x[0].split("#")[1])))
        temp_list += (sorted([sublist for sublist in values_list if 'Скорость вращения вентилятора' in sublist[0]], key=lambda x: int(x[0].split("#")[1])))
        return temp_list
    
    def correlate_values(self, graphs_list, values_list, names_list):
        while values_list:
            for graphs_item in graphs_list:
                for values_item in values_list:          
                    if graphs_item[0] not in names_list:
                        if len(graphs_item) > 60:
                            del graphs_item[1]
                        graphs_list[graphs_list.index(graphs_item)].append(graphs_item[-1])
                        break
                    if values_item[0] == graphs_item[0]:
                        if len(graphs_item) > 60:
                            del graphs_item[1]
                        graphs_list[graphs_list.index(graphs_item)].append(values_item[1])
                        del values_list[values_list.index(values_item)]
                        break               

    def closeEvent(self, event):
        self.hide()
        self.graphs_thread.running = False
        self.stop_thread()
        super().closeEvent(event)