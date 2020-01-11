import configparser

class Configuration:
    def __init__(self, configuration_file):
            
            self.config = configparser.ConfigParser(
                    interpolation=configparser.ExtendedInterpolation())
            self.config.read(configuration_file)
            self.cfg = self.config['USER']
            self.active_task_prefixes = (
                    self.cfg['active_task_prefixes'].split('\n'))
            self.portfolio_files = self.cfg['portfolio_files'].split('\n')
