#Импортируем из остальных файлов проекта необходимые зависимости - классы, функции и модули
from PyQt6.QtWidgets import QLabel

#Класс для отображения и корректной работы гиперссылок на сайт производителя
class HyperlinkLabel(QLabel):
    def __init__(self, text, link):
        super().__init__()
        self.setText(f'<a href="{link}">{text}</a>')
        self.setOpenExternalLinks(True)