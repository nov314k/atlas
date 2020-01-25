import configparser
import unittest

from json_settings import JsonSettings


class ConfigParserTest(unittest.TestCase):
    
    # atlas_settings_file
    def test_atlas_settings_file(self):
        self.assertEqual(self.js.settings['atlas_settings_file'], self.cfg['atlas_settings_file'])
    
    # atlas_session_file
    def test_atlas_session_file(self):
       self.assertEqual(self.js.settings['atlas_session_file'], self.cfg['atlas_session_file'])
   
    # portfolio_base_dir
    def test_portfolio_base_dir(self):
        self.assertEqual(self.js.settings['portfolio_base_dir'], self.cfg['portfolio_base_dir'])
 
    # portfolio_files
    def test_portfolio_files(self):
        self.assertEqual(self.js.settings['portfolio_files'], self.cfg['portfolio_files'].split('\n'))

    # portfolio_log_file
    def test_portfolio_log_file(self):
        self.assertEqual(self.js.settings['portfolio_log_file'], self.cfg['portfolio_log_file'])
 
    # earned_times_file
    def test_earned_times_file(self):
        self.assertEqual(self.js.settings['earned_times_file'], self.cfg['earned_times_file'])

    # backup_dir
    def test_backup_dir(self):
        self.assertEqual(self.js.settings['backup_dir'], self.cfg['backup_dir'])
 
    # daily_files_archive_dir
    def test_daily_files_archive_dir(self):
        self.assertEqual(self.js.settings['daily_files_archive_dir'], self.cfg['daily_files_archive_dir'])

    # daily_file
    def test_daily_file(self):
        self.assertEqual(self.js.settings['daily_file'], self.cfg['daily_file'])

    # booked_file
    def test_booked_file(self):
        self.assertEqual(self.js.settings['booked_file'], self.cfg['booked_file'])

    # periodic_file
    def test_periodic_file(self):
        self.assertEqual(self.js.settings['periodic_file'], self.cfg['periodic_file'])

    # shlist_file
    def test_shlist_file(self):
        self.assertEqual(self.js.settings['shlist_file'], self.cfg['shlist_file'])

    # today_file
    def test_today_file(self):
        self.assertEqual(self.js.settings['today_file'], self.cfg['today_file'])

    # tab_order
    def test_tab_order(self):
        self.assertEqual(self.js.settings['tab_order'], self.cfg['tab_order'].split('\n'))

    # tokens_in_sorting_order
    def test_tokens_in_sorting_order(self):
        self.assertEqual(self.js.settings['tokens_in_sorting_order'], self.cfg['tokens_in_sorting_order'].split('\n'))

    # space
    def test_space(self):
        self.assertEqual(self.js.settings['space'], self.cfg['space'][1])

    # heading_prefix
    def test_heading_prefix(self):
        self.assertEqual(self.js.settings['heading_prefix'], self.cfg['heading_prefix'])

    # ttl_heading
    def test_ttl_heading(self):
        self.assertEqual(self.js.settings['ttl_heading'], self.cfg['ttl_heading'])

    # incoming_heading
    def test_incoming_heading(self):
        self.assertEqual(self.js.settings['incoming_heading'], self.cfg['incoming_heading'])

    # tasks_proposed_heading
    def test_tasks_proposed_heading(self):
        self.assertEqual(self.js.settings['tasks_proposed_heading'], self.cfg['tasks_proposed_heading'])

    # tasks_done_heading
    def test_tasks_done_heading(self):
        self.assertEqual(self.js.settings['tasks_done_heading'], self.cfg['tasks_done_heading'])

    # the_end_heading
    def test_the_end_heading(self):
        self.assertEqual(self.js.settings['the_end_heading'], self.cfg['the_end_heading'])

    # special_heading_suffix
    def test_special_heading_suffix(self):
        self.assertEqual(self.js.settings['special_heading_suffix'], self.cfg['special_heading_suffix'])

    # due_prop
    def test_due_prop(self):
        self.assertEqual(self.js.settings['due_prop'], self.cfg['due_prop'])

    # dur_prop
    def test_dur_prop(self):
        self.assertEqual(self.js.settings['dur_prop'], self.cfg['dur_prop'])

    # rec_prop
    def test_rec_prop(self):
        self.assertEqual(self.js.settings['rec_prop'], self.cfg['rec_prop'])

    # daily_rec_prop_val
    def test_daily_rec_prop_val(self):
        self.assertEqual(self.js.settings['daily_rec_prop_val'], self.cfg['daily_rec_prop_val'])

    # tag_prefix
    def test_tag_prefix(self):
        self.assertEqual(self.js.settings['tag_prefix'], self.cfg['tag_prefix'])

    # work_tag
    def test_work_tag(self):
        self.assertEqual(self.js.settings['work_tag'], self.cfg['work_tag'])

    # incoming_tag
    def test_incoming_tag(self):
        self.assertEqual(self.js.settings['incoming_tag'], self.cfg['incoming_tag'])

    # cat_prefix
    def test_cat_prefix(self):
        self.assertEqual(self.js.settings['cat_prefix'], self.cfg['cat_prefix'])

    # shlist_cat
    def test_shlist_cat(self):
        self.assertEqual(self.js.settings['shlist_cat'], self.cfg['shlist_cat'])

    # top_task_prefix
    def test_top_task_prefix(self):
        self.assertEqual(self.js.settings['top_task_prefix'], self.cfg['top_task_prefix'])

    # open_task_prefix
    def test_open_task_prefix(self):
        self.assertEqual(self.js.settings['open_task_prefix'], self.cfg['open_task_prefix'])

    # done_task_prefix
    def test_done_task_prefix(self):
        self.assertEqual(self.js.settings['done_task_prefix'], self.cfg['done_task_prefix'])

    # info_task_prefix
    def test_info_task_prefix(self):
        self.assertEqual(self.js.settings['info_task_prefix'], self.cfg['info_task_prefix'])

    # paused_task_prefix
    def test_paused_task_prefix(self):
        self.assertEqual(self.js.settings['paused_task_prefix'], self.cfg['paused_task_prefix'])

    # for_rescheduling_task_prefix
    def test_for_rescheduling_task_prefix(self):
        self.assertEqual(self.js.settings['for_rescheduling_task_prefix'], self.cfg['for_rescheduling_task_prefix'])

    # rescheduled_periodic_task_prefix
    def test_rescheduled_periodic_task_prefix(self):
        self.assertEqual(self.js.settings['rescheduled_periodic_task_prefix'], self.cfg['rescheduled_periodic_task_prefix'])

    # day_symbol
    def test_day_symbol(self):
        self.assertEqual(self.js.settings['day_symbol'], self.cfg['day_symbol'])

    # month_symbol
    def test_month_symbol(self):
        self.assertEqual(self.js.settings['month_symbol'], self.cfg['month_symbol'])

    # year_symbol
    def test_year_symbol(self):
        self.assertEqual(self.js.settings['year_symbol'], self.cfg['year_symbol'])

    # date_separator
    def test_date_separator(self):
        self.assertEqual(self.js.settings['date_separator'], self.cfg['date_separator'])

    # time_separator
    def test_time_separator(self):
        self.assertEqual(self.js.settings['time_separator'], self.cfg['time_separator'])

    # log_entry_prefix
    def test_log_entry_prefix(self):
        self.assertEqual(self.js.settings['log_entry_prefix'], self.cfg['log_entry_prefix'])

    # log_line_length
    def test_log_line_length(self):
        self.assertEqual(self.js.settings['log_line_length'], self.cfg.getint('log_line_length'))

    # earned_time_balance_form
    def test_earned_time_balance_form(self):
        self.assertEqual(self.js.settings['earned_time_balance_form'], self.cfg['earned_time_balance_form'])

    # atlas_files_extension
    def test_atlas_files_extension(self):
        self.assertEqual(self.js.settings['atlas_files_extension'], self.cfg['atlas_files_extension'])

    # get_data_from_calendars
    def test_get_data_from_calendars(self):
        self.assertEqual(self.js.settings['get_data_from_calendars'], self.cfg.getboolean('get_data_from_calendars'))

    # active_task_prefixes
    def test_active_task_prefixes(self):
        self.assertEqual(self.js.settings['active_task_prefixes'], self.cfg['active_task_prefixes'].split('\n'))

    # reserved_word_prefixes
    def test_reserved_word_prefixes(self):
        self.assertEqual(self.js.settings['reserved_word_prefixes'], self.cfg['reserved_word_prefixes'].split('\n'))

    # Utility functions
    def setUp(self):
        self.js = JsonSettings()
        self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self.config.read('config_file.ini')
        self.cfg = self.config['USER']

if __name__ == '__main__':
    unittest.main()
