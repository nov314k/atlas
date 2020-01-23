"""Atlas engine: logic and functionality.

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

import datetime
import logging
import os
import re
import shutil
from dateutil.relativedelta import relativedelta


def _read_file(file_path, single_string=False):
    with open(file_path, 'r') as file_path_:
        if single_string:
            lines = file_path_.read()
            # TODO Make both branches do same kind of trimming
            lines.rstrip()
        else:
            lines = file_path_.readlines()
            numof_lines_to_the_end = len(lines)
            # for idx, line in enumerate(lines):
            #    # TODO Fix this hard-coded constant
            #    if "# THE END #" in line:
            #        numof_lines_to_the_end = idx + 1
            lines = lines[:numof_lines_to_the_end]
    return lines

def _write_file(file_path, contents):
    with open(file_path, 'w') as file_path_:
        file_path_.write(contents)


class Engine:
    """Atlas model: all core functionality (commands)."""

    def __init__(self, config):
        """Initiates Editor instance variables."""

        self.current_path = ''
        self.cfg = config.cfg
        self.cfg_space = config.cfg_space
        self.cfg_newline = config.cfg_newline
        self.cfg_portfolio_files = config.cfg_portfolio_files
        self.cfg_active_task_prefixes = config.cfg_active_task_prefixes

    def _line_is_heading(self, line):
        if len(line) > 0 and line[0] == self.cfg['heading_prefix']:
            return True
        return False

    def _line_is_heading_ttl(self, line):
        if self._line_is_heading(line) and self.cfg['ttl_heading'] in line:
            return True
        return False

    def _line_is_heading_incoming(self, line):
        if self._line_is_heading(line) and self.cfg['incoming_heading'] in line:
            return True
        return False

    def _line_is_heading_task_group(self, line):
        if (self._line_is_heading(line)
                and not self._line_is_heading_ttl(line)
                and not self._line_is_heading_ttl(line)):
            return True
        return False

    def _line_is_task_basic(self, line):
        if (len(line) > 0
                and line[0] in self.cfg_active_task_prefixes
                and self.cfg['dur_prop'] in line
                and self.cfg['due_prop'] not in line
                and self.cfg['rec_prop'] not in line):
            return True
        return False

    def _line_is_task_tt(self, line):
        if (self._line_is_task_basic(line)
                and line[0] == self.cfg['top_task_prefix']):
            return True
        return False

    def _line_is_task_due(self, line):
        if (len(line) > 0
                and line[0] == self.cfg['open_task_prefix']
                and self.cfg['dur_prop'] in line
                and self.cfg['due_prop'] in line
                and self.cfg['rec_prop'] not in line):
            return True
        return False

    def _line_is_task_daily(self, line):
        if (len(line) > 0
                and line[0] == self.cfg['open_task_prefix']
                and self.cfg['dur_prop'] in line
                and self.cfg['due_prop'] not in line
                and self.cfg['daily_rec_prop_val'] in line):
            return True
        return False

    def _line_is_task_periodic(self, line):
        if (len(line) > 0
                and line[0] == self.cfg['open_task_prefix']
                and self.cfg['dur_prop'] in line
                and self.cfg['due_prop'] in line
                and self.cfg['rec_prop'] in line
                and self.cfg['daily_rec_prop_val'] not in line):
            return True
        return False

    def _line_is_task_any(self, line):
        if (self._line_is_task_basic(line)
                or self._line_is_task_tt(line)
                or self._line_is_task_due(line)
                or self._line_is_task_periodic(line)
                or self._line_is_task_daily(line)):
            return True
        return False
    def _line_is_task_shlist(self, line):
        if (len(line) > 0
                and line[0] == self.cfg['open_task_prefix']
                and self.cfg['dur_prop'] in line
                and self.cfg['shlist_cat'] in line):
            return True
        return False

    def _file_is_dtf(self, file_path):
        # TODO Fix assumption that folder separator is always /
        file_name_and_ext = file_path.split('/')[-1]
        file_name = file_name_and_ext.split('.')[0]
        if re.match(r'\d{8}', file_name):
            return True
        return False

    def eight_digit_date(self, day, month, year):
        edd = str(year)
        if month < 10:
            edd += "0"
        edd += str(month)
        if day < 10:
            edd += "0"
        edd += str(day)
        return edd

    def mark_ordinary_task_done(self, file_path, line_num):

        """Function docstring."""

        lines = _read_file(file_path)
        # TODO Check that the method is not called from the last line
        # TODO This should be done when reading the file -- ignore all
        #  trailing blank lines after # THE END #
        selected_task = lines[line_num]
        if not self._file_is_dtf(file_path):
            return
        if not self._line_is_task_any(selected_task):
            return
        del lines[line_num]
        now = datetime.datetime.now()
        taux = self.cfg_newline
        taux += self.cfg['done_task_prefix']
        taux += self.cfg_space + now.strftime("%Y-%m-%d")
        taux += self.cfg_space + selected_task
        lines.append(taux)
        contents = "".join(line for line in lines)
        _write_file(file_path, contents)
        self.mark_task_done_at_origin(selected_task)

    def mark_task_done_at_origin(self, task):
        """Function docstring."""

        for fpath in self.cfg_portfolio_files:
            lines = _read_file(fpath)
            in_ttl = False
            linum_found = -1
            task_found = False
            fpath_found = None
            for j, _ in enumerate(lines):
                if lines[j]:
                    if (lines[j][0] == self.cfg['heading_prefix']
                            and self.cfg['ttl_heading'] in lines[j]):
                        in_ttl = True
                    elif lines[j][0] == self.cfg['heading_prefix']:
                        in_ttl = False
                    if (lines[j][0] in self.cfg_active_task_prefixes
                            and self.get_task_text(lines[j]) in task
                            and not task_found
                            and not in_ttl):
                        linum_found = j
                        task_found = True
                        fpath_found = fpath
                        break
            if task_found:
                break
        if linum_found > -1:
            if self.cfg['rec_prop'] in lines[linum_found]:
                lines[linum_found] = self.update_due_date(lines[linum_found])
            else:
                lines[linum_found] = (self.cfg['done_task_prefix']
                                      + self.cfg_space + lines[linum_found][2:])
            contents = "".join(line for line in lines)
            _write_file(fpath_found, contents)
        return

    def mark_task_for_rescheduling(self, file_path, line_num,
                                   mark_as_rescheduled=False):
        """Function docstring."""

        now = datetime.datetime.now()
        lines = _read_file(file_path)
        selected_task = lines[line_num]
        # TODO Check that we're coming from DTF!
        if not self._line_is_task_periodic(selected_task):
            return
        del lines[line_num]
        marked_task = self.cfg['for_rescheduling_task_prefix']
        if mark_as_rescheduled:
             marked_task = self.cfg['rescheduled_periodic_task_prefix']
        marked_task += (self.cfg_space
                        + now.strftime("%Y-%m-%d")
                        + self.cfg_space
                        + selected_task)
        lines.append(marked_task)
        contents = "".join(line for line in lines)
        _write_file(file_path, contents)
        return contents

    def reschedule_periodic_task(self, file_path, line_num):
        """Function docstring."""

        lines = _read_file(file_path)
        selected_task = lines[line_num]
        del lines[line_num]
        selected_task = re.sub(r'\d{2}:\d{2}' + self.cfg_space,
                               "",
                               selected_task)
        if not self._line_is_task_periodic(selected_task):
            return
        self.mark_done_at_origin(task)
        self.mark_task_for_rescheduling(mark_as_rescheduled=True)

        # TODO Consider adding an option
        # to determine whether the user wants this done
        # self._analyse_tasks()
        # self._schedule_tasks()
        return

    def toggle_tt(self, file_path, line_num):
        """Docstring."""

        lines = _read_file(file_path)
        updated_lines = []
        for idx, line in enumerate(lines):
            if idx == line_num and self._line_is_task_basic(line):
                if self._line_is_task_tt(line):
                    updated_lines.append(self.cfg['open_task_prefix']
                                         + lines[idx][1:])
                else:
                    updated_lines.append(self.cfg['top_task_prefix']
                                         + lines[idx][1:])
            else:
                updated_lines.append(lines[idx])
        contents = "".join(line for line in updated_lines)
        _write_file(file_path, contents)

    def generate_ttl(self, file_path):
        """Generate Top Tasks List (TTL)"""

        lines = _read_file(file_path)
        processed_lines = []
        below_incoming_header = False
        below_task_group_header = False
        ttl_tasks = [self.cfg['heading_prefix'] + self.cfg_space + self.cfg[
            'ttl_heading'], self.cfg_newline, self.cfg_newline]
        for idx, line in enumerate(lines):
            if below_incoming_header:
                processed_lines.append(line)
            if below_task_group_header and self._line_is_task_tt(line):
                ttl_tasks.append(line)
            if self._line_is_heading_incoming(line):
                below_incoming_header = True
                processed_lines.append(line)
            if self._line_is_heading_task_group(line):
                below_task_group_header = True
        processed_lines = ttl_tasks + [self.cfg_newline] + processed_lines
        contents = "".join(line for line in processed_lines)
        _write_file(file_path, contents)

    def generate_ttls(self):
        for file_path in self.cfg_portfolio_files:
            self.generate_ttl(file_path)

    def extract_booked(self):
        due_tasks = []
        for file_path in self.cfg_portfolio_files:
            lines = _read_file(file_path)
            for line in lines:
                if self._line_is_task_due(line):
                    due_tasks.append(line)
        contents = "".join(line for line in due_tasks)
        _write_file(self.cfg['booked_file'], contents)

    def extract_daily(self):
        daily_tasks = []
        for file_path in self.cfg_portfolio_files:
            lines = _read_file(file_path)
            for line in lines:
                if self._line_is_task_daily(line):
                    daily_tasks.append(line)
        contents = "".join(line for line in daily_tasks)
        _write_file(self.cfg['daily_file'], contents)

    def extract_periodic(self):
        periodic_tasks = []
        for file_path in self.cfg_portfolio_files:
            lines = _read_file(file_path)
            for line in lines:
                if self._line_is_task_periodic(line):
                    periodic_tasks.append(line)
        contents = "".join(line for line in periodic_tasks)
        _write_file(self.cfg['periodic_file'], contents)

    def extract_shlist(self):
        shlist_tasks = []
        for file_path in self.cfg_portfolio_files:
            lines = _read_file(file_path)
            for line in lines:
                if self._line_is_task_shlist(line):
                    shlist_tasks.append(line)
        contents = "".join(line for line in shlist_tasks)
        _write_file(self.cfg['shlist_file'], contents)

    def extract_auxiliaries(self):
        self.extract_booked()
        self.extract_daily()
        self.extract_periodic()
        self.extract_shlist()

    def collect_tasks_for_date(self, day, month, year):
        tasks = []
        day_for_planning = datetime.datetime(year, month, day)
        # Add daily tasks
        daily_tasks = _read_file(self.cfg['daily_file'])
        for task in daily_tasks:
            tasks.append(task)
        # Add booked (due) tasks
        due_tasks = _read_file(self.cfg['booked_file'])
        for task in due_tasks:
            if self.get_task_due_date(task) <= day_for_planning:
                tasks.append(task)
        # Add periodic tasks
        periodic_tasks = _read_file(self.cfg['periodic_file'])
        for task in periodic_tasks:
            if self.get_task_due_date(task) <= day_for_planning:
                tasks.append(task)
        # Add top tasks
        for file_path in self.cfg_portfolio_files:
            lines = _read_file(file_path)
            for line in lines:
                if self._line_is_task_tt(line):
                    tasks.append(line)
        return tasks

    def order_tasks_for_date(self, tasks):
        ordered_tasks = []
        already_processed_tasks = []
        for token in self.cfg['tokens_in_sorting_order'].split('\n'):
            for task in tasks:
                if token in task and task not in already_processed_tasks:
                    ordered_tasks.append(task)
                    already_processed_tasks.append(task)
        return ordered_tasks

    def prepare_day_plan(self, day, month, year):
        self.generate_ttls()
        self.extract_auxiliaries()
        tasks_for_date = self.collect_tasks_for_date(day, month, year)
        ordered_tasks = self.order_tasks_for_date(tasks_for_date)
        with open(self.cfg['today_file'], 'w') as today_file_:
            print("# Daily task list", file=today_file_)
            for task in ordered_tasks:
                print(task[:-1], file=today_file_)
            print("# Tasks DONE", file=today_file_)
        file_name = self.eight_digit_date(day, month, year)
        file_name_n_ext = file_name + self.cfg['atlas_files_extension']
        shutil.copyfile(self.cfg['today_file'],
                        self.cfg['portfolio_base_dir'] + file_name_n_ext)

    def _move_daily_tasks_file(self):
        """In development. Do not use."""

        ctab = self._view.current_tab
        if not self.running_from_daily_tasks_file(ctab):
            return
        fnae = os.path.basename(ctab.path)
        ctab_idx = self._view.tabs.indexOf(ctab)
        self._view.tabs.removeTab(ctab_idx)
        shutil.move(
            self.cfg['portfolio_base_dir'] + fnae,
            self.cfg['daily_files_archive_dir'] + fnae)

    def _add_adhoc_task(self):
        """In development. Do not use."""

        result = self._view._show_add_adhoc_task_dialog()
        current_tab = self._view.current_tab
        if result:
            task_finished = result[3]
            # If incoming task is a work task, add work tag to existing tags
            if result[4]:
                result[2] += self.cfg_space + self.cfg['work_tag']
            lines = current_tab.text().split(self.c_newline)
            extra_line_before = ''
            extra_line_after = ''
            # If active tab is a portfolio file
            if current_tab.path in self.cfg_portfolio_files:
                # TODO Add a suitable message for why we're returning
                if task_finished:
                    return
                ordering_string = self.cfg['heading_prefix'] + \
                    self.cfg_space
                ordering_string += self.cfg['incoming_heading']
                extra_line_before = self.c_newline
                extra_line_after = ''
            # TODO Check if active tab is a daily file (currently assumed!)
            else:
                lines = lines[:-1]
                ordering_string = self.cfg['heading_prefix'] + \
                    self.cfg_space
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
            taux = extra_line_before + task_status_mark + self.cfg_space
            # Add task and duration
            taux += result[0] + self.cfg_space + \
                self.cfg['dur_prop'] + result[1]
            # Add tags
            taux += self.cfg_space + result[2] + extra_line_after
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

    def _tag_current_line(self):
        """In development. Do not use."""

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
                    and lines[i][0] in self.cfg_active_task_prefixes
                    and tag not in lines[i]):
                line = lines[i] + self.cfg_space + tag
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

    def _analyse_tasks(self):
        """In development. Do not use."""

        tab = self._view.current_tab
        tasks_aux = tab.text().split(self.c_newline)
        tasks = []
        total_duration = 0
        work_duration = 0
        earned_duration = 0
        work_earned_duration = 0
        for task in tasks_aux:
            if task:
                task = re.sub(r'\d{2}:\d{2}' + self.cfg_space, "", task)
                if task[0] in self.cfg_active_task_prefixes:
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
            f"{self.cfg['info_task_prefix'] + self.cfg_space}"
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

    def _schedule_tasks(self):
        """In development. Do not use."""

        tab = self._view.current_tab
        tasks = tab.text().split(self.c_newline)
        start_time = datetime.datetime.now()
        scheduled_tasks = []
        for task in tasks:
            if task:
                task = re.sub(r'\d{2}:\d{2}' + self.cfg_space, "", task)
                if task[0] in self.cfg_active_task_prefixes:
                    sts = f"{start_time.hour:02}:{start_time.minute:02}"
                    idx = 2 - 2
                    # Has the task already been schedulled?
                    if task[4] == ':':
                        idx = 10 - 2
                    new_task = sts + self.cfg_space + task[idx:]
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

    def _extract_earned_time(self):
        """In development. Do not use."""

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
                extract = file_name + self.cfg_space + task + self.c_newline
        with open(self.cfg['earned_times_file'], 'a') as file_:
            file_.write(extract)

    def _log_progress(self):
        """In development. Do not use."""

        log_entry = self._format_log_entry(self._view._show_log_progress_dialog())
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

    def _back_up(self):
        """In development. Do not use."""

        now = datetime.datetime.now()
        try:
            shutil.copytree(
                self.cfg['portfolio_base_dir'],
                self.cfg['backup_dir'] + now.strftime("%Y%m%d%H%M%S"))
        except shutil.Error as ex:
            logging.error("Directory not copied. Error: %s", ex)
        except OSError as ex:
            logging.error("Directory not copied. Error: %s", ex)

    def _sort_periodic_tasks(self):
        """In development. Do not use."""

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

    def _format_log_entry(self, entry):
        """In development. Do not use."""

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

        words = task.split(self.cfg_space)
        for word in words:
            if self.cfg['dur_prop'] in word:
                duration = int(word.split(self.cfg['time_separator'])[1])
        return int(duration)

    def get_task_text(self, task):
        words = task.split(self.cfg_space)
        task_text = ''
        for word in words:
            # Beware of special letters (and words beginning with them)
            if (self.word_has_active_task_prefix(word)
                    or self.props_in_word(word)
                    or self.word_has_reserved_word_prefix(word)):
                pass
            else:
                task_text += word + self.cfg_space
        return task_text.rstrip(self.cfg_space)

    def get_task_due_date(self, task):
        words = task.split(self.cfg_space)
        for word in words:
            if self.cfg['due_prop'] in word:
                datum = word.split(self.cfg['property_separator'])[1]
                year, month, day = datum.split(self.cfg['date_separator'])
        return datetime.datetime(int(year), int(month), int(day))

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
        words = periodic_task.split(self.cfg_space)
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

    def word_has_active_task_prefix(self, word):
        if (len(word) == 1
                and word[0] in self.cfg_active_task_prefixes):
            return True
        return False

    def word_has_reserved_word_prefix(self, word):
        if (word
                and word[0] in self.cfg['reserved_word_prefixes'].split('\n')):
            return True
        return False
