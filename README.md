整个项目分为三大部分：
    1. 模拟登录知乎并保存cookie(zhihu_login.py  YDM.py)  (模拟登录模块仅适用于Windows平台)
        这个脚本基于selenium，Chrome版本为60，chromedriver版本为2.33
        整体流程如下：使用selenium请求知乎登录界面，提交用户名密码，判断是否有验证码（验证码在填写密码之后出现），
        若无验证码，则直接点击登录按钮进行登录，若有验证码则判断验证码类型（包含中文点击验证码、英文输入验证码），
        若为中文验证码，则放弃登录再次请求（知乎验证码出现概率随机），若出现英文验证码，则利用“云打码”API进行识别，然后自动填充进行登录。
        也提供了将验证码保存至本地，手动打码这一选择。最终登录之后，获取知乎主页title列表并打印。
        那个zhihu_login.py文件为主程序，YDM.py为云打码接口且依赖于yundamaAPI.dll
        chrome60和webdriver2.33 还有yundamaAPI.dll我都放到自己的百度云盘了，这是链接：
        链接：https://pan.baidu.com/s/18aQsDdQPJ9n7XzJ7buCadQ   提取码：mwuy
    2. 分布式爬虫爬取用户信息(MasterFollowing.py conn_redis.py activities.py get_proxy.py)
        MasterFollowing.py 以配置文件中的一个用户名为起点，循环遍历用户的following列表，将用户唯一Token存入redis中，供activities.py获取以便拼接出用户详细信息url进行用户信息采集。
        有一个地方值得注意，在抓取知乎用户信息时，知乎似乎对并发请求的数量作出了限制，一旦并发请求数超过阀值，就会请求失败，即使在我使用代理IP的情况下依然是这样，这个问题最终未能解决。
        get_proxy.py是我在调用代理IP时封装的接口。
        我想到的不触发知乎验证的最终方法，使用schedule定时调度任务来每隔一段时间模拟登录知乎，更新session.txt中的cookie，MasterFollowing.py和activities.py两个爬虫脚本在请求时
        均携带cookie请求，这样应该不会触发知乎验证了吧。
    3.  data_nanlysis目录下的DataAnalysis.py， 使用matplotlib来进行数据分析。

ps: PublicLog.py 为封装的公共日志接口