from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QPushButton

from util import get_QPixmap


class PicButton(QPushButton):
    def __init__(self, app, path, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = get_QPixmap(app, path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


class TogglePicButton(PicButton):
    def __init__(self, app, path, parent=None):
        super().__init__(app, path, parent)
        self.setCheckable(True)
        self.setChecked(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        opacity = 0.5 if not self.isChecked() else 1.0
        painter.setOpacity(opacity)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()
