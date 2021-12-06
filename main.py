from actions_toolkit import core

from app.action import Action

# 获取输入
email = core.get_input('email', required=True)
passwd = core.get_input('passwd', required=True)
host = core.get_input('host') or 'cordcloud.us,cordcloud.one,cordcloud.biz,c-cloud.xyz'

# host 预处理：切分、过滤空值
hosts = [h for h in host.split(',') if h]

core.info('欢迎使用 CordCloud Action ❤\n\n'
          '📕 入门指南: https://github.com/marketplace/actions/cordcloud-action\n'
          '📣 由 Yang Libin 维护: https://github.com/yanglbme\n')

success, err = False, None

for i, h in enumerate(hosts):
    # 依次尝试每个 host
    try:
        action = Action(email, passwd, host=h)
        action.run()
        success = True
        # 成功则终止
        break
    except Exception as e:
        err = str(e)
        if i != len(hosts) - 1:
            core.warning(f'host：{h}, 错误信息：{str(e)}')
if not success:
    core.set_failed(f'{err}')
