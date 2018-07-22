#!/usr/bin/env python
#
# Copyright (c) 2018, Pierre Bourdon <delroth@gmail.com>
# SPDX-License-Identifier: Apache-2.0
"""
Entry point of the ps4-remote-play program.
"""

import sys

from ps4rp import __version__

from PySide2 import QtWidgets


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PS4 Remote Play')

        self.button = QtWidgets.QPushButton('Click me!')
        self.button.clicked.connect(self.on_button_click)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def on_button_click(self):
        QtWidgets.QMessageBox.information(
            self, 'Hello, World!',
            'This is ps4-remote-play v%s' % __version__.__version__)


def main():
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
