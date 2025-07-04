import json
import webbrowser

import SCOFunctions.AppFunctions as AF
import SCOFunctions.HelperFunctions as HF
import SCOFunctions.MainFunctions as MF
import SCOFunctions.MUserInterface as MUI
from PyQt5 import QtCore, QtGui, QtWidgets
from SCOFunctions.FastExpand import FastExpandSelector
from SCOFunctions.MFilePath import innerPath
from SCOFunctions.MLogging import Logger, catch_exceptions
from SCOFunctions.MTheming import MColors
from SCOFunctions.Settings import Setting_manager as SM
from SCOFunctions.MTranslation import translate

logger = Logger('TABM', Logger.levels.INFO)


class MainTab(QtWidgets.QWidget):
    def __init__(self, parent, APPVERSION):
        super().__init__()
        self.p = parent
        ch_distance = 20

        # Start with Windows
        self.CH_StartWithWindows = QtWidgets.QCheckBox(self)
        self.CH_StartWithWindows.setGeometry(QtCore.QRect(20, ch_distance, 230, 17))
        self.CH_StartWithWindows.setText(translate("Start with Windows"))
        self.CH_StartWithWindows.setToolTip(translate("The app will start automatically with Windows"))

        # Start minimized
        self.CH_StartMinimized = QtWidgets.QCheckBox(self)
        self.CH_StartMinimized.setGeometry(QtCore.QRect(20, 2 * ch_distance, 230, 17))
        self.CH_StartMinimized.setText(translate("Start minimized"))
        self.CH_StartMinimized.setToolTip(translate("The app will start minimized"))

        # Enable logging
        self.CH_EnableLogging = QtWidgets.QCheckBox(self)
        self.CH_EnableLogging.setGeometry(QtCore.QRect(20, 4 * ch_distance, 230, 17))
        self.CH_EnableLogging.setText(translate("Enable logging"))
        self.CH_EnableLogging.setToolTip(translate("App logs will be saved into a text file"))

        # Show session hidden
        self.CH_ShowSession = QtWidgets.QCheckBox(self)
        self.CH_ShowSession.setGeometry(QtCore.QRect(20, 5 * ch_distance, 300, 17))
        self.CH_ShowSession.setText(translate("Show session stats"))
        self.CH_ShowSession.setToolTip(translate("Shows how many games you played and won in the current session on the overlay"))

        # Show player winrate and notes
        self.CH_ShowPlayerWinrates = QtWidgets.QCheckBox(self)
        self.CH_ShowPlayerWinrates.setGeometry(QtCore.QRect(20, 6 * ch_distance, 230, 17))
        self.CH_ShowPlayerWinrates.setText(translate("Show player winrates and notes"))
        self.CH_ShowPlayerWinrates.setToolTip(translate(
            "The number of games and winrate you had with your ally will be shown when a game starts.\nPlayer note will show as well if specified. Requires restart to enable."
        ))

        # Language selection
        self.LA_Language = QtWidgets.QLabel(self)
        self.LA_Language.setGeometry(QtCore.QRect(20, 7 * ch_distance, 60, 17))
        self.LA_Language.setText(translate("Language"))
        self.LA_Language.setToolTip(translate("Select interface language"))
        
        self.CB_Language = QtWidgets.QComboBox(self)
        self.CB_Language.setGeometry(QtCore.QRect(85, 7 * ch_distance - 2, 120, 22))
        self.CB_Language.addItems(["简体中文", "English"])
        self.CB_Language.setToolTip("Select interface language / 选择界面语言")
        self.CB_Language.currentIndexChanged.connect(self.p.change_language)

        # Mnimized when clicked
        self.CH_MinimizeToTray = QtWidgets.QCheckBox(self)
        self.CH_MinimizeToTray.setGeometry(QtCore.QRect(20, 3 * ch_distance, 300, 17))
        self.CH_MinimizeToTray.setText(translate("Minimize to tray"))
        self.CH_MinimizeToTray.setToolTip(translate("On closing the app will minimize to tray. The app can be closed there."))

        # Duration
        self.SP_Duration = QtWidgets.QSpinBox(self)
        self.SP_Duration.setGeometry(QtCore.QRect(250, 20, 42, 22))

        self.LA_Duration = QtWidgets.QLabel(self)
        self.LA_Duration.setGeometry(QtCore.QRect(300, 20, 191, 21))
        self.LA_Duration.setText(translate("Duration"))
        self.LA_Duration.setToolTip(translate("How long the overlay will show after a new game is analysed."))

        # Monitor
        self.SP_Monitor = QtWidgets.QSpinBox(self)
        self.SP_Monitor.setGeometry(QtCore.QRect(360, 20, 42, 22))
        self.SP_Monitor.setMinimum(1)
        self.SP_Monitor.setToolTip(translate("Determines on which monitor the overlay will be shown"))

        self.LA_Monitor = QtWidgets.QLabel(self)
        self.LA_Monitor.setGeometry(QtCore.QRect(410, 20, 47, 20))
        self.LA_Monitor.setText(translate("Monitor"))
        self.LA_Monitor.setToolTip(translate("Determines on which monitor the overlay will be shown"))

        # Charts
        self.CH_ShowCharts = QtWidgets.QCheckBox(self)
        self.CH_ShowCharts.setGeometry(QtCore.QRect(250, 3 * ch_distance, 300, 17))
        self.CH_ShowCharts.setText(translate("Show charts"))
        self.CH_ShowCharts.setToolTip(translate("Show charts on overlay"))
        self.CH_ShowCharts.setText("Show charts")
        self.CH_ShowCharts.setToolTip("Show charts on overlay")
        self.CH_ShowCharts.clicked.connect(self.p.show_charts)

        # Dark theme
        self.CH_DarkTheme = QtWidgets.QCheckBox(self)
        self.CH_DarkTheme.setGeometry(QtCore.QRect(250, 4 * ch_distance, 300, 17))
        self.CH_DarkTheme.setText("Dark theme")
        self.CH_DarkTheme.setToolTip("Enables dark theme. Requires restart!")
        self.CH_DarkTheme.stateChanged.connect(self.p.change_theme)

        # Fast expand
        self.CH_FastExpand = QtWidgets.QCheckBox(self)
        self.CH_FastExpand.setGeometry(QtCore.QRect(250, 5 * ch_distance, 300, 17))
        self.CH_FastExpand.setText("Fast expand hints")
        self.CH_FastExpand.setToolTip("Show fast expand hint dialogue when a new game starts.\n"
                                      f"maps: {', '.join(FastExpandSelector.valid_maps)}\n"
                                      f"commanders: {', '.join(FastExpandSelector.valid_commanders)}")

        # Force hidden
        self.CH_ForceHideOverlay = QtWidgets.QCheckBox(self)
        self.CH_ForceHideOverlay.setGeometry(QtCore.QRect(250, 6 * ch_distance, 300, 17))
        self.CH_ForceHideOverlay.setText("Don\'t show overlay on-screen")
        self.CH_ForceHideOverlay.setToolTip(
            "The overlay won't show directly on your screen. You can use this setting\nfor example when it's meant to be visible only on stream.")

        # Replay folder
        self.LA_AccountFolder = QtWidgets.QLabel(self)
        self.LA_AccountFolder.setGeometry(QtCore.QRect(520, 15, 350, 16))
        self.LA_AccountFolder.setText("Change locations of StarCraft II account folder and screenshot folder")

        self.BT_ChooseFolder = QtWidgets.QPushButton(self)
        self.BT_ChooseFolder.setGeometry(QtCore.QRect(520, 36, 150, 25))
        self.BT_ChooseFolder.setText('Account folder')
        self.BT_ChooseFolder.setToolTip(
            'Choose your account folder.\nThis is usually not necessary and the app will find its location automatically.')
        self.BT_ChooseFolder.clicked.connect(self.p.findReplayFolder)

        self.LA_CurrentReplayFolder = QtWidgets.QLabel(self)
        self.LA_CurrentReplayFolder.setEnabled(False)
        self.LA_CurrentReplayFolder.setGeometry(QtCore.QRect(520, 53, 400, 31))

        # Screenshot folder
        self.BT_ScreenshotLocation = QtWidgets.QPushButton(self)
        self.BT_ScreenshotLocation.setGeometry(QtCore.QRect(520, 90, 150, 25))
        self.BT_ScreenshotLocation.setText('Screenshot folder')
        self.BT_ScreenshotLocation.setToolTip('Choose the folder where screenshots are saved')
        self.BT_ScreenshotLocation.clicked.connect(self.p.chooseScreenshotFolder)

        self.LA_ScreenshotLocation = QtWidgets.QLabel(self)
        self.LA_ScreenshotLocation.setEnabled(False)
        self.LA_ScreenshotLocation.setGeometry(QtCore.QRect(520, 108, 400, 31))

        # Info label
        self.LA_InfoLabel = QtWidgets.QLabel(self)
        self.LA_InfoLabel.setGeometry(QtCore.QRect(20, 560, 800, 20))

        # Apply
        self.BT_MainApply = QtWidgets.QPushButton(self)
        self.BT_MainApply.setGeometry(QtCore.QRect(867, 400, 75, 25))
        self.BT_MainApply.setText('Apply')
        self.BT_MainApply.clicked.connect(self.p.saveSettings)

        # Reset
        self.BT_MainReset = QtWidgets.QPushButton(self)
        self.BT_MainReset.setGeometry(QtCore.QRect(785, 400, 75, 25))
        self.BT_MainReset.setText('Reset')
        self.BT_MainReset.clicked.connect(self.p.resetSettings)
        self.BT_MainReset.setToolTip("Resets all settings on this tab apart from login for starcraft2coop.com")

        # Screenshot
        self.BT_Screenshot = QtWidgets.QPushButton(self)
        self.BT_Screenshot.setGeometry(QtCore.QRect(19, 400, 157, 40))
        self.BT_Screenshot.setText('Overlay screenshot')
        self.BT_Screenshot.setToolTip('Take screenshot of the overlay and save it on your desktop or chosen location')
        self.BT_Screenshot.clicked.connect(self.p.save_screenshot)

        # Create desktop shortcut

        self.BT_Desktop_shortcut = QtWidgets.QPushButton(self)
        self.BT_Desktop_shortcut.setGeometry(QtCore.QRect(351, 400, 157, 40))
        self.BT_Desktop_shortcut.setText('Create desktop shortcut')
        self.BT_Desktop_shortcut.clicked.connect(HF.create_shortcut)

        if not AF.isWindows() or not AF.isFrozen():
            self.BT_Desktop_shortcut.setDisabled(True)
            self.BT_Desktop_shortcut.setToolTip("Only available when the app is packaged and on Windows")

        ### Hotkey frame
        self.FR_HotkeyFrame = QtWidgets.QFrame(self)
        self.FR_HotkeyFrame.setGeometry(QtCore.QRect(20, 170, 411, 211))
        self.FR_HotkeyFrame.setAutoFillBackground(True)
        self.FR_HotkeyFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_HotkeyFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        # Label
        self.LA_Hotkeys = QtWidgets.QLabel(self.FR_HotkeyFrame)
        self.LA_Hotkeys.setGeometry(QtCore.QRect(0, 10, 411, 20))
        self.LA_Hotkeys.setStyleSheet("font-weight: bold")
        self.LA_Hotkeys.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_Hotkeys.setText(translate("Hotkeys"))

        # Show/hide
        self.BT_ShowHide = QtWidgets.QPushButton(self.FR_HotkeyFrame)
        self.BT_ShowHide.setGeometry(QtCore.QRect(19, 50, 115, 25))
        self.BT_ShowHide.setText(translate("Show / Hide"))
        self.BT_ShowHide.clicked.connect(MF.keyboard_SHOWHIDE)

        self.KEY_ShowHide = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_ShowHide.setGeometry(QtCore.QRect(20, 80, 113, 20))
        self.KEY_ShowHide.setToolTip(translate('The key for both showing and hiding the overlay'))
        self.KEY_ShowHide.keySequenceChanged.connect(self.p.hotkey_changed)

        # Show
        self.BT_Show = QtWidgets.QPushButton(self.FR_HotkeyFrame)
        self.BT_Show.setGeometry(QtCore.QRect(149, 50, 115, 25))
        self.BT_Show.setText(translate("Show"))
        self.BT_Show.clicked.connect(MF.keyboard_SHOW)

        self.KEY_Show = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Show.setGeometry(QtCore.QRect(150, 80, 113, 20))
        self.KEY_Show.setToolTip(translate('The key for just showing the overlay'))
        self.KEY_Show.keySequenceChanged.connect(self.p.hotkey_changed)

        # Hide
        self.BT_Hide = QtWidgets.QPushButton(self.FR_HotkeyFrame)
        self.BT_Hide.setGeometry(QtCore.QRect(279, 50, 115, 25))
        self.BT_Hide.setText(translate("Hide"))
        self.BT_Hide.clicked.connect(MF.keyboard_HIDE)

        self.KEY_Hide = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Hide.setGeometry(QtCore.QRect(280, 80, 113, 20))
        self.KEY_Hide.setToolTip(translate('The key for just hiding the overlay'))
        self.KEY_Hide.keySequenceChanged.connect(self.p.hotkey_changed)

        # Newer
        self.BT_Newer = QtWidgets.QPushButton(self.FR_HotkeyFrame)
        self.BT_Newer.setGeometry(QtCore.QRect(19, 120, 115, 25))
        self.BT_Newer.setText(translate("Show newer replay"))
        self.BT_Newer.clicked.connect(MF.keyboard_NEWER)

        self.KEY_Newer = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Newer.setGeometry(QtCore.QRect(20, 150, 113, 20))
        self.KEY_Newer.setToolTip(translate('The key for showing a newer replay than is currently displayed'))
        self.KEY_Newer.keySequenceChanged.connect(self.p.hotkey_changed)

        # Older
        self.BT_Older = QtWidgets.QPushButton(self.FR_HotkeyFrame)
        self.BT_Older.setGeometry(QtCore.QRect(149, 120, 115, 25))
        self.BT_Older.setText(translate("Show older replay"))
        self.BT_Older.clicked.connect(MF.keyboard_OLDER)

        self.KEY_Older = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Older.setGeometry(QtCore.QRect(150, 150, 113, 20))
        self.KEY_Older.setToolTip(translate('The key for showing an older replay than is currently displayed'))
        self.KEY_Older.keySequenceChanged.connect(self.p.hotkey_changed)

        # Winrates
        self.BT_Winrates = QtWidgets.QPushButton(self.FR_HotkeyFrame)
        self.BT_Winrates.setGeometry(QtCore.QRect(279, 120, 115, 25))
        self.BT_Winrates.setText(translate("Show player info"))
        self.BT_Winrates.clicked.connect(MF.keyboard_PLAYERWINRATES)
        self.BT_Winrates.setToolTip(translate('The key for showing the last player winrates and notes'))

        self.KEY_Winrates = MUI.CustomKeySequenceEdit(self.FR_HotkeyFrame)
        self.KEY_Winrates.setGeometry(QtCore.QRect(280, 150, 113, 20))
        self.KEY_Winrates.setToolTip(translate('The key for showing the last player winrates and notes'))
        self.KEY_Winrates.keySequenceChanged.connect(self.p.hotkey_changed)

        # Colors
        self.FR_CustomizeColors = QtWidgets.QFrame(self)
        self.FR_CustomizeColors.setGeometry(QtCore.QRect(445, 170, 241, 211))
        self.FR_CustomizeColors.setAutoFillBackground(True)
        self.FR_CustomizeColors.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_CustomizeColors.setFrameShadow(QtWidgets.QFrame.Plain)

        # Customize colors
        self.LA_CustomizeColors = QtWidgets.QLabel(self.FR_CustomizeColors)
        self.LA_CustomizeColors.setGeometry(QtCore.QRect(0, 10, 241, 20))
        self.LA_CustomizeColors.setStyleSheet("font-weight: bold")
        self.LA_CustomizeColors.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_CustomizeColors.setText("Customize colors")

        # Note
        self.LA_More = QtWidgets.QLabel(self.FR_CustomizeColors)
        self.LA_More.setEnabled(False)
        self.LA_More.setGeometry(QtCore.QRect(0, 19, 241, 31))
        self.LA_More.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_More.setText("more via editing custom.css")

        color_x_offset = 50
        color_height = 20
        color_width = 140

        self.LA_P1 = QtWidgets.QPushButton(self.FR_CustomizeColors)
        self.LA_P1.setGeometry(QtCore.QRect(color_x_offset, 70, color_width, color_height))
        self.LA_P1.clicked.connect(lambda: self.openColorDialog(self.LA_P1))

        self.LA_P2 = QtWidgets.QPushButton(self.FR_CustomizeColors)
        self.LA_P2.setGeometry(QtCore.QRect(color_x_offset, 100, color_width, color_height))
        self.LA_P2.clicked.connect(lambda: self.openColorDialog(self.LA_P2))

        self.LA_Amon = QtWidgets.QPushButton(self.FR_CustomizeColors)
        self.LA_Amon.setGeometry(QtCore.QRect(color_x_offset, 130, color_width, color_height))
        self.LA_Amon.clicked.connect(lambda: self.openColorDialog(self.LA_Amon))

        self.LA_Mastery = QtWidgets.QPushButton(self.FR_CustomizeColors)
        self.LA_Mastery.setGeometry(QtCore.QRect(color_x_offset, 160, color_width, color_height))
        self.LA_Mastery.clicked.connect(lambda: self.openColorDialog(self.LA_Mastery))

        # Aom
        self.FR_Aom = QtWidgets.QFrame(self)
        self.FR_Aom.setGeometry(QtCore.QRect(700, 170, 241, 211))
        self.FR_Aom.setAutoFillBackground(True)
        self.FR_Aom.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FR_Aom.setFrameShadow(QtWidgets.QFrame.Plain)

        self.LA_AomPage = QtWidgets.QLabel(self.FR_Aom)
        self.LA_AomPage.setGeometry(QtCore.QRect(0, 10, 241, 20))
        self.LA_AomPage.setStyleSheet("font-weight: bold")
        self.LA_AomPage.setAlignment(QtCore.Qt.AlignCenter)
        self.LA_AomPage.setText("Settings for starcraft2coop.com")

        self.ED_AomAccount = QtWidgets.QLineEdit(self.FR_Aom)
        self.ED_AomAccount.setGeometry(QtCore.QRect(62, 70, 121, 20))
        self.ED_AomAccount.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_AomAccount.setPlaceholderText("account name")

        self.ED_AomSecretKey = QtWidgets.QLineEdit(self.FR_Aom)
        self.ED_AomSecretKey.setGeometry(QtCore.QRect(62, 100, 121, 20))
        self.ED_AomSecretKey.setAlignment(QtCore.Qt.AlignCenter)
        self.ED_AomSecretKey.setPlaceholderText("secret key")
        self.ED_AomSecretKey.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)

        self.BT_AomTest = QtWidgets.QPushButton(self.FR_Aom)
        self.BT_AomTest.setGeometry(QtCore.QRect(75, 160, 85, 25))
        self.BT_AomTest.clicked.connect(self.validateAOM)
        self.BT_AomTest.setText("Verify")
        self.BT_AomTest.setToolTip("Test if the combination of the account name and the secret key is valid")

        # Manual parse
        self.BT_ManualParse = QtWidgets.QPushButton(self)
        self.BT_ManualParse.setGeometry(QtCore.QRect(185, 400, 157, 40))
        self.BT_ManualParse.setText("Parse replay")
        self.BT_ManualParse.setToolTip("Parse selected replay, show it on the overlay, and save data to a json file.")
        self.BT_ManualParse.clicked.connect(self.parse_replay)

        # Paypal
        x = 835
        y = 520
        self.IMG_Front_Donate = QtWidgets.QLabel(self)
        self.IMG_Front_Donate.setGeometry(QtCore.QRect(835, y, 145, 50))
        self.IMG_Front_Donate.setPixmap(QtGui.QPixmap(innerPath("src/paypal.png")))
        self.IMG_Front_Donate.setGraphicsEffect(MUI.get_shadow())

        self.BT_Front_Donate = QtWidgets.QPushButton(self)
        self.BT_Front_Donate.setGeometry(QtCore.QRect(x - 5, y, 140, 50))
        self.BT_Front_Donate.clicked.connect(self.paypal_clicked)
        self.BT_Front_Donate.setStyleSheet("QPushButton {border: 0px; background: transparent}")
        self.BT_Front_Donate.setToolTip(f'Donate to support this app')

        # Version
        self.LA_Version = QtWidgets.QLabel(self)
        self.LA_Version.setGeometry(QtCore.QRect(825, 560, 141, 20))
        self.LA_Version.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing)
        self.LA_Version.setText(f"The app is up to date (v{str(APPVERSION)[0]}.{str(APPVERSION)[1:]})")
        self.LA_Version.setEnabled(False)

    def openColorDialog(self, button):
        """ Color picker. After the color is picked, color is saved into settings, and button updated (text and color) """
        button_dict = {self.LA_P1: 'Player 1', self.LA_P2: 'Player 2', self.LA_Amon: '  Amon', self.LA_Mastery: 'Mastery'}
        settings_dict = {self.LA_P1: 'color_player1', self.LA_P2: 'color_player2', self.LA_Amon: 'color_amon', self.LA_Mastery: 'color_mastery'}

        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            button.setText(f"{button_dict.get(button,'')} | {color.name()}")
            button.setStyleSheet(f'background-color: {color.name()}; color: black')
            SM.settings[settings_dict[button]] = color.name()
            MF.update_init_message()
            MF.resend_init_message()

    def validateAOM(self):
        """ Validates if name/key combination is valid """
        key = self.ED_AomSecretKey.text()
        account = self.ED_AomAccount.text()

        if key != '' and account != '':
            response = HF.validate_aom_account_key(account, key)

            if 'Success' in response:
                self.p.sendInfoMessage(response, color=MColors.msg_success)
            else:
                self.p.sendInfoMessage(response, color=MColors.msg_failure)
        else:
            self.p.sendInfoMessage('Fill your account name and secret key first!')

    @catch_exceptions(logger)
    def parse_replay(self, something):
        """ Lets the user choose the replay, parses it and shows it on overlay
        Second argument passed by PyQt5, needs to be here for to pass the correct number of arguments"""
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_():
            f = dialog.selectedFiles()[0]

            if not f.endswith('.SC2Replay'):
                self.p.sendInfoMessage("Not a valid replay file!", color=MColors.msg_failure)
                return

            output = MF.show_overlay(f, add_replay=False)
            if isinstance(output, dict):
                with open(f.replace('.SC2Replay', '.json'), 'w') as outfile:
                    json.dump(output, outfile, indent=2)
            elif output == 'Error':
                self.p.sendInfoMessage("Failed to parse the replay file!", color=MColors.msg_failure)

    @staticmethod
    def paypal_clicked():
        webbrowser.open("https://www.paypal.com/paypalme/FluffyMaguro")

    def set_status(self, message, color=None):
        """设置状态栏信息
        
        参数:
        message - 要显示的消息
        color - 消息颜色 (可选)
        """
        self.LA_InfoLabel.setText(message)
        self.LA_InfoLabel.setStyleSheet(f'color: {color if color is not None else MColors.msg}')
