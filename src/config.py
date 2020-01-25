import configparser
import json

class Config:
    def __init__(self, configuration_ini_file):
        self.config = configparser.ConfigParser(
                interpolation=configparser.ExtendedInterpolation())
        self.config.read(configuration_ini_file)

        # TODO Check whether this approach correctly handles default values
        # (or it just over-writes them with the latest one)
        self.cfg = dict()
        self.cfg['newline'] = '\n'
        for section in self.config:
            for item in self.config[section]:
                if item == 'win_newline' and self.config[section].getboolean(item):
                    self.cfg['newline'] = '\r\n'
                if item == 'space':
                    self.cfg[item] = self.config[section][item][1]
                elif (item == 'active_task_prefixes'
                        or item == 'portfolio_files'
                        or item == 'tab_order'
                        or item == 'tokens_in_sorting_order'):
                    self.cfg[item] = self.config[section][item].split(self.cfg['newline'])
                else:
                    self.cfg[item] = self.config[section][item]

