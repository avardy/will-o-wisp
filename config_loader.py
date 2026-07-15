'''
Used to load a dictionary from a configuration file.
'''

import json
import numpy as np

# There are two local config files.  We'll decide which to open right here:

config_dir = f'config'
config_filename = f'{config_dir}/config.json'

calib_dir = f'calib'
calib_K_filename = f'{calib_dir}/calib_K.json'
calib_D_filename = f'{calib_dir}/calib_D.json'

class Config:
    video_channel = None
    show_input = None
    fullscreen = None
    use_tg_calibration = None
    use_homography = None
    tg_tag_size = None
    tg_delta = None
    use_homography = None
    output_width = None
    output_height = None
    screen_corners = None
    calib_K = None
    calib_D = None

class ConfigLoader:
    _config = None

    @classmethod
    def get(cls):
        if not ConfigLoader._config is None:
            return ConfigLoader._config

        try:
            # BAD: From json, to a dict, to the Config class above!?!?  This
            # is needlessly ugly.  But at least this ugliness is now restricted
            # to this file.

            dict = json.load(open(config_filename, 'r'))
            ConfigLoader._config = Config()

            ConfigLoader._config.video_channel = dict['video_channel']
            ConfigLoader._config.show_input = bool(dict['show_input'])
            ConfigLoader._config.fullscreen = bool(dict['fullscreen'])
            ConfigLoader._config.use_tg_calibration = bool(dict['use_tg_calibration'])
            ConfigLoader._config.use_homography = bool(dict['use_homography'])
            ConfigLoader._config.tg_tag_size = dict['tg_tag_size']
            ConfigLoader._config.tg_delta = dict['tg_delta']
            ConfigLoader._config.input_width = dict['input_width']
            ConfigLoader._config.input_height = dict['input_height']
            ConfigLoader._config.output_width = dict['output_width']
            ConfigLoader._config.output_height = dict['output_height']
            ConfigLoader._config.screen_corners = []
            ConfigLoader._config.screen_corners.append( dict['upper_left'] )
            ConfigLoader._config.screen_corners.append( dict['upper_right'] )
            ConfigLoader._config.screen_corners.append( dict['lower_right'] )
            ConfigLoader._config.screen_corners.append( dict['lower_left'] )
        except:
            print('Cannot load config: %s'% config_filename)  

        try:
            with open(calib_K_filename, "r") as calib_file:
                ConfigLoader._config.calib_K = np.asarray(json.load(calib_file))
            with open(calib_D_filename, "r") as calib_file:
                ConfigLoader._config.calib_D = np.asarray(json.load(calib_file))
        except:
            print(f'Trouble loading from {calib_K_filename} or {calib_D_filename}.')  

        return ConfigLoader._config
