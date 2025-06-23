"""
Main module for StarCraft II Co-op Overlay.

Causal chain:
Setup -> Load Settings -> UI
                       -> Server manager for websockets (thread)
                       -> Check replays (loop of threads)
                       -> Twitch bot (thread)
                       -> Mass replay analysis -> checking for new games (thread)
                                               -> Generate stats (function)
                       -> keyboard threads (keyboard module)
                       -> thread for checking wake status

This is my first big project, so there is a mix of very old code and new one.
Overall it's messy with a lot of coupling, not enough separation between UI and 
core functinality, and similar issues. It's a great learning experience nevertheless.

"""
import importlib
import json
import os
import platform
import shutil
import sys
import threading
import traceback
import urllib.request
from datetime import datetime
from functools import partial
from multiprocessing import freeze_support
from types import TracebackType
from typing import Type

import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets

import SCOFunctions.AppFunctions as AF
import SCOFunctions.HelperFunctions as HF
import SCOFunctions.MainFunctions as MF
import SCOFunctions.MassReplayAnalysis as MR
import SCOFunctions.MUserInterface as MUI
import SCOFunctions.Tabs as Tabs
from SCOFunctions.FastExpand import FastExpandSelector
from SCOFunctions.MFilePath import innerPath, truePath
from SCOFunctions.MLogging import Logger, catch_exceptions
from SCOFunctions.MTheming import MColors, set_dark_theme
from SCOFunctions.MTranslation import translate, translate_widget_recursive
from SCOFunctions.Settings import Setting_manager as SM

logger = Logger('SCO', Logger.levels.INFO)
Logger.file_path = truePath("Logs.txt")

APPVERSION = 247


def excepthook(exc_type: Type[BaseException], exc_value: Exception, exc_tback: TracebackType):
    """ Provides the top-most exception handling. Logs unhandled exceptions and cleanly shuts down the app."""
    # Log the exception
    try:
        s = "".join(traceback.format_exception(exc_type, exc_value, exc_tback))
        logger.error(f"Unhandled exception!\n{s}")
    except Exception:
        logger.error("Failed to log error!!!")

    # Try to save settings
    try:
        ui.saveSettings()
    except Exception:
        logger.error("Failed to save settings.")

    # Shut down other threads
    try:
        TabWidget.tray_icon.hide()
        ui.stop_full_analysis()
        MF.stop_threads()
    except Exception:
        logger.error("Failed to order the app to stop checking api")
    sys.exit()


sys.excepthook = excepthook


class Signal_Manager(QtCore.QObject):
    """ 
    Small object for emiting signals.

    Through this object non-PyQt threads can safely interact with PyQt.
    Threads can emit signals and some method connected to this signal 
    will be called in the primary PyQt thread.
    
    """
    pass


class MultipleInstancesRunning(Exception):
    """ Custom exception for multiple instance of the app running"""
    pass


