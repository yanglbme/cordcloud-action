from actions_toolkit import core

from app.action import Action

if __name__ == '__main__':
    try:
        email = core.get_input('email', required=True)
        passwd = core.get_input('passwd', required=True)
        host = core.get_input('host') or 'cordcloud.site'

        action = Action(email, passwd, host=host)
        action.run()
    except Exception as e:
        core.set_failed(f'{str(e)}')
