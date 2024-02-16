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
            massive.extend(self.parse(temp_massive))
            for j in i.SubHardware:
                j.Update()
                temp_massive = []
                for subsensor in j.Sensors:
                    temp_info = self.parse_sensor(subsensor)
                    if temp_info:
                        temp_massive.append(temp_info)
                massive.extend(self.parse(temp_massive))
        
    def parse_sensor(self, sensor):
        if sensor.Value:
            return [sensor.Index, sensor.Name, sensor.Value, str(sensor.SensorType), hwtypes[sensor.Hardware.HardwareType]]

    def parse(self, massive):
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