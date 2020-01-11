import datetime
import os
import sys
from model.logic import Model as model

def running_from_daily_tasks_file(tab):
    """Docstring."""

    file_name = os.path.basename(tab.path).split('.')[0]
    if not re.match(r'\d{8}', file_name):
        message = ("This command can only be run from a daily tasks file.")
        self._view.show_message(message)
        return False
    return True

class Controller:
    def __init__(self, config, view, model):
        self._view = view
        self._model = model
        self.cfg = config.cfg
        if self.cfg['newline'] == 'linux':
            self.c_newline = '\n'
        else:
            self.c_newline = '\r\n'
        self.su_dropdown_menus()
        self.open_portfolio()
        
    def su_dropdown_menus(self):
        """Set up the drop-down menu.

        All Atlas commands (functions) are shown in drop-down menus.

        """

        menu_actions = dict()
        # File
        menu_actions['new_file'] = self.new_file
        menu_actions['open_file'] = self.open_file
        menu_actions['save_file'] = self.save_file
        menu_actions['save_file_as'] = self.save_file_as
        menu_actions['close_file'] = self.close_file
        menu_actions['quit'] = self.quit
        # Move
        menu_actions['goto_tab_left'] = self._view.goto_tab_left
        menu_actions['goto_tab_right'] = self._view.goto_tab_right
        menu_actions['move_line_up'] = self._view.move_line_up
        menu_actions['move_line_down'] = self._view.move_line_down
        menu_actions['move_daily_tasks_file'] = self._model.move_daily_tasks_file
        # Task
        menu_actions['mark_task_done'] = self.mark_task_done
        menu_actions['mark_task_for_rescheduling'] = \
            self._model.mark_task_for_rescheduling
        menu_actions['reschedule_periodic_task'] = \
            self._model.reschedule_periodic_task
        menu_actions['add_adhoc_task'] = self._model.add_adhoc_task
        menu_actions['tag_current_line'] = self._model.tag_current_line
        menu_actions['toggle_tt'] = self._model.toggle_tt
        # Lists
        menu_actions['generate_ttl'] = self._model.generate_ttl
        menu_actions['generate_ttls'] = self._model.generate_ttls
        menu_actions['extract_auxiliaries'] = self._model.extract_auxiliaries
        menu_actions['prepare_day_plan'] = self._model.prepare_day_plan
        menu_actions['analyse_tasks'] = self._model.analyse_tasks
        menu_actions['schedule_tasks'] = self._model.schedule_tasks
        menu_actions['extract_earned_time'] = self._model.extract_earned_time
        # Logs
        menu_actions['log_progress'] = self._model.log_progress
        # ~ menu_actions['log_expense'] = self._model.log_expense
        menu_actions['back_up'] = self._model.back_up
        # Other
        menu_actions['sort_periodic_tasks'] = self._model.sort_periodic_tasks
        menu_actions['extract_daily'] = self._model.extract_daily
        menu_actions['extract_booked'] = self._model.extract_booked
        menu_actions['extract_periodic'] = self._model.extract_periodic
        menu_actions['extract_shlist'] = self._model.extract_shlist
        self._view.setup_menu(menu_actions)

    def open_portfolio(self):
            """Function docstring."""

            launch_paths = set()
            for old_path in self.cfg['tab_order'].split('\n'):
                if old_path in launch_paths:
                    continue
                self.open_file(old_path)
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
                self.open_file(self.cfg['portfolio_base_dir'] + file_name)
    
    def new_file(self):
        """Add a new tab."""

        self._view.add_tab(None, "", self.c_newline)
    
    def open_file(self, path=None):
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
            path = self._view.get_open_file_path(
                    self.cfg['portfolio_base_dir'],
                    self.cfg['atlas_files_extension'])
        # Was the dialog canceled?
        if not path:
            return
        # Do not open a life area if it is already open
        for widget in self._view.widgets:
            if os.path.samefile(path, widget.path):
                msg = "'{}' is already open."
                self._view.show_message(msg.format(os.path.basename(path)))
                self._view.focus_tab(widget)
                return
        file_content = ''
        with open(path, encoding=self.cfg['encoding']) as faux:
            lines = faux.readlines()
            for line in lines:
                file_content += line
        self._view.add_tab(path, file_content, '\n')
    
    def save_file(self, path=None, tab=None):
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

        if not tab:
            tab = self._view.current_tab
        if not path:
            # If it is a newly added tab, not saved before
            if tab.path is None:
                tab.path = self._view.get_save_file_path(
                        self.cfg['portfolio_base_dir'])
            # Was the dialog canceled?
            if not tab.path:
                return
            path = tab.path
        with open(path, 'w', encoding=self.cfg['encoding']) as faux:
            faux.writelines(tab.text())
        tab.setModified(False)

    def save_file_as(self):
        """Save file in active tab to a different path.

        After getting the new path, it checks if the new path is already open.
        If it is not open, calls `self.save_file()` with the new file name
        provided.

        """

        path = self._view.get_save_file_path(self.cfg['portfolio_base_dir'])
        # Was the dialog canceled?
        if not path:
            return
        for widget in self._view.widgets:
            if widget.path == path:
                # if os.path.samefile(path, widget.path):
                msg = "'{}' is open. Close if before overwriting."
                self._view.show_message(msg.format(os.path.basename(path)))
                self._view.focus_tab(widget)
                return
        self.save_file(path)

    def close_file(self):
        """Close the current file (remove the current tab).

        Returning `False` indicates that the user, when answering to the
        question, chose 'Cancel'. Returning `True` indicates that the user
        answered with either 'Yes' or 'No'. This is primarily used by `quit()`
        to indicate whether to abort the quitting process if a user choses
        'Cancel'. If a user choses 'Cancel', they decide that they want to deal
        with the changes in the file in the normal program operation mode
        ('manually').

        """

        current_tab = self._view.current_tab
        current_tab_idx = self._view.tabs.indexOf(current_tab)
        if current_tab.isModified():
            answer = self._view.show_yes_no_question(
                "Do you want to save changes to the file before closing?",
                "File:    " + current_tab.path)
            if answer == QMessageBox.Yes:
                self.save_file()
            if answer == QMessageBox.Cancel:
                return False
        self._view.tabs.removeTab(current_tab_idx)
        return True

    def quit(self):
        """Quit Atlas.

        Confirm if and how the user wants to save changes. Saves session
        settings before exiting.

        """

        for tab in self._view.widgets:
            current_tab_index = self._view.tabs.indexOf(tab)
            self._view.tabs.setCurrentIndex(current_tab_index)
            user_chose_yes_or_no = self.close_file()
            if not user_chose_yes_or_no:
                return
        # self.save_session_settings()
        sys.exit(0)

    def mark_task_done(self):
        self._model.mark_task_done(self._view.current_tab)
