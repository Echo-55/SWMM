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
                    self.steamcmd_installed = True
                    return True
                    # TODO: Change this back
                    # if os.path.exists(os.path.join(self.steamcmd_path, 'steamcmd.exe')):
                    #     self.steamcmd_installed = True
                    #     return True
            except KeyError:
                return False
        else:
            if os.path.exists(self.steamcmd_path):
                self.steamcmd_installed = True
                return True
                # TODO: Change this back
                # if os.path.exists(os.path.join(self.steamcmd_path, 'steamcmd.exe')):
                #     self.steamcmd_installed = True
                #     return True
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
        # calculate batch size
        batch_size = self.batch_size
        # calculate number of batches
        num_batches = len(mod_list) // batch_size
        # calculate the remainder
        remainder = len(mod_list) % batch_size
        # if there is a remainder, add one to the number of batches
        if remainder:
            num_batches += 1

        # loop through the number of batches
        for i in range(num_batches):
            # calculate the start index
            start_index = i * batch_size
            # calculate the end index
            end_index = start_index + batch_size
            # get the batch
            batch = mod_list[start_index:end_index]
            # download the batch
            self.download_mods_batch(batch)

    def download_mods_batch(self, mod_list: list):
        """
        Download a batch of mods

        Parameters
        ----------
        mod_list : list
            A list of mods to download

        Returns
        -------
        success : bool
            Whether or not the download was successful
        """
        # if the game is not chosen
        if not self.game:
            raise ValueError('Game not chosen')
        # if the mod folder path is not chosen
        if not self.mod_folder_path:
            raise ValueError('Mod folder path not chosen')
        # if the steamcmd path is not chosen
        if not self.steamcmd_path:
            raise ValueError('SteamCMD path not chosen')
        # if steamcmd is not installed
        if not self.steamcmd_installed:
            # raise SteamCMDNotInstalledException(self.steamcmd_path)
            self.install_steamcmd(self.steamcmd_path)
        
        # create the steamcmd command
        steamcmd_command = f'steamcmd +login anonymous +workshop_download_item '
        # loop through the mods in the batch
        for mod in mod_list:
            # add the mod to the steamcmd command
            steamcmd_command += f'{self.appid} {mod} '
        # add the mod folder path to the steamcmd command
        steamcmd_command += f'+quit'

        print(f'steamcmd_command: {steamcmd_command}')
        
        # run the steamcmd command
        # os.system(steamcmd_command)