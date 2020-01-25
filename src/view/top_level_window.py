"""Docstring."""

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QAction, QDesktopWidget, QWidget, QVBoxLayout,
                             QTabWidget, QFileDialog, QMessageBox, QMainWindow,
                             QShortcut)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QIcon
from pkg_resources import resource_filename
from view.prepare_day_dialog import PrepareDayDialog
from view.log_progress_dialog import LogProgressDialog
from view.add_adhoc_task_dialog import AddAdhocTaskDialog
from view.editor_pane import EditorPane
from view.menu_bar import MenuBar
from view.file_tabs import FileTabs


def screen_size():
    """Docstring."""

    screen = QDesktopWidget().screenGeometry()
    return screen.width(), screen.height()


class TopLevelWindow(QMainWindow):
    """Docstring."""

    title = "Atlas"
    icon = 'icon'
    timer = None
    open_file = pyqtSignal(str)
    previous_folder = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = QWidget()
        self.read_only_tabs = False
        self.menu_bar = MenuBar(self.widget)
        self.tabs = FileTabs()
        self.open_file_heading = "Open file"
        self.save_file_heading = "Save file"
        self.atlas_file_extension_for_saving = "Atlas (*.pmd.txt)"

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
        actions['move_daily_tasks_file'] = move_daily_tasks_file

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
        actions['add_adhoc_task'] = add_adhoc_task

        tag_current_line = QAction("Tag current line", self)
        tag_current_line.setShortcut("Alt+T")
        task_menu.addAction(tag_current_line)
        actions['tag_current_line'] = tag_current_line

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
        actions['analyse_tasks'] = analyse_tasks

        schedule_tasks = QAction("Schedule tasks", self)
        schedule_tasks.setShortcut("Alt+S")
        lists_menu.addAction(schedule_tasks)
        actions['schedule_tasks'] = schedule_tasks

        extract_earned_time = QAction("Extract earned time", self)
        extract_earned_time.setShortcut("Alt+X")
        lists_menu.addAction(extract_earned_time)
        actions['extract_earned_time'] = extract_earned_time

        # Logs
        logs_menu = menu_bar.addMenu("Logs")

        log_progress = QAction("Log progress", self)
        log_progress.setShortcut("Alt+L")
        logs_menu.addAction(log_progress)
        actions['log_progress'] = log_progress

        log_expense = QAction("Log expense", self)
        log_expense.setShortcut("Alt+E")
        logs_menu.addAction(log_expense)
        actions['log_expense'] = log_expense

        back_up = QAction("Back up portfolio", self)
        back_up.setShortcut("Alt+B")
        logs_menu.addAction(back_up)
        actions['back_up'] = back_up

        # Other
        other_menu = menu_bar.addMenu("Other")

        sort_periodic_tasks = QAction("Sort periodic tasks", self)
        sort_periodic_tasks.setShortcut("Alt+Q")
        other_menu.addAction(sort_periodic_tasks)
        actions['sort_periodic_tasks'] = sort_periodic_tasks

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

        # Connections
        for key in actions:
            actions[key].triggered.connect(functions[key])

    @property
    def current_tab(self):
        """Docstring."""

        return self.tabs.currentWidget()

    def get_open_file_path(self, folder, extensions):
        """Get the path of the file to load (dialog)."""

        extensions = '*' + extensions
        path, _ = QFileDialog.getOpenFileName(self.widget,
                                              self.open_file_heading,
                                              folder,
                                              extensions)
        return path

    def get_save_file_path(self, folder):
        """Get the path of the file to save (dialog)."""

        path, _ = QFileDialog.getSaveFileName(
                self.widget,
                self.open_file_heading, folder,
                self.atlas_file_extension_for_saving)
        return path

    def add_tab(self, path, text, newline):
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

    @property
    def tab_count(self):
        """Docstring."""

        return self.tabs.count()

    @property
    def widgets(self):
        """Docstring."""

        return [self.tabs.widget(i) for i in range(self.tab_count)]

    @property
    def modified(self):
        """Docstring."""

        for widget in self.widgets:
            if widget.isModified():
                return True
        return False

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

    def change_mode(self):
        """Docstring."""

        self.button_bar.change_mode()

    def set_timer(self, duration, callback):
        """Docstring."""

        self.timer = QTimer()
        self.timer.timeout.connect(callback)
        self.timer.start(duration * 1000)  # Measured in milliseconds.

    def stop_timer(self):
        """Docstring."""

        if self.timer:
            self.timer.stop()
            self.timer = None

    def connect_prepare_day_plan(self, handler, shortcut):
        """Docstring."""

        self.prepare_day_plan_shortcut = QShortcut(QKeySequence(shortcut),
                                                   self)
        self.prepare_day_plan_shortcut.activated.connect(handler)

    def connect_log_progress(self, handler, shortcut):
        """Docstring."""

        self.log_progress_shortcut = QShortcut(QKeySequence(shortcut), self)
        self.log_progress_shortcut.activated.connect(handler)

    def connect_log_expense(self, handler, shortcut):
        """Docstring."""

        self.log_expense_shortcut = QShortcut(QKeySequence(shortcut), self)
        self.log_expense_shortcut.activated.connect(handler)

    def connect_add_adhoc_task(self, handler, shortcut):
        """Docstring."""

        self.adhoc_task_shortcut = QShortcut(QKeySequence(shortcut), self)
        self.adhoc_task_shortcut.activated.connect(handler)

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
