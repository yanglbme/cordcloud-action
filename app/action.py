import requests


class Action:
    def __init__(self, username: str, passwd: str, host: str = 'cordcloud.biz'):
        self.username = username
        self.passwd = passwd
        self.host = host.replace('https://', '').replace('http://', '')
        self.session = requests.session()

    def format_url(self, path):
        return f'https://{self.host}/{path}'

    def check_in(self) -> str:
        login_url = self.format_url('auth/login')
        check_in_url = self.format_url('user/checkin')
        form_data = {
            'email': self.username,
            'passwd': self.passwd,
            'code': ''
        }
        self.session.post(login_url, data=form_data)
        resp = self.session.post(check_in_url)
        return resp.json()['msg']

    def run(self) -> str:
        return self.check_in()
