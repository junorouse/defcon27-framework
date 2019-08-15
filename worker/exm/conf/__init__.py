import os
import importlib.util


class Settings:
    def __init__(self):
        spec = importlib.util.spec_from_file_location('settings', os.getenv('SETTING_PATH'))
        user_settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_settings)

        for setting in dir(user_settings):
            if setting.isupper():
                # Load setting from user
                setattr(self, setting, getattr(user_settings, setting))

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        return

settings = Settings()
