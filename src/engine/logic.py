"""Implement Atlas logic.

Copyright notice
----------------
Copyright (C) 2019, 2020 Novak Petrovic
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
import engine.prepare_todays_tasks


def sort_tasks(tasks, tags_in_sorting_order):
    """Function docstring."""

    sorted_tasks = []
    for tag in tags_in_sorting_order:
        for task in tasks:
            if tag in task:
                sorted_tasks.append(task)
    return sorted_tasks


class Model:
    """Atlas model: all core functionality (commands)."""

    def __init__(self, config, view):
        """Initiates Editor instance variables.


        Parameters
        ----------
        config
            User configuration settings.

        """

        self.current_path = ''
        self.cfg = config.cfg
        if self.cfg['newline'] == 'linux':
            self.c_newline = '\n'
        else:
            self.c_newline = '\r\n'
        self.c_active_task_prefixes = self.cfg['cfg_active_task_prefixes']
        self.c_portfolio_files = self.cfg['cfg_portfolio_files']
        self._view = view
        # self.read_settings_file(self.config_file)

    # ~ def setup(self):
        # ~ """Function docstring."""

        # ~ self.setup_menu()
        # ~ self.open_portfolio()
    
    # ~ def get_tab(self, path):
        # ~ """Function docstring."""

        # ~ normalised_path = os.path.normcase(os.path.abspath(path))
        # ~ for tab in self._view.widgets:
            # ~ if tab.path:
                # ~ tab_path = os.path.normcase(os.path.abspath(tab.path))
                # ~ if tab_path == normalised_path:
                    # ~ self._view.focus_tab(tab)
                    # ~ return tab
        # ~ return self._view.current_tab

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

    def mark_task_done(self, tab):
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

#        tab = self._view.current_tab
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
                and current_task[0] not in self.c_active_task_prefixes):
            return
        contents = self.mark_ordinary_task_done(tab)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.cfg['encoding']))
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
        tasks = tab.text().split(self.c_newline)
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
            contents += task + self.c_newline
        contents = contents.rstrip(self.c_newline)
        return contents

    def mark_done_at_origin(self, task):
        """Function docstring."""

        if (len(task) < 1
                or task[0] not in self.c_active_task_prefixes
                or self.cfg['daily_rec_prop_val'] in task):
            return
        idx = -1
        tasks = []
        tab_idx = -1
        task_found = False
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path in self.c_portfolio_files:
                tasks = self._view.tabs.widget(i).text().split(self.c_newline)
                in_ttl = False
                for j, _ in enumerate(tasks):
                    if tasks[j]:
                        if (tasks[j][0] == self.cfg['heading_prefix']
                                and self.cfg['ttl_heading'] in tasks[j]):
                            in_ttl = True
                        elif tasks[j][0] == self.cfg['heading_prefix']:
                            in_ttl = False
                        if (tasks[j][0] in self.c_active_task_prefixes
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
            contents += task_ + self.c_newline
        contents = contents.rstrip(self.c_newline)
        if tab_idx > -1:
            self._view.tabs.setCurrentIndex(tab_idx)
            tab = self._view.tabs.widget(tab_idx)
            tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.cfg['encoding']))

    def mark_task_for_rescheduling(self, mark_rescheduled_periodic_task=False):
        """Function docstring."""

        now = datetime.datetime.now()
        tab = self._view.current_tab
        first_visible_line = tab.firstVisibleLine()
        tasks = tab.text().split(self.c_newline)
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
            contents += task + self.c_newline
        contents = contents.rstrip(self.c_newline)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.cfg['encoding']))
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
                or task[0] not in self.c_active_task_prefixes
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
            lines = current_tab.text().split(self.c_newline)
            extra_line_before = ''
            extra_line_after = ''
            # If active tab is a portfolio file
            if current_tab.path in self.c_portfolio_files:
                # TODO Add a suitable message for why we're returning
                if task_finished:
                    return
                ordering_string = self.cfg['heading_prefix'] + \
                    self.cfg['space'][1]
                ordering_string += self.cfg['incoming_heading']
                extra_line_before = self.c_newline
                extra_line_after = ''
            # TODO Check if active tab is a daily file (currently assumed!)
            else:
                lines = lines[:-1]
                ordering_string = self.cfg['heading_prefix'] + \
                    self.cfg['space'][1]
                ordering_string += self.cfg['tasks_proposed_heading']
                extra_line_before = self.c_newline
                extra_line_after = ''
                if task_finished:
                    extra_line_before = ''
                    extra_line_after = self.c_newline
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
                contents += line + self.c_newline
                if ordering_string in line and not task_finished:
                    contents += taux
            if task_finished:
                contents += taux + self.c_newline
            contents = contents.rstrip(self.c_newline)
            # Send contents to tab and save tab to file
            current_tab.SendScintilla(
                current_tab.SCI_SETTEXT, contents.encode(self.encoding))
            # self._view.save_file(current_tab)

    def tag_current_line(self):
        """Function docstring."""

        current_tab = self._view.current_tab
        first_visible_line = current_tab.firstVisibleLine()
        tag = self.cfg['tag_prefix'] + current_tab.label.split('.')[0]
        if FILE_CHANGED_ASTERISK in tag:
            tag = tag[:-2]
        lines = current_tab.text().split(self.c_newline)
        row = current_tab.getCursorPosition()[0]
        col = 0
        contents = ""
        for i, _ in enumerate(lines):
            if (i == row
                    and lines[i]
                    and lines[i][0] in self.c_active_task_prefixes
                    and tag not in lines[i]):
                line = lines[i] + self.cfg['space'][1] + tag
                contents += line + self.c_newline
                col = len(line)
            else:
                contents += lines[i] + self.c_newline
        contents = contents.rstrip(self.c_newline)
        current_tab.SendScintilla(
            current_tab.SCI_SETTEXT, contents.encode(ENCODING))
        current_tab.setFirstVisibleLine(first_visible_line)
        current_tab.setCursorPosition(row, col)
        self._view.save_file(current_tab)

    def toggle_tt(self):
        """Function docstring."""

        tab = self._view.current_tab
        first_visible_line = tab.firstVisibleLine()
        lines = tab.text().split(self.c_newline)
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
            contents += new_lines[i] + self.c_newline
        contents = contents.rstrip(self.c_newline)
        tab.SendScintilla(
            tab.SCI_SETTEXT, contents.encode(ENCODING))
        tab.setFirstVisibleLine(first_visible_line)
        tab.setCursorPosition(row, col - 1)
        self._view.save_file(tab)

    def generate_ttl(self, tab=None):
        """Generate Top Tasks List (TTL) for the current file (tab)."""

        if not tab:
            tab = self._view.current_tab
        tasks_aux = tab.text().split(self.c_newline)
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
            contents += tasks[i] + self.c_newline
        contents = contents.rstrip(self.c_newline)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.cfg['encoding']))
        # self._view.save_file(tab.path, tab)

    def generate_ttls(self):
        """Generate Top Tasks Lists (TTLs) for all portfolio files."""

        for widget in self._view.widgets:
            current_tab_index = self._view.tabs.indexOf(widget)
            self._view.tabs.setCurrentIndex(current_tab_index)
            if widget.path in self.c_portfolio_files:
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
                self.cfg['atlas_config_file'])
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
        # self.open_file(self.cfg['portfolio_base_dir'] + file_name)

    def analyse_tasks(self):
        """Function docstring."""

        tab = self._view.current_tab
        tasks_aux = tab.text().split(self.c_newline)
        tasks = []
        total_duration = 0
        work_duration = 0
        earned_duration = 0
        work_earned_duration = 0
        for task in tasks_aux:
            if task:
                task = re.sub(r'\d{2}:\d{2}' + self.cfg['space'][1], "", task)
                if task[0] in self.c_active_task_prefixes:
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
            contents += tasks[i] + self.c_newline
        contents = contents.rstrip(self.c_newline)
        tab.SendScintilla(tab.SCI_SETTEXT, contents.encode(self.encoding))

    def schedule_tasks(self):
        """Function docstring."""

        tab = self._view.current_tab
        tasks = tab.text().split(self.c_newline)
        start_time = datetime.datetime.now()
        scheduled_tasks = []
        for task in tasks:
            if task:
                task = re.sub(r'\d{2}:\d{2}' + self.cfg['space'][1], "", task)
                if task[0] in self.c_active_task_prefixes:
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
            contents += task + self.c_newline
        contents = contents.rstrip(self.c_newline)
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
        tasks = ctab.text().split(self.c_newline)
        for task in tasks:
            if self.cfg['earned_time_balance_form'] in task:
                extract = file_name + self.cfg['space'][1] + task + self.c_newline
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
                lines = log_tab.text().split(self.c_newline)
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
                contents += log_entry + self.c_newline + NEWLINE + log_tab.text()
                log_tab.SendScintilla(
                    log_tab.SCI_SETTEXT, contents.encode(ENCODING))
                self.save_file(log_tab)
                self._view.tabs.setCurrentIndex(current_tab_index)
        else:
            return

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
        tasks = tab.text().split(self.c_newline)
        contents = ""
        for task in sorted(tasks):
            if len(task) > 0:
                contents += task + self.c_newline
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
            if widget.path in self.c_portfolio_files:
                lines = widget.text().split(self.c_newline)
                for line in lines:
                    if (self.cfg['daily_rec_prop_val'] in line
                            and line[0] in self.c_active_task_prefixes):
                        daily_tasks.append(line)
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path == self.cfg['daily_file']:
                daily_tab_index = i
        contents = ""
        for i, _ in enumerate(daily_tasks):
            contents += daily_tasks[i] + self.c_newline
        contents = contents.rstrip(self.c_newline)
        self._view.tabs.setCurrentIndex(daily_tab_index)
        daily_tab = self._view.tabs.widget(daily_tab_index)
        daily_tab.SendScintilla(daily_tab.SCI_SETTEXT,
                                contents.encode(self.cfg['encoding']))
        # self.save_file(daily_tab.path, daily_tab)
        self._view.tabs.setCurrentIndex(current_tab_index)

    def extract_booked(self):
        """Extract to file tasks with the due-date property defined."""

        current_tab = self._view.current_tab
        current_tab_index = self._view.tabs.indexOf(current_tab)
        booked_tasks = []
        booked_tab_index = -1
        for widget in self._view.widgets:
            if widget.path in self.c_portfolio_files:
                lines = widget.text().split(self.c_newline)
                for line in lines:
                    if (self.cfg['due_prop'] in line
                            and self.cfg['rec_prop'] not in line
                            and line[0] in self.c_active_task_prefixes):
                        booked_tasks.append(line)
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path == self.cfg['booked_file']:
                booked_tab_index = i
        booked_tab = self._view.tabs.widget(booked_tab_index)
        contents = ""
        for i, _ in enumerate(booked_tasks):
            contents += booked_tasks[i] + self.c_newline
        contents = contents.rstrip(self.c_newline)
        self._view.tabs.setCurrentIndex(booked_tab_index)
        booked_tab = self._view.tabs.widget(booked_tab_index)
        booked_tab.SendScintilla(booked_tab.SCI_SETTEXT,
                                 contents.encode(self.cfg['encoding']))
        # self.save_file(booked_tab.path, booked_tab)
        self._view.tabs.setCurrentIndex(current_tab_index)

    def extract_periodic(self):
        """Extract to file tasks with the periodic property defined."""

        current_tab = self._view.current_tab
        current_tab_index = self._view.tabs.indexOf(current_tab)
        periodic_tasks = []
        periodic_tab_index = -1
        for widget in self._view.widgets:
            if widget.path in self.c_portfolio_files:
                lines = widget.text().split(self.c_newline)
                for line in lines:
                    if (self.cfg['rec_prop'] in line
                            and self.cfg['daily_rec_prop_val'] not in line
                            and line[0] in self.c_active_task_prefixes):
                        periodic_tasks.append(line)
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path == self.cfg['periodic_file']:
                periodic_tab_index = i
        periodic_tab = self._view.tabs.widget(periodic_tab_index)
        contents = ""
        for i, _ in enumerate(periodic_tasks):
            contents += periodic_tasks[i] + self.c_newline
        contents = contents.rstrip(self.c_newline)
        self._view.tabs.setCurrentIndex(periodic_tab_index)
        periodic_tab = self._view.tabs.widget(periodic_tab_index)
        periodic_tab.SendScintilla(periodic_tab.SCI_SETTEXT,
                                   contents.encode(self.cfg['encoding']))
        # self.save_file(periodic_tab.path, periodic_tab)
        self._view.tabs.setCurrentIndex(current_tab_index)

    def extract_shlist(self):
        """Extract to file tasks with the shopping list category defined."""

        current_tab = self._view.current_tab
        current_tab_index = self._view.tabs.indexOf(current_tab)
        shlist_tasks = []
        shlist_tab_index = -1
        for widget in self._view.widgets:
            if widget.path in self.c_portfolio_files:
                lines = widget.text().split(self.c_newline)
                for line in lines:
                    if (self.cfg['shlist_cat'] in line
                            and line[0] in self.c_active_task_prefixes):
                        shlist_tasks.append(line)
        for i in range(self._view.tab_count):
            if self._view.tabs.widget(i).path == self.cfg['shlist_file']:
                shlist_tab_index = i
        print(shlist_tab_index)
        shlist_tab = self._view.tabs.widget(shlist_tab_index)
        contents = ""
        for i, _ in enumerate(shlist_tasks):
            contents += shlist_tasks[i] + self.c_newline
        contents = contents.rstrip(self.c_newline)
        self._view.tabs.setCurrentIndex(shlist_tab_index)
        shlist_tab = self._view.tabs.widget(shlist_tab_index)
        shlist_tab.SendScintilla(shlist_tab.SCI_SETTEXT,
                                 contents.encode(self.cfg['encoding']))
        # self._view.save_file(shlist_tab.path, shlist_tab)
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
            entry = (entry[:self.cfg.getint('log_line_length')]
                    + self.c_newline
                    + entry[self.cfg.getint('log_line_length'):])
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

    # ~ def save_session_settings(self):
        # ~ x = self._view.x()
        # ~ y = self._view.y()
        # ~ w = self._view.width()
        # ~ h = self._view.height()
        # ~ self.config.set('USER', 'x_coord', '10')
        # ~ self.config.set('USER', 'y_coord', '10')
        # ~ self.config.set('USER', 'width_ratio', '0.6')
        # ~ self.config.set('USER', 'height_ratio', '0.6')
        # ~ # TODO Rename settings_file to config_file
        # ~ with open(self.config_file, 'w') as config_file:
            # ~ self.config.write(config_file, False)

    def word_has_active_task_prefix(self, word):
        if (len(word) == 1
                and word[0] in self.c_active_task_prefixes):
            return True
        return False

    def word_has_reserved_word_prefix(self, word):
        if (word
                and word[0] in self.cfg['reserved_word_prefixes'].split('\n')):
            return True
        return False
