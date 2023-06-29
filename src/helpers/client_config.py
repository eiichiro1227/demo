import yaml


class ClientConfig:
    def __init__(self, client_name: str):
        self.client_name = client_name

    def load_config_file(self) -> dict:
        config_path = f'./clients/{self.client_name}/config.yml'
        with open(config_path, "r", encoding='utf-8') as yaml_file:
            config = yaml.load(yaml_file, Loader=yaml.FullLoader)
            return config

    def client_path(self) -> str:
        return f'./clients/{self.client_name}'
