"""Docstring."""

import os
import datetime
import re
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAction, QDesktopWidget, QWidget, QVBoxLayout,
                             QTabWidget, QFileDialog, QMessageBox, QMainWindow,
                             QShortcut)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QIcon
from pkg_resources import resource_filename
from src.interface.prepare_day_dialog import PrepareDayDialog
from src.interface.log_progress_dialog import LogProgressDialog
from src.interface.add_adhoc_task_dialog import AddAdhocTaskDialog
from src.interface.editor_pane import EditorPane
from src.interface.menu_bar import MenuBar
from src.interface.file_tabs import FileTabs


class TopLevelWindow(QMainWindow):
    """Docstring."""

    # open_file = pyqtSignal(str)
    # previous_folder = None

    def __init__(self, config, doer, parent=None):
        """TopLevelWindow init."""

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
        """Set up horizontal drop-down menu bar."""

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
        file_menu.addAction(save_file_as)
        save_file_as.triggered.connect(self.file_save_as)

        save_file_all = QAction("Save all files", self)
        open_file.setShortcut("Ctrl+Shift+S")
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

    def update_top_window_title(self, filename=None):
        """Docstring."""

        title = self.cfg['top_window_title']
        if filename:
            title += " - " + filename
        self.setWindowTitle(title)

    # Portfolio menu commands

    def portfolio_open(self):
        """Function docstring."""

        for file_path in self.cfg_tab_order:
            self.file_open(file_path)
        today = datetime.datetime.now()
        file_name = f"{today.year}{today.month:02}{today.day:02}"
        file_name_n_ext = file_name + self.cfg['atlas_files_extension']
        if os.path.isfile(self.cfg['portfolio_base_dir'] + file_name_n_ext):
            self.file_open(self.cfg['portfolio_base_dir'] + file_name_n_ext)

    def portfolio_reload_currently_open_tabs(self):
        for tab in self.widgets:
            contents = self.read_file(tab.path, single_string=True)
            tab.setText(contents)

    def portfolio_quit(self):
        """Quit Atlas.

        Confirm if and how the user wants to save changes. Saves session
        settings before exiting.

        """

        for tab in self.widgets:
            current_tab_index = self.tabs.indexOf(tab)
            self.tabs.setCurrentIndex(current_tab_index)
            user_chose_yes_or_no = self.file_close()
            if not user_chose_yes_or_no:
                return
        # self.save_session_settings()
        sys.exit(0)

    # File menu commands

    def file_new(self):
        """Add a new tab."""

        self.add_tab(None, "", self.c_newline)
    
    def file_open(self, path=None):
        """Open a file from disk in a new tab.

        If `path` is not specified, it displays a dialog for the user to choose
        the path to open. Does not open an already opened file.

        Parameters
        ----------
        path : str
            Path to save tab contents to.

        """

        # Get the path from the user if it's not defined
        if not path:
            path = self.get_open_file_path()
        # Was the dialog canceled?
        if not path:
            return
        # Do not open a life area if it is already open
        for widget in self.widgets:
            if os.path.samefile(path, widget.path):
                msg = "'{}' is already open."
                self.show_message(msg.format(os.path.basename(path)))
                self.focus_tab(widget)
                return
        file_content = ''
        with open(path, encoding=self.cfg['encoding']) as faux:
            lines = faux.readlines()
            for line in lines:
                file_content += line
        self.add_tab(path, file_content)

    def file_save(self, file_path=None, tab=None):
        """Save file contained in a tab to disk.

        If `tab` is not specified, it assumes that we want to save the file
        contained in the currently active tab. If it is a newly added tab
        not save before (and hence a file does not exist on disk), a dialog is
        displayed to choose the save path. Even though the path of a tab is
        contained in the tab, due to different usage scenarios for this
        function, it is best to keep these two parameters separate.

        Parameters
        ----------
        file_path : str
            Path to save tab contents to.
        tab : EditorPane
            Tab containing the contents to save to `path`.

        """

        if tab is None:
            tab = self.current_tab
        if file_path is None:
            # If it is a newly added tab, not saved before
            if tab.path is None:
                tab.path = self.get_save_file_path()
            # Was the dialog canceled?
            if tab.path is None:
                return
            file_path = tab.path
        with open(file_path, 'w', encoding=self.cfg['encoding']) as file_path_:
            file_path_.writelines(tab.text())
        tab.setModified(False)

    def file_save_as(self):
        """Save file in active tab to a different path.

        After getting the new path, it checks if the new path is already open.
        If it is not open, calls `self.save_file()` with the new file name
        provided.

        """

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
        """Docstring."""

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
        """Close the current file (remove the current tab).

        Returning `False` indicates that the user, when answering to the
        question, chose 'Cancel'. Returning `True` indicates that the user
        answered with either 'Yes' or 'No'. This is primarily used by `quit()`
        to indicate whether to abort the quitting process if a user choses
        'Cancel'. If a user choses 'Cancel', they decide that they want to deal
        with the changes in the file in the normal program operation mode
        ('manually').

        """

        current_tab = self.current_tab
        current_tab_idx = self.tabs.indexOf(current_tab)
        if current_tab.isModified():
            answer = self.show_yes_no_question(
                "Do you want to save changes to the file before closing?",
                "File:    " + current_tab.path)
            if answer == QMessageBox.Yes:
                self.save_file()
            if answer == QMessageBox.Cancel:
                return False
        self.tabs.removeTab(current_tab_idx)
        return True

    # Move menu commands

    def goto_tab_left(self):
        """Change focus to one tab left. Allows for wrapping around."""

        tab = self.current_tab
        index = self.tabs.indexOf(tab)
        if index-1 < 0:
            tab_left_idx = self.tab_count - 1
        else:
            tab_left_idx = index - 1
        self.tabs.setCurrentIndex(tab_left_idx)

    def goto_tab_right(self):
        """Change focus to one tab right. Allows for wrapping around."""

        tab = self.current_tab
        index = self.tabs.indexOf(tab)
        if index+1 > self.tab_count-1:
            tab_right_idx = 0
        else:
            tab_right_idx = index + 1
        self.tabs.setCurrentIndex(tab_right_idx)

    def move_line_up(self):
        """Move current line of text one row up."""

        tab = self.current_tab
        first_visible_line = tab.firstVisibleLine()
        tasks = tab.text().split('\n')
        row = tab.getCursorPosition()[0]
        if row > 0:
            for i, _ in enumerate(tasks):
                if i == row - 1:
                    temp = tasks[i]
                    tasks[i] = tasks[i + 1]
                    tasks[i + 1] = temp
            contents = ""
            for task in tasks:
                contents += task + self.c_newline
            contents = contents.rstrip(self.c_newline)
            tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.cfg['encoding']))
            tab.setFirstVisibleLine(first_visible_line)
            tab.setCursorPosition(row - 1, 0)

    def move_line_down(self):
        """Move current line of text one row down."""

        tab = self.current_tab
        first_visible_line = tab.firstVisibleLine()
        tasks = tab.text().split(self.c_newline)
        row = tab.getCursorPosition()[0]
        if row < len(tasks) - 1:
            for i in range(len(tasks) - 1, -1, -1):
                if i == row + 1:
                    temp = tasks[i]
                    tasks[i] = tasks[i - 1]
                    tasks[i - 1] = temp
            contents = ""
            for task in tasks:
                contents += task + self.c_newline
            contents = contents.rstrip(self.c_newline)
            tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.cfg['encoding']))
            tab.setFirstVisibleLine(first_visible_line)
            tab.setCursorPosition(row + 1, 0)

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
        """Docstring."""

        message_box = QMessageBox(self)
        message_box.setText(message)
        message_box.setWindowTitle("Atlas")
        if information:
            message_box.setInformativeText(information)
        if icon and hasattr(message_box, icon):
            message_box.setIcon(getattr(message_box, icon))
        else:
            message_box.setIcon(message_box.Warning)
        message_box.exec()

    def show_confirmation(self, message, information=None, icon=None):
        """Docstring."""

        message_box = QMessageBox(self)
        message_box.setText(message)
        message_box.setWindowTitle("Atlas")
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
        """Ask the user a yes/no/cancel question.

        Answering 'Yes' allows for performing a certain action; answering 'No'
        allows for not performing the same action. Answering with 'Cancel'
        aborts the question and goes back to normal program operation mode so
        that the user can make their decision in that mode before proceeding.

        """

        message_box = QMessageBox(self)
        message_box.setWindowTitle("Atlas")
        message_box.setText(message)
        if information:
            message_box.setInformativeText(information)
        message_box.setIcon(message_box.Question)
        message_box.setStandardButtons(
            message_box.Yes | message_box.No | message_box.Cancel)
        message_box.setDefaultButton(message_box.Yes)
        return message_box.exec()

    def show_prepare_day_plan_dialog(self, target_day, target_month, target_year):
        """Docstring."""

        # ~ finder = FindReplaceDialog(self)
        finder = PrepareDayDialog(self)
        finder.setup(target_day, target_month, target_year)
        if finder.exec():
            return (finder.target_day(), finder.target_month(),
                    finder.target_year())
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
