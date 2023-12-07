from typing import TYPE_CHECKING, Optional
import os
from io import BytesIO
from zipfile import ZipFile
import requests
import re

from dataclasses import dataclass

from src.Utils import SteamCMDNotInstalledException

if TYPE_CHECKING:
    from src.Utils import Config

@dataclass
class Game:
    name: str
    appid: str
    mod_folder_path: str

class SteamCMD:
    """
    SteamCMD class
    """
    def __init__(self, master_config: 'Config', game: Optional[Game]=None):
        """
        SteamCMD class init
        """
        self.config = master_config
        self.batch_size: int = int(self.config.get('DOWNLOADER', 'batch_count', fallback=5))
        
        self._steamcmd_installed: bool = False
        self.steamcmd_path: str = ''
        self.steamcmd_username: str = ''
        self.steamcmd_password: str = ''

        self.game: Optional[Game] = game if game else None
        # if the game is chosen, get the game info from config
        if self.game:
            self.appid = self.config.get(self.game.name, 'appid')
            self.mod_folder_path = self.config.get(self.game.name, 'mod_folder_path')
        else:
            self.appid = None
            self.mod_folder_path = None
        
        print(f'appid: {self.appid}')
        print(f'mod_folder_path: {self.mod_folder_path}')
        
        # check if steamcmd is installed
        self.check_for_steamcmd()

    @property
    def steamcmd_installed(self) -> bool:
        """
        Check if steamcmd is installed
        """
        return self._steamcmd_installed
    
    @steamcmd_installed.setter
    def steamcmd_installed(self, value: bool):
        """
        Set the steamcmd installed value
        """
        self._steamcmd_installed = value
    
    def check_for_steamcmd(self) -> bool:
        """
        Check if steamcmd is installed
        """
        if not self.steamcmd_path:
            try:
                self.steamcmd_path = self.config['DEFAULT']['steamcmd_path']
                if os.path.exists(self.steamcmd_path):
                    # self.steamcmd_installed = True
                    # return True
                    # TODO: Change this back
                    if os.path.exists(os.path.join(self.steamcmd_path, 'steamcmd.exe')):
                        self.steamcmd_installed = True
                        return True
            except KeyError:
                return False
        else:
            if os.path.exists(self.steamcmd_path):
                # self.steamcmd_installed = True
                # return True
                # TODO: Change this back
                if os.path.exists(os.path.join(self.steamcmd_path, 'steamcmd.exe')):
                    self.steamcmd_installed = True
                    return True
        return False
    
    def install_steamcmd(self, install_path=None):
        """
        Install steamcmd. If install_path is None, check the config for a steamcmd path, if that is None,
        install it in the current directory
        
        Parameters
        ----------
        install_path : str
            The path to install steamcmd to
            
        Returns
        -------
        success : bool
            Whether or not the installation was successful
        """
        # if the user specified a steamcmd path
        if install_path:
            self.steamcmd_path = install_path
        # else check if the user specified a steamcmd path in the config
        elif self.config['DEFAULT']['steamcmd_path']:
            try:
                self.steamcmd_path = self.config['DEFAULT']['steamcmd_path']
                if self.steamcmd_path.endswith('.exe'):
                    self.steamcmd_path = self.steamcmd_path.split('\\steamcmd.exe')[0]
            except KeyError:
                # if the user didn't specify a steamcmd path just install it in the current directory
                self.steamcmd_path = os.path.join(os.getcwd(), 'steamcmd')
        # else install it in the current directory
        else:
            self.steamcmd_path = os.path.join(os.getcwd(), 'steamcmd')
        
        # download steamcmd
        resp = requests.get(
                "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
            )
        ZipFile(BytesIO(resp.content)).extractall(self.steamcmd_path)

        # write the steamcmd path to the config
        self.config['DEFAULT']['steamcmd_path'] = self.steamcmd_path
        with open(self.config.config_file, 'w') as config_file:
            self.config.write(config_file)
        
        # confirm the installation
        if self.check_for_steamcmd():
            return True
        else:
            return False
    
    def download_mod_from_url(self, url: str):
        """
        Download a mod from a url

        Parameters
        ----------
        url : str
            The URL to download the mod from

        Returns
        -------
        success : bool
            Whether or not the download was successful
        """
        pass

    def get_mod_info_from_url(self, url: str):
        """
        Get the mod info from a url

        Parameters
        ----------
        url : str
            The URL to get the mod info from

        Returns
        -------
        mod_info : dict
            The mod info
        """
        tuple_list = []
        # if the url has the &search parameter, remove it
        if re.search(r'&search', url):
            url = url.split('&search')[0]

        # try to get the page
        try:
            x = requests.get(url)
        except Exception as e:
            print(e)
            return None
        
        # collection
        if re.search("SubscribeCollectionItem", x.text):
            dls = re.findall(r"SubscribeCollectionItem[\( ']+(\d+)[ ',]+(\d+)'", x.text)
            for wid, appid in dls:
                print(f'wid: {wid}, appid: {appid}')
                tuple_list.append((wid, appid))

        # workshop
        elif re.search("ShowAddToCollection", x.text):
            wid, appid = re.findall(r"ShowAddToCollection[\( ']+(\d+)[ ',]+(\d+)'", x.text)[0]
            print(f'wid: {wid}, appid: {appid}')
            tuple_list.append((wid, appid))

        else:
            print('No match')
            return None
        
        return tuple_list

    def download_mods_list(self, mod_list: list):
        """
        Download a list of mods

        Parameters
        ----------
        mod_list : list
            A list of mods to download

        Returns
        -------
        success : bool
            Whether or not the download was successful
        """
        for i in mod_list:
            print(self.get_mod_info_from_url(i))