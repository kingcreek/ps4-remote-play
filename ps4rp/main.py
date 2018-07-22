#!/usr/bin/env python
#
# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0
"""
Entry point of the ps4-remote-play program.
"""

import sys

from ps4rp import __version__
from ps4rp import registry

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
        QtWidgets.QMessageBox.information(
            self, 'Hello, World!',
            'This is ps4-remote-play v%s' % __version__.__version__
        )

    def _on_connect_click(self):
        QtWidgets.QMessageBox.warning(
            self, 'Operation unsupported',
            'Connecting to a console is not yet supported.'
        )


def main():
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
