"""Docstring."""

from PyQt5.QtWidgets import QTabWidget


class FileTabs(QTabWidget):
    """Docstring."""

    def __init__(self):
        """Docstring."""

        super(FileTabs, self).__init__()
        self.setStyleSheet("""
            font-size: 12px;
        """)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self.change_tab)

    def remove_tab(self, tab_idx):
        """Remove tab with index `tab_idx`."""

        super(FileTabs, self).removeTab(tab_idx)

    def change_tab(self, tab_id):
        """Docstring."""

        current_tab = self.widget(tab_id)
        window = self.nativeParentWidget()
        if current_tab:
            window.update_title(current_tab.label)
        else:
            window.update_title(None)
