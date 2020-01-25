from PyQt5.QtWidgets import QTabWidget


class FileTabs(QTabWidget):

    def __init__(self):

        super(FileTabs, self).__init__()
        self.setStyleSheet("""
            font-size: 12px;
        """)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self.change_tab)

    def remove_tab(self, tab_idx):

        super(FileTabs, self).removeTab(tab_idx)

    def change_tab(self, tab_id):

        current_tab = self.widget(tab_id)
        window = self.nativeParentWidget()
        if current_tab:
            window.update_top_window_title(current_tab.label)
        else:
            window.update_top_window_title(None)
