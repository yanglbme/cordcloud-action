from app.action import Action

email = 'contact@yanglibin.info'
passwd = 'xxx'
host = 'c-cloud.xyz'
action = Action(email, passwd, host=host)
action.run()
