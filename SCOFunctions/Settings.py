import os
import json
import traceback
from datetime import datetime

from SCOFunctions.MLogging import Logger
logger = Logger('SETT', Logger.levels.INFO)


def update_with_defaults(loaded: dict, default: dict):
    """ Checks `loaded` dictionary, and fills all keys that are not present with values
    from `default` dictionary. This is done recursively for any dictionaries inside"""
    if not isinstance(default, dict) or not isinstance(loaded, dict):
        raise TypeError('default and loaded has to be dictionaries')

    for key in default:
        # If there is a new key
        if not key in loaded:
            loaded[key] = default[key]
        # If dictionary recursively do the same
        if isinstance(default[key], dict):
            update_with_defaults(loaded[key], default[key])


class CSettings:
    def __init__(self):
        self.filepath = None
        self.default_settings = {
            'start_with_windows': False,
            'start_minimized': False,
            'enable_logging': True,
            'show_player_winrates': True,
            'duration': 60,
            'monitor': 1,
            'force_hide_overlay': False,
            'show_session': True,
            'dark_theme': True,
            'fast_expand': False, 
            'minimize_to_tray': True,
            'language': 'zh_CN',
            'account_folder': None,
            'screenshot_folder': None,
            'hotkey_show/hide': 'Ctrl+Shift+*',
            'hotkey_show': None,
            'hotkey_hide': None,
            'hotkey_newer': 'Ctrl+Alt+/',
            'hotkey_older': 'Ctrl+Alt+*',
            'hotkey_winrates': 'Ctrl+Alt+-',
            'color_player1': '#0080F8',
            'color_player2': '#00D532',
            'color_amon': '#FF0000',
            'color_mastery': '#FFDC87',
            'aom_account': None,
            'aom_secret_key': None,
            'player_notes': dict(),
            'main_names': list(),
            'right_offset': 0,
            'top_offset': 0,
            'width': 0.7,
            'force_width': False,
            'show_charts': True,
            'replay_check_interval': 3,
            'height': 1,
            'font_scale': 1,
            'check_for_multiple_instances': True,
            'subtract_height': 1,
            'webflag': 'CoverWindow',
            'full_analysis_atstart': False
        }

        # We don't need a deepcopy here. When resetting only the lower level gets changed.
        self.settings = self.default_settings.copy()

    def load_settings(self, filepath: str):
        """ Load settings from a file"""
        self.filepath = filepath
        try:
            # Try to load base config if there is one
            if os.path.isfile(self.filepath):
                with open(self.filepath, 'r') as f:
                    self.settings = json.load(f)

            # If it's not there, save default settings
            else:
                with open(self.filepath, 'w') as f:
                    json.dump(self.settings, f, indent=2)
        except Exception:
            logger.error(f'Error while loading settings:\n{traceback.format_exc()}')
            # Save corrupted file on the side
            if os.path.isfile(self.filepath):
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.replace(self.filepath, f'{self.filepath.replace(".json","")}_corrupted ({now}).json')

        # Make sure all keys are here. This checks dictionaries recursively and fill missing keys.
        update_with_defaults(self.settings, self.default_settings)

    def save_settings(self):
        """ Save settings to an already definied filepath"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info('Settings saved')
        except Exception:
            logger.error(f'Error while saving settings\n{traceback.format_exc()}')

    def settings_for_logs(self):
        """ Returns current settings that can be safely saved into logs"""
        out = self.settings.copy()
        out['aom_secret_key'] = "set" if out['aom_secret_key'] else None
        # Only delete 'rng_choices' if it exists (legacy key from older versions)
        if 'rng_choices' in out:
            del out['rng_choices']
        del out['player_notes']
        return out

    def width_for_graphs(self):
        """ Checks whether the width needs to be changed for graphs"""
        if self.settings['show_charts'] and self.settings['width'] < 0.7 and not self.settings['force_width']:
            self.settings['width'] = 0.7


Setting_manager = CSettings()