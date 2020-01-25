import configparser


class Config:
    def __init__(self, configuration_ini_file):
        self.config = configparser.ConfigParser(
                interpolation=configparser.ExtendedInterpolation())
        self.config.read(configuration_ini_file)
        self.cfg = self.config['USER']

        self.cfg['space'] = self.cfg['space'][1]
        self.cfg['active_task_prefixes'] = \
            self.cfg['active_task_prefixes'].split('\n')
        self.cfg['tokens_in_sorting_order'] = \
            self.cfg['tokens_in_sorting_order'].split('\n')
        self.cfg['tab_order'] = self.cfg['tab_order'].split('\n')
        self.cfg['portfolio_files'] = self.cfg['portfolio_files'].split('\n')
        if self.cfg['newline'] == 'linux':
            self.cfg['newline'] = '\n'
        else:
            self.cfg['newline'] = '\r\n'
