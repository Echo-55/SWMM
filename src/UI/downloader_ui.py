import math
import os
import re
import shutil
import subprocess
import sys
import tkinter as tk
from io import BytesIO
from zipfile import ZipFile
import requests
import customtkinter as ctk
import typing


if typing.TYPE_CHECKING:
    from src import ModDownloader
    from src.Utils import Config


class ModDownloaderUI(ctk.CTk):
    """
    Customtkinter UI class for the Steam Workshop Downloader
    """
    def __init__(self, mod_downloader: 'ModDownloader', config_master: 'Config'):
        """
        Customtkinter UI for the Steam Workshop Downloader
        """
        super().__init__()
        
        self.mod_downloader = mod_downloader
        self.config = config_master
        self.running = False # Keeps track of whether the UI is running or not
        self.batch_limit = 5 # The number of mods to download at once

        self.download_list = []
        self.rename_mode = False
        self.copy_mode = False
        self.game_choice = ""

        # configure window
        self.title("Steam Workshop Downloader")
        self.geometry("800x660")
        self._set_appearance_mode("dark")
        
        self.padx = 7
        self.pady = 4

        # configure grid layout
        # self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        # self.grid_columnconfigure((2, 3), weight=1)
        # self.grid_rowconfigure((0, 1, 2), weight=1)
        
        self._create_widgets()

    def _create_widgets(self):
        """
        Create the widgets for the UI
        
        Parameters
        ----------
        None

        Returns
        -------
        None

        Examples
        --------
        >>> _create_widgets()
        """
        self._create_options_frame()
        self._create_main_frame()
        self._create_console_output_frame()
        self._create_buttons_frame()
    
    def _create_options_frame(self):
        """
        Create the options frame
        """
        # SECTION - OPTIONS FRAME
        # Options frame that lives at the top of the window
        self.options_frame = ctk.CTkFrame(self, height=100)
        self.options_frame.pack(padx=self.padx, pady=self.pady, fill="x", side="top")

        # game selection combobox
        self.combobox_game_var = ctk.StringVar( # a variable to hold the combobox value. Default is "Choose Game"
            self.options_frame, value="Choose Game", name="game_option"
        )
        self.game_combobox = ctk.CTkComboBox(
            self.options_frame,
            values=self.mod_downloader.config.get_game_list_from_config(),
            command=self._game_combobox_callback,
            variable=self.combobox_game_var,
        )
        self.game_combobox.pack(padx=self.padx, pady=self.pady, side="left")

        # mode selection
        self.mode_help_button = ctk.CTkButton( # a button to open the mode help window
            self.options_frame,
            text="Mode help",
            anchor="center",
            width=30,
            height=20,
            command=self._mode_help_callback,
        )
        self.mode_help_button.pack(padx=self.padx, pady=self.pady, side="right")
        
        # rename mode checkbox
        self.rename_mode_var = ctk.StringVar(self, value=0, name="rename_mode_var")
        self.rename_mode_checkbox = ctk.CTkCheckBox(
            self.options_frame,
            text="Rename Mode",
            command=self.rename_checkbox_event,
            variable=self.rename_mode_var,
            onvalue=1,
            offvalue=0,
        )
        self.rename_mode_checkbox.pack(padx=self.padx, pady=self.pady, side="right")
        # copy mode checkbox
        self.copy_mode_var = ctk.StringVar(self, value=0, name="copy_mode_var")
        self.copy_mode_checkbox = ctk.CTkCheckBox(
            self.options_frame,
            text="Copy Mode",
            command=self.copy_checkbox_event,
            variable=self.copy_mode_var,
            onvalue=1,
            offvalue=0,
        )
        self.copy_mode_checkbox.pack(padx=self.padx, pady=self.pady, side="right")
    
    def _create_main_frame(self):
        """
        Create the main frame
        """
        #SECTION - MAIN FRAME
        # configure main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(
            padx=self.padx, pady=self.pady, fill="both", expand=True, side="top"
        )

        # configure url input frame
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(
            padx=self.padx, pady=self.pady, fill="both", expand=True, side="left"
        )
        # url input label
        self.url_input_label = ctk.CTkLabel(self.input_frame, text="Workshop URLs")
        self.url_input_label.pack(padx=2, pady=2, side="top")
        # url input field
        self.url_input = ctk.CTkTextbox(self.input_frame, height=250, width=250)
        self.url_input.pack(
            padx=self.padx, pady=self.pady, side="left", fill="both", expand=True
        )
        # Bind right click to paste inside the url input field and add a newline
        self.url_input.bind(
            "<Button-3>",
            lambda a: self.url_input.insert(tk.END, self.clipboard_get() + "\n"),
        )
    
    def _create_console_output_frame(self):
        """
        Create the console output frame
        """
        #SECTION - CONSOLE OUTPUT FRAME
        # configure console output
        self.console_output_frame = ctk.CTkFrame(self.main_frame)
        self.console_output_frame.pack(
            padx=self.padx, pady=self.pady, fill="both", expand=True, side="right"
        )
        # console output label
        self.console_output_label = ctk.CTkLabel(
            self.console_output_frame, text="Console Output"
        )
        self.console_output_label.pack(padx=2, pady=2, side="top")
        # console output field
        self.console_output = ctk.CTkTextbox(
            self.console_output_frame, height=250, width=250
        )
        self.console_output.pack(
            padx=self.padx, pady=self.pady, side="right", fill="both", expand=True
        )
    
    def _create_buttons_frame(self):
        """
        Create the buttons frame
        """
        #SECTION - BUTTON FRAME
        # configure button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(padx=self.padx, pady=self.pady, fill="both", side="bottom")

        # configure buttons
        self.download_button = ctk.CTkButton(
            self.button_frame, text="Download", command=self._dl_button_callback
        )
        self.download_button.pack(padx=self.padx, pady=self.pady)

    def get_wids_from_str(self, text: str):
        """Takes a string of text and returns a list of tuples containing
        the appid and workshop id of each workshop item.

        Parameters
        ----------
        text : str
            A string of text containing workshop item URLs.

        Returns
        -------
        list
            A list of tuples containing the appid and workshop id of each workshop
            item.

        Examples
        --------
        >>> get_wids("https://steamcommunity.com/sharedfiles/filedetails/?id=123456789")
        [(12345, 123456789)]
        """
        tuple_list = [] # list of tuples containing appid and wid
        
        for line in text.splitlines(): # loop through each line in the text
            if len(line) > 0: # if the line isn't empty
                
                if re.search(r"&search", line): # if the line contains a search query, remove it
                    url = line.split("&search")[0]
                
                try: # check if the url is valid
                    x = requests.get(url)
                except Exception as e:
                    print(e) # TODO handle this better
                    continue
                
                # if the url is a collection
                if re.search("SubscribeCollectionItem", x.text):
                    dls = re.findall( # find all the appid and wid pairs
                        r"SubscribeCollectionItem[\( ']+(\d+)[ ',]+(\d+)'", x.text
                    )
                    for wid, appid in dls: # add each pair to the tuple list
                        tuple_list.append((appid, wid))
                
                # if the url is a workshop item
                elif re.search("ShowAddToCollection", x.text): 
                    wid, appid = re.findall(
                        r"ShowAddToCollection[\( ']+(\d+)[ ',]+(\d+)'", x.text
                    )[0]
                    tuple_list.append((appid, wid))
                
                # if the url is invalid
                else: 
                    self.console_output.insert( # output to the console
                        tk.END,
                        '"'
                        + line
                        + "\" doesn't look like a valid workshop item...\n",
                    )
                    self.console_output.see(tk.END)
                    self.console_output.update()
        
        return tuple_list

    def _dl_button_callback(self):
        """
        Callback for the download button
        """
        modes_enabled = [] # list of modes enabled

        if self.running: # if the downloader is already running, return
            return
        self.running = True
        
        self.download_button.configure(state="disabled") # disable the download button
        self.console_output.delete("1.0", tk.END) # clear the console output

        # create progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.button_frame,
            height=15,
            width=600,
            determinate_speed=1,
            mode="determinate",
        )
        self.progress_bar.pack(padx=self.padx, pady=self.pady)
        self.progress_bar.set(0)

        # build list from input box to be passed to the downloader
        self.download_list = self.get_wids_from_str(self.url_input.get("1.0", tk.END))

        # handle modes
        if self.rename_mode_var.get() == "1":
            self.rename_mode = True
            modes_enabled.append("Rename mode")
        if self.copy_mode_var.get() == "1":
            self.copy_mode = True
            modes_enabled.append("Copy mode")
        print(f"Modes enabled: {modes_enabled}")
        
        # get the steamcmd object from the mod downloader
        self.mod_downloader.steamcmd
        
        # if steamcmd isn't installed, install it
        if not self.mod_downloader.steamcmd.steamcmd_installed:
            self.mod_downloader.steamcmd.steamcmd_path = os.path.join(os.getcwd(), "steamcmd")
            self.config['DEFAULT']['steam_cmd_path'] = self.mod_downloader.steamcmd.steamcmd_path
            
            self.console_output.insert(tk.END, "Installing steamcmd...")
            self.console_output.see(tk.END)
            self.console_output.update()
            
            print(self.mod_downloader.steamcmd.install_steamcmd(self.mod_downloader.steamcmd.steamcmd_path))
            
            self.console_output.insert(tk.END, " DONE\n")
            self.console_output.see(tk.END)
            self.console_output.update()

        # try:
        #     # download = self.download_list
        #     l = len(self.download_list)

        #     for i in range(math.ceil(l / lim)):
        #         batch = self.download_list[i * lim : min((i + 1) * lim, l)]
        #         batch_count = len(batch)
        #         print(f"Batch count: {batch_count}")

        #         # assemble command line
        #         args = [os.path.join(steampath, "steamcmd.exe")]
        #         if login is not None and passw is not None:
        #             args.append(f"+login {login} {passw}")
        #         else:
        #             # args.append("+force_install_dir 'F:\\Games\\RimWorld.v1.4.3525\\aatest'")
        #             args.append("+login anonymous")
        #         for appid, wid in batch:
        #             args.append(f"+workshop_download_item {appid} {int(wid)}")
        #         args.append("validate")
        #         args.append("+quit")
        #         print(args)

        #         # call steamcmd
        #         process = subprocess.Popen(
        #             args,
        #             stdout=subprocess.PIPE,
        #             stderr=subprocess.PIPE,
        #             errors="ignore",
        #             creationflags=subprocess.CREATE_NO_WINDOW,
        #         )

        #         # stdout, stderr = process.communicate()
        #         # print(f'stdout: {stdout}')
        #         # print(f'stderr: {stderr}')

        #         # show output
        #         while True:
        #             out = process.stdout.readline()
        #             if m := re.search("Redirecting stderr to", out):
        #                 self.console_output.insert(tk.END, out[: m.span()[0]] + "\n")
        #                 break
        #             if re.match("-- type 'quit' to exit --", out):
        #                 continue
        #             self.console_output.insert(tk.END, out)
        #             self.console_output.see(tk.END)
        #             self.console_output.update()
        #             return_code = process.poll()
        #             # print(out.strip())
        #             # print(return_code)
        #             if return_code is not None:
        #                 for out in process.stdout.readlines():
        #                     # print(out.strip())
        #                     self.console_output.insert(tk.END, out)
        #                 self.console_output.see(tk.END)
        #                 self.console_output.update()
        #                 break

        #         # move mods
        #         pc = {}
        #         for appid, wid in batch:
        #             if (
        #                 appid in pc
        #                 or cfg.get(appid, "path", fallback=defaultpath)
        #                 or defaultpath
        #             ):
        #                 path = pc.get(
        #                     appid,
        #                     cfg.get(
        #                         appid,
        #                         "path",
        #                         fallback=defaultpath
        #                         and os.path.join(defaultpath, appid),
        #                     ),
        #                 )

        #                 # cfg.add_section(appid)
        #                 # cfg.set(appid, 'path', path)
        #                 # cfg.write()

        #                 batch_count = len(batch)
        #                 p_val = 100 / batch_count
        #                 # self.progress_bar.configure(determinate_speed=p_val)
        #                 self.progress_bar.start()

        #                 if os.path.exists(self.get_mod_path(steampath, appid, wid)):
        #                     # download was successful
        #                     self.progress_bar.step()
        #                     steam_mod_path = self.get_mod_path(steampath, appid, wid)
        #                     new_path = os.path.join(path, wid)
        #                     self.console_output.insert(
        #                         tk.END, "================================\n"
        #                     )
        #                     self.console_output.insert(
        #                         tk.END, "Steam download complete\n"
        #                     )
        #                     self.console_output.insert(
        #                         tk.END, f"Moving {str(wid)} to {new_path} ...\n"
        #                     )
        #                     self.console_output.see(tk.END)
        #                     self.console_output.update()

        #                     if self.rename_mode:
        #                         self.progress_bar.step()
        #                         rename_folder = os.path.join(path, "rename_folder")
        #                         self.console_output.insert(
        #                             tk.END,
        #                             f"\nRename mode is enabled. Mods will be renamed from wid to mod name and put in {rename_folder}\n",
        #                         )
        #                         self.console_output.see(tk.END)
        #                         self.console_output.update()

        #                         if appid == "108600":
        #                             m_path = f"{steam_mod_path}/mods"
        #                             mod_name = os.listdir(m_path)
        #                         else:
        #                             mod_name = []
        #                             mod_name.append(os.path.basename(steam_mod_path))

        #                         mod_count = len(mod_name)
        #                         print(f"Mod name(s): {mod_name}")
        #                         print(f"Mod count: {mod_count}")

        #                         self.console_output.insert(
        #                             tk.END, f"Found {mod_count} mod(s). \n"
        #                         )
        #                         self.console_output.see(tk.END)
        #                         self.console_output.update()

        #                         if mod_count > 1:
        #                             p_val = 100 / mod_count
        #                             self.progress_bar.configure(number_of_steps=p_val)

        #                             for _, each in enumerate(mod_name):
        #                                 print(each)
        #                                 new_path = os.path.join(rename_folder, each)

        #                                 # delete old version
        #                                 if os.path.exists(new_path):
        #                                     shutil.rmtree(new_path)

        #                                 if self.copy_mode:
        #                                     print(f"copy_mode: {self.copy_mode}")
        #                                     # TODO broken?
        #                                     shutil.copytree(
        #                                         os.path.join(steam_mod_path, each),
        #                                         new_path,
        #                                     )
        #                                 else:
        #                                     shutil.move(
        #                                         os.path.join(steam_mod_path, each),
        #                                         new_path,
        #                                     )

        #                                 # increment the progress bar
        #                                 self.progress_bar.step()

        #                                 self.console_output.insert(
        #                                     tk.END,
        #                                     f"{each} installed to {rename_folder}/{each}\n",
        #                                 )
        #                                 self.console_output.see(tk.END)
        #                                 self.console_output.update()
        #                         else:
        #                             self.progress_bar.set(1)

        #                             new_path = os.path.join(rename_folder, mod_name[0])
        #                             print(f"new_path: {new_path}")

        #                             if os.path.exists(new_path):
        #                                 shutil.rmtree(new_path)

        #                             if self.copy_mode:
        #                                 shutil.copytree(steam_mod_path, new_path)
        #                             else:
        #                                 shutil.move(steam_mod_path, new_path)

        #                             self.console_output.insert(
        #                                 tk.END, f"{mod_name} installed to: {new_path}\n"
        #                             )
        #                             self.console_output.see(tk.END)
        #                             self.console_output.update()
        #                     elif self.copy_mode:
        #                         self.progress_bar.step()
        #                         shutil.copytree(
        #                             steam_mod_path, new_path, dirs_exist_ok=True
        #                         )
        #                     else:
        #                         self.progress_bar.step()
        #                         if os.path.exists(new_path):
        #                             shutil.rmtree(new_path)
        #                         shutil.move(steam_mod_path, new_path)
        #                     self.console_output.insert(tk.END, " DONE\n")
        #                     self.console_output.see(tk.END)
        #                     self.console_output.update()
        #                 pc[appid] = path
        #     # reset state
        #     self.progress_bar.stop()
        #     self.progress_bar.set(1)
        #     self.url_input.delete("1.0", tk.END)
        # except Exception as ex:
        #     self.console_output.insert(tk.END, type(ex))
        #     self.console_output.insert(tk.END, ex)
        #     self.console_output.see(tk.END)
        #     self.console_output.update()
        # finally:
        #     self.progress_bar.stop()
        #     self.progress_bar.set(1)
        #     path = ""
        #     # TODO
        #     # open_install_folder_on_complete: bool =
        #     running = False
        #     self.progress_bar.destroy()
        #     self.download_button.configure(state="enabled")

    #!SECTION - UI CALLBACKS
    def _mode_help_callback(self):
        """
            Creates a new top level window that shows help text for the modes
            
            Parameters
            ----------
            None
            
            Returns
            -------
            None
        """
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help Window")
        help_window.geometry("600x200")
        help_window_label_rename = ctk.CTkLabel(
            help_window,
            text="Turn rename mode on if you want to rename mod folder from wid to mod name",
        )
        help_window_label_rename.pack(
            side="top", fill="both", expand=True, padx=self.padx, pady=self.pady
        )
        help_window_label_copy = ctk.CTkLabel(
            help_window,
            text="Turn copy mode on if you want to copy mod folder from steamcmd path instead of move",
        )
        help_window_label_copy.pack(
            side="top", fill="both", expand=True, padx=self.padx, pady=self.pady
        )

    def _game_combobox_callback(self, choice):
        self.game_choice = choice
        print(f"Game choice: {self.game_choice}")

    #!SECTION - UI EVENTS
    def rename_checkbox_event(self):
        state = self.rename_mode_var.get()
        self.rename_mode = True if state == "1" else False
        print(f"Rename mode: {self.rename_mode}")

    def copy_checkbox_event(self):
        state = self.copy_mode_var.get()
        self.copy_mode = True if state == "1" else False
        print(f"Copy mode: {self.copy_mode}")

    def get_mod_path(self, base, appid, wid):
        return os.path.join(base, "steamapps/workshop/content/", str(appid), str(wid))

    def input_box_return(self, event):
        self.url_input.insert(tk.END, "\n")