from app.action import Action

email = 'contact@yanglibin.info'
passwd = 'xxxxxxxx'
host = 'cordcloud.us'
action = Action(email, passwd, host=host)
action.run()
