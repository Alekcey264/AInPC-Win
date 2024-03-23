from global_import import *

def get_gpu_info(name):
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM gpu_info WHERE gpu_name = ?', (name,))
        return cursor.fetchone()
    except sqlite3.Error as error:
        pass
    finally:
        if not cursor.fetchone():
            message_box = QMessageBox()
            message_box.setWindowTitle('Ошибка')
            message_box.setText(f'Возникла ошибка в ходе получения информации о видеокарте {name}, пожалуйста, попробуйте открыть вкладку повторно или перезапустите программу.')
            message_box.setIcon(QMessageBox.Icon.Warning)
            message_box.exec()
        if conn:
            conn.close()

print(get_gpu_info("asd"))