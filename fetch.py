from global_import import *

hwtypes = ['Mainboard','SuperIO','CPU','RAM','GpuNvidia','GpuAti','TBalancer','Heatmaster','HDD']


class StatsThread(QThread):
    sensors_signal = pyqtSignal(list)
    def __init__(self):
        QThread.__init__(self)
        self.running = False
        
    def fetch_stats(self, massive):
        massive.clear()
        for i in dll_access.Hardware:
            i.Update()
            temp_massive = []
            for sensor in i.Sensors:
                temp_info = self.parse_sensor(sensor)
                if temp_info:
                    temp_massive.append(temp_info)
            massive.extend(self.parse_values(temp_massive))
            for j in i.SubHardware:
                j.Update()
                temp_massive = []
                for subsensor in j.Sensors:
                    temp_info = self.parse_sensor(subsensor)
                    if temp_info:
                        temp_massive.append(temp_info)
                massive.extend(self.parse_values(temp_massive))
        
    def parse_sensor(self, sensor):
        if sensor.Value:
            return [sensor.Index, sensor.Name, sensor.Value, str(sensor.SensorType), hwtypes[sensor.Hardware.HardwareType]]

    def parse_values(self, massive):
        result_list = []
        for item in massive:
            key = item[3]
            found = False
            for group in result_list:
                if group[0][3] == key:
                    group.append(item)
                    found = True
                    break
            if not found:
                result_list.append([item])
        return result_list

    def run(self):
        self.running = True
        while self.running:
            container = []
            self.fetch_stats(container)
            self.sensors_signal.emit(container)
            self.sleep(1)

    def stop(self):
        self.terminate()

class GraphsThread(QThread):
    graphs_signal = pyqtSignal(list)
    def __init__(self):
        QThread.__init__(self)
        self.running = False

    def fetch_stats(self, massive):
        self.values = []
        self.names = []
        for i in dll_access.Hardware:
            i.Update()
            for sensor in i.Sensors:
                self.parse_sensor(sensor, self.values, self.names)
            for j in i.SubHardware:
                j.Update()
                for subsensor in j.Sensors:
                    self.parse_sensor(subsensor, self.values, self.names)
        massive.extend([self.values, self.names])
    
    def parse_sensor(self, sensor, values, names):
        sensor_types = [['Temperature', 'SuperIO'], ['Fan', 'SuperIO'], ['Load', 'CPU'], ['Temperature', 'CPU'], ['Clock', 'CPU'], ['Load', 'RAM'], ['Temperature', 'Gpu'], ['Clock', 'Gpu']]
        not_allowed = ['CPU Total', 'CPU Package', 'Distance to TjMax', 'Max', 'Virtual', 'Average']
        if sensor.Value:
            sensor_type = str(sensor.SensorType)
            hardware_type = hwtypes[sensor.Hardware.HardwareType]
            for item in sensor_types:
                if sensor_type in item[0] and item[1] in hardware_type:
                    name = sensor.Name
                    flag = True
                    for subitem in not_allowed:
                        if subitem in name:
                            flag = False
                            break
                    if not flag:
                        continue
                    if 'Temperature' in name and sensor_type == 'Temperature' and hardware_type == 'SuperIO':
                        name = name.replace('Temperature', 'Температура сенсора материнской платы')
                    elif 'Fan' in name and sensor_type == 'Fan' and hardware_type == 'SuperIO':
                        name = name.replace('Fan', 'Скорость вращения вентилятора')
                    elif 'CPU Core' in name and sensor_type == 'Load':
                        name = name.replace('CPU Core', 'Загруженность ядра').replace('Thread', 'потока')
                    elif 'CPU Core' in name and sensor_type == 'Temperature':
                        name = name.replace('CPU Core', 'Температура ядра процессора')
                    elif 'CPU Core' in name and sensor_type == 'Clock':
                        name = name.replace('CPU Core', 'Частота работы ядра процессора')
                    elif 'Bus Speed' in name and sensor_type == 'Clock':
                        name = name.replace('Bus Speed', 'Частота работы шины процессора')
                    elif 'Memory' in name and sensor_type == 'Load' and hardware_type == 'RAM':
                        name = name.replace('Memory', 'Загруженность оперативной памяти')
                    elif 'GPU Core' in name and sensor_type == 'Temperature':
                        name = name.replace('GPU Core', 'Температура ядра видеокарты')
                    elif 'GPU Memory' in name and sensor_type == 'Temperature':
                        name = name.replace('GPU Memory', 'Температура памяти видеокарты')
                    elif 'GPU Core' in name and sensor_type == 'Clock':
                        name = name.replace('GPU Core', 'Частота работы ядра видеокарты')
                    elif 'GPU Memory' in name and sensor_type == 'Clock':
                        name = name.replace('GPU Memory', 'Частота работы памяти видеокарты')
                    elif 'GPU Hot Spot' in name and sensor_type == 'Temperature':
                        name = name.replace('GPU Hot Spot', 'Температура Hot Spot видеокарты')
                    elif 'GPU Memory' in name and sensor_type == 'Temperature':
                        name = name.replace('GPU Memory', 'Температура памяти видеокарты')

                    values.append([name, float(sensor.Value)])
                    names.append(name)

    def run(self):
        self.running = True
        while self.running:
            container = []
            self.fetch_stats(container)
            self.graphs_signal.emit(container)
            self.sleep(1)

    def stop(self):
        self.terminate()

