import clr
import os
from pyuac import main_requires_admin

hwtypes = ['Mainboard','SuperIO','CPU','RAM','GpuNvidia','GpuAti','TBalancer','Heatmaster','HDD']

def initialize():
     
    dll_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'LibreHardwareMonitorLib.dll'))
    clr.AddReference(dll_path)

    from LibreHardwareMonitor import Hardware

    computer = Hardware.Computer()
    computer.IsMotherboardEnabled = True
    computer.IsCpuEnabled = True
    computer.IsMemoryEnabled = True
    computer.IsGpuEnabled = True
    computer.IsStorageEnabled = True
    computer.Open()

    return computer

def fetch_stats(handle, massive):
    massive.clear()
    for i in handle.Hardware:
        i.Update()
        temp_massive = []
        for sensor in i.Sensors:
            temp_info = parse_sensor(sensor)
            if temp_info:
                temp_massive.append(temp_info)
        massive.extend(parse(temp_massive))
        for j in i.SubHardware:
            j.Update()
            temp_massive = []
            for subsensor in j.Sensors:
                temp_info = parse_sensor(subsensor)
                if temp_info:
                    temp_massive.append(temp_info)
            massive.extend(parse(temp_massive))

def parse(massive):
    result_list = []
    for item in massive:
        key = item[2]
        found = False
        for group in result_list:
            if group[0][2] == key:
                group.append(item)
                found = True
                break
        if not found:
            result_list.append([item])
    return result_list

def parse_sensor(sensor):
    if sensor.Value:
        #if str(sensor.SensorType) == type_of_sensor and device == hwtypes[sensor.Hardware.HardwareType]:
            return [hwtypes[sensor.Hardware.HardwareType], 
                            sensor.Hardware.Name, str(sensor.SensorType), sensor.Index, 
                            sensor.Name, sensor.Value]


@main_requires_admin
def main():
    temperature_massive = []
    HardwareHandle = initialize()
    fetch_stats(HardwareHandle, temperature_massive)
    print(len(temperature_massive))
    print(*temperature_massive, sep = "\n*******\n")

if __name__ == "__main__":
    main()
        
        