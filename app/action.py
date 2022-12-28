import re
from typing import Tuple

import requests
import urllib3

urllib3.disable_warnings()


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

    def login(self) -> dict:
        login_url = self.format_url('auth/login')
        form_data = {
            'email': self.email,
            'passwd': self.passwd,
            'code': self.code
        }
        return self.session.post(login_url, data=form_data,
                                 timeout=self.timeout, verify=False).json()

    def check_in(self) -> dict:
        check_in_url = self.format_url('user/checkin')
        return self.session.post(check_in_url, timeout=self.timeout, verify=False).json()

    def info(self) -> Tuple:
        user_url = self.format_url('user')
        html = self.session.get(user_url, verify=False).text
        today_used = re.search('<span class="traffic-info">今日已用</span>(.*?)<code class="card-tag tag-red">(.*?)</code>',
                               html,
                               re.S)
        total_used = re.search(
            '<span class="traffic-info">过去已用</span>(.*?)<code class="card-tag tag-orange">(.*?)</code>',
            html, re.S)
        rest = re.search(
            '<span class="traffic-info">剩余流量</span>(.*?)<code class="card-tag tag-green" id="remain">(.*?)</code>',
            html, re.S)
        if today_used and total_used and rest:
            return today_used.group(2), total_used.group(2), rest.group(2)
        return ()

    def run(self):
        self.login()
        self.check_in()
        self.info()
