import qdarkstyle
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QIcon, QPainter
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QDialog
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from groups import LoginGroupBox, InputGroupBox, EphemerisGroupBox
from service import GoogleService
from util import get_QPixmap, app_logo


class EphemerisApp(QSystemTrayIcon):
    def __init__(self, app_ctx: ApplicationContext):
        self.is_pinned = False
        self.app_ctx = app_ctx
        self.app = self.app_ctx.app
        self.app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        self.app.setQuitOnLastWindowClosed(False)
        self.dialog = EphemerisDialog(self)
        super().__init__()
        self.initialize_self()
        menu = QMenu()
        quit_a = QAction("Quit")
        menu.addAction(quit_a)
        quit_a.triggered.connect(self.app.quit)
        self.app.focusChanged.connect(self.on_focus_change)
        self.setContextMenu(menu)

    def initialize_self(self):
        # Initialize system tray icon
        icon = app_logo(self.app_ctx)
        self.setIcon(icon)
        self.setVisible(True)
        self.activated.connect(self.system_icon)

    def on_focus_change(self, old, new):
        if self.is_pinned:
            return
        print(old, new)
        if new is None:
            self.dialog.setVisible(False)

    def system_icon(self, reason):
        if reason != self.DoubleClick:
            return
        print('Clicked')
        print(QCursor.pos())
        self.dialog.setVisible(True)
        self.dialog.raise_()
        self.dialog.activateWindow()
        self.dialog.move(self._get_relative_pos())

    def _get_relative_pos(self):
        cursor_pos = QCursor.pos()
        relative_pos = QPoint()
        w_size = self.dialog.size()
        s_size = self.app.primaryScreen().size()
        x = cursor_pos.x() - ((w_size.width()) / 2)
        if (x + w_size.width()) > s_size.width():
            x = s_size.width() - w_size.width()
        relative_pos.setX(x)
        y = self._get_y_pos(cursor_pos, w_size, s_size)
        relative_pos.setY(y)
        return relative_pos

    @staticmethod
    def _get_y_pos(cursor_pos, w_size, s_size):
        y = (cursor_pos.y() - (w_size.height()))
        if cursor_pos.y() > (s_size.width() / 2):
            y = cursor_pos.y()
        return y


class EphemerisDialog(QDialog):
    def __init__(self, app: EphemerisApp, parent=None):
        super(EphemerisDialog, self).__init__(parent)
        self.offset = QPoint()
        self.ephemeris = app
        self.app = app.app_ctx
        self._header_title = 'E P H E M E R I S'
        self.google_service = GoogleService(self.app)

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self._create_head())
        self._bottom_btn = QPushButton()
        self._current_view = self._get_start_view()
        self._main_layout.addWidget(self._current_view)
        self._main_layout.addWidget(self._bottom_btn)
        self.setLayout(self._main_layout)
        self._set_flags()

    def switch_current_view(self, new: EphemerisGroupBox):
        self._main_layout.replaceWidget(self._current_view, new)
        self._current_view.deleteLater()
        self._current_view = new
        self._switch_button(new)
        self.refresh()
        self.raise_()

    def refresh(self):
        self.setVisible(False)
        self.setVisible(True)

    def _switch_button(self, group):
        self._bottom_btn.setText(group.button_label)
        self._bottom_btn.setIcon(QIcon() if group.button_icon is None else group.button_icon)
        try:
            self._bottom_btn.disconnect()
        except():
            pass
        self._bottom_btn.clicked.connect(group.button_click)
        self._bottom_btn.setFocus()

    def _get_start_view(self):
        if not self.google_service.is_token_exists():
            group = LoginGroupBox(self)
            self._switch_button(group)
            return group
        else:
            self.google_service.prepare_credentials()
            self.google_service.build_resource()
            group = InputGroupBox(self)
            self._switch_button(group)
            return group

    def _set_flags(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)

    def _create_head(self):
        logo = QLabel()
        logo.setPixmap(get_QPixmap(self.app, 'logo_transparent_tiny.png'))
        label = QLabel(self._header_title)
        logo.setBuddy(label)
        header = QHBoxLayout()
        header.addWidget(logo)
        header.addWidget(label)
        header.addStretch()
        self.pin = PinButton(self.app)
        self.pin.clicked.connect(self._on_pin_click)
        header.addStretch(1)
        header.addWidget(self.pin)
        return header

    def _on_pin_click(self):
        self.ephemeris.is_pinned = self.pin.isChecked()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.ephemeris.is_pinned)
        print(f'set to {self.ephemeris.is_pinned}')
        self.show()

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x - x_w, y - y_w)


class PinButton(QPushButton):
    def __init__(self, app, parent=None):
        super(PinButton, self).__init__(parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.pixmap_0 = get_QPixmap(app, 'pin_0.png')
        self.pixmap_1 = get_QPixmap(app, 'pin_1.png')

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self.pixmap_1 if self.isChecked() else self.pixmap_0
        painter.drawPixmap(event.rect(), pixmap)

    def sizeHint(self):
        return self.pixmap_0.size()