class UI_TabWidget(object):

    def setupUI(self, TabWidget: MUI.CustomQTabWidget):
        TabWidget.setWindowTitle(f"StarCraft Co-op Overlay (v{str(APPVERSION)[0]}.{str(APPVERSION)[1:]})")
        TabWidget.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        TabWidget.setFixedSize(980, 610)
        TabWidget.tray_icon.setToolTip(f'StarCraft Co-op Overlay')

        self.signal_manager = Signal_Manager()
        self.write_permissions = True

        # Tabs
        self.TAB_Main = Tabs.MainTab(self, APPVERSION)
        self.TAB_Players = Tabs.PlayerTab(self, TabWidget)
        self.TAB_Games = Tabs.GameTab(self, TabWidget)
        self.TAB_Stats = Tabs.StatsTab(self)
        self.TAB_Links = Tabs.LinkTab(self)
        self.TAB_Mutations = Tabs.MutationTab(TabWidget)
        self.TAB_MutatorStats = Tabs.MutatorStatsTab()
        self.TAB_CustomMaps = Tabs.CustomMapsTab()

        # Add tabs to the widget
        TabWidget.addTab(self.TAB_Main, "Settings")
        TabWidget.addTab(self.TAB_Games, "Games")
        TabWidget.addTab(self.TAB_Players, "Players")
        TabWidget.addTab(self.TAB_Mutations, "Weeklies")
        TabWidget.addTab(self.TAB_MutatorStats, "突变因子统计")
        TabWidget.addTab(self.TAB_CustomMaps, "自定义地图")
        TabWidget.addTab(self.TAB_Stats, "Statistics")
        TabWidget.addTab(self.TAB_Links, "Links")

        QtCore.QMetaObject.connectSlotsByName(TabWidget)

        if not AF.isWindows():
            self.TAB_Main.CH_StartWithWindows.setChecked(False)
            self.TAB_Main.CH_StartWithWindows.setEnabled(False)

        self.FastExpandSelector = None
        self.CAnalysis = None
        
        # 应用中文翻译
        self.apply_translation(TabWidget)

    def apply_translation(self, TabWidget):
        """应用中文翻译到整个界面"""
        # 翻译窗口标题
        TabWidget.setWindowTitle(translate(f"StarCraft Co-op Overlay (v{str(APPVERSION)[0]}.{str(APPVERSION)[1:]})"))
        TabWidget.tray_icon.setToolTip(translate('StarCraft Co-op Overlay'))
        
        # 翻译标签页标题
        for i in range(TabWidget.count()):
            tab_text = TabWidget.tabText(i)
            TabWidget.setTabText(i, translate(tab_text))
            
        # 递归翻译每个标签页的所有控件
        translate_widget_recursive(self.TAB_Main)
        translate_widget_recursive(self.TAB_Players)
        translate_widget_recursive(self.TAB_Games)
        translate_widget_recursive(self.TAB_Stats)
        translate_widget_recursive(self.TAB_Links)
        translate_widget_recursive(self.TAB_Mutations)
        translate_widget_recursive(self.TAB_MutatorStats)
        translate_widget_recursive(self.TAB_CustomMaps)

    def loadSettings(self):
        """ Loads settings from the config file if there is any, updates UI elements accordingly"""
        self.downloading = False

        SM.load_settings(truePath('Settings.json'))

        # Check for multiple instances
        if SM.settings['check_for_multiple_instances'] and AF.isWindows():
            if HF.app_running_multiple_instances():
                logger.error('App running at multiple instances. Closing!')
                raise MultipleInstancesRunning

        # Update fix font size
        font = QtGui.QFont()
        if AF.isWindows():
            font.fromString(f"MS Shell Dlg 2,{8.25*SM.settings['font_scale']},-1,5,50,0,0,0,0,0")
        else:
            font.setPointSize(font.pointSize() * SM.settings['font_scale'])
        app.setFont(font)

        # Charts
        SM.width_for_graphs()

        # Dark theme
        if SM.settings['dark_theme']:
            set_dark_theme(self, app, TabWidget, APPVERSION)

        # 设置用户账户文件夹路径
        onedrive_path = r'C:\Users\11727\OneDrive\Documents\StarCraft II\Accounts'
        if os.path.isdir(onedrive_path):
            SM.settings['account_folder'] = onedrive_path
            logger.info(f"设置账户文件夹为: {onedrive_path}")
        else:
            # 检查默认路径是否有效，如果无效则尝试查找
            SM.settings['account_folder'] = HF.get_account_dir(SM.settings['account_folder'])

        # Screenshot folder
        if SM.settings['screenshot_folder'] in {None, ''} or not os.path.isdir(SM.settings['screenshot_folder']):
            SM.settings['screenshot_folder'] = os.path.normpath(os.path.join(os.path.expanduser('~'), 'Desktop'))

        self.updateUI()
        self.check_for_updates()

        if SM.settings['start_minimized']:
            TabWidget.hide()
            TabWidget.show_minimize_message()
        else:
            TabWidget.show()

        # Check write permissions
        self.write_permissions = HF.write_permission_granted()
        if not self.write_permissions:
            self.sendInfoMessage('Permission denied. Add an exception to your anti-virus for this folder. Sorry', color=MColors.msg_failure)

        Logger.LOGGING = SM.settings['enable_logging'] if self.write_permissions else False

        self.manage_keyboard_threads()

        self.full_analysis_running = False

        # Delete install bat if it's there. Show patchnotes
        if os.path.isfile(truePath('install.bat')):
            os.remove(truePath('install.bat'))
            self.show_patchnotes()

    def show_patchnotes(self):
        """ Shows a widget with the lastest patchnotes.
        Usually shown only after an update (after deleting install.bat)"""
        try:
            file = innerPath('src/patchnotes.json')
            if not os.path.isfile(file):
                return

            with open(file, 'r') as f:
                patchnotes = json.load(f)

            patchnotes = patchnotes.get(str(APPVERSION), None)

            if patchnotes is None:
                return
            if len(patchnotes) == 0:
                return

            self.WD_patchnotes = MUI.PatchNotes(APPVERSION, patchnotes=patchnotes, icon=QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        except Exception:
            logger.error(traceback.format_exc())

    def check_for_updates(self):
        """ Checks for updates and changes UI accordingly"""

        # Skip if there is already a button (perhaps we have awoken and there is still an update ready)
        if hasattr(self, "BT_NewUpdate"):
            return

        self.new_version = HF.new_version(APPVERSION)

        if not self.new_version:
            return

        TabWidget.show_update_message()
        self.TAB_Main.LA_Version.setText('New version available!')

        # Create button
        self.BT_NewUpdate = QtWidgets.QPushButton(self.TAB_Main)
        self.BT_NewUpdate.setGeometry(QtCore.QRect(351, 400, 157, 40))
        self.BT_NewUpdate.setText('Download update')
        self.BT_NewUpdate.setStyleSheet('font-weight: bold; background-color: #5BD3C4; color: black')
        self.BT_NewUpdate.clicked.connect(self.start_download)
        self.BT_NewUpdate.show()

        # Check if it's already downloaded
        save_path = truePath(f'Updates\\{self.new_version["link"].split("/")[-1]}')

        if not AF.isWindows():
            self.sendInfoMessage('Update available', color=MColors.msg_success)
            return

        if os.path.isfile(save_path):
            self.update_is_ready_for_install()
        else:
            self.PB_download = QtWidgets.QProgressBar(self.TAB_Main)
            self.PB_download.setGeometry(21, 569, 830, 10)
            self.PB_download.hide()

    def start_download(self):
        """ Starts downloading an update"""
        if self.downloading:
            return

        self.downloading = True
        self.BT_NewUpdate.setText('Downloading')
        self.BT_NewUpdate.setEnabled(False)
        self.BT_NewUpdate.setStyleSheet('font-weight: bold; background-color: #CCCCCC')
        self.BT_NewUpdate.clicked.disconnect()
        self.PB_download.show()

        if not os.path.isdir(truePath('Updates')):
            os.mkdir(truePath('Updates'))

        save_path = truePath(f'Updates\\{self.new_version["link"].split("/")[-1]}')
        urllib.request.urlretrieve(self.new_version["link"], save_path, self.download_progress_bar_updater)

    def download_progress_bar_updater(self, blocknum, blocksize, totalsize):
        """ Updates the progress bar accordingly"""
        readed_data = blocknum * blocksize

        if totalsize > 0:
            download_percentage = readed_data * 100 / totalsize
            self.PB_download.setValue(int(download_percentage))
            QtWidgets.QApplication.processEvents()

            if download_percentage >= 100:
                self.update_is_ready_for_install()
                self.downloading = False

    def update_is_ready_for_install(self):
        """ Changes button text and connect it to another function"""
        self.BT_NewUpdate.setText('Restart and update')
        self.BT_NewUpdate.setEnabled(True)
        self.BT_NewUpdate.setStyleSheet('font-weight: bold; background-color: #5BD3C4; color: black')
        try:
            self.BT_NewUpdate.clicked.disconnect()
        except Exception:
            pass
        self.BT_NewUpdate.clicked.connect(self.install_update)

    def install_update(self):
        """ Starts the installation """
        archive = truePath(f'Updates\\{self.new_version["link"].split("/")[-1]}')
        where_to_extract = truePath('Updates\\New')
        app_folder = truePath('')

        # Check hash
        file_hash = HF.get_hash(archive, sha=True)
        if self.new_version["hash"] != file_hash:
            os.remove(archive)
            logger.error(f'Incorrect hash: {self.new_version["hash"]} != {file_hash}')
            self.sendInfoMessage("Error! Incorrect hash for the downloaded archive.", color=MColors.msg_failure)
            self.BT_NewUpdate.clicked.disconnect()
            self.BT_NewUpdate.clicked.connect(self.start_download)
            self.BT_NewUpdate.setText('Download update')
            return

        # Delete previously extracted archive
        if os.path.isdir(where_to_extract):
            shutil.rmtree(where_to_extract)

        # Extract archive
        HF.extract_archive(archive, where_to_extract)

        # Create and run install.bat file
        installfile = truePath('install.bat')
        with open(installfile, 'w') as f:
            f.write('\n'.join(('@echo off',
                                'echo Installation will start shortly...',
                                'timeout /t 7 /nobreak > NUL',
                                # Copy files
                                f'robocopy "{where_to_extract}" "{os.path.abspath(app_folder)}" /E',
                                'timeout /t 7 /nobreak > NUL',
                                # Remove old directory
                                f'rmdir /s /q "{truePath("Updates")}"',
                                'echo Installation completed...',
                                # Start application
                                f'"{truePath("SCO.exe")}"'
                                ))) # yapf: disable

        self.saveSettings()
        os.startfile(installfile)
        app.quit()

    def updateUI(self):
        """ Update UI elements based on the current settings """
        self.TAB_Main.CH_StartWithWindows.setChecked(SM.settings['start_with_windows'])
        self.TAB_Main.CH_StartMinimized.setChecked(SM.settings['start_minimized'])
        self.TAB_Main.CH_EnableLogging.setChecked(SM.settings['enable_logging'])
        self.TAB_Main.CH_ShowPlayerWinrates.setChecked(SM.settings['show_player_winrates'])
        self.TAB_Main.CH_ForceHideOverlay.setChecked(SM.settings['force_hide_overlay'])
        self.TAB_Main.CH_ShowCharts.setChecked(SM.settings['show_charts'])
        self.TAB_Main.CH_DarkTheme.setChecked(SM.settings['dark_theme'])
        self.TAB_Main.CH_FastExpand.setChecked(SM.settings['fast_expand'])
        self.TAB_Main.CH_MinimizeToTray.setChecked(SM.settings['minimize_to_tray'])
        self.TAB_Main.CH_MinimizeToTray.stateChanged.connect(self.saveSettings)
        self.TAB_Main.SP_Duration.setProperty("value", SM.settings['duration'])
        self.TAB_Main.SP_Monitor.setProperty("value", SM.settings['monitor'])
        self.TAB_Main.LA_CurrentReplayFolder.setText(SM.settings['account_folder'])
        self.TAB_Main.LA_ScreenshotLocation.setText(SM.settings['screenshot_folder'])
        self.TAB_Main.CH_ShowSession.setChecked(SM.settings['show_session'])

        self.TAB_Main.KEY_ShowHide.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_show/hide']))
        self.TAB_Main.KEY_Show.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_show']))
        self.TAB_Main.KEY_Hide.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_hide']))
        self.TAB_Main.KEY_Newer.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_newer']))
        self.TAB_Main.KEY_Older.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_older']))
        self.TAB_Main.KEY_Winrates.setKeySequence(QtGui.QKeySequence.fromString(SM.settings['hotkey_winrates']))

        self.TAB_Main.ED_AomAccount.setText(SM.settings['aom_account'])
        self.TAB_Main.ED_AomSecretKey.setText(SM.settings['aom_secret_key'])

        self.TAB_Main.LA_P1.setText(f"Player 1 | {SM.settings['color_player1']}")
        self.TAB_Main.LA_P1.setStyleSheet(f"background-color: {SM.settings['color_player1']}; color: black")
        self.TAB_Main.LA_P2.setText(f"Player 2 | {SM.settings['color_player2']}")
        self.TAB_Main.LA_P2.setStyleSheet(f"background-color: {SM.settings['color_player2']}; color: black")
        self.TAB_Main.LA_Amon.setText(f"  Amon | {SM.settings['color_amon']}")
        self.TAB_Main.LA_Amon.setStyleSheet(f"background-color: {SM.settings['color_amon']}; color: black")
        self.TAB_Main.LA_Mastery.setText(f"Mastery | {SM.settings['color_mastery']}")
        self.TAB_Main.LA_Mastery.setStyleSheet(f"background-color: {SM.settings['color_mastery']}; color: black")


        self.TAB_Stats.CH_FA_atstart.setChecked(SM.settings['full_analysis_atstart'])

    def saveSettings(self):
        """ Saves main settings in the settings file. """
        previous_settings = SM.settings.copy()

        self.save_playernotes_to_settings()

        SM.settings['start_with_windows'] = self.TAB_Main.CH_StartWithWindows.isChecked()
        SM.settings['start_minimized'] = self.TAB_Main.CH_StartMinimized.isChecked()
        SM.settings['enable_logging'] = self.TAB_Main.CH_EnableLogging.isChecked()
        SM.settings['show_player_winrates'] = self.TAB_Main.CH_ShowPlayerWinrates.isChecked()
        SM.settings['force_hide_overlay'] = self.TAB_Main.CH_ForceHideOverlay.isChecked()
        SM.settings['show_charts'] = self.TAB_Main.CH_ShowCharts.isChecked()
        SM.settings['dark_theme'] = self.TAB_Main.CH_DarkTheme.isChecked()
        SM.settings['fast_expand'] = self.TAB_Main.CH_FastExpand.isChecked()
        SM.settings['minimize_to_tray'] = self.TAB_Main.CH_MinimizeToTray.isChecked()
        SM.settings['show_session'] = self.TAB_Main.CH_ShowSession.isChecked()
        SM.settings['duration'] = self.TAB_Main.SP_Duration.value()
        SM.settings['monitor'] = self.TAB_Main.SP_Monitor.value()

        self.check_to_remove_hotkeys()
        SM.settings['hotkey_show/hide'] = self.TAB_Main.KEY_ShowHide.get_hotkey_string()
        SM.settings['hotkey_show'] = self.TAB_Main.KEY_Show.get_hotkey_string()
        SM.settings['hotkey_hide'] = self.TAB_Main.KEY_Hide.get_hotkey_string()
        SM.settings['hotkey_newer'] = self.TAB_Main.KEY_Newer.get_hotkey_string()
        SM.settings['hotkey_older'] = self.TAB_Main.KEY_Older.get_hotkey_string()
        SM.settings['hotkey_winrates'] = self.TAB_Main.KEY_Winrates.get_hotkey_string()

        SM.settings['aom_account'] = self.TAB_Main.ED_AomAccount.text()
        SM.settings['aom_secret_key'] = self.TAB_Main.ED_AomSecretKey.text()

        SM.settings['full_analysis_atstart'] = self.TAB_Stats.CH_FA_atstart.isChecked()
        
        SM.width_for_graphs()


        # Save settings
        SM.save_settings()

        # Message
        self.sendInfoMessage('Settings applied')

        # Check for overlapping hoykeys
        hotkeys = [
            SM.settings['hotkey_show/hide'], SM.settings['hotkey_show'], SM.settings['hotkey_hide'],
            SM.settings['hotkey_newer'], SM.settings['hotkey_older'], SM.settings['hotkey_winrates']
        ]

        hotkeys = [h for h in hotkeys if not h in {None, ''}]
        if len(hotkeys) > len(set(hotkeys)):
            self.sendInfoMessage('Warning: Overlapping hotkeys!', color=MColors.msg_failure)

        # Logging
        Logger.LOGGING = SM.settings['enable_logging'] if self.write_permissions else False

        # Update settings for other threads
        MF.update_init_message()

        # Compare
        changed_keys = set()
        for key in previous_settings:
            if previous_settings[key] != SM.settings[key] and not (previous_settings[key] is None and SM.settings[key] == ''):
                if key == 'aom_secret_key':
                    logger.info(f'Changed: {key}: ... → ...')
                else:
                    logger.info(f'Changed: {key}: {previous_settings[key]} → {SM.settings[key]}')
                changed_keys.add(key)

        # Registry
        if 'start_with_windows' in changed_keys:
            out = HF.add_to_startup(SM.settings['start_with_windows'])
            if out is not None:
                self.sendInfoMessage(f'Warning: {out}', color=MColors.msg_failure)
                SM.settings['start_with_windows'] = False
                self.TAB_Main.CH_StartWithWindows.setChecked(SM.settings['start_with_windows'])

        # Resend init message if duration has changed. Colors are handle in color picker.
        if 'duration' in changed_keys:
            MF.resend_init_message()

        # Monitor update
        if 'monitor' in changed_keys and hasattr(self, 'WebView'):
            self.set_WebView_size_location(SM.settings['monitor'])

        # Update keyboard threads
        self.manage_keyboard_threads(previous_settings=previous_settings)

        # Show/hide overlay
        if hasattr(self, 'WebView') and SM.settings['force_hide_overlay'] and self.WebView.isVisible():
            self.WebView.hide()
        elif hasattr(self, 'WebView') and not SM.settings['force_hide_overlay'] and not self.WebView.isVisible():
            self.WebView.show()

    def hotkey_changed(self):
        """ Wait a bit for the sequence to update, and then check if not to delete the key"""
        self.wait_ms(50)
        try:
            self.check_to_remove_hotkeys()
        except Exception:
            logger.error(traceback.format_exc())

    def check_to_remove_hotkeys(self):
        """ Checks if a key is 'Del' and sets it to None """
        key_dict = {
            self.TAB_Main.KEY_ShowHide: 'hotkey_show/hide',
            self.TAB_Main.KEY_Show: 'hotkey_show',
            self.TAB_Main.KEY_Hide: 'hotkey_hide',
            self.TAB_Main.KEY_Newer: 'hotkey_newer',
            self.TAB_Main.KEY_Older: 'hotkey_older',
            self.TAB_Main.KEY_Winrates: 'hotkey_winrates'
        }

        for key in key_dict:
            if key.keySequence().toString() == 'Del':
                key.setKeySequence(QtGui.QKeySequence.fromString(""))
                logger.info(f"Removed key for {key_dict[key]}")
                self.saveSettings()
                break

    def manage_keyboard_threads(self, previous_settings=None):
        """ Compares previous settings with current ones, and restarts keyboard threads if necessary.
        if `previous_settings` is None, then init hotkeys instead """
        hotkey_func_dict = {
            'hotkey_show/hide': MF.keyboard_SHOWHIDE,
            'hotkey_show': MF.keyboard_SHOW,
            'hotkey_hide': MF.keyboard_HIDE,
            'hotkey_newer': MF.keyboard_NEWER,
            'hotkey_older': MF.keyboard_OLDER,
            'hotkey_winrates': MF.keyboard_PLAYERWINRATES
        }

        # Init
        if previous_settings is None:
            self.hotkey_hotkey_dict = dict()
            for key in hotkey_func_dict:
                if not SM.settings[key] in {None, ''}:
                    try:
                        self.hotkey_hotkey_dict[key] = keyboard.add_hotkey(SM.settings[key], hotkey_func_dict[key])
                    except Exception:
                        logger.error(traceback.format_exc())
                        self.sendInfoMessage(f'Failed to initialize hotkey ({key.replace("hotkey_","")})! Try a different one.',
                                             color=MColors.msg_failure)
        # Update
        else:
            for key in hotkey_func_dict:
                # Update current value if the hotkey changed
                if previous_settings[key] != SM.settings[key] and not SM.settings[key] in {None, ''}:
                    if key in self.hotkey_hotkey_dict:
                        keyboard.remove_hotkey(self.hotkey_hotkey_dict[key])
                    try:
                        self.hotkey_hotkey_dict[key] = keyboard.add_hotkey(SM.settings[key], hotkey_func_dict[key])
                        logger.info(f'Changed hotkey of {key} to {SM.settings[key]}')
                    except Exception:
                        logger.error(f'Failed to change hotkey {key}\n{traceback.format_exc()}')

                # Remove current hotkey no value
                elif SM.settings[key] in {None, ''} and key in self.hotkey_hotkey_dict:
                    try:
                        keyboard.remove_hotkey(self.hotkey_hotkey_dict[key])
                        del self.hotkey_hotkey_dict[key]
                        logger.info(f'Removing hotkey of {key}')
                    except Exception:
                        logger.error(f'Failed to remove hotkey {key}\n{traceback.format_exc()}')

    def resetSettings(self):
        """ Resets settings to default values and updates UI """
        previous_settings = SM.settings.copy()
        SM.settings = SM.default_settings.copy()
        SM.settings['account_folder'] = HF.get_account_dir(path=SM.settings['account_folder'])
        SM.settings['screenshot_folder'] = previous_settings['screenshot_folder']
        SM.settings['aom_account'] = self.TAB_Main.ED_AomAccount.text()
        SM.settings['aom_secret_key'] = self.TAB_Main.ED_AomSecretKey.text()
        SM.settings['player_notes'] = previous_settings['player_notes']
        self.updateUI()
        self.saveSettings()
        self.sendInfoMessage('All settings have been reset!')
        MF.update_init_message()
        MF.resend_init_message()
        self.manage_keyboard_threads(previous_settings=previous_settings)

    def chooseScreenshotFolder(self):
        """ Changes screenshot folder location """
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory(SM.settings['screenshot_folder'])
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_():
            folder = os.path.normpath(dialog.selectedFiles()[0])
            logger.info(f'Changing screenshot_folder to {folder}')
            self.TAB_Main.LA_ScreenshotLocation.setText(folder)
            SM.settings['screenshot_folder'] = folder
            self.sendInfoMessage(f'Screenshot folder set succesfully! ({folder})', color=MColors.msg_success)

    def findReplayFolder(self):
        """ Finds and sets account folder """
        dialog = QtWidgets.QFileDialog()
        if not SM.settings['account_folder'] in {None, ''}:
            dialog.setDirectory(SM.settings['account_folder'])
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_():
            folder = dialog.selectedFiles()[0]
            if 'StarCraft' in folder and '/Accounts' in folder:
                logger.info(f'Changing accountdir to {folder}')
                SM.settings['account_folder'] = folder
                self.TAB_Main.LA_CurrentReplayFolder.setText(folder)
                self.sendInfoMessage(f'Account folder set succesfully! ({folder})', color=MColors.msg_success)
                MF.update_names_and_handles(folder, MF.AllReplays)
                if self.CAnalysis is not None:
                    self.updating_maps = QtWidgets.QWidget()
                    self.updating_maps.setWindowTitle('Adding replays')
                    self.updating_maps.setGeometry(700, 500, 300, 100)
                    self.updating_maps.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
                    self.updating_maps_label = QtWidgets.QLabel(self.updating_maps)
                    self.updating_maps_label.setGeometry(QtCore.QRect(10, 10, 280, 80))
                    self.updating_maps_label.setText('<b>Please wait</b><br><br>You might need to restart for the game list and stats to update.')
                    self.updating_maps_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.updating_maps_label.setWordWrap(True)
                    self.updating_maps.show()
                    self.CAnalysis.update_accountdir(folder)
                    self.updating_maps.hide()
                    self.TAB_Stats.generate_stats()
                    self.update_winrate_data()

            else:
                self.sendInfoMessage('Invalid account folder!', color=MColors.msg_failure)

    def create_reset_overlay(self):
        """ Creates or resets the webwidget overlay"""

        # Hide and delete old web windget if we are resetting
        if hasattr(self, "WebView"):
            logger.info("Resetting overlay")
            self.WebView.hide()
            self.WebView.deleteLater()

        # Custom CSS/JS
        if not os.path.isfile(truePath('Layouts/custom.css')):
            with open(truePath('Layouts/custom.css'), 'w') as f:
                f.write('/* insert custom css here */')

        if not os.path.isfile(truePath('Layouts/custom.js')):
            with open(truePath('Layouts/custom.js'), 'w') as f:
                f.write('// insert custom javascript here')

        # Load overlay
        if not os.path.isfile(truePath('Layouts/Layout.html')):
            self.sendInfoMessage("Error! Failed to locate the html file", color=MColors.msg_failure)
            logger.error("Error! Failed to locate the html file")
            return

        self.WebView = MUI.CustomWebView()
        self.WebView.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput | QtCore.Qt.WindowStaysOnTopHint
                                    | eval(f"QtCore.Qt.{SM.settings['webflag']}") | QtCore.Qt.NoDropShadowWindowHint
                                    | QtCore.Qt.WindowDoesNotAcceptFocus)

        self.WebView.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.WebPage = MUI.WebEnginePage(self.WebView)
        self.WebView.setPage(self.WebPage)
        self.WebPage.setBackgroundColor(QtCore.Qt.transparent)
        self.set_WebView_size_location(SM.settings['monitor'])

        self.WebView.load(QtCore.QUrl().fromLocalFile(truePath('Layouts/Layout.html')))

        if not SM.settings['force_hide_overlay']:
            self.WebView.show()

        MF.WEBPAGE = self.WebPage

    def start_main_functionality(self):
        """ Create replay analysis and adds all found replays"""
        logger.info(f'\n>>> Starting (v{APPVERSION/100:.2f})'
                    f' [{AF.app_type()}]'
                    f' [{platform.system()} {platform.release()}]'
                    f'\n{SM.settings_for_logs()}')

        self.create_reset_overlay()

        # Pass current settings
        MF.update_init_message()

        # Start server thread
        self.thread_server = threading.Thread(target=MF.server_thread, daemon=True)
        self.thread_server.start()

        # Init replays, names & handles. This should be fast
        MF.initialize_replays_names_handles()

        # PyQt threadpool
        self.threadpool = QtCore.QThreadPool()

        # Check for new replays
        thread_replays = MUI.Worker(MF.check_replays)
        thread_replays.signals.result.connect(self.check_replays_finished)
        self.threadpool.start(thread_replays)

        # Start mass replay analysis
        thread_mass_analysis = MUI.Worker(MR.mass_replay_analysis_thread, SM.settings['account_folder'], progress_callback=True)
        thread_mass_analysis.signals.progress.connect(self.mass_analysis_progress_update)
        thread_mass_analysis.signals.result.connect(self.mass_analysis_finished)

        if TabWidget.taskbar_progress is not None:
            TabWidget.taskbar_progress.setValue(0)
            TabWidget.taskbar_progress.resume()
            TabWidget.taskbar_progress.show()

        self.threadpool.start(thread_mass_analysis)
        logger.info('Starting mass replay analysis')

        # Check for the PC to be awoken from sleep
        thread_awakening = MUI.Worker(MF.wait_for_wake)
        thread_awakening.signals.result.connect(self.pc_waken_from_sleep)
        self.threadpool.start(thread_awakening)


    def mass_analysis_progress_update(self, progress):
        """ Updates status bar with progress info"""
        logger.info(f"Progress: {progress}")


    def show_charts(self, show):
        """ Show/hide charts. Update BG width."""
        SM.settings['show_charts'] = show
        if show:
            MF.sendEvent('showhide_charts(true)', raw=True)
        else:
            MF.sendEvent('showhide_charts(false)', raw=True)

    def set_WebView_size_location(self, monitor):
        """ Set correct size and width for the widget. Setting it to full shows black screen on my machine, works fine on notebook (thus -1 offset) """
        try:
            sg = QtWidgets.QDesktopWidget().screenGeometry(int(SM.settings['monitor'] - 1))
            self.WebView.setFixedSize(int(sg.width() * SM.settings['width']),
                                      int(sg.height() * SM.settings['height']) - SM.settings['subtract_height'])

            offset = QtCore.QPoint(-self.WebView.width() + 1 + int(SM.settings['right_offset']), int(SM.settings['top_offset']))
            self.WebView.move(sg.topRight() + offset)
            logger.info(f'Using monitor {int(monitor)} ({sg.width()}x{sg.height()})')
        except Exception:
            logger.error(f"Failed to set to monitor {monitor}\n{traceback.format_exc()}")

    def pc_waken_from_sleep(self, diff):
        """ This function is run when the PC is awoken """
        if diff is None:
            return

        logger.info(f'The computer just awoke! ({HF.strtime(diff, show_seconds=True)})')
        thread_awakening = MUI.Worker(MF.wait_for_wake)
        thread_awakening.signals.result.connect(self.pc_waken_from_sleep)
        self.threadpool.start(thread_awakening)

        # Check for new updates & reset keyboard threads
        self.check_for_updates()
        self.reset_keyboard_thread()

    def reset_keyboard_thread(self):
        """ Resets keyboard thread"""
        global keyboard
        try:
            keyboard.unhook_all()
            keyboard = importlib.reload(keyboard)
            self.manage_keyboard_threads()
            logger.info(f'Resetting keyboard thread')
        except Exception:
            logger.error(f"Failed to reset keyboard\n{traceback.format_exc}")

    def check_replays_finished(self, replay_dict):
        """ Launches function again. Adds game to game tab. Updates player winrate data. """

        # Show/hide overlay (just to make sure)
        if hasattr(self, 'WebView') and SM.settings['force_hide_overlay'] and self.WebView.isVisible():
            self.WebView.hide()
        elif hasattr(self, 'WebView') and not SM.settings['force_hide_overlay']:
            self.WebView.show()

        # Launch thread anew
        thread_replays = MUI.Worker(MF.check_replays)
        thread_replays.signals.result.connect(self.check_replays_finished)
        self.threadpool.start(thread_replays)

        # Delay updating new data to prevent lag when showing the overlay
        self.wait_ms(2000)
        self.TAB_Games.add_new_game_data(replay_dict)
        if self.CAnalysis is not None and replay_dict['mutators']:
            self.TAB_Mutations.update_data(self.CAnalysis.get_weekly_data())

    def save_playernotes_to_settings(self):
        """ Saves player notes from UI to settings dict"""
        for player in self.TAB_Players.player_winrate_UI_dict:
            if not self.TAB_Players.player_winrate_UI_dict[player].get_note() in {None, ''}:
                SM.settings['player_notes'][player] = self.TAB_Players.player_winrate_UI_dict[player].get_note()
            elif player in SM.settings['player_notes']:
                del SM.settings['player_notes'][player]

    def wait_ms(self, time):
        """ Pause executing for `time` in miliseconds"""
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(time, loop.quit)
        loop.exec_()

    @catch_exceptions(logger)
    def mass_analysis_finished(self, result):
        """ When mass replay analysis is finished.
        Creates plots, shows info to the user. """

        # Save CAnalysis
        self.CAnalysis = result
        if TabWidget.taskbar_progress is not None:
            TabWidget.taskbar_progress.setValue(100)
            TabWidget.taskbar_progress.hide()

        # Update game tab
        self.TAB_Games.initialize_data(self.CAnalysis)

        # Update stats tab
        player_names = (', ').join(self.CAnalysis.main_names)
        self.TAB_Stats.LA_IdentifiedPlayers.setText(f"Main players: {player_names}")
        self.TAB_Stats.LA_GamesFound.setText(f"Games found: {len(self.CAnalysis.ReplayData)}")
        self.TAB_Stats.LA_Stats_Wait.deleteLater()
        self.TAB_Games.LA_Games_Wait.deleteLater()
        self.TAB_Stats.generate_stats()
        self.TAB_Mutations.update_data(self.CAnalysis.get_weekly_data())
        
        # 更新突变因子统计数据
        self.TAB_MutatorStats.calculate_mutator_stats(self.CAnalysis.ReplayData)
        
        # 更新自定义地图统计数据
        self.TAB_CustomMaps.analyze_custom_maps(self.CAnalysis.ReplayData)

        self.update_winrate_data()
        MF.check_names_handles()
        MF.CAnalysis = self.CAnalysis

        # Show player winrates
        if SM.settings['show_player_winrates']:
            thread_check_for_newgame = MUI.Worker(MF.check_for_new_game, progress_callback=True)
            thread_check_for_newgame.signals.progress.connect(self.map_identified)
            self.threadpool.start(thread_check_for_newgame)

        # Connect & run full analysis if set
        self.TAB_Stats.BT_FA_run.setEnabled(True)
        self.TAB_Stats.BT_FA_run.clicked.connect(self.run_f_analysis)
        if SM.settings['full_analysis_atstart']:
            self.run_f_analysis()

    def map_identified(self, data):
        """Shows fast expand widget when a valid new map is identified"""
        logger.info(f'Identified map: {data}')

        # Don't proceed if the function disabled or not a valid map
        if not SM.settings['fast_expand'] or not data[0] in FastExpandSelector.valid_maps:
            return

        if self.FastExpandSelector is None:
            self.FastExpandSelector = FastExpandSelector()
        self.FastExpandSelector.setData(data)
        self.FastExpandSelector.show()

    def dump_all(self):
        """ Dumps all replay data from mass analysis into a file """
        self.TAB_Stats.BT_FA_dump.setEnabled(False)
        thread_dump_all = MUI.Worker(self.CAnalysis.dump_all)
        thread_dump_all.signals.result.connect(partial(self.TAB_Stats.BT_FA_dump.setEnabled, True))
        self.threadpool.start(thread_dump_all)

    def run_f_analysis(self):
        """ runs full analysis """
        if self.full_analysis_running:
            logger.error('Full analysis is already running')
            return

        if TabWidget.taskbar_progress is not None:
            TabWidget.taskbar_progress.setValue(0)
            TabWidget.taskbar_progress.resume()
            TabWidget.taskbar_progress.show()

        self.TAB_Stats.BT_FA_run.setEnabled(False)
        self.TAB_Stats.BT_FA_stop.setEnabled(True)
        self.full_analysis_running = True
        thread_full_analysis = MUI.Worker(self.CAnalysis.run_full_analysis, progress_callback=True)
        thread_full_analysis.signals.result.connect(self.full_analysis_finished)
        thread_full_analysis.signals.progress.connect(self.full_analysis_progress)
        self.threadpool.start(thread_full_analysis)

    def full_analysis_progress(self, progress):
        """ Updates progress from full analysis"""
        self.TAB_Stats.CH_FA_status.setText(progress[2])
        if TabWidget.taskbar_progress is not None and progress[1] != 0:
            TabWidget.taskbar_progress.setValue(int(100 * progress[0] / progress[1]))

    def full_analysis_finished(self, finished_completely):
        self.TAB_Stats.generate_stats()
        self.full_analysis_running = False
        if finished_completely:
            self.TAB_Stats.CH_FA_atstart.setChecked(True)
            if TabWidget.taskbar_progress is not None:
                TabWidget.taskbar_progress.setValue(100)
                TabWidget.taskbar_progress.hide()

    def stop_full_analysis(self):
        if self.CAnalysis is not None:
            if TabWidget.taskbar_progress is not None:
                TabWidget.taskbar_progress.pause()
            self.CAnalysis.closing = True
            self.full_analysis_running = False
            self.TAB_Stats.BT_FA_run.setEnabled(True)
            self.TAB_Stats.BT_FA_stop.setEnabled(False)
            self.CAnalysis.save_cache()

    def update_winrate_data(self):
        """ Update player tab & set winrate data in MF """
        if self.CAnalysis is not None:
            self.winrate_data = self.CAnalysis.calculate_player_winrate_data()
            self.TAB_Players.update(self.winrate_data)
            MF.set_player_winrate_data(self.winrate_data)
        else:
            logger.error('Can\'t update winrate data before mass analysis is finished')

    def save_screenshot(self):
        """ Saves screenshot of the overlay and saves it on the desktop"""
        try:
            # 确保截图文件夹存在
            screenshot_folder = SM.settings['screenshot_folder']
            if not os.path.exists(screenshot_folder):
                os.makedirs(screenshot_folder)
                
            p = QtGui.QImage(self.WebView.grab())
            height = p.height() * 1060 / 1200
            width = p.height() * 600 / 1200
            if SM.settings['show_charts']:
                width = p.height() * 1070 / 1200

            p = p.copy(int(p.width() - width), int(p.height() * 20 / 1200), int(width), int(height))
            p = p.convertToFormat(QtGui.QImage.Format_RGB888)

            name = f'Overlay_{datetime.now().strftime("%H%M%S")}.png'
            path = os.path.abspath(os.path.join(screenshot_folder, name))

            p.save(path, 'png')

            # Files smaller than 10kb consider as empty
            if os.path.getsize(path) < 10000:
                self.sendInfoMessage(f'Show overlay before taking screenshot!', color=MColors.msg_failure)
                os.remove(path)
            else:
                logger.info(f'Taking screenshot! {path}')
                self.sendInfoMessage(f'Taking screenshot! {path}', color=MColors.msg_success)
        except Exception:
            logger.error(traceback.format_exc())
            self.sendInfoMessage(f'Screenshot failed!', color=MColors.msg_failure)


    def sendInfoMessage(self, message, color=None):
        self.TAB_Main.set_status(translate(message), color)

    def change_theme(self):
        """ Changes UI theme between dark and light """
        SM.settings['dark_theme'] = self.TAB_Main.CH_DarkTheme.isChecked()
        set_dark_theme(self, app, TabWidget, APPVERSION)

    def redo_full_analysis(self):
        """ Redo full analysis from scratch """
        # Deletes the cache and starts the analysis again
        if os.path.isfile(HF.cache_path("MassReplayAnalysisCache.p")):
            os.remove(HF.cache_path("MassReplayAnalysisCache.p"))
        self.run_f_analysis()


if __name__ == "__main__":
    freeze_support()
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    TabWidget = MUI.CustomQTabWidget()
    try:
        ui = UI_TabWidget()
        ui.setupUI(TabWidget)
        ui.loadSettings()
        ui.start_main_functionality()
    except MultipleInstancesRunning:
        sys.exit()
    except Exception:
        logger.error(traceback.format_exc())
        TabWidget.tray_icon.hide()
        MF.stop_threads()
        sys.exit()

    # Do stuff before the app is closed
    exit_event = app.exec_()
    TabWidget.tray_icon.hide()
    ui.stop_full_analysis()
    MF.stop_threads()
    ui.saveSettings()
    logger.info('Exit')
    sys.exit(exit_event)
