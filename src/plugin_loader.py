import importlib
import os
import sys

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__), 'plugins')

class PluginLoader:
    def __init__(self, app):
        self.app = app
        self.plugins = []

    def discover_plugins(self):
        sys.path.insert(0, PLUGIN_FOLDER)
        for fname in os.listdir(PLUGIN_FOLDER):
            if fname.endswith('.py') and fname != 'plugin_base.py':
                mod_name = fname[:-3]
                try:
                    mod = importlib.import_module(mod_name)
                    for attr in dir(mod):
                        obj = getattr(mod, attr)
                        if hasattr(obj, '__bases__') and 'PluginBase' in [b.__name__ for b in obj.__bases__]:
                            self.plugins.append(obj())
                except Exception as e:
                    print(f"Erro ao carregar plugin {mod_name}: {e}")
        sys.path.pop(0)

    def activate_plugins(self):
        for plugin in self.plugins:
            try:
                plugin.activate(self.app)
            except Exception as e:
                print(f"Erro ao ativar plugin {plugin.name}: {e}")
