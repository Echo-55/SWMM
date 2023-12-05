from typing import TYPE_CHECKING, Optional
import os
from io import BytesIO
from zipfile import ZipFile
import requests

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
        
        self.steamcmd_installed: bool = False
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
        
        self.check_for_steamcmd()
    
    def check_for_steamcmd(self):
        """
        Check if steamcmd is installed
        """
        if not self.steamcmd_path:
            try:
                self.steamcmd_path = self.config['DEFAULT']['steamcmd_path']
                if os.path.exists(self.steamcmd_path):
                    if os.path.exists(os.path.join(self.steamcmd_path, 'steamcmd.exe')):
                        self.steamcmd_installed = True
                        return True
            except KeyError:
                return False
        else:
            if os.path.exists(self.steamcmd_path):
                if os.path.exists(os.path.join(self.steamcmd_path, 'steamcmd.exe')):
                    self.steamcmd_installed = True
                    return True
    
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
            except KeyError:
                # if the user didn't specify a steamcmd path just install it in the current directory
                self.steamcmd_path = os.path.join(os.getcwd(), 'steamcmd')
            
        # download steamcmd
        resp = requests.get(
                "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
            )
        ZipFile(BytesIO(resp.content)).extractall(self.steamcmd_path)
        
        # confirm the installation
        if self.check_for_steamcmd():
            return True
        else:
            return False
    
    def download_mod(self, appid, mod_wid, mods_folder):
        """
        Download a mod
        """