class InitializingGraphsThread(QThread):
    iniatilizing_graphs_signal = pyqtSignal(list)
    def __init__(self, splash):
        QThread.__init__(self)
        self.splash = splash

    def fetch_stats(self, massive):
        self.values = []
        self.names = []
        self.current_values = []
        self.current_names = []
        self.values_max = 1
        self.values_current = 0
        for _ in range(20):
            if self.values_max >= self.values_current:
                pass
            else:
                self.values_max = self.values_current
                self.values = self.current_values
                self.names = self.current_names
            self.current_values = []
            self.current_names = []
            for i in dll_access.Hardware:
                i.Update()
                for sensor in i.Sensors:
                    self.parse_sensor(sensor, self.current_values, self.current_names)
                for j in i.SubHardware:
                    j.Update()
                    for subsensor in j.Sensors:
                        self.parse_sensor(subsensor, self.current_values, self.current_names)
            self.values_current = len(self.current_values)
        massive.extend([self.values, self.names])
    
    def parse_sensor(self, sensor, values, names):
        sensor_types = [['Temperature', 'SuperIO'], ['Fan', 'SuperIO'], ['Load', 'CPU'], ['Temperature', 'CPU'], ['Clock', 'CPU'], ['Load', 'RAM'], ['Temperature', 'Gpu'], ['Clock', 'Gpu']]
        not_allowed = ['CPU Total', 'CPU Package', 'Distance to TjMax', 'Max', 'Virtual', 'Average']
        if sensor.Value:
            sensor_type = str(sensor.SensorType)
            hardware_type = hwtypes[sensor.Hardware.HardwareType]
            for item in sensor_types:
                if sensor_type in item[0] and item[1] in hardware_type:
                    name = sensor.Name
                    flag = True
                    for subitem in not_allowed:
                        if subitem in name:
                            flag = False
                            break
                    if not flag:
                        continue
                    if 'Temperature' in name and sensor_type == 'Temperature' and hardware_type == 'SuperIO':
                        name = name.replace('Temperature', 'Температура сенсора материнской платы')
                    elif 'Fan' in name and sensor_type == 'Fan' and hardware_type == 'SuperIO':
                        name = name.replace('Fan', 'Скорость вращения вентилятора')
                    elif 'CPU Core' in name and sensor_type == 'Load':
                        name = name.replace('CPU Core', 'Загруженность ядра').replace('Thread', 'потока')
                    elif 'CPU Core' in name and sensor_type == 'Temperature':
                        name = name.replace('CPU Core', 'Температура ядра процессора')
                    elif 'CPU Core' in name and sensor_type == 'Clock':
                        name = name.replace('CPU Core', 'Частота работы ядра процессора')
                    elif 'Bus Speed' in name and sensor_type == 'Clock':
                        name = name.replace('Bus Speed', 'Частота работы шины процессора')
                    elif 'Memory' in name and sensor_type == 'Load' and hardware_type == 'RAM':
                        name = name.replace('Memory', 'Загруженность оперативной памяти')
                    elif 'GPU Core' in name and sensor_type == 'Temperature':
                        name = name.replace('GPU Core', 'Температура ядра видеокарты')
                    elif 'GPU Memory' in name and sensor_type == 'Temperature':
                        name = name.replace('GPU Memory', 'Температура памяти видеокарты')
                    elif 'GPU Core' in name and sensor_type == 'Clock':
                        name = name.replace('GPU Core', 'Частота работы ядра видеокарты')
                    elif 'GPU Memory' in name and sensor_type == 'Clock':
                        name = name.replace('GPU Memory', 'Частота работы памяти видеокарты')
                    elif 'GPU Hot Spot' in name and sensor_type == 'Temperature':
                        name = name.replace('GPU Hot Spot', 'Температура Hot Spot видеокарты')
                    elif 'GPU Memory' in name and sensor_type == 'Temperature':
                        name = name.replace('GPU Memory', 'Температура памяти видеокарты')

                    values.append([name, float(sensor.Value)])
                    names.append(name)

    def run(self):
        container = []
        self.fetch_stats(container)
        container.append(self.splash)
        self.iniatilizing_graphs_signal.emit(container)

def initialize_cpu_info():
    cpu_name = str(popen("wmic cpu get name").read().encode()).split("\\n\\n")
    cpu_name = cpu_name[1].strip()
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cpu_info WHERE cpu_name = ?", (cpu_name,))
        info = cursor.fetchone()
        return int(info[3]), int(info[4])
        
    except sqlite3.Error as error:
        message_box = QMessageBox()
        message_box.setWindowTitle("Ошибка")
        message_box.setText(f"Возникла ошибка в ходе получения информации о процессоре {cpu_name}, пожалуйста, попробуйте открыть вкладку повторно или перезапустите программу.")
        message_box.setIcon(QMessageBox.Icon.Warning)
        message_box.exec()
    finally:
        if conn:
            conn.close()

def initialize_dll():
    file = getcwd() + '\\LibreHardwareMonitorLib'
    clr.AddReference(file)

    from LibreHardwareMonitor import Hardware

    computer = Hardware.Computer()
    computer.IsMotherboardEnabled = True
    computer.IsCpuEnabled = True
    computer.IsMemoryEnabled = True
    computer.IsGpuEnabled = True
    computer.IsStorageEnabled = True
    computer.Open()

    return computer

dll_access = initialize_dll()