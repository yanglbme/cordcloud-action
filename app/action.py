import requests


class Action:
    def __init__(self, email: str, passwd: str, code: str = '', host: str = 'cordcloud.us'):
        self.email = email
        self.passwd = passwd
        self.code = code
        self.host = host.replace('https://', '').replace('http://', '').strip()
        self.session = requests.session()
        self.timeout = 6

    def format_url(self, path) -> str:
        return f'https://{self.host}/{path}'

    def login(self):
        login_url = self.format_url('auth/login')
        form_data = {
            'email': self.email,
            'passwd': self.passwd,
            'code': self.code
        }
        return self.session.post(login_url, data=form_data,
                                 timeout=self.timeout).json()

    def check_in(self):
        check_in_url = self.format_url('user/checkin')
        return self.session.post(check_in_url, timeout=self.timeout).json()

    def run(self):
        self.login()
        self.check_in()
