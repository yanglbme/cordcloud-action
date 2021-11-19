import requests
from actions_toolkit import core

from app.util import now


class Action:
    def __init__(self, email: str, passwd: str, code: str = '', host: str = 'cordcloud.site'):
        self.email = email
        self.passwd = passwd
        self.code = code
        self.host = host.replace('https://', '').replace('http://', '')
        self.session = requests.session()

    def format_url(self, path) -> str:
        return f'https://{self.host}/{path}'

    def login(self) -> dict:
        login_url = self.format_url('auth/login')
        form_data = {
            'email': self.email,
            'passwd': self.passwd,
            'code': self.code
        }
        resp = self.session.post(login_url, data=form_data)
        return resp.json()

    def check_in(self) -> dict:
        check_in_url = self.format_url('user/checkin')
        resp = self.session.post(check_in_url)
        return resp.json()

    def run(self):
        res = self.login()
        if res['ret'] != 1:
            raise Exception(f'[{now()}] CordCloud 帐号登录异常，错误日志：{res}')
        core.info(f'[{now()}] 帐号登录成功，结果：{res}')

        res = self.check_in()
        if res['ret'] != 1:
            raise Exception(f'CordCloud 帐号自动签到续命异常，错误日志：{res}')
        core.info(f'[{now()}] 帐号续命成功，结果：{res}')
