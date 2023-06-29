from requests import get

class JenkinsBase:
    def __init__(self) -> None:
        self.domain = 'http://34.146.97.227'
        self.auth = ('user', 'EQzM8kLcoUTW')

    def get_last_build(self, path):
        uri = f'{self.domain}{path}/lastBuild/api/json?tree=result,timestamp'
        return get(uri, auth=self.auth).json()
