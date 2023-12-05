# Author: Echo55
# Description: 

import argparse
from src import ModUpdater, ModDownloader
from src.Utils import Config, pprint, cprint
from PyQt6.QtWidgets import QApplication
import sys
import qdarktheme

USE_MYCONFIG = True

def main():

    parser = argparse.ArgumentParser(description='Steam workshop mod manager.')

    # arg to auto start the downloader
    parser.add_argument('-d', '--download', action='store_true', help='Download mods')

    # arg to auto start the updater
    parser.add_argument('-u', '--update', action='store_true', help='Update mods')

    # arg for game selection
    parser.add_argument('-g', '--game', action='store', help='Select a game')

    # arg to use my config file
    parser.add_argument('-m', '--myconfig', action='store_true', help='Use my config file')

    args = parser.parse_args()

    if args.myconfig:
        config = Config(myconfig=USE_MYCONFIG)
    else:
        config = Config()

    if args.download:
        # when the user doesn't start with the ui, we confirm they choose a game in the ModDownloader class
        # could be changed to a prompt here
        app = QApplication(sys.argv)
        qdarktheme.setup_theme()
        downloader = ModDownloader(config, start_with_ui=True, selected_game=args.game)
        app.exec()

    if args.update:
        # if not args.game:
        #     args.game = input('Please select a game to update mods for')

        updater = ModUpdater(config, mod_wid="708455313")
        print(updater.needs_update)

if __name__ == "__main__":
    main()

