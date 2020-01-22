"""Docstring."""

import os
import datetime
import re
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QAction, QDesktopWidget, QWidget, QVBoxLayout,
                             QTabWidget, QFileDialog, QMessageBox, QMainWindow,
                             QShortcut)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QIcon
from pkg_resources import resource_filename
from interface.prepare_day_dialog import PrepareDayDialog
from interface.log_progress_dialog import LogProgressDialog
from interface.add_adhoc_task_dialog import AddAdhocTaskDialog
from interface.editor_pane import EditorPane
from interface.menu_bar import MenuBar
from interface.file_tabs import FileTabs


def screen_size():
    """Docstring."""

    screen = QDesktopWidget().screenGeometry()
    return screen.width(), screen.height()

def eight_digit_date(day, month, year):
    # TODO Change over to f-strings
    edd = str(year)
    if month < 10:
        edd += "0"
    edd += str(month)
    if day < 10:
        edd += "0"
    edd += str(day)
    return edd

class TopLevelWindow(QMainWindow):
    """Docstring."""

    title = "Atlas"
    icon = 'icon'
    timer = None
    open_file = pyqtSignal(str)
    previous_folder = None

    def __init__(self, config, engine, parent=None):
        """TopLevelWindow init."""

        super().__init__(parent)
        self._engine = engine
        self.cfg = config.cfg
        self.c_space = config.cfg['space'][1]
        self.c_active_task_prefixes = config.cfg['active_task_prefixes']
        if self.cfg['newline'] == 'linux':
            self.c_newline = '\n'
        else:
            self.c_newline = '\r\n'
        
        self.widget = QWidget()
        self.read_only_tabs = False
        self.menu_bar = MenuBar(self.widget)
        self.tabs = FileTabs()
        self.open_file_heading = "Open file"
        self.save_file_heading = "Save file"
        self.atlas_file_extension_for_saving = "Atlas (*.pmd.txt)"
        self.setup()

    def setup(self):
        """Docstring."""

        self.setWindowIcon(QIcon(
            resource_filename('resources', 'images/' + self.icon)))
        self.update_title()
        screen_width, screen_height = screen_size()
        self.setMinimumSize(screen_width // 2, screen_height // 2)
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        widget_layout = QVBoxLayout()
        self.widget.setLayout(widget_layout)
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)
        self.showMaximized()

    def setup_menu(self, functions):
        """Set up horizontal drop-down menu bar."""

        actions = dict()
        menu_bar = self.menuBar()

        # Portfolio
        portfolio_menu = menu_bar.addMenu("Portfolio")
        portfolio_menu.addAction(QAction("New portfolio", self))
        portfolio_menu.addAction(QAction("Open portfolio", self))
        portfolio_menu.addAction(QAction("Save portfolio", self))
        portfolio_menu.addAction(QAction("Save portfolio as", self))

        quit = QAction("Quit", self)
        quit.setShortcut("Ctrl+Q")
        portfolio_menu.addAction(quit)
        actions['quit'] = quit

        # File
        file_menu = menu_bar.addMenu("File")

        new_file = QAction("New file", self)
        new_file.setShortcut("Ctrl+N")
        file_menu.addAction(new_file)
        actions['new_file'] = new_file

        open_file = QAction("Open file", self)
        open_file.setShortcut("Ctrl+O")
        file_menu.addAction(open_file)
        actions['open_file'] = open_file

        save_file = QAction("Save file", self)
        save_file.setShortcut("Ctrl+S")
        file_menu.addAction(save_file)
        actions['save_file'] = save_file

        save_file_as = QAction("Save file as", self)
        file_menu.addAction(save_file_as)
        actions['save_file_as'] = save_file_as


        save_file_all = QAction("Save all files", self)
        file_menu.addAction(save_file_all)
        actions['save_file_all'] = save_file_all

        close_file = QAction("Close file", self)
        close_file.setShortcut("Ctrl+W")
        file_menu.addAction(close_file)
        actions['close_file'] = close_file

        # Move
        move_menu = menu_bar.addMenu("Move")

        goto_tab_left = QAction("Go to tab left", self)
        goto_tab_left.setShortcut("Ctrl+PgUp")
        move_menu.addAction(goto_tab_left)
        actions['goto_tab_left'] = goto_tab_left

        goto_tab_right = QAction("Go to tab right", self)
        goto_tab_right.setShortcut("Ctrl+PgDown")
        move_menu.addAction(goto_tab_right)
        actions['goto_tab_right'] = goto_tab_right

        move_line_up = QAction("Move line up", self)
        move_line_up.setShortcut("Alt+Up")
        move_menu.addAction(move_line_up)
        actions['move_line_up'] = move_line_up

        move_line_down = QAction("Move line down", self)
        move_line_down.setShortcut("Alt+Down")
        move_menu.addAction(move_line_down)
        actions['move_line_down'] = move_line_down

        move_daily_tasks_file = QAction("Move daily tasks file", self)
        move_daily_tasks_file.setShortcut("Alt+M")
        move_menu.addAction(move_daily_tasks_file)
        actions['_move_daily_tasks_file'] = move_daily_tasks_file

        # Task
        task_menu = menu_bar.addMenu("Task")

        mark_task_done = QAction("Mark task done", self)
        mark_task_done.setShortcut("Alt+D")
        task_menu.addAction(mark_task_done)
        actions['mark_task_done'] = mark_task_done

        mark_task_for_rescheduling = QAction("Mark task for rescheduling",
                                             self)
        mark_task_for_rescheduling.setShortcut("Alt+R")
        task_menu.addAction(mark_task_for_rescheduling)
        actions['mark_task_for_rescheduling'] = mark_task_for_rescheduling

        reschedule_periodic_task = QAction("Reschedule periodic task", self)
        reschedule_periodic_task.setShortcut("Shift+Alt+R")
        task_menu.addAction(reschedule_periodic_task)
        actions['reschedule_periodic_task'] = reschedule_periodic_task

        add_adhoc_task = QAction("Add ad hoc task", self)
        add_adhoc_task.setShortcut("Alt+I")
        task_menu.addAction(add_adhoc_task)
        actions['_add_adhoc_task'] = add_adhoc_task

        tag_current_line = QAction("Tag current line", self)
        tag_current_line.setShortcut("Alt+T")
        task_menu.addAction(tag_current_line)
        actions['_tag_current_line'] = tag_current_line

        toggle_tt = QAction("Toggle TT", self)
        toggle_tt.setShortcut("Alt+G")
        task_menu.addAction(toggle_tt)
        actions['toggle_tt'] = toggle_tt

        # Lists
        lists_menu = menu_bar.addMenu("Lists")

        generate_ttl = QAction("Generate TTL", self)
        generate_ttl.setShortcut("Alt+N")
        lists_menu.addAction(generate_ttl)
        actions['generate_ttl'] = generate_ttl

        generate_ttls = QAction("Generate TTLs", self)
        generate_ttls.setShortcut("Shift+Alt+N")
        lists_menu.addAction(generate_ttls)
        actions['generate_ttls'] = generate_ttls

        extract_auxiliaries = QAction("Extract auxiliaries", self)
        extract_auxiliaries.setShortcut("Alt+A")
        lists_menu.addAction(extract_auxiliaries)
        actions['extract_auxiliaries'] = extract_auxiliaries

        prepare_day_plan = QAction("Prepare day plan", self)
        prepare_day_plan.setShortcut("Alt+P")
        lists_menu.addAction(prepare_day_plan)
        actions['prepare_day_plan'] = prepare_day_plan

        analyse_tasks = QAction("Analyse tasks", self)
        analyse_tasks.setShortcut("Alt+Y")
        lists_menu.addAction(analyse_tasks)
        actions['_analyse_tasks'] = analyse_tasks

        schedule_tasks = QAction("Schedule tasks", self)
        schedule_tasks.setShortcut("Alt+S")
        lists_menu.addAction(schedule_tasks)
        actions['_schedule_tasks'] = schedule_tasks

        extract_earned_time = QAction("Extract earned time", self)
        extract_earned_time.setShortcut("Alt+X")
        lists_menu.addAction(extract_earned_time)
        actions['_extract_earned_time'] = extract_earned_time

        # Logs
        logs_menu = menu_bar.addMenu("Logs")

        log_progress = QAction("Log progress", self)
        log_progress.setShortcut("Alt+L")
        logs_menu.addAction(log_progress)
        actions['_log_progress'] = log_progress

        back_up = QAction("Back up portfolio", self)
        back_up.setShortcut("Alt+B")
        logs_menu.addAction(back_up)
        actions['_back_up'] = back_up

        # Other
        other_menu = menu_bar.addMenu("Other")

        sort_periodic_tasks = QAction("Sort periodic tasks", self)
        sort_periodic_tasks.setShortcut("Alt+Q")
        other_menu.addAction(sort_periodic_tasks)
        actions['_sort_periodic_tasks'] = sort_periodic_tasks

        extract_daily = QAction("Extract daily", self)
        other_menu.addAction(extract_daily)
        actions['extract_daily'] = extract_daily

        extract_booked = QAction("Extract booked", self)
        other_menu.addAction(extract_booked)
        actions['extract_booked'] = extract_booked

        extract_periodic = QAction("Extract periodic", self)
        other_menu.addAction(extract_periodic)
        actions['extract_periodic'] = extract_periodic

        extract_shlist = QAction("Extract shlist", self)
        other_menu.addAction(extract_shlist)
        actions['extract_shlist'] = extract_shlist

        # Connect actions with functions
        for action in actions:
            actions[action].triggered.connect(functions[action])

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

    # START Utility Functions

    def _add_tab(self, path, text, newline):
        """Docstring."""

        new_tab = EditorPane(path, text, newline)
        new_tab_index = self.tabs.addTab(new_tab, new_tab.label)

        @new_tab.modificationChanged.connect
        def on_modified():
            """Docstring."""

            modified_tab_index = self.tabs.currentIndex()
            self.tabs.setTabText(modified_tab_index, new_tab.label)
            self.update_title(new_tab.label)

        @new_tab.open_file.connect
        def on_open_file(file):
            """Docstring."""

            # Bubble the signal up
            self.open_file.emit(file)

        self.tabs.setCurrentIndex(new_tab_index)
        new_tab.setFocus()
        if self.read_only_tabs:
            new_tab.setReadOnly(self.read_only_tabs)
        return new_tab

    def _get_open_file_path(self, folder, extensions):
        """Get the path of the file to load (dialog)."""

        extensions = '*' + extensions
        path, _ = QFileDialog.getOpenFileName(self.widget,
                                              self.open_file_heading,
                                              folder,
                                              extensions)
        return path

    def _get_save_file_path(self, folder):
        """Get the path of the file to save (dialog)."""

        path, _ = QFileDialog.getSaveFileName(
                self.widget,
                self.open_file_heading, folder,
                self.atlas_file_extension_for_saving)
        return path

    def _read_file(self, fpath, single_string=False):
        with open(fpath, 'r') as fpath_:
            if single_string:
                lines = fpath_.read()
            else:
                lines = fpath_.readlines()
        return lines

    def _running_from_daily_tasks_file(self, tab):
        """Check if the command is issued while a daily tasks tab is active.

        :param tab widget: active tab when the command was invoked
        :type tab: widget
        :returns boolean:
        """

        file_name = os.path.basename(tab.path).split('.')[0]
        if not re.match(r'\d{8}', file_name):
            message = ("This command can only be run"
                       "from a daily tasks file.")
            self.show_message(message)
            return False
        return True

    def portfolio_open(self):
        """Function docstring."""

        launch_paths = set()
        for old_path in self.cfg['tab_order'].split('\n'):
            if old_path in launch_paths:
                continue
            self.file_open(old_path)
        danas = datetime.datetime.now()
        file_name = str(danas.year)
        if danas.month < 10:
            file_name += "0"
        file_name += str(danas.month)
        if danas.day < 10:
            file_name += "0"
        file_name += str(danas.day)
        file_name += self.cfg['atlas_files_extension']
        if os.path.isfile(self.cfg['portfolio_base_dir'] + file_name):
            self.file_open(self.cfg['portfolio_base_dir'] + file_name)

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

    def portfolio_reload_currently_open_files(self):
        for tab in self.widgets:
            contents = self._read_file(tab.path, single_string=True)
            tab.setText(contents)

    def file_new(self):
        """Add a new tab."""

        self._add_tab(None, "", self.c_newline)
    
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
            path = self._get_open_file_path(
                    self.cfg['portfolio_base_dir'],
                    self.cfg['atlas_files_extension'])
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
        self._add_tab(path, file_content, '\n')

    def file_save(self, path=None, tab=None):
        """Save file contained in a tab to disk.

        If `tab` is not specified, it assumes that we want to save the file
        contained in the currently active tab. If it is a newly added tab
        not save before (and hence a file does not exist on disk), a dialog is
        displayed to choose the save path. Even though the path of a tab is
        contained in the tab, due to different usage scenarios for this
        function, it is best to keep these two parameters separate.

        Parameters
        ----------
        path : str
            Path to save tab contents to.
        tab : EditorPane
            Tab containing the contents to save to `path`.

        """
        # TODO Review logic!
        if not tab:
            tab = self.current_tab
        if not path:
            # If it is a newly added tab, not saved before
            if tab.path is None:
                tab.path = self._get_save_file_path(
                        self.cfg['portfolio_base_dir'])
            # Was the dialog canceled?
            if not tab.path:
                return
            path = tab.path
        with open(path, 'w', encoding=self.cfg['encoding']) as path_:
            path_.writelines(tab.text())
        tab.setModified(False)

    def file_save_as(self):
        """Save file in active tab to a different path.

        After getting the new path, it checks if the new path is already open.
        If it is not open, calls `self.save_file()` with the new file name
        provided.

        """

        path = self.get_save_file_path(self.cfg['portfolio_base_dir'])
        # Was the dialog canceled?
        if not path:
            return
        for widget in self.widgets:
            if widget.path == path:
                # if os.path.samefile(path, widget.path):
                msg = "'{}' is open. Close if before overwriting."
                self.show_message(msg.format(os.path.basename(path)))
                self.focus_tab(widget)
                return
        self.file_save(path)

    def file_save_all(self):
        for tab in self.widgets:
            ctab_idx = self.tabs.indexOf(tab)
            self.tabs.setCurrentIndex(ctab_idx)
            self.file_save(path=tab.path, tab=tab)
            # TODO Make sure you return to current tab!!

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

    def goto_tab_left(self):
        """Change focus to one tab left. Allows for wrapping around."""

        tab = self.current_tab
        index = self.tabs.indexOf(tab)
        if index-1 < 0:
            next_tab = self.tab_count - 1
        else:
            next_tab = index - 1
        self.tabs.setCurrentIndex(next_tab)

    def goto_tab_right(self):
        """Change focus to one tab right. Allows for wrapping around."""

        tab = self.current_tab
        index = self.tabs.indexOf(tab)
        if index+1 > self.tab_count-1:
            next_tab = 0
        else:
            next_tab = index + 1
        self.tabs.setCurrentIndex(next_tab)

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

    def mark_task_done(self):
        """Mark current task as done.

        Marks the current task as done first in the daily tasks file, and then
        also at task definition. This method can only be run from a daily tasks
        file, and only on tasks that have an `open_task_prefix`. It calls
        `mark_ordinary_task_done()` to do the actual work. Special care is
        taken to preserve the view. After marking a task as done, it calls
        `_analyse_tasks()` and `_schedule_tasks()` to refresh the information.

        Notes
        -----
        In current code, care has been taken to avoid the bug where tab title
        is incorrectly changed when switching between tabs. Be aware of this
        when changing the code.

        """

        ctab = self.current_tab
        self.file_save_all()
        if not self._running_from_daily_tasks_file(ctab):
            return
        ctab_idx = self.tabs.indexOf(ctab)
        fv_line = ctab.firstVisibleLine()
        crow = ctab.getCursorPosition()[0]
        ctask = ctab.text(crow)
        ctask = re.sub(r'\d{2}:\d{2}' + self.c_space, "", ctask)
        if (ctask and ctask[0] not in self.c_active_task_prefixes):
            return
        self._engine.mark_ordinary_task_done(ctab.path, crow)
        self.portfolio_reload_currently_open_files()
        ctab.setFirstVisibleLine(fv_line)
        ctab.setCursorPosition(crow, 0)

    def mark_task_for_rescheduling(self):
        """Docstring."""

        ctab = self.current_tab
        self.file_save_all()
        if not self._running_from_daily_tasks_file(ctab):
            return
        ctab_idx = self.tabs.indexOf(ctab)
        fv_line = ctab.firstVisibleLine()
        crow = ctab.getCursorPosition()[0]
        ctask = ctab.text(crow)
        ctask = re.sub(r'\d{2}:\d{2}' + self.c_space, "", ctask)
        if (ctask and ctask[0] not in self.c_active_task_prefixes):
            return
        self._engine.mark_task_for_rescheduling(ctab.path, crow)
        self.portfolio_reload_currently_open_files()
        ctab.setFirstVisibleLine(fv_line)
        ctab.setCursorPosition(crow, 0)

    def toggle_tt(self):
        # TODO Change over current_tab to selected_tab
        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        self.file_save_all()
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        selected_task = selected_tab.text(selected_row)
        selected_task = re.sub(r'\d{2}:\d{2}' + self.c_space, "", selected_task)
        self._engine.toggle_tt(selected_tab.path, selected_row)
        self.portfolio_reload_currently_open_files()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def generate_ttl(self):
        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        self.file_save_all()
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        selected_task = selected_tab.text(selected_row)
        self._engine.generate_ttl(selected_tab.path)
        self.portfolio_reload_currently_open_files()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def generate_ttls(self):
        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        self.file_save_all()
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        selected_task = selected_tab.text(selected_row)
        self._engine.generate_ttls()
        self.portfolio_reload_currently_open_files()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def extract_booked(self):
        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        self.file_save_all()
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        selected_task = selected_tab.text(selected_row)
        self._engine.extract_booked()
        self.portfolio_reload_currently_open_files()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def extract_auxiliaries(self):
        selected_tab = self.current_tab
        selected_row = selected_tab.getCursorPosition()[0]
        self.file_save_all()
        selected_tab_idx = self.tabs.indexOf(selected_tab)
        first_visible_line = selected_tab.firstVisibleLine()
        selected_task = selected_tab.text(selected_row)
        self._engine.extract_auxiliaries()
        self.portfolio_reload_currently_open_files()
        self.tabs.setCurrentIndex(selected_tab_idx)
        selected_tab.setFirstVisibleLine(first_visible_line)
        selected_tab.setCursorPosition(selected_row, 0)

    def prepare_day_plan(self):
        today = datetime.datetime.now()
        day, month, year = self.show_prepare_day_plan(str(today.day),
                                                      str(today.month),
                                                      str(today.year))
        file_name = eight_digit_date(day, month, year)
        file_name_n_ext = file_name + self.cfg['atlas_files_extension']
        dtf_open = False
        for idx in range(self.tab_count):
            if (self.tabs.widget(idx).path
                    == self.cfg['portfolio_base_dir'] + file_name_n_ext):
                dtf_open = True
        if dtf_open:
            self.tabs.removeTab(idx)
        self._engine.prepare_day_plan(day, month, year)
        self.file_open(self.cfg['portfolio_base_dir'] + file_name_n_ext)

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

    def update_title(self, filename=None):
        """Docstring."""

        title = self.title
        if filename:
            title += " - " + filename
        self.setWindowTitle(title)

    def show_prepare_day_plan(self, target_day, target_month, target_year):
        """Docstring."""

        # ~ finder = FindReplaceDialog(self)
        finder = PrepareDayDialog(self)
        finder.setup(target_day, target_month, target_year)
        if finder.exec():
            return (finder.target_day(), finder.target_month(),
                    finder.target_year())
        return None

    def show_log_progress(self):
        """Docstring."""

        log_entry = LogProgressDialog(self)
        log_entry.setup()
        if log_entry.exec():
            return log_entry.log_entry()
        return None

    def show_add_adhoc_task(self):
        """Docstring."""

        adhoc_task = AddAdhocTaskDialog(self)
        adhoc_task.setup()
        if adhoc_task.exec():
            return adhoc_task.adhoc_task()
        return None
