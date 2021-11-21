import requests
from actions_toolkit import core

from app.util import now


class Action:
    def __init__(self, email: str, passwd: str, code: str = '', host: str = 'cordcloud.site'):
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
        res = self.session.post(login_url, data=form_data, timeout=self.timeout).json()
        if res['ret'] != 1:
            raise Exception(f'[{now()}] CordCloud 帐号登录异常，错误日志：{res}')
        core.info(f'[{now()}] 帐号登录成功，结果：{res}')

    def check_in(self):
        check_in_url = self.format_url('user/checkin')
        res = self.session.post(check_in_url, timeout=self.timeout).json()
        if res['ret'] != 1:
            raise Exception(f'[{now()}] CordCloud 帐号自动签到续命异常，错误日志：{res}')

    def run(self):
        core.info('欢迎使用 CordCloud Action ❤\n\n'
                  '📕 入门指南: https://github.com/marketplace/actions/cordcloud-action\n'
                  '📣 由 Yang Libin 维护: https://github.com/yanglbme\n')
        self.login()
        self.check_in()
        core.info(f'[{now()}] CordCloud Action 成功结束运行！')
