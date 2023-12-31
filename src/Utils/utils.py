from threading import Thread
from typing import TYPE_CHECKING, Optional
import os
from io import BytesIO
from zipfile import ZipFile
import requests
import re
import math
import subprocess
from PyQt6.QtWidgets import QMessageBox
import sys

from dataclasses import dataclass

from src.Utils import SteamCMDNotInstalledException

if TYPE_CHECKING:
    from downloader import ModDownloader

@dataclass
class Game:
    name: str
    appid: str
    mod_folder_path: str

class SteamCMD:
    """
    SteamCMD class
    """
    # def __init__(self, master_config: 'Config', game: Optional[Game]=None):
    def __init__(self, mod_downloader: 'ModDownloader'):
        """
        SteamCMD class init
        """
        self.config = mod_downloader.config
        self.batch_size: int = int(self.config.get('DOWNLOADER', 'batch_count', fallback=5))
        
        self._mod_downloader: 'ModDownloader' = mod_downloader
        self.downloader_tab = None

        self._steamcmd_installed: bool = False
        self.fresh_install: bool = False
        self.steamcmd_path: str = self.config.get('DEFAULT', 'steamcmd_path', fallback='')
        self.steamcmd_username: str = self.config.get('DEFAULT', 'steamcmd_username', fallback='')
        self.steamcmd_password: str = self.config.get('DEFAULT', 'steamcmd_password', fallback='')

        self.game: Optional[Game] = mod_downloader.game if mod_downloader.game else None
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
    
    def check_for_steamcmd(self):
        """
        Check if steamcmd is installed and also if it is a fresh installation
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
        return False
    
    def check_fresh_install(self):
        """
        Check if steamcmd is a fresh install
        """
        if os.path.exists(os.path.join(self.steamcmd_path, 'steamapps')):
            self.fresh_install = False
            return False
        else:
            self.fresh_install = True
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
            self.fresh_install = True if self.check_fresh_install() else False
            return True
        else:
            return False
    
    def update_steamcmd(self):
        """
        Update steamcmd. Useful for when steamcmd is first downloaded but not installed
        
        Returns
        -------
        success : bool
            Whether or not the update was successful
        """
        if self.steamcmd_installed:
            # run steamcmd with the update args
            args = [os.path.join(self.steamcmd_path, 'steamcmd.exe')]
            args.append('+login anonymous')
            args.append('+quit')
            self.run_steamcmd_threaded(args)
            return True
        else:
            raise SteamCMDNotInstalledException('SteamCMD is not installed')

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
            print(f'Error getting page: {e}')
            if self._mod_downloader.ui_running:
                self.add_text_to_console(f'Error getting page: {e}', color='red')
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
            if self._mod_downloader.ui_running:
                self.add_text_to_console('No match', color='red')
            return None
        
        return tuple_list

    def download_mods_list(self, mod_list: list):
        """
        Download a list of mods

        Parameters
        ----------
        mod_list : list
            A list of urls to download mods from

        Returns
        -------
        success : bool
            Whether or not the download was successful
        """
        # get the wids and appid for each of the mods
        download_list = []
        for url in mod_list:
            download_list.append(self.get_mod_info_from_url(url))
        
        dl_length = len(download_list)
        batch_limit = math.ceil(dl_length / self.batch_size)
        # get the number of batches
        if dl_length % self.batch_size == 0:
            batch_limit = dl_length // self.batch_size
        else:
            batch_limit = (dl_length // self.batch_size) + 1

        all_batches = []

        # download the mods in batches
        for i in range(batch_limit):
            # get the batch
            batch = download_list[i * self.batch_size : (i + 1) * self.batch_size]
            batch_count = len(batch)
            all_batches.append(batch)
            print(f'Batch {i + 1} of {batch_limit} ({batch_count} mods)')

            # build the args list
            args = [os.path.join(self.steamcmd_path, 'steamcmd.exe')]
            args.append('+login anonymous') # TODO: Add login
            # args.append(f'+force_install_dir {self.mod_folder_path}')

            for i in batch: # batch is a list of tuples
                for wid, appid in i: # i is a tuple
                    args.append(f'+workshop_download_item {appid} {wid}')

            args.append("validate")
            args.append('+quit')

            print(args)
            # do the ui stuff
            # if self._mod_downloader.ui_running:
            #     self._mod_downloader.ui.downloader_tab.add_text_to_console(' '.join(args), color='yellow')

            # run steamcmd
            # self.run_steamcmd(args)
            self.run_steamcmd_threaded(args)
    
    def run_steamcmd_threaded(self, args: list):
        """
        Run steamcmd in a thread with the given args

        Parameters
        ----------
        args : list
            The args to run steamcmd with

        Returns
        -------
        success : bool
            Whether or not the download was successful
        """
        t = Thread(target=self.run_steamcmd, args=(args,))
        t.start()
        return True
    
    def update_progress_bar(self, progress: int):
        """
        Update the progress bar

        Parameters
        ----------
        progress : int
            The progress to update the bar with
        """
        self._mod_downloader.ui.downloader_tab.update_progress_bar(progress)
    
    def error_message(self, message: str):
        """
        Show an error message

        Parameters
        ----------
        message : str
            The message to show
        """
        yeet = QMessageBox()
        yeet.setText(message)
        yeet.buttonClicked.connect(lambda: sys.exit())
        yeet.exec()
        
    def add_text_to_console(self, text: str, newline: bool=True, color: str='white'):
        """
        Add text to the console

        Parameters
        ----------
        text : str
            The text to add
        color : str
            The color of the text
        """
        if not self.downloader_tab:
            self.downloader_tab = self._mod_downloader.ui.downloader_tab
        self.downloader_tab.add_text_to_console(text, newline=newline, color=color)

    def run_steamcmd(self, args: list):
        """
        Run steamcmd with the given args

        Parameters
        ----------
        args : list
            The args to run steamcmd with

        Returns
        -------
        success : bool
            Whether or not the download was successful
        """
        if self.steamcmd_installed:
            # os.system(' '.join(args))

            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, errors='ignore')
            # stdout, stderr = proc.communicate()
            
            while True:
                out = proc.stdout.readline()
                
                if out == b'' and proc.poll() is not None:
                    break
                
                if out:
                    if m := re.search("Redirecting stderr to", out):
                        print(m)
                        if self._mod_downloader.ui_running:
                            self.add_text_to_console(f'{out[: m.span()[0]]} \n', color='red')
                            break
                        
                    if re.match("-- type 'quit' to exit --", out):
                        continue
                    
                    return_code = proc.poll()
                    print(f'return code: {return_code}')
                    if return_code is not None:
                        for out in proc.stdout.readlines():
                            self.add_text_to_console(out.decode('utf-8'), color='green')
                            print(out.decode('utf-8'))
                            break
                        
            # self.downloader_tab.update_progress_bar(100)
            self.downloader_tab.progress_bar.setVisible(False)
            self.downloader_tab.spinner_button.setVisible(False)
            self.downloader_tab.download_button.setEnabled(True)
            self.downloader_tab.download_button.setVisible(True)

            # if stdout:
            #     print(stdout.decode('utf-8'))
            #     line = stdout.decode('utf-8')
                
            #     if yeet := re.search("Redirecting stderr to", line):
            #         # how can I stop the process or return an error or something here?
            #         print(yeet)
                
            #     if self._mod_downloader.ui_running:
            #         self._mod_downloader.ui.downloader_tab.add_text_to_console(stdout.decode('utf-8'), color='green')
            # if stderr:
            #     print(stderr.decode('utf-8'))
            #     if self._mod_downloader.ui_running:
            #         self._mod_downloader.ui.downloader_tab.add_text_to_console(stderr.decode('utf-8'), color='red')

            # return True

        else:
            raise SteamCMDNotInstalledException('SteamCMD is not installed')