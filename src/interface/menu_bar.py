"""Docstring."""

from PyQt5.QtWidgets import QDesktopWidget, QMenuBar


def screen_size():
    """Docstring."""

    screen = QDesktopWidget().screenGeometry()
    return screen.width(), screen.height()


class MenuBar(QMenuBar):
    """Docstring."""

    def __init__(self, parent):
        """Docstring."""

        # Uncommenting this results in a Gtk-Message:
        # GtkDialog mapped without a transient parent. This is discouraged.
        # super().__init__(parent)
        pass

    def setup(self):
        """Docstring."""

        self.addMenu("&Portfolio")
        self.addMenu("la&File")
        self.addMenu("&Task")
        self.addMenu("&Log")
