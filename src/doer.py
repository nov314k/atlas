"""Atlas doer/model/engine: logic and functionality.

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


class Doer:
    """Atlas doer/model/engine: logic and functionality."""

    def __init__(self, config):
        """Doer initialization."""

        self.cfg = config.cfg

    # Core functionality

    def mark_task_done(self, file_path, line_num):
        """Mark any task done in daily tasks file and at origin.

        It can only be called from a daily tasks file. It works for all four
        types of tasks: basic, booked, periodic, and daily. There are some
        differences in the way in which different types of tasks are marked
        as done at origin. Origin simply means the task group file in which
        the task was defined.

        Illustratively: It adds 'x YYYY-MM-DD ' prefix to the task and moves
        to the end of the daily tasks file. It calls
        `mark_task_done_at_origin()` to do the rest of the work in a relevant
        task group file.

        """

        lines = self.read_file(file_path)
        selected_task = lines[line_num]
        if (not self.file_is_dtf(file_path)
                or not self.line_is_task_any(selected_task)):
            return
        del lines[line_num]
        now_ = datetime.datetime.now()
        done_task = (f"{self.cfg['done_task_prefix']}"
                     f"{self.cfg['space']}"
                     f"{now_.strftime('%Y-%m-%d')}"
                     f"{self.cfg['space']}"
                     f"{selected_task}")
        lines.append(done_task)
        self.write_file(file_path, lines)
        self.mark_task_done_at_origin(selected_task)

    def mark_task_done_at_origin(self, task):
        """Mark task as done in the task group file where it was defined.

        Searches the task group files to find where the task was defined. It
        stops looking after it finds the first occurrence. Searching is done
        on the basis of task directive. It only looks through tasks in the
        main body of the task group file (below TTL and INCOMING tasks). Search
        order is as defined in `cfg['portfolio_files']`. As opposed to
        marking a task done in a daily tasks file, where they are moved to
        the end of the file, it marks tasks done in-place, without changing
        the position of the task in the task group file.

        For basic and booked tasks it simply replaces existing prefix with
        the done task prefix, without adding the date of completion (as it is
        done on the daily tasks file). For periodic tasks, it updates the due
        date to the next due date, without changing the prefix (using the
        `task_update_due_date()` method. It does not modify daily tasks (as there is
        no point in doing that).

        TODO Make sure (for periodic tasks) new due date is after current date.

        """

        for file_path in self.cfg['portfolio_files']:
            lines = self.read_file(file_path)
            in_ttl = False
            task_found = False
            selected_row = -1
            selected_task = None
            selected_file_path = None
            for idx, line in enumerate(lines):
                if self.line_is_heading_ttl(line):
                    in_ttl = True
                elif self.line_is_heading(line):
                    in_ttl = False
                if (self.line_is_task_basic_due_periodic(line)
                        and self.get_task_definition(line) in task
                        and not task_found
                        and not in_ttl):
                    task_found = True
                    selected_row = idx
                    selected_task = line
                    selected_file_path = file_path
                    break
            if task_found:
                if self.line_is_task_periodic(selected_task):
                    lines[selected_row] = self.task_update_due_date(
                        lines[selected_row])
                else:
                    # NOTE `1:` removes old task prefix
                    lines[selected_row] = (f"{self.cfg['done_task_prefix']}"
                                           f"{lines[selected_row][1:]}")
            self.write_file(selected_file_path, lines)

    def mark_task_for_rescheduling(self, file_path, line_num,
                                   mark_as_rescheduled=False):
        """Mark task for rescheduling.

        It only works for periodic tasks, and it can only be called from a
        daily tasks file. `mark_as_rescheduled=True`, allows re-using this
        method when we are rescheduling a periodic tasks.

        Illustratively: It adds 'r' prefix and moves task to the end of the
        file. Instead of 'r', it adds 'R' in the case of
        `mark_as_rescheduled=True`.

        """

        now_ = datetime.datetime.now()
        lines = self.read_file(file_path)
        selected_task = lines[line_num]
        if (not self.file_is_dtf(file_path)
                or not self.line_is_task_periodic(selected_task)):
            return
        del lines[line_num]
        prefix = self.cfg['for_rescheduling_task_prefix']
        if mark_as_rescheduled:
            prefix = self.cfg['rescheduled_periodic_task_prefix']
        marked_task = (f"{prefix}"
                       f"{self.cfg['space']}"
                       f"{now_.strftime('%Y-%m-%d')}"
                       f"{self.cfg['space']}"
                       f"{selected_task}")
        lines.append(marked_task)
        self.write_file(file_path, lines)

    def reschedule_periodic_task(self, file_path, line_num):
        """Reschedule a periodic task.

        Updates the due date of a periodic task at its origin (task group
        file). It marks the task as having been rescheduled in the daily
        tasks file.

        """

        lines = self.read_file(file_path)
        selected_task = lines[line_num]
        del lines[line_num]
        if not self.line_is_task_periodic(selected_task):
            return
        self.mark_task_done_at_origin(selected_task)
        self.mark_task_for_rescheduling(mark_as_rescheduled=True)

    def toggle_tt(self, file_path, line_num):
        """Toggle the top task and open task prefixes.

        It only works for basic and top tasks.

        """

        lines = self.read_file(file_path)
        processed_lines = []
        for idx, line in enumerate(lines):
            if idx == line_num and self.line_is_task_basic(line):
                if self.line_is_task_tt(line):
                    processed_lines.append((f"{self.cfg['open_task_prefix']}"
                                            f"{lines[idx][1:]}"))
                else:
                    processed_lines.append((f"{self.cfg['top_task_prefix']}"
                                            f"{lines[idx][1:]}"))
            else:
                processed_lines.append(lines[idx])
        self.write_file(file_path, processed_lines)

    def generate_ttl(self, file_path):
        """Generate the top tasks list (TTL) for the given task group."""

        lines = self.read_file(file_path)
        processed_lines = []
        below_incoming_header = False
        below_task_group_header = False
        ttl_tasks = [(f"{self.cfg['heading_prefix']}" 
                      f"{self.cfg['space']}" 
                      f"{self.cfg['ttl_heading']}"),
                     self.cfg['newline'],
                     self.cfg['newline']]
        for idx, line in enumerate(lines):
            if below_incoming_header:
                processed_lines.append(line)
            if below_task_group_header and self.line_is_task_tt(line):
                ttl_tasks.append(line)
            if self.line_is_heading_incoming(line):
                below_incoming_header = True
                processed_lines.append(line)
            if self.line_is_heading_task_group(line):
                below_task_group_header = True
        processed_lines = ttl_tasks + [self.cfg['newline']] + processed_lines
        self.write_file(file_path, processed_lines)

    def generate_ttls(self):
        """Generate a top tasks list for each task group file in portfolio."""

        for file_path in self.cfg['portfolio_files']:
            self.generate_ttl(file_path)

    def extract_booked(self):
        """Extract booked tasks into their auxiliary file."""

        booked_tasks = []
        for file_path in self.cfg['portfolio_files']:
            lines = self.read_file(file_path)
            for line in lines:
                if self.line_is_task_booked(line):
                    booked_tasks.append(line)
        self.write_file(self.cfg['booked_file'], booked_tasks)

    def extract_daily(self):
        """Extract daily tasks into their auxiliary file."""

        daily_tasks = []
        for file_path in self.cfg['portfolio_files']:
            lines = self.read_file(file_path)
            for line in lines:
                if self.line_is_task_daily(line):
                    daily_tasks.append(line)
        self.write_file(self.cfg['daily_file'], daily_tasks)

    def extract_periodic(self):
        """Extract periodic tasks into their auxiliary file."""

        periodic_tasks = []
        for file_path in self.cfg['portfolio_files']:
            lines = self.read_file(file_path)
            for line in lines:
                if self.line_is_task_periodic(line):
                    periodic_tasks.append(line)
        self.write_file(self.cfg['periodic_file'], periodic_tasks)

    def extract_shlist(self):
        """Extract shlist tasks into their auxiliary file."""

        shlist_tasks = []
        for file_path in self.cfg['portfolio_files']:
            lines = self.read_file(file_path)
            for line in lines:
                if self.line_is_task_shlist(line):
                    shlist_tasks.append(line)
        self.write_file(self.cfg['shlist_file'], shlist_tasks)

    def extract_auxiliaries(self):
        """Generate all auxiliary files."""
        self.extract_booked()
        self.extract_daily()
        self.extract_periodic()
        self.extract_shlist()

    def collect_tasks_for_date(self, year, month, day):
        """Collect all tasks to be done on a given date.

        Tasks from each of the four task categories are gathered into a list.

        """

        tasks = []
        day_for_planning = datetime.datetime(year, month, day)

        # Add daily tasks
        daily_tasks = self.read_file(self.cfg['daily_file'])
        for task in daily_tasks:
            tasks.append(task)

        # Add booked (due) tasks
        due_tasks = self.read_file(self.cfg['booked_file'])
        for task in due_tasks:
            if self.get_task_due_value(task) <= day_for_planning:
                tasks.append(task)

        # Add periodic tasks
        periodic_tasks = self.read_file(self.cfg['periodic_file'])
        for task in periodic_tasks:
            if self.get_task_due_value(task) <= day_for_planning:
                tasks.append(task)

        # Add top tasks
        for file_path in self.cfg['portfolio_files']:
            lines = self.read_file(file_path)
            for line in lines:
                if self.line_is_task_tt(line):
                    tasks.append(line)
        return tasks

    def order_tasks_for_date(self, tasks):
        """Order collected tasks as per the configured sorting order.

        Once tasks are collected for a particular date using
        `collect_tasks_for_date()`, order (sort) them in the order defined
        in `cfg['tokens_in_sorting_order']`.

        """

        ordered_tasks = []
        already_processed_tasks = []
        for token in self.cfg['tokens_in_sorting_order']:
            for task in tasks:
                if token in task and task not in already_processed_tasks:
                    ordered_tasks.append(task)
                    already_processed_tasks.append(task)
        return ordered_tasks

    def prepare_daily_tasks_file(self, year, month, day):
        """Prepare daily tasks file for the given date.
        
        It generated fresh top tasks lists for each portfolio task group 
        file, and it extracts all auxiliary files anew.
        
        TODO Consider not saving to the "today" file (as in todo.txt)
        
        """

        self.generate_ttls()
        self.extract_auxiliaries()
        tasks_for_date = self.collect_tasks_for_date(year, month, day)
        ordered_tasks = self.order_tasks_for_date(tasks_for_date)
        with open(self.cfg['today_file'], 'w') as today_file_:
            print(self.cfg['daily_tasks_file_heading'], file=today_file_)
            for task in ordered_tasks:
                print(task.rstrip(self.cfg['newline']), file=today_file_)
            print(self.cfg['done_tasks_and_log_heading'], file=today_file_)
        file_name = f"{year}{month:02}{day:02}"
        file_name_n_ext = f"{file_name}{self.cfg['atlas_files_extension']}"
        file_path = f"{self.cfg['portfolio_base_dir']}{file_name_n_ext}"
        shutil.copyfile(self.cfg['today_file'], file_path)

    # Utilities

    def get_task_definition(self, task):
        """Get task directive from task definition."""

        words = task.split(self.cfg['space'])
        task_text = ''
        for word in words:
            # Beware of special letters (and words beginning with them)!
            if (self.word_has_active_task_prefix(word)
                    or self.word_has_property(word)
                    or self.word_has_reserved_word_prefix(word)):
                pass
            else:
                task_text += word + self.cfg['space']
        return task_text.rstrip(self.cfg['space'])

    def get_task_duration(self, task):
        """Get task duration from task definition."""

        words = task.split(self.cfg['space'])
        for word in words:
            if self.cfg['dur_prop'] in word:
                duration = int(word.split(self.cfg['time_separator'])[1])
                return int(duration)

    def get_task_due_value(self, task):
        """Get task due date from task definition."""

        words = task.split(self.cfg['space'])
        for word in words:
            if self.cfg['due_prop'] in word:
                datum = word.split(self.cfg['property_separator'])[1]
                year, month, day = datum.split(self.cfg['date_separator'])
                return datetime.datetime(int(year), int(month), int(day))

    def get_task_rec_value(self, task):
        words = task.split(self.cfg['space'])
        for word in words:
            if self.cfg['rec_prop'] in word:
                rec_value = word.split(self.cfg['property_separator'])[1]
                return rec_value

    def task_update_due_date(self, task):
        """Update the due date of a periodic task."""

        due_value = self.get_task_due_value(task)
        rec_value = self.get_task_rec_value(task)
        if self.cfg['rec_prop_absolute_sign'] in rec_value:
            rec_period = rec_value[-1]
            rec_value = rec_value[1:-1]
        else:
            rec_period = rec_value[-1]
            rec_value = rec_value[0:-1]
            due_value = datetime.datetime.now()
        if rec_period == self.cfg['month_symbol']:
            due_value += relativedelta(months=rec_value)
        elif rec_period == self.cfg['year_symbol']:
            due_value += relativedelta(years=rec_value)
        else:
            due_value += relativedelta(days=rec_value)
        return (re.sub(self.cfg['due_prop'] + r'\d{4}-\d{2}-\d{2}',
                       self.cfg['due_prop'] + due_value.strftime("%Y-%m-%d"),
                       task))

    def minutes_to_hh_mm(self, mins):
        """Convert minutes to zero-padded two-digit hours and minutes."""

        hours_ = mins // 60
        mins_ = mins % 60
        return f"{hours_:02}{self.cfg['time_separator']}{mins_:02}"

    # Checkers

    def file_is_dtf(self, file_path):
        """Is file a daily tasks file?"""

        # TODO Fix assumption that folder separator is always /
        file_name_and_ext = file_path.split('/')[-1]
        file_name = file_name_and_ext.split('.')[0]
        if re.match(r'\d{8}', file_name):
            return True
        return False

    def line_is_heading(self, line):
        """Is line a heading?"""

        if len(line) > 0 and line[0] == self.cfg['heading_prefix']:
            return True
        return False

    def line_is_heading_ttl(self, line):
        """Is line a top tasks list (TTL) heading?"""

        if self.line_is_heading(line) and self.cfg['ttl_heading'] in line:
            return True
        return False

    def line_is_heading_incoming(self, line):
        """"Is line an INCOMING tasks heading?"""

        if self.line_is_heading(line) and self.cfg['incoming_heading'] in line:
            return True
        return False

    def line_is_heading_task_group(self, line):
        """Is line a task group heading?"""

        if (self.line_is_heading(line)
                and not self.line_is_heading_ttl(line)
                and not self.line_is_heading_ttl(line)):
            return True
        return False

    def line_is_task_basic(self, line):
        """Is line a basic task?"""

        if (len(line) > 0
                and line[0] in self.cfg['active_task_prefixes']
                and self.cfg['dur_prop'] in line
                and self.cfg['due_prop'] not in line
                and self.cfg['rec_prop'] not in line):
            return True
        return False

    def line_is_task_tt(self, line):
        """Is line a top task?"""

        if (self.line_is_task_basic(line)
                and line[0] == self.cfg['top_task_prefix']):
            return True
        return False

    def line_is_task_booked(self, line):
        """Is line a booked task?"""

        if (len(line) > 0
                and line[0] == self.cfg['open_task_prefix']
                and self.cfg['dur_prop'] in line
                and self.cfg['due_prop'] in line
                and self.cfg['rec_prop'] not in line):
            return True
        return False

    def line_is_task_periodic(self, line):
        """Is line a periodic task?"""

        if (len(line) > 0
                and line[0] == self.cfg['open_task_prefix']
                and self.cfg['dur_prop'] in line
                and self.cfg['due_prop'] in line
                and self.cfg['rec_prop'] in line
                and self.cfg['daily_rec_prop_val'] not in line):
            return True
        return False

    def line_is_task_daily(self, line):
        """Is line a daily task?"""

        if (len(line) > 0
                and line[0] == self.cfg['open_task_prefix']
                and self.cfg['dur_prop'] in line
                and self.cfg['due_prop'] not in line
                and self.cfg['daily_rec_prop_val'] in line):
            return True
        return False

    def line_is_task_basic_due_periodic(self, line):
        """Is line a basic, due, or a periodic task?"""

        if (self.line_is_task_basic(line)
                or self.line_is_task_booked(line)
                or self.line_is_task_periodic(line)):
            return True
        return False

    def line_is_task_any(self, line):
        """Is line a basic, due, periodic, or a daily task?"""
        if (self.line_is_task_basic(line)
                or self.line_is_task_tt(line)
                or self.line_is_task_booked(line)
                or self.line_is_task_periodic(line)
                or self.line_is_task_daily(line)):
            return True
        return False

    def line_is_task_shlist(self, line):
        """Is line a shopping list (shlist) task?"""

        if (len(line) > 0
                and line[0] == self.cfg['open_task_prefix']
                and self.cfg['dur_prop'] in line
                and self.cfg['shlist_cat'] in line):
            return True
        return False

    def word_has_property(self, word):
        """Is a property definition contained in word?"""

        if (self.cfg['due_prop'] in word
                or self.cfg['dur_prop'] in word
                or self.cfg['rec_prop'] in word):
            return True
        return False

    def word_has_active_task_prefix(self, word):
        """Does the word have an active task prefix?"""

        if (len(word) == 1
                and word[0] in self.cfg['active_task_prefixes']):
            return True
        return False

    def word_has_reserved_word_prefix(self, word):
        """Does the word have a reserved word prefix?"""

        if (len(word) > 0
                and word[0] in self.cfg['reserved_word_prefixes']):
            return True
        return False

    # Reader and writer

    def read_file(self, file_path, single_string=False):
        """Read file from disk, return contents as a single string or a list."""

        with open(file_path, 'r', encoding=self.cfg['encoding']) as file_path_:
            if single_string:
                lines = file_path_.read()
            else:
                lines = file_path_.readlines()
        return lines

    def write_file(self, file_path, lines):
        """Write list to file."""

        contents = "".join(line for line in lines)
        with open(file_path, 'w', encoding=self.cfg['encoding']) as file_path_:
            file_path_.write(contents)

    # Some experimental features, not for everyday use!

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
                result[2] += self.cfg['space'] + self.cfg['work_tag']
            lines = current_tab.text().split(self.cfg['newline'])
            extra_line_before = ''
            extra_line_after = ''
            # If active tab is a portfolio file
            if current_tab.path in self.cfg['portfolio_files']:
                # TODO Add a suitable message for why we're returning
                if task_finished:
                    return
                ordering_string = (self.cfg['heading_prefix']
                                   + self.cfg['space'])
                ordering_string += self.cfg['incoming_heading']
                extra_line_before = self.c_newline
                extra_line_after = ''
            # TODO Check if active tab is a daily file (currently assumed!)
            else:
                lines = lines[:-1]
                ordering_string = self.cfg['heading_prefix'] + \
                    self.cfg['space']
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
            taux = extra_line_before + task_status_mark + self.cfg['space']
            # Add task and duration
            taux += result[0] + self.cfg['space'] + \
                self.cfg['dur_prop'] + result[1]
            # Add tags
            taux += self.cfg['space'] + result[2] + extra_line_after
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
                    and lines[i][0] in self.cfg['active_task_prefixes']
                    and tag not in lines[i]):
                line = lines[i] + self.cfg['space'] + tag
                contents += line + self.cfg['newline']
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
                task = re.sub(r'\d{2}:\d{2}' + self.cfg['space'], "", task)
                if task[0] in self.cfg['active_task_prefixes']:
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
            f"{self.minutes_to_hh_mm(earned_duration)} "
            f"({self.minutes_to_hh_mm(work_earned_duration)})"
        )
        tasks.insert(0, statistic)
        statistic = (
            f"> Remaining tasks duration (work) = "
            f"{self.minutes_to_hh_mm(total_duration)} "
            f"({self.minutes_to_hh_mm(work_duration)})"
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

        now_ = datetime.datetime.now()
        try:
            shutil.copytree(
                self.cfg['portfolio_base_dir'],
                self.cfg['backup_dir'] + now_.strftime("%Y%m%d%H%M%S"))
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
                    + self.cfg['newline']
                    + entry[self.cfg.getint('log_line_length'):])
        return entry