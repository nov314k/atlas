"""Graphical interface to the Atlas Doer."""

import os
import datetime
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QDesktopWidget, QWidget, QVBoxLayout,
                             QTabWidget, QFileDialog, QMessageBox, QMainWindow)
from pkg_resources import resource_filename
from src.interface.prepare_day_dialog import PrepareDayDialog
from src.interface.log_progress_dialog import LogProgressDialog
from src.interface.add_adhoc_task_dialog import AddAdhocTaskDialog
from src.interface.editor_pane import EditorPane
from src.interface.menu_bar import MenuBar
from src.interface.file_tabs import FileTabs


class TopLevelWindow(QMainWindow):
    """Top level window. """

    # open_file = pyqtSignal(str)
    # previous_folder = None

    def __init__(self, config, doer, parent=None):
        """TopLevelWindow initialization."""

        super().__init__(parent)

        self.doer = doer
        self.cfg = config.cfg
        self.cfg_space = config.cfg_space
        self.cfg_newline = config.cfg_newline
        self.cfg_tab_order = config.cfg_tab_order
        self.cfg_portfolio_files = config.cfg_portfolio_files
        self.cfg_active_task_prefixes = config.cfg_active_task_prefixes

        screen_width, screen_height = self.screen_size()
        self.setMinimumSize(screen_width // 2, screen_height // 2)
        # TODO Consider adding 'resources' and 'images/' to .ini
        self.setWindowIcon(QIcon(
            resource_filename('resources', 'images/' + self.cfg['atlas_icon'])))
        self.update_top_window_title()

        self.widget = QWidget()
        self.widget.setLayout(QVBoxLayout())

        self.menu_bar = MenuBar(self.widget)
        self.setup_menu_bar()

        self.tabs = FileTabs()
        self.tabs.setMovable(True)
        self.read_only_tabs = False
        self.setCentralWidget(self.tabs)
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)

    def setup_menu_bar(self):
        """Set up drop-down menu bar."""

        menu_bar = self.menuBar()

        # Portfolio menu
        portfolio_menu = menu_bar.addMenu("Portfolio")
        portfolio_menu.addAction(QAction("New portfolio", self))
        portfolio_menu.addAction(QAction("Open portfolio", self))
        portfolio_menu.addAction(QAction("Save portfolio", self))
        portfolio_menu.addAction(QAction("Save portfolio as", self))

        quit = QAction("Quit", self)
        quit.setShortcut("Ctrl+Q")
        portfolio_menu.addAction(quit)
        quit.triggered.connect(self.portfolio_quit)

        # File menu
        file_menu = menu_bar.addMenu("File")

        new_file = QAction("New file", self)
        new_file.setShortcut("Ctrl+N")
        file_menu.addAction(new_file)
        new_file.triggered.connect(self.file_new)

        open_file = QAction("Open file", self)
        open_file.setShortcut("Ctrl+O")
        file_menu.addAction(open_file)
        open_file.triggered.connect(self.file_open)

        save_file = QAction("Save file", self)
        save_file.setShortcut("Ctrl+S")
        file_menu.addAction(save_file)
        save_file.triggered.connect(self.file_save)

        save_file_as = QAction("Save file &as", self)
        save_file_as.setShortcut("Ctrl+Shift+A")
        file_menu.addAction(save_file_as)
        save_file_as.triggered.connect(self.file_save_as)

        save_file_all = QAction("Save all files", self)
        save_file_all.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(save_file_all)
        save_file_all.triggered.connect(self.file_save_all)

        close_file = QAction("Close file", self)
        close_file.setShortcut("Ctrl+W")
        file_menu.addAction(close_file)
        close_file.triggered.connect(self.file_close)

        # Move menu
        move_menu = menu_bar.addMenu("Move")

        goto_tab_left = QAction("Go to tab left", self)
        goto_tab_left.setShortcut("Ctrl+PgUp")
        move_menu.addAction(goto_tab_left)
        goto_tab_left.triggered.connect(self.goto_tab_left)

        goto_tab_right = QAction("Go to tab right", self)
        goto_tab_right.setShortcut("Ctrl+PgDown")
        move_menu.addAction(goto_tab_right)
        goto_tab_right.triggered.connect(self.goto_tab_right)

        move_line_up = QAction("Move line up", self)
        move_line_up.setShortcut("Alt+Up")
        move_menu.addAction(move_line_up)
        move_line_up.triggered.connect(self.move_line_up)

        move_line_down = QAction("Move line down", self)
        move_line_down.setShortcut("Alt+Down")
        move_menu.addAction(move_line_down)
        move_line_down.triggered.connect(self.move_line_down)

        # Task menu
        task_menu = menu_bar.addMenu("Task")

        mark_task_done = QAction("Mark task done", self)
        mark_task_done.setShortcut("Alt+D")
        task_menu.addAction(mark_task_done)
        mark_task_done.triggered.connect(self.mark_task_done)

        mark_task_for_rescheduling = QAction("Mark task for rescheduling",
                                             self)
        mark_task_for_rescheduling.setShortcut("Alt+R")
        task_menu.addAction(mark_task_for_rescheduling)
        mark_task_for_rescheduling.triggered.connect(
            self.mark_task_for_rescheduling)

        reschedule_periodic_task = QAction("Reschedule periodic task", self)
        reschedule_periodic_task.setShortcut("Shift+Alt+R")
        task_menu.addAction(reschedule_periodic_task)
        reschedule_periodic_task.triggered.connect(
            self.reschedule_periodic_task)

        toggle_tt = QAction("Toggle TT", self)
        toggle_tt.setShortcut("Alt+G")
        task_menu.addAction(toggle_tt)
        toggle_tt.triggered.connect(self.toggle_tt)

        # Lists menu
        lists_menu = menu_bar.addMenu("Lists")

        generate_ttl = QAction("Generate TTL", self)
        generate_ttl.setShortcut("Alt+N")
        lists_menu.addAction(generate_ttl)
        generate_ttl.triggered.connect(self.generate_ttl)

        generate_ttls = QAction("Generate TTLs", self)
        generate_ttls.setShortcut("Shift+Alt+N")
        lists_menu.addAction(generate_ttls)
        generate_ttls.triggered.connect(self.generate_ttls)

        extract_auxiliaries = QAction("Extract auxiliaries", self)
        extract_auxiliaries.setShortcut("Alt+A")
        lists_menu.addAction(extract_auxiliaries)
        extract_auxiliaries.triggered.connect(self.extract_auxiliaries)

        prepare_day_plan = QAction("Prepare day plan", self)
        prepare_day_plan.setShortcut("Alt+P")
        lists_menu.addAction(prepare_day_plan)
        prepare_day_plan.triggered.connect(self.prepare_day_plan)

        # Other menu
        other_menu = menu_bar.addMenu("Other")

        extract_shlist = QAction("Extract shlist", self)
        other_menu.addAction(extract_shlist)
        extract_shlist.triggered.connect(self.extract_shlist)

    @property
    def current_tab(self):
        """Docstring."""

        return self.tabs.currentWidget()

    @property
    def modified(self):
        """Docstring."""

        for widget in self.widgets:
            if widget.isModified():
                return True
        return False

    @property
    def tab_count(self):
        """Docstring."""

        return self.tabs.count()

    @property
    def widgets(self):
        """Docstring."""

        return [self.tabs.widget(i) for i in range(self.tab_count)]

    # Utilities

    def add_tab(self, path, text):
        """Docstring."""

        new_tab = EditorPane(path, text, self.cfg_newline)
        new_tab_index = self.tabs.addTab(new_tab, new_tab.label)

        # @new_tab.modificationChanged.connect
        # def on_modified():
        #     """Docstring."""
        #
        #     modified_tab_index = self.tabs.currentIndex()
        #     self.tabs.setTabText(modified_tab_index, new_tab.label)
        #     self.update_top_window_title(new_tab.label)

        # @new_tab.open_file.connect
        # def on_open_file(file):
        #    """Docstring."""
        #
        #     # Bubble the signal up
        #     self.open_file.emit(file)

        self.tabs.setCurrentIndex(new_tab_index)
        new_tab.setFocus()
        return new_tab

    def get_open_file_path(self):
        """Get the path of the file to load (dialog)."""

        # TODO Consider moving "Open file" to .ini configuration
        path, _ = QFileDialog.getOpenFileName(
            self.widget,
            "Open file",
            self.cfg['portfolio_base_dir'],
            self.cfg['atlas_file_extension_for_saving'])
        return path

    def get_save_file_path(self):
        """Get the path of the file to save (dialog)."""

        # TODO Consider moving "Save file" to .ini configuration
        path, _ = QFileDialog.getSaveFileName(
            self.widget,
            "Save file",
            self.cfg['portfolio_base_dir'],
            self.cfg['atlas_file_extension_for_saving'])
        return path

    def update_top_window_title(self, filename=None):
        """Docstring."""

        title = self.cfg['top_window_title']
        if filename:
            title += " - " + filename
        self.setWindowTitle(title)

    @staticmethod
    def read_file(file_path, single_string=False):
        with open(file_path, 'r') as file_path_:
            if single_string:
                lines = file_path_.read()
            else:
                lines = file_path_.readlines()
        return lines

    @staticmethod
    def screen_size():
        """Docstring."""

        screen = QDesktopWidget().screenGeometry()
        return screen.width(), screen.height()

    @staticmethod
    def write_file(self, file_path, contents):
        with open(file_path, 'w', encoding=self.cfg['encoding']) as file_path_:
            file_path_.write(contents)

    # Portfolio menu commands

    def portfolio_open(self):
        """Open portfolio files, and today's DTF if available."""

        for file_path in self.cfg_tab_order:
            self.file_open(file_path)
        today = datetime.datetime.now()
        file_name = f"{today.year}{today.month:02}{today.day:02}"
        file_name_n_ext = file_name + self.cfg['atlas_files_extension']
        if os.path.isfile(self.cfg['portfolio_base_dir'] + file_name_n_ext):
            self.file_open(self.cfg['portfolio_base_dir'] + file_name_n_ext)

    def portfolio_reload_currently_open_tabs(self):
        """Reload all currently open tabs."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        for tab in self.widgets:
            contents = self.read_file(tab.path, single_string=True)
            tab.setText(contents)
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def portfolio_quit(self):
        """Confirm if user wants to save changes before quitting."""

        for tab in self.widgets:
            tab_index = self.tabs.indexOf(tab)
            self.tabs.setCurrentIndex(tab_index)
            self.file_close()
        sys.exit(0)

    # File menu commands

    def file_new(self):
        """Add a new tab."""

        self.add_tab(None, "")
    
    def file_open(self, file_path=None):
        """Open a file from disk in a new tab.

        If `path` is not specified, it displays a dialog for the user to choose
        the path to open. Does not open an already opened file.

        Parameters
        ----------
        file_path : str
            Path to save tab contents to.

        """

        # Get the path from the user if it's not defined
        if file_path is None:
            file_path = self.get_open_file_path()
        # Was the dialog canceled?
        if file_path is None:
            return
        # Do not open a life area if it is already open
        for widget in self.widgets:
            if os.path.samefile(file_path, widget.path):
                msg = "'{}' is already open."
                self.show_message(msg.format(os.path.basename(file_path)))
                self.focus_tab(widget)
                return
        contents = self.read_file(file_path, single_string=True)
        self.add_tab(file_path, contents)

    def file_save(self, file_path=None, tab=None):
        """Save file in selected tab to disk.

        If `tab` is not specified, it assumes that we want to save the file
        contained in the currently selected tab. If it is a newly added tab,
        not saved before (and hence a file does not exist on disk), a dialog
        is displayed to choose the save path. Even though the path of a tab
        is contained in the tab, due to different usage scenarios for this
        function, it is best to keep these two parameters separate.

        Parameters
        ----------
        file_path : str
            Path to save tab contents to.
        tab : EditorPane
            Tab containing the contents to save to `path`.

        """

        # TODO Check the logic throughout
        if not tab:
            tab = self.current_tab
        if not file_path:
            # If it is a newly added tab, not saved before
            if tab.path is None:
                tab.path = self.get_save_file_path()
            # Was the dialog canceled?
            if tab.path is None:
                return
            file_path = tab.path
        self.write_file(self, file_path, tab.text())
        tab.setModified(False)

    def file_save_as(self):
        """Save file in selected tab to a different file path."""

        file_path = self.get_save_file_path()
        if file_path is None:
            return
        for widget in self.widgets:
            if widget.path == file_path:
                # if os.path.samefile(path, widget.path):
                msg = "'{}' is open. Close if before overwriting."
                self.show_message(msg.format(os.path.basename(file_path)))
                self.focus_tab(widget)
                return
        self.file_save(file_path=file_path)

    def file_save_all(self):
        """Save all open tabs."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        for tab in self.widgets:
            tab_idx = self.tabs.indexOf(tab)
            self.tabs.setCurrentIndex(tab_idx)
            self.file_save(file_path=tab.path, tab=tab)
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def file_close(self):
        """Close the current file (remove the current tab)."""

        selected_tab = self.current_tab
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        if selected_tab.path is None:
            self.file_save_as()
        if selected_tab.path is None:
            return
        if selected_tab.isModified():
            answer = self.show_yes_no_question(
                "Do you want to save changes to the file before closing?",
                "File:    " + selected_tab.path)
            if answer == QMessageBox.Yes:
                self.file_save()
            if answer == QMessageBox.Cancel:
                return
        self.tabs.removeTab(selected_tab_idx)

    # Move menu commands

    def goto_tab_left(self):
        """Change focus to one tab left. Allows for wrapping around."""

        selected_tab = self.current_tab
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        if selected_tab_idx - 1 < 0:
            tab_to_left_idx = self.tab_count - 1
        else:
            tab_to_left_idx = selected_tab_idx - 1
        self.tabs.setCurrentIndex(tab_to_left_idx)

    def goto_tab_right(self):
        """Change focus to one tab right. Allows for wrapping around."""

        selected_tab = self.current_tab
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        if selected_tab_idx + 1 > self.tab_count-1:
            tab_to_right_idx = 0
        else:
            tab_to_right_idx = selected_tab_idx + 1
        self.tabs.setCurrentIndex(tab_to_right_idx)

    def move_line_up(self):
        """Swap the current (selected) row with the one above it."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        first_visible_line = selected_tab.firstVisibleLine()
        lines = selected_tab.text().split(self.cfg_newline)
        if selected_row > 0:
            for idx, _ in enumerate(lines):
                if idx == selected_row - 1:
                    temp_line = lines[idx]
                    lines[idx] = lines[idx + 1]
                    lines[idx + 1] = temp_line
            contents = "".join(line + self.cfg_newline for line in lines)
            contents = contents[:-1]
            selected_tab.SendScintilla(selected_tab.SCI_SETTEXT,
                                       contents.encode(self.cfg['encoding']))
            selected_tab.setFirstVisibleLine(first_visible_line)
            selected_tab.setCursorPosition(selected_row - 1, 0)

    def move_line_down(self):
        """Swap the current (selected) row with the one below it."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        first_visible_line = selected_tab.firstVisibleLine()
        lines = selected_tab.text().split(self.cfg_newline)
        if selected_row < len(lines) - 1:
            for idx in range(len(lines) - 1, -1, -1):
                if idx == selected_row + 1:
                    temp_line = lines[idx]
                    lines[idx] = lines[idx - 1]
                    lines[idx - 1] = temp_line
            contents = "".join(line + self.cfg_newline for line in lines)
            contents = contents.rstrip(self.cfg_newline)
            selected_tab.SendScintilla(selected_tab.SCI_SETTEXT,
                                       contents.encode(self.cfg['encoding']))
            selected_tab.setFirstVisibleLine(first_visible_line)
            selected_tab.setCursorPosition(selected_row + 1, 0)

    # Task menu commands

    def mark_task_done(self):
        """Interface to doer.mark_task_done()."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        self.file_save_all()
        # TODO Consider generalizing as it follows the same pattern
        self.doer.mark_ordinary_task_done(selected_tab.path, selected_row)
        self.portfolio_reload_currently_open_tabs()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def mark_task_for_rescheduling(self):
        """Interface to doer.mark_task_for_rescheduling()."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        self.file_save_all()
        # TODO Consider generalizing as it follows the same pattern
        self.doer.mark_task_for_rescheduling(selected_tab.path, selected_row)
        self.portfolio_reload_currently_open_tabs()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def reschedule_periodic_task(self):
        """Interface to doer.reschedule_periodic_task."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        self.file_save_all()
        # TODO Consider generalizing as it follows the same pattern
        self.doer.reschedule_periodic_task(selected_tab.path, selected_row)
        self.portfolio_reload_currently_open_tabs()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def toggle_tt(self):
        """Interface to doer.toggle_tt()."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        self.file_save_all()
        # TODO Consider generalizing as it follows the same pattern
        self.doer.toggle_tt(selected_tab.path, selected_row)
        self.portfolio_reload_currently_open_tabs()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    # Lists menu commands

    def generate_ttl(self):
        """Interface to doer.generate_ttl()."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        self.file_save_all()
        # TODO Consider generalizing as it follows the same pattern
        self.doer.generate_ttl(selected_tab.path)
        self.portfolio_reload_currently_open_tabs()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def generate_ttls(self):
        """Interface to doer.generate_ttls()."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        self.file_save_all()
        # TODO Consider generalizing as it follows the same pattern
        self.doer.generate_ttls()
        self.portfolio_reload_currently_open_tabs()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def extract_auxiliaries(self):
        """Interface to self.doer.extract_auxiliaries()."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        self.file_save_all()
        # TODO Consider generalizing as it follows the same pattern
        self.doer.extract_auxiliaries()
        self.portfolio_reload_currently_open_tabs()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def prepare_day_plan(self):
        """Interface to doer.prepare_day_plan()."""

        self.file_save_all()
        today = datetime.datetime.now()
        day, month, year = self.show_prepare_day_plan_dialog(str(today.day),
                                                             str(today.month),
                                                             str(today.year))
        file_name = f"{year}{month:02}{day:02}"
        file_name_n_ext = file_name + self.cfg['atlas_files_extension']
        dtf_open = False
        for idx in range(self.tab_count):
            if (self.tabs.widget(idx).path
                    == self.cfg['portfolio_base_dir'] + file_name_n_ext):
                dtf_open = True
        if dtf_open:
            self.tabs.removeTab(idx)
        self.doer.prepare_day_plan(day, month, year)
        self.file_open(self.cfg['portfolio_base_dir'] + file_name_n_ext)

    # Other menu commands

    def extract_shlist(self):
        """Interface to doer.extract_shlist()."""

        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        self.file_save_all()
        # TODO Consider generalizing as it follows the same pattern
        self.doer.extract_shlist()
        self.portfolio_reload_currently_open_tabs()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    # Show messages and dialogs

    def show_message(self, message, information=None, icon=None):
        """Show message box."""

        message_box = QMessageBox(self)
        message_box.setText(message)
        message_box.setWindowTitle(self.cfg['top_window_title'])
        if information:
            message_box.setInformativeText(information)
        if icon and hasattr(message_box, icon):
            message_box.setIcon(getattr(message_box, icon))
        else:
            message_box.setIcon(message_box.Warning)
        message_box.exec()

    def show_confirmation(self, message, information=None, icon=None):
        """Show confirmation box, with OK and Cancel buttons."""

        message_box = QMessageBox(self)
        message_box.setText(message)
        message_box.setWindowTitle(self.cfg['top_window_title'])
        if information:
            message_box.setInformativeText(information)
        if icon and hasattr(message_box, icon):
            message_box.setIcon(getattr(message_box, icon))
        else:
            message_box.setIcon(message_box.Warning)
        message_box.setStandardButtons(message_box.Cancel | message_box.Ok)
        message_box.setDefaultButton(message_box.Cancel)
        return message_box.exec()

    def show_yes_no_question(self, message, information=None):
        """Ask the user a yes/no/cancel question."""

        message_box = QMessageBox(self)
        message_box.setWindowTitle(self.cfg['top_window_title'])
        message_box.setText(message)
        if information:
            message_box.setInformativeText(information)
        message_box.setIcon(message_box.Question)
        message_box.setStandardButtons(
            message_box.Yes | message_box.No | message_box.Cancel)
        message_box.setDefaultButton(message_box.Yes)
        return message_box.exec()

    def show_prepare_day_plan_dialog(self, proposed_day, proposed_month,
                                     proposed_year):
        """Show prepare day dialog, with proposed target day/month/year."""

        prepare_day_dialog = PrepareDayDialog(self)
        prepare_day_dialog.setup(proposed_day, proposed_month, proposed_year)
        if prepare_day_dialog.exec():
            return (prepare_day_dialog.target_day(),
                    prepare_day_dialog.target_month(),
                    prepare_day_dialog.target_year())
        return None

    def _show_log_progress_dialog(self):
        """Experimental. Do not use."""

        log_entry = LogProgressDialog(self)
        log_entry.setup()
        if log_entry.exec():
            return log_entry.log_entry()
        return None

    def _show_add_adhoc_task_dialog(self):
        """Experimental. Do not use."""

        adhoc_task = AddAdhocTaskDialog(self)
        adhoc_task.setup()
        if adhoc_task.exec():
            return adhoc_task.adhoc_task()
        return None
