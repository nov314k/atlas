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
        menu_actions['move_daily_tasks_file'] = self._model.move_daily_tasks_file
        # Task
        menu_actions['mark_task_done'] = self._view.mark_task_done
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

    def mark_task_done(self):
        self._model.mark_task_done(self._view.current_tab)
