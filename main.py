from actions_toolkit import core

from app.action import Action

if __name__ == '__main__':
    username = core.get_input('username')
    passwd = core.get_input('passwd')
    host = core.get_input('host') or 'cordcloud.biz'
    action = Action(username, passwd, host)
    try:
        res = action.run()
        core.info(f'CordCloud Action 运行成功，结果：{res}')
    except Exception as e:
        core.set_failed(str(e))
