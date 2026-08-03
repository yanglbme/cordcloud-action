import json
import os
from string import Template

import pyotp
from actions_toolkit import core

from app import log
from app.action import Action

action_info = {
    'action': 'CordCloud Action',
    'author': 'Yang Libin',
    'github': 'https://github.com/yanglbme',
    'marketplace': 'https://github.com/marketplace/actions/cordcloud-action'
}

welcome = Template('欢迎使用 $action ❤\n\n📕 入门指南: $marketplace\n📣 由 $author 维护: $github\n')
log.info(welcome.substitute(action_info))


def _load_config() -> dict:
    """读取本地配置文件（便于本地调试）。

    默认读取当前目录下的 config.json，也可通过环境变量 CC_CONFIG 指定路径。
    在 GitHub Actions 环境中（GITHUB_ACTIONS=true）会忽略配置文件，只使用 Secrets 传入的参数。
    """
    if os.environ.get('GITHUB_ACTIONS', '').lower() == 'true':
        return {}
    path = os.environ.get('CC_CONFIG') or os.path.join(os.getcwd(), 'config.json')
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


CONFIG = _load_config()

if CONFIG:
    log.info('已从 config.json 读取本地配置参数（仅本地调试生效）')


def get_input(name: str, default: str = '', required: bool = False) -> str:
    """获取配置，优先级：config.json > 环境变量。"""
    if name in CONFIG and CONFIG[name] not in (None, ''):
        return str(CONFIG[name])
    try:
        value = core.get_input(name)
    except Exception:
        value = ''
    if not value and required:
        raise ValueError(f'缺少必需参数：{name}（可在 config.json 或环境变量 INPUT_{name.upper()} 中配置）')
    return value or default


try:
    # 获取输入（config.json 中的值优先于环境变量）
    email = get_input('email', required=True)
    passwd = get_input('passwd', required=True)
    secret = get_input('secret')
    device_code = get_input('device_code')
    device_token = get_input('device_token')
    device_fingerprint = get_input('device_fingerprint')
    imap_host = get_input('imap_host')
    imap_port = int(get_input('imap_port') or 993)
    imap_user = get_input('imap_user')
    imap_password = get_input('imap_password')
    imap_timeout = int(get_input('imap_timeout') or 120)
    host = get_input('host') or 'cordcloud.us,cordcloud.one,cordcloud.biz,c-cloud.xyz,cordc.xyz'

    # 生成 TOTP 码，需要时间同步
    code = ''
    if secret:
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            log.info(f'两步验证码已生成: {code}')
        except Exception as e:
            log.warning(f'生成两步验证码失败: {str(e)}，将尝试不使用验证码登录')

    # host 预处理：切分、过滤空值
    hosts = [h for h in host.split(',') if h]

    for h in hosts:
        # 依次尝试每个 host
        log.info(f'当前尝试 host：{h}')
        action = Action(email, passwd, code=code, host=h,
                        device_code=device_code, device_token=device_token,
                        device_fingerprint=device_fingerprint,
                        imap_host=imap_host, imap_port=imap_port,
                        imap_user=imap_user, imap_password=imap_password,
                        imap_timeout=imap_timeout)
        try:
            # 登录
            res = action.login()
            if res.get('ret') != 1:
                # 登录失败：ret == 2 表示需陌生设备验证，ret == 0 表示帐号/密码等错误
                # 直接终止，避免继续尝试其他站点导致验证码作废
                if res.get('ret') == 2:
                    log.set_failed(f'需要完成陌生设备验证才能登录：{res.get("msg")}')
                else:
                    log.set_failed(f'帐号登录失败：{res.get("msg")}')
            log.info('帐号登录成功')

            # 签到
            res = action.check_in()
            if res.get('ret') != 1 and '您似乎已经签到过' not in res.get('msg', ''):
                log.set_failed(f'帐号签到失败：{res.get("msg")}')
            log.info(f'帐号签到：{res.get("msg")}')

            # 流量信息（签到成功或已签到都会输出）
            traffic = res.get('trafficInfo') or {}
            if not all(k in traffic for k in ('todayUsedTraffic', 'lastUsedTraffic', 'unUsedTraffic')):
                account = action.info()
                if account:
                    today_used, last_used, unused = account
                    traffic = {
                        'todayUsedTraffic': today_used,
                        'lastUsedTraffic': last_used,
                        'unUsedTraffic': unused
                    }
            if traffic:
                log.info(
                    f'帐号流量使用情况：今日已用 {traffic["todayUsedTraffic"]}, 过去已用 {traffic["lastUsedTraffic"]}, 剩余流量 {traffic["unUsedTraffic"]}')

            # 成功运行，退出循环
            log.info('CordCloud Action 成功结束运行！')
            break
        except Exception as e:
            # 当前 host 异常，尝试下一个 host
            log.warning(f'当前 host 运行异常，尝试下一个 host：{e}')
    else:
        # 尝试了所有 hosts 都失败
        log.set_failed('所有 host 均运行失败！')
except Exception as e:
    log.set_failed(str(e))
