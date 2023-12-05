from typing import TYPE_CHECKING, Optional
import os
from src.UI.new_downloader_ui import Ui_Downloader

from src.Utils import SteamCMD, Game, cprint, pprint

if TYPE_CHECKING:
    from .Utils import Config

class ModDownloader:
    def __init__(self, config_master: 'Config', start_with_ui: bool=False, selected_game: str=''):
        """
        Mod Downloader class
        
        Parameters
        ----------
        
        config_master : Config
            The config object
        start_with_ui : bool
            Whether or not to start with the UI
        game : str
            The game to download mods for
        """
        self.config = config_master
        self.selected_game: str = selected_game
        if self.selected_game:
            appid = self.config.get(self.selected_game, 'appid')
            mod_folder_path = self.config.get(self.selected_game, 'mod_folder_path')
            self.game: Optional[Game] = Game(self.selected_game, appid, mod_folder_path)
        else:
            self.game: Optional[Game] = None

        self.steamcmd = SteamCMD(self.config, self.game)
        
        if start_with_ui:
            self.start_ui()
        else:
            self._init_mod_downloader()
    
    def _init_mod_downloader(self):
        """
        Initialize the mod downloader
        """
        self._get_game()
        self._get_mod_folder()
        self._get_mod_list()
    
    def _get_game(self):
        """
        Get the game from the config
        """
        # if the user didn't choose a game
        if not self.game:
            # get the game list from the config
            game_list = self.config.get_game_list_from_config()
            # if there is only one game
            if len(game_list) == 1:
                # set the game to the only game in the list
                self.game = game_list[0]
            # if there are multiple games
            elif len(game_list) > 1:
                # print the game list
                pprint(game_list)
                # ask the user to select a game
                cprint('Please select a game to download mods for: ', 'yellow')
                # get the user's input
                self.game = input('Please select a game to download mods for: ')
            # if there are no games
            else:
                # raise an exception
                raise Exception('No games found in config')
            
            # set the game to the game object
            self.game = Game(self.game, self.config[self.game]['appid'], self.config[self.game]['mod_folder_path'])
            
            # print the game
            pprint(self.game)
    
    def _get_mod_folder(self):
        """
        Get the mod folder from the config
        """
        pass
        # # if the game has a mod folder
        # if self.game.mod_folder_path:
        #     # if the mod folder exists
        #     if os.path.exists(self.game.mod_folder_path):
        #         # set the mod folder
        #         self.mods_folder = self.game.mod_folder_path
        #     # if the mod folder doesn't exist
        #     else:
        #         # raise an exception
        #         raise Exception(f'Mod folder not found at {self.game.mod_folder_path}')
        # # if the game doesn't have a mod folder
        # else:
        #     # raise an exception
        #     raise Exception(f'No mod folder found for {self.game.name}')
    
    def _get_mod_list(self):
        """
        Get a list of mods from local mod folder
        """
        if self.mods_folder:
            if os.path.exists(self.mods_folder):
                return os.listdir(self.mods_folder)
    
    def start_ui(self):
        """
        Start the UI for the mod downloader
        """
        # from src.UI.downloader_ui import ModDownloaderUI
        # self.ui = ModDownloaderUI(self, self.config)
        # self.ui.url_input.bind('<<Paste>>', self.ui.input_box_return)
        # self.ui.mainloop()
        from src.UI.new_downloader_ui import Ui_Downloader
        self.ui = Ui_Downloader(self)
        self.ui.show()
    
    #TODO Should I put this here or in the UI?
    def _ui_download_callback(self, download_list):
        """
        Callback for the UI to download mods
        """
