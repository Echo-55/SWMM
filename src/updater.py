from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from termcolor import cprint
import typing
import os
from datetime import datetime

from .Utils import RemovedFromSteamException

if typing.TYPE_CHECKING:
    from .Utils import Config

@dataclass
class Mod:
    """
        This class is responsible for storing mod information.
    """
    name: str
    version: str
    appid: str
    local_path: str
    local_modified_time_epoch: str
    url: str
    steam_created_time: str
    steam_modified_time: str



class ModUpdater:
    """
        This class is responsible for checking for mod updates as well as updating the mod.
    """
    def __init__(self, config_master: 'Config', mod_wid):
        self.config = config_master
        self.wid = mod_wid
        self.url = f'https://steamcommunity.com/sharedfiles/filedetails/?id={self.wid}'
        self.needs_update = False
        self.removed_from_steam = False

        self.steam_created_time_str = None
        self.steam_created_time_epoch = None
        self.steam_updated_time_str = None
        self.steam_updated_time_epoch = None
        
        self.local_modified_time_epoch = None

        self.get_mod_page()
        self.get_local_modified_time()
        
        self.needs_update = self.check_for_update()

    def __str__(self):
        return f"{self.mod_name} - {self.wid}"
    
    def get_mod_page(self):
        """
        This method is responsible for getting the mod info from steam.

        Args:
            None

        Returns:
            None
        """
        # get the mod info
        self.get = requests.get(self.url)
        self.content = self.get.text

        # make the soup
        soup = BeautifulSoup(self.content, 'html.parser')

        # the mod info we're after is in the div with class 'detailsStatRight'
        self.mod_name = soup.title.get_text().split("::")[1].strip()

        self.appid = soup.find_all('a', class_='apphub_sectionTab')[0]['href'].split('/')[-1]
        self.game_name = soup.find_all('div', class_='apphub_AppName ellipsis')[0].get_text().strip()

        self.mod_info = soup.find_all('div', class_='detailsStatRight')
        # if there's nothing in the mod_info list, the mod has been removed from steam
        if len(self.mod_info) == 0:
            self.removed_from_steam = True
            print(f"{self.mod_name} has been removed from Steam")
            return
            # TODO: Raise exception or not? I kinda plan to use this in a for loop, so it might be better to just return
            # raise RemovedFromSteamException(self.name)
        # if there's only two items in the mod_info list, the mod has never been updated
        if len(self.mod_info) == 2:
            self.steam_created_time_str = self.mod_info[1].get_text()
            
            self.steam_updated_time = None
        # if there's three items in the mod_info list, the mod has been updated
        if len(self.mod_info) == 3:
            self.steam_created_time_str = self.mod_info[1].get_text()
            self.steam_updated_time = self.mod_info[2].get_text()
            
        
        cprint(f'\nself.created: {self.steam_created_time_str}', 'yellow')
        cprint(f'self.updated: {self.steam_updated_time}', 'yellow')
        self.steam_created_time_epoch = self.convert_time_to_epoch(self.steam_created_time_str)
        print(f'self.created epoch: {self.steam_created_time_epoch}')
    
    def get_local_modified_time(self):
        """
            This method is responsible for getting the local modified time of the mod.
        """
        mod_folder = self.config.get(self.game_name, 'mod_folder_path')
        if not os.path.exists(mod_folder):
            raise FileNotFoundError(f'{mod_folder} does not exist')
        
        # TODO: Add support for mod names instead of just wids
        # mod_path = os.path.join(mod_folder, self.mod_name)
        mod_path = os.path.join(mod_folder, self.wid)

        if not os.path.exists(mod_path):
            raise FileNotFoundError(f'{mod_path} does not exist')
        
        self.local_modified_time_epoch = os.path.getmtime(mod_path)
        
        cprint(f'\nLocal modified time: {self.local_modified_time_epoch}', 'yellow')
        cprint(f'Steam updated time: {self.steam_updated_time}', 'yellow')
    
    def convert_time_to_epoch(self, time_str):
        """
            This method is responsible for converting the steam time string to epoch time.
        """
        # Jun 22, 2016 @ 4:54am
        format_ = '%b %d, %Y @ %I:%M%p'
        epoch_time = datetime.strptime(time_str, format_).timestamp()
        return epoch_time

    def check_for_update(self):
        """
            This method is responsible for checking if the mod needs to be updated.
        """
        if self.removed_from_steam:
            return False

        if self.steam_updated_time is None:
            return False
        
        if self.local_modified_time_epoch is None:
            return False
        
        # if self.local_modified_time_epoch < self.steam_updated_time:
        #     return True
        
        return False