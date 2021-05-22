import abc
import datetime

import service_models
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGroupBox, QLineEdit, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from util import get_QPixmap


class EphemerisGroupBox(QGroupBox):
    def __init__(self, dia, button_label):
        super().__init__()
        self.dia = dia
        self.bottom_btn = QPushButton(button_label)
        self.bottom_btn.pressed.connect(self.button_click)

    @abc.abstractmethod
    def button_click(self):
        pass


class LoginGroupBox(EphemerisGroupBox):
    def __init__(self, dia):
        super().__init__(dia, ' Login with Google')
        layout = QVBoxLayout()
        layout.addWidget(self.bottom_btn)
        self.bottom_btn.setIcon(QIcon(get_QPixmap(self.dia.app_ctx, 'google.png')))
        self.setLayout(layout)

    def button_click(self):
        self.dia.google_service.prepare_credentials()
        self.dia.google_service.build_resource()
        self.dia.switch_current_view(InputGroupBox(self.dia))


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
        layout.addWidget(self.bottom_btn)
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
        self.e_t_label = QLabel(self._get_string_elapsed())
        self.e_label = QLabel('&Elapsed time: ')
        self.e_label.setBuddy(self.e_t_label)

        elapsed_layout = QHBoxLayout()
        elapsed_layout.addWidget(self.e_label)
        elapsed_layout.addWidget(self.e_t_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_elapsed)
        self.timer.start(1000)

        layout = QVBoxLayout()
        layout.addLayout(elapsed_layout)
        layout.addWidget(self.bottom_btn)
        self.setLayout(layout)

    def _update_elapsed(self):
        self.elapsed += 1
        self.e_t_label.setText(self._get_string_elapsed())

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
