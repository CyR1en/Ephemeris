import qdarkstyle
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QDialog
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from groups import LoginGroupBox, InputGroupBox, EphemerisGroupBox
from service import GoogleService
from widgets import PicButton
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
        self.app.focusChanged.connect(self.on_focus_change)

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
        if new is None and self.dialog is not None:
            self.dialog.setVisible(False)

    def system_icon(self, reason):
        if reason != self.DoubleClick:
            return
        self.dialog.setVisible(True)
        self.dialog.move(self._get_relative_pos())
        self.dialog.activateWindow()
        self.dialog.raise_()

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
        self.setFixedWidth(230)
        self._set_flags()

    def switch_current_view(self, new: EphemerisGroupBox):
        self._main_layout.replaceWidget(self._current_view, new)
        self._current_view.deleteLater()
        self._current_view = new
        self._switch_button(new)
        self.refresh()
        self.raise_()
        self.activateWindow()

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
        self._setup_header_widgets()
        header.addWidget(logo)
        header.addWidget(label)
        header.addStretch(2)
        header.addWidget(self.cog)
        return header

    def _setup_header_widgets(self):
        self.cog = PicButton(self.app, 'cog.png')
        self.cog.setContextMenuPolicy(Qt.CustomContextMenu)

        self.menu = QMenu()
        self.quit_a = QAction("Quit")
        self.pin_a = QAction("Pin")
        self.menu.addAction(self.pin_a)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_a)
        self.pin_a.triggered.connect(self._on_pin_click)
        self.quit_a.triggered.connect(self.app.app.quit)

        self.cog.setMenu(self.menu)

    def _on_cog_click(self, point):
        self.menu.exec_(self.cog.mapToGlobal(point))

    def _on_pin_click(self):
        self.ephemeris.is_pinned = not self.ephemeris.is_pinned
        text = 'Unpin' if self.ephemeris.is_pinned else 'Pin'
        self.pin_a.setText(text)
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
