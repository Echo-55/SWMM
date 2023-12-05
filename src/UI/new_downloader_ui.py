from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget
from typing import TYPE_CHECKING, Optional
from termcolor import colored, cprint, COLORS

if TYPE_CHECKING:
    from src.downloader import ModDownloader


class UiTab_Downloader(QtWidgets.QTabWidget):
    def __init__(self, parent_window: 'Ui_Downloader'):
        super().__init__()
        self.parent_window = parent_window

        self.setupUi()

    def setupUi(self):
        """Setup the ui for the downloader tab
        """
        self.layout_ = QtWidgets.QGridLayout()
        self.setLayout(self.layout_)

        self.url_input_label = QtWidgets.QLabel('Enter Mod URLs here:')
        self.layout_.addWidget(self.url_input_label, 0, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.url_input_box = QtWidgets.QTextEdit()
        self.layout_.addWidget(self.url_input_box, 1, 0)

        self.console_output_label = QtWidgets.QLabel('Console Output:')
        self.layout_.addWidget(self.console_output_label, 0, 1, QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.console_output_box = QtWidgets.QTextEdit()
        self.console_output_box.setReadOnly(True)
        self.layout_.addWidget(self.console_output_box, 1, 1)
        
        self.download_button = QtWidgets.QPushButton('Download')
        self.download_button.clicked.connect(self.download_mod)
        # TODO: Column stretch
        self.layout_.addWidget(self.download_button, 2, 0, 1, 2, QtCore.Qt.AlignmentFlag.AlignHCenter)

    def download_mod(self):
        """Download the mod from the url
        """
        url = self.url_input_box.toPlainText()
        self.add_text_to_console(f'Downloading mod from url: {url}', color='green')

    def add_text_to_console(self, text: str, newline: bool=True, color: str='white'):
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
        self.console_output_box.setTextColor(QtGui.QColor('white'))

class UI_Options(QWidget):
    def __init__(self, parent_window: 'Ui_Downloader'):
        super().__init__()
        self.parent_window = parent_window
        self.mod_downloader = parent_window.mod_downloader

        self.setupUi()

    def setupUi(self):
        """Setup the ui for the options widget
        """
        self.layout_ = QtWidgets.QGridLayout()
        self.setLayout(self.layout_)

        self.game_selection_label = QtWidgets.QLabel('Select a game:')
        self.layout_.addWidget(self.game_selection_label, 0, 0)

        self.game_selection_box = QtWidgets.QComboBox()
        self.game_selection_box.addItems(self.mod_downloader.config.get_game_list_from_config())
        self.game_selection_box.currentTextChanged.connect(self.game_selection_changed)
        self.game_selection_box.addItems(self.mod_downloader.config.get_game_list_from_config())
        self.layout_.addWidget(self.game_selection_box, 0, 1)
    
    def game_selection_changed(self):
        """When the game selection is changed
        """
        self.game_selection = self.game_selection_box.currentText()
        self.game_selected = True
        self.game = self.mod_downloader.config.get_game_info_from_config(self.game_selection)
        self.parent_window.downloader_tab.add_text_to_console(f'Game selected: {self.game_selection}', color='green')

class Ui_Downloader(QWidget):
    def __init__(self, mod_downloader: 'ModDownloader', parent_window: Optional[QWidget]=None):
        super().__init__()
        self.mod_downloader = mod_downloader
        self.parent_window = parent_window
        
        self.running = False
        self.game_list = []
        self.game_selected = False
        self.game_selection = ''
        self.game = None

        self.rename_mode = False
        self.copy_mode = False

        self.setupUi()

    def setupUi(self):
        """Setup the ui for the mod downloader
        """
        self.setWindowTitle('Mod Downloader')
        self.windowSize = QtCore.QSize(800, 600)

        self.resize(self.windowSize)
        self.setMinimumSize(self.windowSize)
        
        self.layout_ = QtWidgets.QGridLayout()
        self.setLayout(self.layout_)

        # tabs widget
        self.tabs_widget = QtWidgets.QTabWidget()
        self.layout_.addWidget(self.tabs_widget, 2, 0)
        # downloader tab
        self.downloader_tab = UiTab_Downloader(self)
        self.tabs_widget.addTab(self.downloader_tab, 'Downloader')

        # options widget
        self.options_widget = UI_Options(self)
        self.layout_.addWidget(self.options_widget, 1, 0)

        self.togge_options_visibility_button = QtWidgets.QPushButton('Show Options')
        self.togge_options_visibility_button.setCheckable(True)
        self.togge_options_visibility_button.clicked.connect(self.toggle_options_visibility)
        self.layout_.addWidget(self.togge_options_visibility_button, 0, 0)

    def toggle_options_visibility(self):
        """Toggle the visibility of the options widget
        """
        if self.options_widget.isVisible():
            self.options_widget.setVisible(False)
            self.togge_options_visibility_button.setText('Show Options')
        else:
            self.options_widget.setVisible(True)
            self.togge_options_visibility_button.setText('Hide Options')