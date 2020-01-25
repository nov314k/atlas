"""Docstring."""

import configparser
import sys
import datetime
# from calfs.get_coming_events import get_coming_events


def prepare_todays_tasks(day, month, year, settings_file):
    """Docstring."""

    config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())
    config.read(settings_file)
    cfg = config['USER']

    portfolio_files = cfg['portfolio_files'].split('\n')
    daily_file = cfg['daily_file']
    booked_file = cfg['booked_file']
    periodic_file = cfg['periodic_file']
    today_file = cfg['today_file']
    tokens_in_sorting_order = cfg['tokens_in_sorting_order'].split('\n')
    heading_prefix = cfg['heading_prefix']
    ttl_heading = cfg['ttl_heading']
    cat_prefix = cfg['cat_prefix']
    done_task_prefix = cfg['done_task_prefix']
    # get_data_from_calendars = settings['get_data_from_calendars']
    # coming_events_file = cfg['coming_events_file']

    new_tasks = []

    date = datetime.date(year, month, day)
    today_str = "{:%Y-%m-%d}".format(date)

    def read_tasks_file(tasks_file):
        """Docstring."""

        with open(tasks_file, 'r') as taks_file_:
            tasks = taks_file_.readlines()
        return tasks

#    def add_daily_segment(tasks, segment):
#        """Docstring."""
#
#        for t in tasks:
#            if segment in t:
#                new_tasks.append(t[:len(t) - 1])

    def add_straightforward_tasks(tasks):
        """Docstring."""

        for task in tasks:
            new_tasks.append(task[:-1])

    def add_project_tasks(project_tasks):
        """Docstring."""

        in_ttl = False
        for task in project_tasks:
            if ttl_heading in task:
                in_ttl = True
            elif task[0] == heading_prefix:
                in_ttl = False
            elif in_ttl and len(task) > 1:
                new_tasks.append(task[:len(task) - 1])

    def sort_tasks(tasks):
        """Docstring."""

        sorted_tasks = []
        for token in tokens_in_sorting_order:
            for task in tasks:
                if (cat_prefix in token
                        and token in task
                        and task not in sorted_tasks):
                    sorted_tasks.append(task)
                elif (token in task
                        and task not in sorted_tasks
                        and cat_prefix not in task):
                    sorted_tasks.append(task)
        return sorted_tasks

    daily_tasks = read_tasks_file(daily_file)
    booked_events = read_tasks_file(booked_file)
    periodic_tasks = read_tasks_file(periodic_file)

    add_straightforward_tasks(daily_tasks)

    # if get_data_from_calendars:
    #    get_coming_events(year, month, day)
    #    coming_events = read_tasks_file(coming_events_file)
    #    add_project_tasks(coming_events)

    for portfolio_file in portfolio_files:
        add_project_tasks(read_tasks_file(portfolio_file))
    for task in booked_events:
        if task[6:6 + 10] <= today_str:
            new_tasks.append(task[:len(task) - 1])
    for task in periodic_tasks:
        if (task[0] != done_task_prefix
                and task[6:6 + 10] <= today_str):
            new_tasks.append(task[:len(task) - 1])

    sorted_tasks = sort_tasks(new_tasks)
    # ~ sorted_tasks = new_tasks

    with open(today_file, 'w') as today_f:
        print("# Tasks proposed for " + today_str, file=today_f)
        for task in sorted_tasks:
            print(task, file=today_f)
        print("# Tasks DONE on " + today_str, file=today_f)


if __name__ == '__main__':
    DAY = int(input("Preparing for day  : "))
    MONTH = int(input("Preparing for month: "))
    YEAR = int(input("Preparing for year : "))
    prepare_todays_tasks(DAY, MONTH, YEAR, sys.argv[1])
