import datetime
import os
import sys
from engine.engine import Engine as engine

def running_from_daily_tasks_file(tab):
    """Docstring."""

    file_name = os.path.basename(tab.path).split('.')[0]
    if not re.match(r'\d{8}', file_name):
        message = ("This command can only be run from a daily tasks file.")
        self._view.show_message(message)
        return False
    return True

class Driver:
    def __init__(self, config, view, model):
        self._view = view
        self._model = model
        self.cfg = config.cfg
        if self.cfg['newline'] == 'linux':
            self.c_newline = '\n'
        else:
            self.c_newline = '\r\n'
        self.su_dropdown_menus()
        self._view.portfolio_open()
        
    def su_dropdown_menus(self):
        """Set up the drop-down menu.

        All Atlas commands (functions) are shown in drop-down menus.

        """

        menu_actions = dict()
        # File
        menu_actions['new_file'] = self._view.file_new
        menu_actions['open_file'] = self._view.file_open
        menu_actions['save_file'] = self._view.file_save
        menu_actions['save_file_as'] = self._view.file_save_as
        menu_actions['save_file_all'] = self._view.file_save_all
        menu_actions['close_file'] = self._view.file_close
        menu_actions['quit'] = self._view.portfolio_quit
        # Move
        menu_actions['goto_tab_left'] = self._view.goto_tab_left
        menu_actions['goto_tab_right'] = self._view.goto_tab_right
        menu_actions['move_line_up'] = self._view.move_line_up
        menu_actions['move_line_down'] = self._view.move_line_down
        menu_actions['_move_daily_tasks_file'] = self._model._move_daily_tasks_file
        # Task
        menu_actions['mark_task_done'] = self._view.mark_task_done
        menu_actions['mark_task_for_rescheduling'] = \
            self._view.mark_task_for_rescheduling
        menu_actions['reschedule_periodic_task'] = \
            self._model.reschedule_periodic_task
        menu_actions['_add_adhoc_task'] = self._model._add_adhoc_task
        menu_actions['_tag_current_line'] = self._model._tag_current_line
        menu_actions['toggle_tt'] = self._view.toggle_tt
        # Lists
        menu_actions['generate_ttl'] = self._view.generate_ttl
        menu_actions['generate_ttls'] = self._view.generate_ttls
        menu_actions['extract_auxiliaries'] = self._view.extract_auxiliaries
        menu_actions['prepare_day_plan'] = self._view.prepare_day_plan
        menu_actions['_analyse_tasks'] = self._model._analyse_tasks
        menu_actions['_schedule_tasks'] = self._model._schedule_tasks
        menu_actions['_extract_earned_time'] = self._model._extract_earned_time
        # Logs
        menu_actions['_log_progress'] = self._model._log_progress
        # ~ menu_actions['log_expense'] = self._model.log_expense
        menu_actions['_back_up'] = self._model._back_up
        # Other
        menu_actions['_sort_periodic_tasks'] = self._model._sort_periodic_tasks
        menu_actions['extract_daily'] = self._model.extract_daily
        menu_actions['extract_booked'] = self._model.extract_booked
        menu_actions['extract_periodic'] = self._model.extract_periodic
        menu_actions['extract_shlist'] = self._model.extract_shlist
        self._view.setup_menu(menu_actions)

    def mark_task_done(self):
        self._model.mark_task_done(self._view.current_tab)
