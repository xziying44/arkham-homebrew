from flaskwebgui import FlaskUI

from server import *

if __name__ == '__main__':
    # 获取屏幕高度和宽度
    FlaskUI(app=app, server="flask", width=1500, height=800).run()
