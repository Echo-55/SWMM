from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QStyle, QStyleOptionButton
from typing import TYPE_CHECKING, Optional, Union
from termcolor import COLORS
from superqt import QCollapsible
import superqt.fonticon as fi
from fonticon_fa6 import FA6S

if TYPE_CHECKING:
    from src.downloader import ModDownloader


class UiTab_Downloader(QtWidgets.QTabWidget):
    def __init__(self, parent_window: "Ui_Downloader"):
        super().__init__()
        self._parent_window = parent_window

        self.setupUi()

    def setupUi(self):
        """Setup the ui for the downloader tab"""
        self.layout_ = QtWidgets.QGridLayout()
        self.setLayout(self.layout_)

        # url input
        self.url_input_label = QtWidgets.QLabel("Enter Mod URLs here:")
        self.layout_.addWidget(
            self.url_input_label, 0, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.url_input_box = QtWidgets.QTextEdit()
        self.url_input_box.setAutoFormatting(
            QtWidgets.QTextEdit.AutoFormattingFlag.AutoNone
        )
        self.url_input_box.setAcceptRichText(False)
        self.layout_.addWidget(self.url_input_box, 1, 0)

        # console output
        self.console_output_label = QtWidgets.QLabel("Console Output:")
        self.layout_.addWidget(
            self.console_output_label, 0, 1, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.console_output_box = QtWidgets.QTextEdit()
        self.console_output_box.setReadOnly(True)
        self.layout_.addWidget(self.console_output_box, 1, 1)
        
        # progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.layout_.addWidget(self.progress_bar, 2, 0, 1, 2)
        
        # spinner icon
        self.spinner_button = QtWidgets.QPushButton()
        self.spinner_button.setIcon(fi.icon(FA6S.spinner, color="green", animation=fi.spin(self.spinner_button)))
        self.spinner_button.setIconSize(QtCore.QSize(16, 16))
        self.spinner_button.setFlat(True)
        self.spinner_button.setVisible(False)
        self.layout_.addWidget(self.spinner_button, 1, 1, QtCore.Qt.AlignmentFlag.AlignHCenter)

        # download button
        self.download_button = QtWidgets.QPushButton("Download")
        self.download_button.clicked.connect(self._handle_download_button)
        # TODO: Column stretch
        self.layout_.addWidget(
            self.download_button, 2, 0, 1, 2, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

    def update_progress_bar(self, value: int):
        """Update the progress bar

        Args:
            value (int): the value to set the progress bar to
        """
        self.progress_bar.setValue(value)

    def _handle_download_button(self):
        """Download the mod from the url"""
        self.add_text_to_console("Starting download...", color="green")
        urls = self.url_input_box.toPlainText().split("\n")
        if len(urls) == 0 or urls[0] == "":
            self.add_text_to_console("No URLs entered", color="red")
            return
        try:
            self._parent_window.mod_downloader.download_mods_list(urls)
            self.download_button.setEnabled(False)
            self.download_button.setVisible(False)
            self.progress_bar.setVisible(True)
            self.spinner_button.setVisible(True)
        except Exception as e:
            self.add_text_to_console(f"Error: {e}", color="red")

    def add_text_to_console(
        self, text: str, newline: bool = True, color: str = "white"
    ):
        """Add text to the console output box

        Args:
            text (str): the text to add
            newline (bool, optional): whether or not to add a newline. Defaults to True.
        """
        if color in COLORS:
            self.console_output_box.setTextColor(QtGui.QColor(color))
        if newline:
            self.console_output_box.append(text)
        else:
            self.console_output_box.insertPlainText(text)
        self.console_output_box.setTextColor(QtGui.QColor("white"))


class Ui_CollapsibleOptions(QCollapsible):
    def __init__(
        self,
        parent_window: "Ui_Downloader",
        title: str = "Options",
        parent: Optional[QWidget] = None,
        expandedIcon: Optional[Union[QIcon, str]] = "▼",
        collapsedIcon: Optional[Union[QIcon, str]] = "▲",
    ):
        super().__init__(title, parent, expandedIcon, collapsedIcon)
        self._parent_window = parent_window
        self.mod_downloader = parent_window.mod_downloader

        self.rename_mode: bool = False
        self.copy_mode: bool = False

        self.setupUi()

    def setupUi(self):
        """Setup the ui for the options widget"""
        # rename mode
        self.rename_mode_checkbox = QtWidgets.QCheckBox()
        self.rename_mode_checkbox.setText("Rename mode")
        self.rename_mode_checkbox.stateChanged.connect(self._handle_rename_mode_changed)
        self.addWidget(self.rename_mode_checkbox)

        # copy mode
        self.copy_mode_checkbox = QtWidgets.QCheckBox()
        self.copy_mode_checkbox.setText("Copy mode")
        self.copy_mode_checkbox.stateChanged.connect(self._handle_copy_mode_changed)
        self.addWidget(self.copy_mode_checkbox)

        # mode help button to spawn a popup
        self.mode_help_button = QtWidgets.QPushButton("Help")
        self.mode_help_button.clicked.connect(self._handle_mode_help_button_clicked)
        self.addWidget(self.mode_help_button)

    def _handle_mode_help_button_clicked(self):
        """When the mode help button is clicked"""
        help_text = "Rename mode: Renames the downloaded file to the name of the mod\nCopy mode: Copies the downloaded file to the mod directory"
        QtWidgets.QMessageBox.information(self, "Mode Help", help_text)

    def _handle_rename_mode_changed(self):
        """When the rename mode is changed"""
        if self.rename_mode_checkbox.isChecked():
            self.rename_mode = True
            self._parent_window.downloader_tab.add_text_to_console(
                "Rename mode enabled", color="green"
            )
        else:
            self.rename_mode = False
            self._parent_window.downloader_tab.add_text_to_console(
                "Rename mode disabled", color="red"
            )

    def _handle_copy_mode_changed(self):
        """When the copy mode is changed"""
        if self.copy_mode_checkbox.isChecked():
            self.copy_mode = True
            self._parent_window.downloader_tab.add_text_to_console(
                "Copy mode enabled", color="green"
            )
        else:
            self.copy_mode = False
            self._parent_window.downloader_tab.add_text_to_console(
                "Copy mode disabled", color="red"
            )


class Ui_Options(QWidget):
    def __init__(self, parent_window: "Ui_Downloader"):
        super().__init__()
        self._parent_window = parent_window
        self.mod_downloader = parent_window.mod_downloader

        self.rename_mode: bool = False
        self.copy_mode: bool = False

        self.setupUi()

    def setupUi(self):
        """Setup the ui for the options widget"""
        # layout
        self.layout_ = QtWidgets.QGridLayout()
        self.setLayout(self.layout_)

        # game selection
        self.game_selection_label = QtWidgets.QLabel("Select a game:")
        self.layout_.addWidget(self.game_selection_label, 0, 0)

        self.game_selection_box = QtWidgets.QComboBox()
        self.game_selection_box.addItems(
            self.mod_downloader.config.get_game_list_from_config()
        )
        self.game_selection_box.currentTextChanged.connect(
            self._handle_game_selection_changed
        )
        self.game_selection_box.addItems(
            self.mod_downloader.config.get_game_list_from_config()
        )
        self.layout_.addWidget(self.game_selection_box, 0, 1)

        # rename mode
        self.rename_mode_label = QtWidgets.QLabel("Rename mode:")
        self.layout_.addWidget(self.rename_mode_label, 1, 0)

        self.rename_mode_checkbox = QtWidgets.QCheckBox()
        self.rename_mode_checkbox.stateChanged.connect(self._handle_rename_mode_changed)
        self.layout_.addWidget(self.rename_mode_checkbox, 1, 1)

        # copy mode
        self.copy_mode_label = QtWidgets.QLabel("Copy mode:")
        self.layout_.addWidget(self.copy_mode_label, 2, 0)

        self.copy_mode_checkbox = QtWidgets.QCheckBox()
        self.copy_mode_checkbox.stateChanged.connect(self._handle_copy_mode_changed)
        self.layout_.addWidget(self.copy_mode_checkbox, 2, 1)

        # mode help button to spawn a popup
        self.mode_help_button = QtWidgets.QPushButton("Help")
        self.mode_help_button.clicked.connect(self._handle_mode_help_button_clicked)
        self.layout_.addWidget(
            self.mode_help_button, 3, 0, 1, 2, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

    def _handle_mode_help_button_clicked(self):
        """When the mode help button is clicked"""
        help_text = "Rename mode: Renames the downloaded file to the name of the mod\nCopy mode: Copies the downloaded file to the mod directory"
        QtWidgets.QMessageBox.information(self, "Mode Help", help_text)

    def _handle_rename_mode_changed(self):
        """When the rename mode is changed"""
        if self.rename_mode_checkbox.isChecked():
            self.rename_mode = True
            self._parent_window.downloader_tab.add_text_to_console(
                "Rename mode enabled", color="green"
            )
        else:
            self.rename_mode = False
            self._parent_window.downloader_tab.add_text_to_console(
                "Rename mode disabled", color="red"
            )

    def _handle_copy_mode_changed(self):
        """When the copy mode is changed"""
        if self.copy_mode_checkbox.isChecked():
            self.copy_mode = True
            self._parent_window.downloader_tab.add_text_to_console(
                "Copy mode enabled", color="green"
            )
        else:
            self.copy_mode = False
            self._parent_window.downloader_tab.add_text_to_console(
                "Copy mode disabled", color="red"
            )

    def _handle_game_selection_changed(self):
        """When the game selection is changed"""
        self.game_selection = self.game_selection_box.currentText()
        self.game_selected = True
        self.game = self.mod_downloader.config.get_game_info_from_config(
            self.game_selection
        )
        self._parent_window.downloader_tab.add_text_to_console(
            f"Game selected: {self.game_selection}", color="green"
        )


class Ui_StatusBar(QtWidgets.QStatusBar):
    def __init__(self, parent_window: "Ui_Downloader"):
        super().__init__()
        self._parent_window = parent_window
        self.game_selection = ""
        self.setupUi()

    @property
    def steamcmd_installed(self):
        return self._parent_window.steamcmd_installed

    @steamcmd_installed.setter
    def steamcmd_installed(self, value: bool):
        self._parent_window.steamcmd_installed = value

    @property
    def game_selected(self):
        return self._parent_window.game_selected

    @game_selected.setter
    def game_selected(self, value: bool):
        self._parent_window.game_selected = value

    @property
    def game_selection(self):
        return self._parent_window.game_selection

    @game_selection.setter
    def game_selection(self, value: str):
        self._parent_window.game_selection = value

    @property
    def game(self):
        return self._parent_window.game

    def update_status(self, widget: QWidget, status: bool):
        """Update the status of one of the widgets in the status bar

        Args:
            widget (str): the widget to update
            status (str): the status to set
        """
        if status:
            checkmark_icon = fi.icon(
                FA6S.check,
                color="green",
                states={
                    "Active": {
                        "glyph_key": FA6S.spinner,
                        "color": "red",
                        "scale_factor": 0.5,
                        "animation": fi.spin(widget),
                    },
                    "Disabled": {
                        "color": "green",
                        "scale_factor": 0.8,
                        "animation": fi.spin(widget),
                    },
                },
            )
            if isinstance(widget, QtWidgets.QLabel):
                widget.setPixmap(checkmark_icon.pixmap(16, 16))
                checkmark_icon.Mode = "Active"
                checkmark_icon.State = "Active"
        else:
            x_icon = fi.icon(FA6S.xmark, color="red")
            if isinstance(widget, QtWidgets.QLabel):
                widget.setPixmap(x_icon.pixmap(16, 16))

    def refresh(self):
        """Refresh the status bar"""
        if self.steamcmd_installed:
            self.update_status(self.steamcmd_status_icon, True)
        else:
            self.update_status(self.steamcmd_status_icon, False)

        if self.game_selected:
            self.update_status(self.game_status_icon, True)
        else:
            self.update_status(self.game_status_icon, False)

    def setupUi(self):
        """Setup the ui for the status bar"""
        # ------------------------------ steamcmd status ----------------------------- #
        # steamcmd status label
        self.steamcmd_status_label = QtWidgets.QLabel("SteamCMD Status:", self)
        self.addWidget(self.steamcmd_status_label)
        # steamcmd status checkmark icon
        self.steamcmd_status_icon = QtWidgets.QLabel(self)
        if self.steamcmd_installed:
            self.update_status(self.steamcmd_status_icon, True)
        else:
            self.update_status(self.steamcmd_status_icon, False)
        self.addWidget(self.steamcmd_status_icon)

        # -------------------------------- game status ------------------------------- #
        # game status label
        self.game_status_label = QtWidgets.QLabel("Game Status:", self)
        self.addWidget(self.game_status_label)
        # game status checkmark icon
        self.game_status_icon = QtWidgets.QLabel(self)
        if self.game_selected:
            self.update_status(self.game_status_icon, True)
        else:
            self.update_status(self.game_status_icon, False)
        self.addWidget(self.game_status_icon)
        self.refresh()


class Ui_MenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent_window: "Ui_Downloader"):
        super().__init__()
        self._parent_window = parent_window
        self.setupUi()

    def setupUi(self):
        """Setup the ui for the menu bar"""
        self.layout_ = QtWidgets.QGridLayout()
        self.setLayout(self.layout_)

        # file menu
        self.file_menu = self.addMenu("File")
        # exit action
        if self.file_menu:
            self.exit_action = QtGui.QAction("Exit")
            self.exit_action.triggered.connect(self._parent_window.close)
            self.file_menu.addAction(self.exit_action)

        # help menu
        self.help_menu = self.addMenu("Help")
        # about action
        if self.help_menu:
            self.about_action = QtGui.QAction("About")
            self.about_action.triggered.connect(self._handle_about_action_triggered)
            self.help_menu.addAction(self.about_action)

    def _handle_about_action_triggered(self):
        """When the about action is triggered"""
        QtWidgets.QMessageBox.about(
            self,
            "About",
            "Mod Downloader\n\nA tool for downloading mods from the Steam Workshop",
        )


class Ui_Downloader(QWidget):
    def __init__(
        self, mod_downloader: "ModDownloader", parent_window: Optional[QWidget] = None
    ):
        super().__init__()
        self.mod_downloader = mod_downloader
        self._parent_window = parent_window

        self.steamcmd_installed = self.mod_downloader.steamcmd_installed

        self.running = False
        self.game_list = []
        self.game_selected = False
        self.game_selection = ""
        self.game = None

        self.rename_mode = False
        self.copy_mode = False

        self.setupUi()
        self.mod_downloader.ui = self
        self.mod_downloader.ui_running = True

        # if steamcmd is not installed, show a popup
        if not self.steamcmd_installed:
            self.show_steamcmd_not_installed_popup()

    @property
    def config(self):
        return self.mod_downloader.config

    @property
    def steamcmd(self):
        return self.mod_downloader.steamcmd

    @property
    def steamcmd_installed(self):
        return self.mod_downloader.steamcmd_installed

    @steamcmd_installed.setter
    def steamcmd_installed(self, value: bool):
        self.mod_downloader.steamcmd_installed = value

    def setupUi(self):
        """Setup the ui for the mod downloader"""
        self.setWindowTitle("Mod Downloader")
        self.windowSize = QtCore.QSize(800, 600)
        self.resize(self.windowSize)
        self.setMinimumSize(self.windowSize)

        self.layout_ = QtWidgets.QGridLayout()
        self.setLayout(self.layout_)

        # menu bar
        self.menu_bar = Ui_MenuBar(self)
        self.layout_.addWidget(self.menu_bar, 0, 0)

        # status bar
        self.status_bar = Ui_StatusBar(self)
        self.layout_.addWidget(self.status_bar, 4, 0)

        # TODO: Change the options button to be a dropdown menu
        # anything cleaner than what it is now
        # options widget
        self.options_widget = Ui_CollapsibleOptions(self)
        # self.options_widget.setVisible(False)
        self.layout_.addWidget(self.options_widget, 2, 0)

        # tabs widget
        self.tabs_widget = QtWidgets.QTabWidget()
        self.layout_.addWidget(self.tabs_widget, 3, 0)
        # downloader tab
        self.downloader_tab = UiTab_Downloader(self)
        self.tabs_widget.addTab(self.downloader_tab, "Downloader")

    def show_steamcmd_not_installed_popup(self):
        """Show a popup if steamcmd is not installed"""
        # show a popup and ask if the user wants to install steamcmd
        popup = QtWidgets.QMessageBox()
        popup.setWindowTitle("SteamCMD not installed")
        popup.setText("SteamCMD is not installed. Would you like to install it?")
        popup.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No
        )
        popup.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Yes)
        popup.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        popup.setWindowIcon(QtGui.QIcon("icons/warning.png"))
        popup.buttonClicked.connect(self._handle_steamcmd_not_installed_popup_clicked)
        popup.exec()

    def _handle_steamcmd_not_installed_popup_clicked(self, button):
        """Handle the steamcmd not installed popup being clicked"""
        if button.text() == "&Yes":
            if self.mod_downloader.steamcmd.install_steamcmd():
                self.status_bar.refresh()
                self.downloader_tab.add_text_to_console(
                    "SteamCMD installed successfully!", color="green"
                )
                self.downloader_tab.add_text_to_console(
                    "Please wait as steamcmd updates...", color="green"
                )
                self.mod_downloader.steamcmd.update_steamcmd()
        else:
            self.close()
