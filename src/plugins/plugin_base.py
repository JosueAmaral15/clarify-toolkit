class PluginBase:
    """
    Interface base para plugins do Clarify.
    Todo plugin deve herdar desta classe e implementar o método `activate`.
    """
    name = "BasePlugin"
    description = "Plugin base do Clarify."

    def activate(self, app):
        """Método chamado ao ativar o plugin. Recebe a instância principal do app."""
        raise NotImplementedError()
