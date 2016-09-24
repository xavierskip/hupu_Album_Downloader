虎扑网相册下载工具
=====================

**虎扑相册现在需要登录才能浏览，所以下载工具需要指定能够登录的虎扑帐号。**

# usage:

`python albumhupu.py  <你想要下载的虎扑相册的url> -u [用户名] [密码]`

第一次使用时会提示你输入虎扑帐号用户名和密码,登录后会记录此帐号的cookie,以后再登录时不需要输入帐号信息。cookie过期后会提示你重新输入帐号信息。
(注意此模块`hupu`会在自己的目录下记录登录帐号的cookies)。

默认情况下,下载的相册图片会保存在当前目录下,本地文件夹名称以虎扑相册文件夹为准。可以修改文件保存路径以及文件夹名称,请使用`python albumhupu.py -h`查看帮助。

`runserver.py` 运行 web 服务用来在网络上搭建此工具。

依赖 Flask网络框架，数据存储需要mysql。

``` requirements.txt
# 抓取部分
requests
# 网络服务部分
Flask
PyMySQL
```

1. 先运行 `python web/db.py` 初始化数据库   
2. 直接运行 `python runserver.py` 开启web服务

[web服务配置]

``` web/config.py
# flask 的配置文件
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
# 抓取相册内容需要指定默认的虎扑帐号
LUSER = <username>
LPWD = <password>
```

# todo:
* 增加选择保存图片目录选项
* 下载相同名称相册时,不会因为文件夹已经存在而引发错误。


