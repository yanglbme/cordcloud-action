from actions_toolkit import core

from app import log
from app.action import Action

author = {
    'name': 'Yang Libin',
    'link': 'https://github.com/yanglbme'
}
marketplace = 'https://github.com/marketplace/actions/cordcloud-action'

log.info(f'欢迎使用 CordCloud Action ❤\n\n📕 入门指南: {marketplace}\n'
         f'📣 由 {author["name"]} 维护: {author["link"]}\n')

try:
    # 获取输入
    email = core.get_input('email', required=True)
    passwd = core.get_input('passwd', required=True)
    host = core.get_input('host') or 'cordcloud.us,cordcloud.one,cordcloud.biz,c-cloud.xyz'

    # host 预处理：切分、过滤空值
    hosts = [h for h in host.split(',') if h]

    for i, h in enumerate(hosts):
        # 依次尝试每个 host
        log.info(f'当前尝试 host：{h}')

        action = Action(email, passwd, host=h)

        try:
            res = action.login()
        except Exception as login_err:
            log.warning(f'CordCloud 帐号登录异常，错误信息：{login_err}')
            continue

        if res['ret'] != 1:
            raise Exception(f'CordCloud 帐号登录失败，错误信息：{res}')
        log.info(f'尝试帐号登录，结果：{res}')

        try:
            res = action.check_in()
        except Exception as check_in_err:
            log.warning(f'CordCloud 账号自动续命异常，错误信息：{check_in_err}')
            continue

        if '您似乎已经签到过' in res['msg']:
            log.warning('当前帐号已经签到过')
        elif res['ret'] != 1:
            raise Exception(f'CordCloud 帐号续命失败，错误信息：{res}')
        else:
            log.info(f'尝试帐号续命，结果：{res}')

        log.info(f'CordCloud Action 成功结束运行！')
        break
except Exception as e:
    core.set_failed(str(e))
