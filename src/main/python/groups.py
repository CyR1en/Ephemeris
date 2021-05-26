import abc
import datetime

from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QIcon, QFont, QPainter
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QLineEdit, QAbstractButton

import service_models
from util import get_QPixmap


class EphemerisGroupBox(QGroupBox):
    def __init__(self, dia, button_label='Button'):
        super().__init__()
        self.dia = dia
        self.button_label = button_label
        self.button_icon = None

    @abc.abstractmethod
    def button_click(self):
        pass


class LoginGroupBox(EphemerisGroupBox):
    def __init__(self, dia):
        super().__init__(dia, ' Login with Google')
        icon = QIcon(get_QPixmap(self.dia.app, 'google.png'))
        self.button_icon = icon
        layout = QVBoxLayout()
        layout.addWidget(self._make_logo())
        self.setLayout(layout)
        self.setStyleSheet('border:none')

    def _make_logo(self):
        logo = QLabel(self)
        logo.setAlignment(Qt.AlignCenter)
        pixmap = get_QPixmap(self.dia.app, 'logo_win.png')
        logo.setPixmap(pixmap)
        return logo

    def button_click(self):
        print('test')
        self.dia.google_service.prepare_credentials()
        self.dia.google_service.build_resource()
        self.dia.switch_current_view(InputGroupBox(self.dia))
        self.dia.app.is_pinned = True


class InputGroupBox(EphemerisGroupBox):
    def __init__(self, dia):
        super().__init__(dia, 'Start Tracking')
        self.name_in = QLineEdit()
        self.desc_in = QLineEdit()

        name_l = QLabel('&Event name:')
        name_l.setBuddy(self.name_in)

        desc_l = QLabel('&Description:')
        desc_l.setBuddy(self.desc_in)

        layout = QVBoxLayout()
        layout.addWidget(name_l)
        layout.addWidget(self.name_in)
        layout.addWidget(desc_l)
        layout.addWidget(self.desc_in)
        self.setLayout(layout)

    def button_click(self):
        self.dia.switch_current_view(TrackingGroupBox(self.dia, self.name_in.text(), self.desc_in.text()))


class TrackingGroupBox(EphemerisGroupBox):
    def __init__(self, dia, summary, description):
        super().__init__(dia, 'Stop Tracking')
        self.summary = summary
        self.desc = description

        self.start = service_models.EventTime()
        self.elapsed = 0
        self.elapsed_label = self._make_counter_label()

        elapsed_layout = QVBoxLayout()
        elapsed_layout.addWidget(self.elapsed_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_elapsed)
        self.timer.start(1000)

        layout = QVBoxLayout()
        layout.addLayout(elapsed_layout)
        self.setLayout(layout)
        self.setStyleSheet('border:none')

    def _make_counter_label(self):
        label = QLabel(self._get_string_elapsed())
        label.setFont(QFont('Arial', 12))
        label.setAlignment(Qt.AlignCenter)
        return label

    def _update_elapsed(self):
        self.elapsed += 1
        self.elapsed_label.setText(self._get_string_elapsed())

    def _get_string_elapsed(self):
        a = datetime.timedelta(seconds=self.elapsed)
        return str(a)

    def button_click(self):
        self.timer.stop()
        end = service_models.EventTime()
        event = service_models.Event(summary=self.summary, description=self.desc,
                                     start=self.start, end=end)
        print(event)
        event_result = self.dia.google_service.insert_event(event)
        print('Event created: %s' % (event_result.get('htmlLink')))
        self.dia.switch_current_view(InputGroupBox(self.dia))
