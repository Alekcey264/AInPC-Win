from PyQt6.QtWidgets import QLabel

class HyperlinkLabel(QLabel):
    def __init__(self, text, link):
        super().__init__()
        self.setText(f'<a href="{link}">{text}</a>')
        self.setOpenExternalLinks(True)