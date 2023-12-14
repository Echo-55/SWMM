from typing import TYPE_CHECKING, Optional
from threading import Thread

from src.Utils import SteamCMD, Game

if TYPE_CHECKING:
    from .Utils import Config
    from src.UI.new_downloader_ui import Ui_Downloader


class ModDownloader:
    def __init__(
        self,
        config_master: "Config",
        start_with_ui: bool = False,
        selected_game: str = "",
    ):
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
        self._config = config_master

        # if the game is chosen, get the game info from config-
        # so that it can be passed to the steamcmd class
        self.selected_game_str: str = selected_game
        if self.selected_game_str:
            # get the appid and mod folder path from the config
            appid = self.config.get(self.selected_game_str, "appid")
            mod_folder_path = self.config.get(self.selected_game_str, "mod_folder_path")
            # create a Game object
            self._game: Optional[Game] = Game(self.selected_game_str, appid, mod_folder_path)
        else:
            # if no game is chosen, set the game to None
            self._game: Optional[Game] = None

        self.steamcmd = SteamCMD(self)

        # flags to check if the downloader and/or ui are running
        self._running: bool = False
        self._ui_running: bool = False

        # if the user wants to start with the ui, start the ui
        if start_with_ui:
            self.start_ui()
        else:
            # TODO: CLI
            self._init_mod_downloader()
        
    # -------------------------------- Properties -------------------------------- #
    @property
    def config(self) -> "Config":
        """
        Get the config object
        """
        return self._config
    
    @config.setter
    def config(self, value: "Config"):
        """
        Set the config object
        """
        self._config = value

    @property
    def game(self) -> Optional[Game]:
        """
        Get the game object
        """
        return self._game
    
    @game.setter
    def game(self, value: Optional[Game]):
        """
        Set the game object
        """
        self._game = value
    
    @property
    def steamcmd_installed(self) -> bool:
        """
        Check if steamcmd is installed
        """
        return self.steamcmd.steamcmd_installed
    
    @steamcmd_installed.setter
    def steamcmd_installed(self, value: bool):
        """
        Set the steamcmd installed value
        """
        self.steamcmd.steamcmd_installed = value

    @property
    def running(self) -> bool:
        """
        Check if the downloader is running
        """
        return self._running
    
    @running.setter
    def running(self, value: bool):
        """
        Set the running value
        """
        self.ui.downloader_tab.download_button.setEnabled(value)
        self._running = value

    @property
    def ui_running(self) -> bool:
        """
        Check if the UI is running
        """
        return self._ui_running
    
    @ui_running.setter
    def ui_running(self, value: bool):
        """
        Set the UI running value
        """
        self._ui_running = value
    
    @property
    def ui(self) -> "Ui_Downloader":
        """
        Get the UI
        """
        return self._ui
    
    @ui.setter
    def ui(self, value: "Ui_Downloader"):
        """
        Set the UI
        """
        self._ui = value

    def _init_mod_downloader(self):
        """
        Initialize the mod downloader
        """
        # TODO
        # self._get_game()
        # self._get_mod_folder()
        # self._get_mod_list()

    def start_ui(self):
        """
        Start the UI for the mod downloader
        """
        from src.UI.new_downloader_ui import Ui_Downloader

        self._ui: 'Ui_Downloader' = Ui_Downloader(self)
        self.ui_running = True
        self._ui.show()

    def download_mod_from_url(self, mod_url: str):
        """
        Download a mod from a url

        Parameters
        ----------
        mod_url : str
            The url to download the mod from
        """
        if self.running:
            return
        self.running = True
        self.steamcmd.download_mod_from_url(mod_url)

    def download_mods_list(self, mod_list: list):
        """
        Download a list of mods

        Parameters
        ----------
        mod_list : list
            A list of mods to download
        """
        if self.running:
            return
        self.running = True
        self.steamcmd.download_mods_list(mod_list)
