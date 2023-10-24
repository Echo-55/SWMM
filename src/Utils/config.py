import os
from termcolor import cprint, colored

from configparser import ConfigParser

from src.Utils.utils import CONFIGFILE, MYCONFIGFILE

default_config = {
    'steamcmd_path': '',
    'steamcmd_username': '',
    'steamcmd_password': '',
}

updater_config = {
    'mod_folder_path': '',
    'mod_wids': '',
    'mod_names': '',
}

downloader_config = {
    'batch_count': '5'
}

class Config(ConfigParser):
    def __init__(self, myconfig=False):
        super().__init__()

        self['DEFAULT'] = default_config
        self['UPDATER'] = updater_config
        self['DOWNLOADER'] = downloader_config

        if myconfig:
            self.config_file = MYCONFIGFILE
        else:
            self.config_file = CONFIGFILE

        cprint(f'target_config: {self.config_file}', 'yellow')
        
        try: # try reading the config file
            self.read(self.config_file)
        except FileNotFoundError: # if it doesn't exist, create it
            with open(self.config_file, 'w') as configfile:
                configfile.write(default_config)
        
        self.check_config()

    def save(self):
        """
        Saves the config file.

        Args:
            None

        Returns:
            None
        """
        with open(self.config_file, 'w') as configfile:
            self.write(configfile)
        
        cprint(f'Config file: {configfile.name} saved', 'green')
    
    def check_config(self):
        """
        Checks the config file for missing values and adds them if they are missing.

        Args:
            None
            
        Returns:
            None
        """
        for key, value in default_config.items():
            if key not in self['DEFAULT']:
                self['DEFAULT'][key] = value
                cprint(f'Added {key} to config', 'yellow')
        
        for key, value in updater_config.items():
            if key not in self['UPDATER']:
                self['UPDATER'][key] = value
                cprint(f'Added {key} to config', 'yellow')
        
        for key, value in downloader_config.items():
            if key not in self['DOWNLOADER']:
                self['DOWNLOADER'][key] = value
                cprint(f'Added {key} to config', 'yellow')
        
        self.save()
    
    def get_game_list_from_config(self):
        """
        Gets a list of games from the config file.

        Args:
            None

        Returns:
            list: a list of games
        """
        skip_sections = ['DEFAULT', 'UPDATER']
        game_list = []
        for section in self.sections():
            if section not in skip_sections:
                game_list.append(section)
        return game_list