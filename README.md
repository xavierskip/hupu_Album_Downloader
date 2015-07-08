虎扑网相册下载工具
=====================

虎扑相册现在需要登录才能浏览，所以下载工具需要指定能够登录的虎扑帐号。

`download.py` 是直接运行的脚本。

uasge：`python download.py  <你想要下载的虎扑相册的url> <用户名> <密码>`

(注意此模块`hupu`会在自己的目录下记录登录帐号的cookies)

`runserver.py` 文件是运行 web服务用来在网络上搭建此工具。

依赖 Flask网络框架，数据存储需要mysql。

``` requirements.txt
# 抓取部分
requests==2.2.1 
# 网络服务部分
Flask==0.10.1
PyMySQL==0.6.6
```

1. 先运行 `python web/db.py` 初始化数据库   
2. 直接运行 `python runserver.py` 开启web服务

[web服务配置]

``` web/config.py
# flask 的配置文件
DEBUG = True
SECRET_KEY = 'YouNev3rKn0w!'
# 新浪微博连接登录的配置
APPKEY = 012345
APPSECRET = 'xxxxxxx'
REDIRECTURI = 'http://localhost'
# 数据库配置
HOST = '127.0.0.1'
PORT = 3306
DBUSER = 'root'
DBPASSWD = 'root'
DB = 'hupu'
# 网站页面下显示的最近更新时间
LASTDATE = '2014-10-19'
# 抓取相册内容需要指定默认的虎扑帐号
LUSER = [username]
LPWD = [password]
```
