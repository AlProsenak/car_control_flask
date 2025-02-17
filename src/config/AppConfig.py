from src.config.Environment import LocalMariaDBEnvironment, LocalEnvironment, ProductionEnvironment, DockerEnvironment


class AppConfig:
    _config_instance = None

    def __init__(self):
        pass

    def init_config(self, environment='local'):
        if self._config_instance is not None:
            return self._config_instance

        if environment == 'local':
            self._config_instance = LocalEnvironment()
        elif environment == 'local-mariadb':
            self._config_instance = LocalMariaDBEnvironment()
        elif environment == 'docker':
            self._config_instance = DockerEnvironment()
        elif environment == 'production':
            self._config_instance = ProductionEnvironment()
        else:
            raise ValueError('Invalid environment value: ' + environment)
        return self._config_instance

    def get_instance(self):
        if self._config_instance is None:
            raise RuntimeError("Configuration not initialized.")
        return self._config_instance
