#!/usr/bin/env python
#
# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0
"""
Entry point of the ps4-remote-play program.
"""

import sys

from ps4rp import discovery
from ps4rp import registry
from ps4rp import registration

from PySide2 import QtWidgets


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PS4 Remote Play')

        self._register_button = QtWidgets.QPushButton('Register new PS4')
        self._register_button.clicked.connect(self._on_register_click)

        self._connect_button = QtWidgets.QPushButton('Connect')
        self._connect_button.clicked.connect(self._on_connect_click)
        self._update_connect_button_state()

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addWidget(self._register_button)
        self._layout.addWidget(self._connect_button)
        self.setLayout(self._layout)

    def _update_connect_button_state(self):
        """Toggles the Connect button between enabled/disabled state based on
        whether a PS4 has already been registered."""
        self._connect_button.setEnabled(len(registry.get_known_consoles()) > 0)

    def _on_register_click(self):
        psn_id, _ = QtWidgets.QInputDialog.getText(
            self, 'Registration', 'Enter your PSN id:'
        )
        pin, _ = QtWidgets.QInputDialog.getInt(
            self, 'Registration', 'Enter the registration PIN:'
        )
        info = registration.find_and_pair_console(psn_id, pin)
        if info is None:
            QtWidgets.QMessageBox.warning(
                self, 'Registration failed',
                'Could not register with the console.'
            )
        else:
            QtWidgets.QMessageBox.information(
                self, 'Registration successful',
                'Registered with PS4 %r.' % info.name
            )
            registry.register_console(info)
            self._update_connect_button_state()

    def _on_connect_click(self):
        # TODO: Allow selection in the UI.
        console = registry.get_known_consoles()[0]
        ip, status = discovery.find_console(console)
        if status is None:
            QtWidgets.QMessageBox.warning(
                self, 'Could not connect',
                'Console could not be found in time.'
            )
            return
        if status == discovery.ConsoleStatus.ready:
            QtWidgets.QMessageBox.information(
                self, 'Console ready!', 'IP: %s' % ip
            )
        else:
            discovery.wake_up(ip, console)
            QtWidgets.QMessageBox.information(
                self, 'Console waking up!',
                'Sent a wakeup command, try again soon.'
            )


def main():
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
