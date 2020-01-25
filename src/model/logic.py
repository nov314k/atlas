"""Implement Atlas logic.

Copyright notice
----------------
Copyright (C) 2019 Novak Petrovic
<npetrovic@gmail.com>

This file is part of Atlas.
For more details see the README (or README.md) file.

Atlas is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License
as published by the Free Software Foundation;
either version 3 of the License, or (at your option) any later version.

Atlas is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import configparser
import datetime
import json
import logging
import os
import re
import shutil
import sys
from dateutil.relativedelta import relativedelta
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox
import model.prepare_todays_tasks


LINE_ENDING = '\n'
NEWLINE = LINE_ENDING
WORKING_MODE = 'pmdtxt'
FILE_CHANGED_ASTERISK = '*'
ENCODING = 'UTF-8'


def sort_tasks(tasks, tags_in_sorting_order):
    """Function docstring."""

    sorted_tasks = []
    for tag in tags_in_sorting_order:
        for task in tasks:
            if tag in task:
                sorted_tasks.append(task)
    return sorted_tasks


class Editor:
    """Editor logic.

    Contains Atlas functionality (commands) implementation.

    Parameters
    ----------
    view : interface.Window (QMainWindow)
        Application main window.
    settings_file : str
        JSON file with portfolio settings.

    """

    def __init__(self, view, settings_file):
        """Initiates Editor instance variables.

        Parameters
        ----------
        view : interface.Window (QMainWindow)
            Application main window.
        settings_file : str
            JSON file with portfolio settings.

        Notes
        -----
        The role of `current_path` should be reviewed.

        `settings` is a dictionary of portfolio settings, read from the
        settings file.

        `WORKING_MODE` is a remnant of a previous implementation, and it
        should be removed.

        """

        self.encoding = 'UTF-8'
        self.line_ending = LINE_ENDING
        self._view = view
        self.current_path = ''
        self.mode = WORKING_MODE
        self.config_file = Path(settings_file)
        self.read_settings_file(self.config_file)

    def read_settings_file(self, settings_file):
        """Read portfolio JSON settins file and store settings

        Settings are stored in `settings` dictionary. Dictionary keys are
        literally the same as JSON properties.

        """

        self.config = configparser.ConfigParser(
                interpolation=configparser.ExtendedInterpolation())
        self.config.read(settings_file)
        self.cfg = self.config['USER']
        self.active_task_prefixes = (
                self.cfg['active_task_prefixes'].split('\n'))
        self.portfolio_files = self.cfg['portfolio_files'].split('\n')

    def setup(self):
        """Function docstring."""

        self.setup_menu()
        self.open_portfolio()

    def setup_menu(self):
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
        menu_actions['goto_tab_left'] = self.goto_tab_left
        menu_actions['goto_tab_right'] = self.goto_tab_right
        menu_actions['move_line_up'] = self.move_line_up
        menu_actions['move_line_down'] = self.move_line_down
        menu_actions['move_daily_tasks_file'] = self.move_daily_tasks_file
        # Task
        menu_actions['mark_task_done'] = self.mark_task_done
        menu_actions['mark_task_for_rescheduling'] = \
            self.mark_task_for_rescheduling
        menu_actions['reschedule_periodic_task'] = \
            self.reschedule_periodic_task
        menu_actions['add_adhoc_task'] = self.add_adhoc_task
        menu_actions['tag_current_line'] = self.tag_current_line
        menu_actions['toggle_tt'] = self.toggle_tt
        # Lists
        menu_actions['generate_ttl'] = self.generate_ttl
        menu_actions['generate_ttls'] = self.generate_ttls
        menu_actions['extract_auxiliaries'] = self.extract_auxiliaries
        menu_actions['prepare_day_plan'] = self.prepare_day_plan
        menu_actions['analyse_tasks'] = self.analyse_tasks
        menu_actions['schedule_tasks'] = self.schedule_tasks
        menu_actions['extract_earned_time'] = self.extract_earned_time
        # Logs
        menu_actions['log_progress'] = self.log_progress
        menu_actions['log_expense'] = self.log_expense
        menu_actions['back_up'] = self.back_up
        # Other
        menu_actions['sort_periodic_tasks'] = self.sort_periodic_tasks
        menu_actions['extract_daily'] = self.extract_daily
        menu_actions['extract_booked'] = self.extract_booked
        menu_actions['extract_periodic'] = self.extract_periodic
        menu_actions['extract_shlist'] = self.extract_shlist
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

        self._view.add_tab(None, "", NEWLINE)

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
        with open(path, encoding=self.encoding) as faux:
            lines = faux.readlines()
            for line in lines:
                file_content += line
        self._view.add_tab(path, file_content, self.line_ending)

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
        with open(path, 'w', encoding=self.encoding) as faux:
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

    def get_tab(self, path):
        """Function docstring."""

        normalised_path = os.path.normcase(os.path.abspath(path))
        for tab in self._view.widgets:
            if tab.path:
                tab_path = os.path.normcase(os.path.abspath(tab.path))
                if tab_path == normalised_path:
                    self._view.focus_tab(tab)
                    return tab
        return self._view.current_tab

    def quit(self, fixme):
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
        self.save_session_settings()
        sys.exit(0)

    def goto_tab_left(self):
        """Change focus to one tab left. Allows for wrapping around."""

        tab = self._view.current_tab
        index = self._view.tabs.indexOf(tab)
        if index-1 < 0:
            next_tab = self._view.tab_count - 1
        else:
            next_tab = index - 1
        self._view.tabs.setCurrentIndex(next_tab)

    def goto_tab_right(self):
        """Change focus to one tab right. Allows for wrapping around."""

        tab = self._view.current_tab
        index = self._view.tabs.indexOf(tab)
        if index+1 > self._view.tab_count-1:
            next_tab = 0
        else:
            next_tab = index + 1
        self._view.tabs.setCurrentIndex(next_tab)

    def move_line_up(self):
        """Move current line of text one row up."""

        tab = self._view.current_tab
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
                contents += task + NEWLINE
            contents = contents.rstrip(NEWLINE)
            tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))
            tab.setFirstVisibleLine(first_visible_line)
            tab.setCursorPosition(row - 1, 0)

    def move_line_down(self):
        """Move current line of text one row down."""

        tab = self._view.current_tab
        first_visible_line = tab.firstVisibleLine()
        tasks = tab.text().split(NEWLINE)
        row = tab.getCursorPosition()[0]
        if row < len(tasks) - 1:
            for i in range(len(tasks) - 1, -1, -1):
                if i == row + 1:
                    temp = tasks[i]
                    tasks[i] = tasks[i - 1]
                    tasks[i - 1] = temp
            contents = ""
            for task in tasks:
                contents += task + NEWLINE
            contents = contents.rstrip(NEWLINE)
            tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))
            tab.setFirstVisibleLine(first_visible_line)
            tab.setCursorPosition(row + 1, 0)

    def move_daily_tasks_file(self):
        """Move the current daily tasks file to its archive dir."""

        ctab = self._view.current_tab
        if not self.running_from_daily_tasks_file(ctab):
            return
        fnae = os.path.basename(ctab.path)
        ctab_idx = self._view.tabs.indexOf(ctab)
        self._view.tabs.removeTab(ctab_idx)
        shutil.move(
            self.cfg['portfolio_base_dir'] + fnae,
            self.cfg['daily_files_archive_dir'] + fnae)

    def mark_task_done(self):
        """Mark current task as done.

        Marks the current task as done first in the daily tasks file, and then
        also at task definition. This method can only be run from a daily tasks
        file, and only on tasks that have an `open_task_prefix`. It calls
        `mark_ordinary_task_done()` to do the actual work. Special care is
        taken to preserve the view. After marking a task as done, it calls
        `analyse_tasks()` and `schedule_tasks()` to refresh the information.

        Notes
        -----
        In current code, care has been taken to avoid the bug where tab title
        is incorrectly changed when switching between tabs. Be aware of this
        when changing the code.

        """

        tab = self._view.current_tab
        if not self.running_from_daily_tasks_file(tab):
            return
        current_tab_index = self._view.tabs.indexOf(tab)
        first_visible_line = tab.firstVisibleLine()
        row = tab.getCursorPosition()[0]
        current_task = tab.text(row)
        current_task = re.sub(r'\d{2}:\d{2}' + self.cfg['space'][1], "",
                              current_task)
        # If it's a blank line
        if (current_task
                and current_task[0]
                not in self.cfg['active_task_prefixes'].split('\n')):
            return
        contents = self.mark_ordinary_task_done(tab)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))
        # TODO Consider adding an option
        # to determine whether the user wants this done
        # self.analyse_tasks()
        # self.schedule_tasks()
        self.mark_done_at_origin(current_task)
        self._view.tabs.setCurrentIndex(current_tab_index)
        tab.setFirstVisibleLine(first_visible_line)
        tab.setCursorPosition(row, 0)

    def mark_ordinary_task_done(self, tab):
        """Function docstring."""

        now = datetime.datetime.now()
        row = tab.getCursorPosition()[0]
        tasks = tab.text().split(NEWLINE)
        if len(tasks[-1]) < 1:
            tasks = tasks[:-1]
        current_task = tasks[row]
        del tasks[row]
        taux = self.cfg['done_task_prefix'] + self.cfg['space'][1] + \
            now.strftime("%Y-%m-%d")
        taux += self.cfg['space'][1] + current_task
        tasks.append(taux)
        contents = ""
        for task in tasks:
            contents += task + NEWLINE
        contents = contents.rstrip(NEWLINE)
        return contents

    def mark_done_at_origin(self, task):
        """Function docstring."""

        if (len(task) < 1
                or task[0] not in self.active_task_prefixes
                or self.cfg['daily_rec_prop_val'] in task):
            return
        idx = -1
        tasks = []
        tab_idx = -1
        task_found = False
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path in self.portfolio_files:
                tasks = self._view.tabs.widget(i).text().split(NEWLINE)
                in_ttl = False
                for j, _ in enumerate(tasks):
                    if tasks[j]:
                        if (tasks[j][0] == self.cfg['heading_prefix']
                                and self.cfg['ttl_heading'] in tasks[j]):
                            in_ttl = True
                        elif tasks[j][0] == self.cfg['heading_prefix']:
                            in_ttl = False
                        if (tasks[j][0] in self.active_task_prefixes
                                and self.get_task_text(tasks[j]) in task
                                and not task_found
                                and not in_ttl):
                            idx = j
                            tab_idx = i
                            task_found = True
                            break
            if task_found:
                break
        if idx > -1:
            if self.cfg['rec_prop'] in tasks[idx]:
                tasks[idx] = self.update_due_date(tasks[idx])
            else:
                tasks[idx] = (self.cfg['done_task_prefix']
                              + self.cfg['space'][1] + tasks[idx][2:])
        contents = ""
        for task_ in tasks:
            contents += task_ + NEWLINE
        contents = contents.rstrip(NEWLINE)
        if tab_idx > -1:
            self._view.tabs.setCurrentIndex(tab_idx)
            tab = self._view.tabs.widget(tab_idx)
            tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))

    def mark_task_for_rescheduling(self, mark_rescheduled_periodic_task=False):
        """Function docstring."""

        now = datetime.datetime.now()
        tab = self._view.current_tab
        first_visible_line = tab.firstVisibleLine()
        tasks = tab.text().split(NEWLINE)
        if len(tasks[-1]) < 1:
            tasks = tasks[:-1]
        row = tab.getCursorPosition()[0]
        current_task = tasks[row]
        del tasks[row]
        taux = self.cfg['for_rescheduling_task_prefix']
        if mark_rescheduled_periodic_task:
            taux = self.cfg['rescheduled_periodic_task_prefix']
        taux += self.cfg['space'][1] + now.strftime("%Y-%m-%d") + \
            self.cfg['space'][1] \
            + current_task
        tasks.append(taux)
        contents = ""
        for task in tasks:
            contents += task + NEWLINE
        contents = contents.rstrip(NEWLINE)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))
        # TODO Consider adding an option
        # to determine whether the user wants this done
        # self.analyse_tasks()
        # self.schedule_tasks()
        tab.setFirstVisibleLine(first_visible_line)
        tab.setCursorPosition(row, 0)

    def reschedule_periodic_task(self):
        """Function docstring."""

        tab = self._view.current_tab
        if not self.running_from_daily_tasks_file(tab):
            return
        row = tab.getCursorPosition()[0]
        task = tab.text(row)
        task = re.sub(r'\d{2}:\d{2}' + self.cfg['space'][1], "", task)
        if (len(task) < 1
                or self.cfg['rec_prop']
                not in task
                or task[0] not in self.cfg['active_task_prefixes'].split('\n')
                or self.cfg['daily_rec_prop_val'] in task):
            return
        tab_index = self._view.tabs.indexOf(tab)
        row = tab.getCursorPosition()[0]
        self.mark_done_at_origin(task)
        self._view.tabs.setCurrentIndex(tab_index)
        self.mark_task_for_rescheduling(True)
        # TODO Consider adding an option
        # to determine whether the user wants this done
        # self.analyse_tasks()
        # self.schedule_tasks()
        return

    def add_adhoc_task(self):
        """Add an ad hoc (incoming) task to an LA file or a DT file.

        Add an ad hoc (incoming) task. There are two main situations: adding an
        ad hoc task to a life area (LA) file, and adding an add hoc task to a
        daily tasks (DT) file. Different values for `extra_line_before` and
        `extra_line_after` are given in those two cases. Then there is also the
        case of adding an already finished task. A finished task is added at
        the end of a daily tasks file (with `extra_line_before` and
        `extra_line_after` suitably adjusted), while it is not added to a
        portfolio file.

        Notes
        -----
        Consider splitting this method into two: one for adding the ad hoc task
        to a life area file, and one for adding an ad hoc task to a daily tasks
        file, since the logic below is getting a bit cumbersome.

        """

        result = self._view.show_add_adhoc_task()
        current_tab = self._view.current_tab
        if result:
            task_finished = result[3]
            # If incoming task is a work task, add work tag to existing tags
            if result[4]:
                result[2] += self.cfg['space'][1] + self.cfg['work_tag']
            lines = current_tab.text().split(NEWLINE)
            extra_line_before = ''
            extra_line_after = ''
            # If active tab is a portfolio file
            if current_tab.path in self.cfg['portfolio_files'].split('\n'):
                # TODO Add a suitable message for why we're returning
                if task_finished:
                    return
                ordering_string = self.cfg['heading_prefix'] + \
                    self.cfg['space'][1]
                ordering_string += self.cfg['incoming_heading']
                extra_line_before = NEWLINE
                extra_line_after = ''
            # TODO Check if active tab is a daily file (currently assumed!)
            else:
                lines = lines[:-1]
                ordering_string = self.cfg['heading_prefix'] + \
                    self.cfg['space'][1]
                ordering_string += self.cfg['tasks_proposed_heading']
                extra_line_before = NEWLINE
                extra_line_after = ''
                if task_finished:
                    extra_line_before = ''
                    extra_line_after = NEWLINE
            task_status_mark = self.cfg['open_task_prefix']
            if task_finished:
                task_status_mark = self.cfg['done_task_prefix']
            # Start constructing the task to add
            taux = extra_line_before + task_status_mark + self.cfg['space'][1]
            # Add task and duration
            taux += result[0] + self.cfg['space'][1] + \
                self.cfg['dur_prop'] + result[1]
            # Add tags
            taux += self.cfg['space'][1] + result[2] + extra_line_after
            # Generate new contents
            contents = ""
            for line in lines:
                contents += line + NEWLINE
                if ordering_string in line and not task_finished:
                    contents += taux
            if task_finished:
                contents += taux + NEWLINE
            contents = contents.rstrip(NEWLINE)
            # Send contents to tab and save tab to file
            current_tab.SendScintilla(
                current_tab.SCI_SETTEXT, contents.encode(self.encoding))
            self.save_file(current_tab)

    def tag_current_line(self):
        """Function docstring."""

        current_tab = self._view.current_tab
        first_visible_line = current_tab.firstVisibleLine()
        tag = self.cfg['tag_prefix'] + current_tab.label.split('.')[0]
        if FILE_CHANGED_ASTERISK in tag:
            tag = tag[:-2]
        lines = current_tab.text().split(NEWLINE)
        row = current_tab.getCursorPosition()[0]
        col = 0
        contents = ""
        for i, _ in enumerate(lines):
            if (i == row
                    and lines[i]
                    and lines[i][0] in self.active_task_prefixes
                    and tag not in lines[i]):
                line = lines[i] + self.cfg['space'][1] + tag
                contents += line + NEWLINE
                col = len(line)
            else:
                contents += lines[i] + NEWLINE
        contents = contents.rstrip(NEWLINE)
        current_tab.SendScintilla(
            current_tab.SCI_SETTEXT, contents.encode(ENCODING))
        current_tab.setFirstVisibleLine(first_visible_line)
        current_tab.setCursorPosition(row, col)
        self.save_file(current_tab)

    def toggle_tt(self):
        """Function docstring."""

        tab = self._view.current_tab
        first_visible_line = tab.firstVisibleLine()
        lines = tab.text().split(NEWLINE)
        cursor_position = tab.getCursorPosition()
        row = cursor_position[0]
        col = cursor_position[1]
        new_lines = []
        for i, _ in enumerate(lines):
            if (i == row
                    and lines[i]
                    and self.cfg['due_prop'] not in lines[i]
                    and self.cfg['rec_prop'] not in lines[i]):
                if lines[i][0] == self.cfg['top_task_prefix']:
                    new_lines.append(self.cfg['open_task_prefix']
                                     + lines[i][1:])
                else:
                    new_lines.append(self.cfg['top_task_prefix']
                                     + lines[i][1:])
            else:
                new_lines.append(lines[i])
        contents = ""
        for i, _ in enumerate(new_lines):
            contents += new_lines[i] + NEWLINE
        contents = contents.rstrip(NEWLINE)
        tab.SendScintilla(
            tab.SCI_SETTEXT, contents.encode(ENCODING))
        tab.setFirstVisibleLine(first_visible_line)
        tab.setCursorPosition(row, col - 1)
        self.save_file(tab)

    def generate_ttl(self, tab=None):
        """Generate Top Tasks List (TTL) for the current file (tab)."""

        if not tab:
            tab = self._view.current_tab
        tasks_aux = tab.text().split(NEWLINE)
        start = -1
        ttl_tasks = []
        for i, _ in enumerate(tasks_aux):
            if tasks_aux[i]:
                if start > -1:
                    if tasks_aux[i][0] == self.cfg['top_task_prefix']:
                        ttl_tasks.append(tasks_aux[i])
                elif (tasks_aux[i][0] == self.cfg['heading_prefix']
                        and self.cfg['ttl_heading'] not in tasks_aux[i]):
                    start = i
        tasks = [self.cfg['heading_prefix'] + self.cfg['space'][1]
                 + self.cfg['ttl_heading'], '']
        for ttl_task in ttl_tasks:
            tasks.append(ttl_task)
        tasks.append('')
        for i in range(start, len(tasks_aux)):
            tasks.append(tasks_aux[i])
        contents = ""
        for i, _ in enumerate(tasks):
            contents += tasks[i] + NEWLINE
        contents = contents.rstrip(NEWLINE)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))
        self.save_file(tab.path, tab)

    def generate_ttls(self):
        """Generate Top Tasks Lists (TTLs) for all portfolio files."""

        for widget in self._view.widgets:
            current_tab_index = self._view.tabs.indexOf(widget)
            self._view.tabs.setCurrentIndex(current_tab_index)
            if widget.path in self.cfg['portfolio_files'].split('\n'):
                self.generate_ttl(widget)

    def extract_auxiliaries(self):
        """Function docstring."""

        self.extract_booked()
        self.extract_daily()
        self.extract_periodic()
        self.extract_shlist()

    def prepare_day_plan(self):
        """Function docstring."""

        self.generate_ttls()
        self.extract_auxiliaries()
        danas = datetime.datetime.now()
        result = self._view.show_prepare_day_plan(
            str(danas.day), str(danas.month), str(danas.year))
        if result:
            target_day, target_month, target_year = result
            model.prepare_todays_tasks.prepare_todays_tasks(
                target_day, target_month, target_year,
                self.cfg['atlas_settings_file'])
        else:
            return
        file_name = str(target_year)
        if target_month < 10:
            file_name += "0"
        file_name += str(target_month)
        if target_day < 10:
            file_name += "0"
        file_name += str(target_day)
        file_name += self.cfg['atlas_files_extension']
        # Close tab with the same name if it is alreday copen
        idx = -1
        for i in range(self._view.tab_count):
            if (self._view.tabs.widget(i).path
                    == self.cfg['portfolio_base_dir'] + file_name):
                idx = i
        if idx > -1:
            self._view.tabs.removeTab(idx)
        shutil.copyfile(self.cfg['today_file'],
                        self.cfg['portfolio_base_dir'] + file_name)
        self.open_file(self.cfg['portfolio_base_dir'] + file_name)

    def analyse_tasks(self):
        """Function docstring."""

        tab = self._view.current_tab
        tasks_aux = tab.text().split(NEWLINE)
        tasks = []
        total_duration = 0
        work_duration = 0
        earned_duration = 0
        work_earned_duration = 0
        for task in tasks_aux:
            if task:
                task = re.sub(r'\d{2}:\d{2}' + self.cfg['space'][1], "", task)
                if task[0] in self.cfg['active_task_prefixes'].split('\n'):
                    if self.cfg['dur_prop'] not in task:
                        self._view.show_message("Please define dur:\n" + task)
                        return
                    else:
                        duration = self.get_task_duration(task)
                        total_duration += duration
                        if self.cfg['work_tag'] in task:
                            work_duration += duration
                elif task[0] == self.cfg['done_task_prefix']:
                    duration = self.get_task_duration(task)
                    earned_duration += duration
                    if self.cfg['work_tag'] in task:
                        work_earned_duration += duration
        # Get rid of previous header information
        for task in tasks_aux:
            if task and task[0] is not self.cfg['info_task_prefix']:
                tasks.append(task)
            # else:
                # tasks.append(task)
        statistic = (
            f"{self.cfg['info_task_prefix'] + self.cfg['space'][1]}"
            f"{self.cfg['earned_time_balance_form']}"
            f"{self.mins_to_hh_mm(earned_duration)} "
            f"({self.mins_to_hh_mm(work_earned_duration)})"
        )
        tasks.insert(0, statistic)
        statistic = (
            f"> Remaining tasks duration (work) = "
            f"{self.mins_to_hh_mm(total_duration)} "
            f"({self.mins_to_hh_mm(work_duration)})"
        )
        tasks.insert(0, statistic)
        contents = ""
        for i, _ in enumerate(tasks):
            contents += tasks[i] + NEWLINE
        contents = contents.rstrip(NEWLINE)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))

    def schedule_tasks(self):
        """Function docstring."""

        tab = self._view.current_tab
        tasks = tab.text().split(NEWLINE)
        start_time = datetime.datetime.now()
        scheduled_tasks = []
        for task in tasks:
            if task:
                task = re.sub(r'\d{2}:\d{2}' + self.cfg['space'][1], "", task)
                if task[0] in self.cfg['active_task_prefixes'].split('\n'):
                    sts = f"{start_time.hour:02}:{start_time.minute:02}"
                    idx = 2 - 2
                    # Has the task already been schedulled?
                    if task[4] == ':':
                        idx = 10 - 2
                    new_task = sts + self.cfg['space'][1] + task[idx:]
                    scheduled_tasks.append(new_task)
                    start_time += datetime.timedelta(
                        minutes=self.get_task_duration(task))
                else:
                    scheduled_tasks.append(task)
            else:
                scheduled_tasks.append(task)
        contents = ""
        for task in scheduled_tasks:
            contents += task + NEWLINE
        contents = contents.rstrip(NEWLINE)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))

    def extract_earned_time(self):
        """Function docstring."""

        ctab = self._view.current_tab
        file_name = os.path.basename(ctab.path).split('.')[0]
        # Check that we're running from a daily tasks file
        if not re.match(r'\d{8}', file_name):
            message = "This command can only be run" \
                      "from a daily tasks file."
            self._view.show_message(message)
            return
        tasks = ctab.text().split(NEWLINE)
        for task in tasks:
            if self.cfg['earned_time_balance_form'] in task:
                extract = file_name + self.cfg['space'][1] + task + NEWLINE
        with open(self.cfg['earned_times_file'], 'a') as file_:
            file_.write(extract)

    def log_progress(self):
        """Function docstring."""

        log_entry = self.format_log_entry(self._view.show_log_progress())
        if log_entry:
            log_tab_index = -1
            for i in range(self._view.tab_count):
                if (self._view.tabs.widget(i).path
                        == self.cfg['portfolio_log_file']):
                    log_tab_index = i
            if log_tab_index > -1:
                curr_stamp = datetime.datetime.now()
                current_tab_index = self._view.tabs.indexOf(
                        self._view.current_tab)
                self._view.tabs.setCurrentIndex(log_tab_index)
                log_tab = self._view.tabs.widget(log_tab_index)
                lines = log_tab.text().split(NEWLINE)
                for line in lines:
                    if line[:4] == self.cfg['log_entry_prefix']:
                        parts = line.split(self.cfg['date_separator'])
                        prev_stamp = datetime.datetime(
                            int(parts[1]),  # year
                            int(parts[2]),  # month
                            int(parts[3]),  # day
                            int(parts[4]),  # hours
                            int(parts[5]),  # minutes
                            int(parts[6]))  # seconds
                        break
                diff = curr_stamp - prev_stamp
                contents = (self.cfg['log_entry_prefix']
                            + "{}{}{:02d}{}{:02d}".format(
                                curr_stamp.year, self.cfg['date_separator'],
                                curr_stamp.month, self.cfg['date_separator'],
                                curr_stamp.day))
                contents += "{}{:02d}{}{:02d}{}{:02d}\n" \
                    .format(self.cfg['date_separator'], curr_stamp.hour,
                            self.cfg['date_separator'], curr_stamp.minute,
                            self.cfg['date_separator'], curr_stamp.second)
                msh = {
                    'min': 0,
                    'sec': 0,
                    'hrs': 0,
                }
                if diff.seconds > 59:
                    msh['min'] = diff.seconds // 60
                    msh['sec'] = diff.seconds % 60
                else:
                    msh['sec'] = diff.seconds
                if msh['min'] > 59:
                    msh['hrs'] = msh['min'] // 60
                    msh['min'] = msh['min'] % 60
                text_aux = "from previous entry"
                contents += "{} days, {}{}{:02d}{}{:02d} {}\n". \
                    format(diff.days, msh['hrs'], self.cfg['time_separator'],
                           msh['min'], self.cfg['time_separator'], msh['sec'],
                           text_aux)
                contents += log_entry + NEWLINE + NEWLINE + log_tab.text()
                log_tab.SendScintilla(
                    log_tab.SCI_SETTEXT, contents.encode(ENCODING))
                self.save_file(log_tab)
                self._view.tabs.setCurrentIndex(current_tab_index)
        else:
            return

    def log_expense(self):
        """Log expense."""

        log_entry = self.format_log_entry(self._view.show_log_expense())
        return log_entry

    def back_up(self):
        """Back up."""

        now = datetime.datetime.now()
        try:
            shutil.copytree(
                self.cfg['portfolio_base_dir'],
                self.cfg['backup_dir'] + now.strftime("%Y%m%d%H%M%S"))
        except shutil.Error as ex:
            logging.error("Directory not copied. Error: %s", ex)
        except OSError as ex:
            logging.error("Directory not copied. Error: %s", ex)

    def sort_periodic_tasks(self):
        """Sort lines in the current tab."""

        tab = self._view.current_tab
        first_visible_line = tab.firstVisibleLine()
        tasks = tab.text().split(NEWLINE)
        contents = ""
        for task in sorted(tasks):
            if len(task) > 0:
                contents += task + NEWLINE
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(ENCODING))
        tab.setFirstVisibleLine(first_visible_line)
        tab.setCursorPosition(0, 0)

    def extract_daily(self):
        """Extract to file tasks with the daily-periodic property defined."""

        current_tab = self._view.current_tab
        current_tab_index = self._view.tabs.indexOf(current_tab)
        daily_tasks = []
        daily_tab_index = -1
        for widget in self._view.widgets:
            if widget.path in self.cfg['portfolio_files'].split('\n'):
                lines = widget.text().split(NEWLINE)
                for line in lines:
                    if (self.cfg['daily_rec_prop_val'] in line
                            and line[0] in self.active_task_prefixes):
                        daily_tasks.append(line)
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path == self.cfg['daily_file']:
                daily_tab_index = i
        contents = ""
        for i, _ in enumerate(daily_tasks):
            contents += daily_tasks[i] + NEWLINE
        contents = contents.rstrip(NEWLINE)
        self._view.tabs.setCurrentIndex(daily_tab_index)
        daily_tab = self._view.tabs.widget(daily_tab_index)
        daily_tab.SendScintilla(daily_tab.SCI_SETTEXT,
                                contents.encode(self.encoding))
        self.save_file(daily_tab.path, daily_tab)
        self._view.tabs.setCurrentIndex(current_tab_index)

    def extract_booked(self):
        """Extract to file tasks with the due-date property defined."""

        current_tab = self._view.current_tab
        current_tab_index = self._view.tabs.indexOf(current_tab)
        booked_tasks = []
        booked_tab_index = -1
        for widget in self._view.widgets:
            if widget.path in self.cfg['portfolio_files'].split('\n'):
                lines = widget.text().split(NEWLINE)
                for line in lines:
                    if (self.cfg['due_prop'] in line
                            and self.cfg['rec_prop'] not in line
                            and line[0] in self.active_task_prefixes):
                        booked_tasks.append(line)
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path == self.cfg['booked_file']:
                booked_tab_index = i
        booked_tab = self._view.tabs.widget(booked_tab_index)
        contents = ""
        for i, _ in enumerate(booked_tasks):
            contents += booked_tasks[i] + NEWLINE
        contents = contents.rstrip(NEWLINE)
        self._view.tabs.setCurrentIndex(booked_tab_index)
        booked_tab = self._view.tabs.widget(booked_tab_index)
        booked_tab.SendScintilla(booked_tab.SCI_SETTEXT,
                                 contents.encode(self.encoding))
        self.save_file(booked_tab.path, booked_tab)
        self._view.tabs.setCurrentIndex(current_tab_index)

    def extract_periodic(self):
        """Extract to file tasks with the periodic property defined."""

        current_tab = self._view.current_tab
        current_tab_index = self._view.tabs.indexOf(current_tab)
        periodic_tasks = []
        periodic_tab_index = -1
        for widget in self._view.widgets:
            if widget.path in self.cfg['portfolio_files'].split('\n'):
                lines = widget.text().split(NEWLINE)
                for line in lines:
                    if (self.cfg['rec_prop'] in line
                            and self.cfg['daily_rec_prop_val'] not in line
                            and line[0] in self.active_task_prefixes):
                        periodic_tasks.append(line)
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path == self.cfg['periodic_file']:
                periodic_tab_index = i
        periodic_tab = self._view.tabs.widget(periodic_tab_index)
        contents = ""
        for i, _ in enumerate(periodic_tasks):
            contents += periodic_tasks[i] + NEWLINE
        contents = contents.rstrip(NEWLINE)
        self._view.tabs.setCurrentIndex(periodic_tab_index)
        periodic_tab = self._view.tabs.widget(periodic_tab_index)
        periodic_tab.SendScintilla(periodic_tab.SCI_SETTEXT,
                                   contents.encode(self.encoding))
        self.save_file(periodic_tab.path, periodic_tab)
        self._view.tabs.setCurrentIndex(current_tab_index)

    def extract_shlist(self):
        """Extract to file tasks with the shopping list category defined."""

        current_tab = self._view.current_tab
        current_tab_index = self._view.tabs.indexOf(current_tab)
        shlist_tasks = []
        shlist_tab_index = -1
        for widget in self._view.widgets:
            if widget.path in self.cfg['portfolio_files'].split('\n'):
                lines = widget.text().split(NEWLINE)
                for line in lines:
                    if (self.cfg['shlist_cat'] in line
                            and line[0] in self.active_task_prefixes):
                        shlist_tasks.append(line)
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path == self.cfg['shlist_file']:
                shlist_tab_index = i
        shlist_tab = self._view.tabs.widget(shlist_tab_index)
        contents = ""
        for i, _ in enumerate(shlist_tasks):
            contents += shlist_tasks[i] + NEWLINE
        contents = contents.rstrip(NEWLINE)
        self._view.tabs.setCurrentIndex(shlist_tab_index)
        shlist_tab = self._view.tabs.widget(shlist_tab_index)
        shlist_tab.SendScintilla(shlist_tab.SCI_SETTEXT,
                                 contents.encode(self.encoding))
        self.save_file(shlist_tab.path, shlist_tab)
        self._view.tabs.setCurrentIndex(current_tab_index)

    # Utilities

    def format_log_entry(self, entry):
        """Format log entry so that each line does not exceed certain length.

        Maximum line length is defined in self.LOG_LINE_LENGTH.

        .. warning:: Currently assumes len(entry) is always < 160.

        :param entry string: log entry before formatting
        :returns string: log entry after formatting
        """

        if entry and len(entry) > self.cfg.getint('log_line_length'):
            entry = entry[:self.cfg.getint('log_line_length')] + NEWLINE \
                + entry[self.cfg.getint('log_line_length'):]
        return entry

    def get_task_duration(self, task):
        """Get task duration from task definition.

        Parameters
        ----------
        task : str
            Task definition.

        Returns
        -------
        int
            Task duration as defined in task definition. Assumed to be in
            minutes.

        """

        words = task.split(self.cfg['space'][1])
        for word in words:
            if self.cfg['dur_prop'] in word:
                duration = int(word.split(self.cfg['time_separator'])[1])
        return int(duration)

    def get_task_text(self, task):
        """Get task text without properties, tags, categories, and symbols.

        Get just the task text (without properties, tags, categories, prefixes,
        symbols, scheduling times, and the like) from full task definition.

        :param task string: task definition
        :returns string: task text
        """

        words = task.split(self.cfg['space'][1])
        task_text = ''
        for word in words:
            # Beware of special letters (and words beginning with them)
            if (self.word_has_active_task_prefix(word)
                    or self.props_in_word(word)
                    or self.word_has_reserved_word_prefix(word)):
                pass
            else:
                task_text += word + self.cfg['space'][1]
        return task_text.rstrip(self.cfg['space'][1])

    def running_from_daily_tasks_file(self, tab):
        """Check if the command is issued while a daily tasks tab is active.

        :param tab widget: active tab when the command was invoked
        :type tab: widget
        :returns boolean:
        """

        file_name = os.path.basename(tab.path).split('.')[0]
        if not re.match(r'\d{8}', file_name):
            message = ("This command can only be run"
                       "from a daily tasks file.")
            self._view.show_message(message)
            return False
        return True

    def mins_to_hh_mm(self, mins):
        """Convert minutes to hours and minutes.

        Convert minutes to hours and minutes; format the return string so that
        both hours and minuts are expressed using two digits, and separated
        using the predefined time separator symbol.

        Parameters
        ----------
        mins : int
            Number of minutes to convert.

        Returns
        -------
        str
           Formatted number of hours and minutes.

        """

        hours_ = mins // 60
        mins_ = mins % 60
        return f"{hours_:02}{self.settings['time_separator']}{mins_:02}"

    def update_due_date(self, periodic_task):
        """Update the due date of a periodic task.

        Update the due date of a periodic task, based on its current due date,
        recurrence period, and recurrence type. Today's date may also be used.

        Parameters
        ----------
        periodic_task : str
            Task definition.

        Returns
        -------
        updated_periodic_task : str
            Updated task definition.

        """

        calculate_from_due_date = False
        words = periodic_task.split(self.cfg['space'][1])
        for word in words:
            if self.cfg['due_prop'] in word:
                due = word[4:]
            elif self.cfg['rec_prop'] in word:
                if self.cfg['tag_prefix'] in word:
                    calculate_from_due_date = True
                rec = ''
                for char in word:
                    if char.isnumeric():
                        rec += char
                rec_period = word[-1]
        rec = int(rec)
        _year, _month, _day = due.split(self.cfg['date_separator'])
        if calculate_from_due_date:
            new_due = datetime.date(int(_year), int(_month), int(_day))
        else:
            new_due = datetime.datetime.now()
        if rec_period == self.cfg['month_symbol']:
            new_due += relativedelta(months=rec)
        elif rec_period == self.cfg['year_symbol']:
            new_due += relativedelta(years=rec)
        else:
            new_due += relativedelta(days=rec)
        updated_periodic_task = (re.sub(self.cfg['due_prop']
                                 + r'\d{4}-\d{2}-\d{2}',
                                 self.cfg['due_prop']
                                 + new_due.strftime("%Y-%m-%d"),
                                 periodic_task))
        return updated_periodic_task

    def props_in_word(self, word):
        """Check if a property definition is contained in `word`."""

        if (self.cfg['due_prop'] in word
                or self.cfg['dur_prop'] in word
                or self.cfg['rec_prop'] in word):
            return True
        return False

    def save_session_settings(self):
        x = self._view.x()
        y = self._view.y()
        w = self._view.width()
        h = self._view.height()
        self.config.set('USER', 'x_coord', '10')
        self.config.set('USER', 'y_coord', '10')
        self.config.set('USER', 'width_ratio', '0.6')
        self.config.set('USER', 'height_ratio', '0.6')
        # TODO Rename settings_file to config_file
        with open(self.config_file, 'w') as config_file:
            self.config.write(config_file, False)

    def word_has_active_task_prefix(self, word):
        if (len(word) == 1
                and word[0] in self.cfg['active_task_prefixes'].split('\n')):
            return True
        return False

    def word_has_reserved_word_prefix(self, word):
        if (word
                and word[0] in self.cfg['reserved_word_prefixes'].split('\n')):
            return True
        return False
