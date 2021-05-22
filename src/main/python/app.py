import qdarkstyle
from PyQt5 import sip
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QAction)
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from groups import LoginGroupBox, InputGroupBox, EphemerisGroupBox
from service import GoogleService
from util import get_QIcon


class EphemerisApp(QSystemTrayIcon):
    def __init__(self):
        self.app_ctx = ApplicationContext()
        self.app = self.app_ctx.app
        # apply_stylesheet(self.app, theme='dark_lightgreen.xml')
        self.app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        self.app.setQuitOnLastWindowClosed(False)
        self.gallery = EphemerisDialog(self.app_ctx)
        super().__init__()
        self.initialize_self()
        menu = QMenu()
        quit_a = QAction("Quit")
        menu.addAction(quit_a)
        quit_a.triggered.connect(self.app.quit)
        self.app.focusChanged.connect(self.on_focus_change)
        self.setContextMenu(menu)
        self.app.exec_()

    def initialize_self(self):
        # Initialize system tray icon
        icon = get_QIcon(self.app_ctx, 'logo.png')
        self.setIcon(icon)
        self.setVisible(True)
        self.activated.connect(self.system_icon)

    def on_focus_change(self, old, new):
        print(old, new)
        if new is None:
            self.gallery.setVisible(False)

    def system_icon(self, reason):
        if reason != self.DoubleClick:
            return
        print('Clicked')
        print(QCursor.pos())
        self.gallery.setVisible(True)
        self.gallery.raise_()
        self.gallery.activateWindow()
        self.gallery.move(self._get_relative_pos())

    def _get_relative_pos(self):
        cursor_pos = QCursor.pos()
        relative_pos = QPoint()
        w_size = self.gallery.size()
        s_size = self.app.primaryScreen().size()
        x = cursor_pos.x() - ((w_size.width()) / 2)
        if (x + w_size.width()) > s_size.width():
            x = s_size.width() - w_size.width()
        relative_pos.setX(x)
        relative_pos.setY(cursor_pos.y() - (w_size.height()))
        return relative_pos


class EphemerisDialog(QDialog):
    def __init__(self, app_ctx, parent=None):
        super(EphemerisDialog, self).__init__(parent)
        self.app_ctx = app_ctx
        self._header_title = 'E P H E M E R I S'
        self.google_service = GoogleService(app_ctx)

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self._create_head())

        self._current_view = self._get_start_view()
        self._main_layout.addWidget(self._current_view)

        self.setLayout(self._main_layout)
        self._set_flags()
        self.setMaximumSize(400, 300)

    def switch_current_view(self, new: EphemerisGroupBox):
        self._main_layout.removeWidget(self._current_view)
        sip.delete(self._current_view)
        self._current_view = new
        self._main_layout.addWidget(self._current_view)
        self.setVisible(True)
        self.raise_()
        self.activateWindow()

    def _get_start_view(self):
        if not self.google_service.is_logged_in():
            return LoginGroupBox(self)
        else:
            self.google_service.prepare_credentials()
            self.google_service.build_resource()
            return InputGroupBox(self)

    def _set_flags(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.Popup)

    def _create_head(self):
        label = QLabel(self._header_title)
        header = QHBoxLayout()
        header.addWidget(label)
        header.addStretch(1)
        return header
