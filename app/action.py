from DrissionPage import Chromium, ChromiumOptions
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
        self.timeout = 10
        self.browser = None
        self.session = None  # requests session

    def format_url(self, path) -> str:
        return f'https://{self.host}/{path}'

    def setup_browser(self):
        """初始化浏览器并设置选项"""
        co = ChromiumOptions()
        co.incognito()  # 使用无痕模式
        co.set_local_port(9911)  # 设置本地端口
        self.browser = Chromium(co)
        self.browser.clear_cache()
        self.browser.set.auto_handle_alert(True)

    def login(self):
        login_url = self.format_url('auth/login')
        tab = self.browser.latest_tab
        tab.get(login_url, timeout=self.timeout)

        # 等待关键元素出现
        if not tab.ele('x://input[@id="email"]', timeout=10):
            tab.refresh()

        # 填写登录表单
        tab.ele('x://input[@id="email"]').input(self.email)
        tab.ele('x://input[@id="passwd"]').input(self.passwd)
        if self.code:
            tab.ele('x://input[@id="code"]').input(self.code)

        # 提交登录表单（点击按钮）
        tab.ele('x://button[@id="login"]').click()

        # 等待跳转或页面加载完成
        tab.wait.load_start()

        # 检查是否遇到 Cloudflare 验证
        if tab.ele('x://div[@class="main-content"]/div', timeout=10):
            print("检测到 Cloudflare 页面")
            try:
                cf_checkbox = tab.ele('x://iframe').ele('x://body//input[@type="checkbox"]')
                if cf_checkbox:
                    cf_checkbox.click()
                    tab.wait(5)  # 等待验证完成
            except Exception as e:
                print("无法找到或点击 Cloudflare 验证框:", e)

        # 再次确保页面加载完成
        tab.wait.doc_loaded(timeout=20)

        # 将浏览器 Cookie 转移到 requests.Session
        cookies = tab.cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        self.session = session

    def check_in(self) -> dict:
        check_in_url = self.format_url('user/checkin')
        response = self.session.post(check_in_url, timeout=self.timeout)
        return response.json()

    def info(self) -> Tuple:
        user_url = self.format_url('user')
        response = self.session.get(user_url, timeout=self.timeout)
        html = response.text

        today_used = re.search(
            r'<span class="traffic-info">今日已用</span>.*?<code class="card-tag tag-red">(.*?)</code>',
            html,
            re.S
        )
        total_used = re.search(
            r'<span class="traffic-info">过去已用</span>.*?<code class="card-tag tag-orange">(.*?)</code>',
            html,
            re.S
        )
        rest = re.search(
            r'<span class="traffic-info">剩余流量</span>.*?<code class="card-tag tag-green" id="remain">(.*?)</code>',
            html,
            re.S
        )

        return (
            today_used.group(1).strip() if today_used else "未知",
            total_used.group(1).strip() if total_used else "未知",
            rest.group(1).strip() if rest else "未知"
        )

    def run(self):
        self.setup_browser()
        try:
            print("开始登录...")
            self.login()
            print("登录完成")

            print("执行签到...")
            result = self.check_in()
            print("签到结果:", result)

            print("获取用户信息...")
            info = self.info()
            print(f"今日已用: {info[0]}, 总已用: {info[1]}, 剩余流量: {info[2]}")
        finally:
            self.browser.quit()