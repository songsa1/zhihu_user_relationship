# Python_song
使用selenium模拟登录知乎
这个脚本基于selenium，Chrome版本为60，chromedriver版本为2.33
整体流程如下：使用selenium请求知乎登录界面，提交用户名密码，判断是否有验证码（验证码在填写密码之后出现），
若无验证码，则直接点击登录按钮进行登录，若有验证码则判断验证码类型（包含中文点击验证码、英文输入验证码），
若为中文验证码，则放弃登录再次请求（知乎验证码出现概率随机），若出现英文验证码，则利用“云打码”API进行识别，然后自动填充进行登录。
也提供了将验证码保存至本地，手动打码这一选择。最终登录之后，获取知乎主页title列表并打印。
那个zhihu_message.py文件为主程序，YDM.py为云打码接口且依赖于yundamaAPI.dll

chrome60和webdriver2.33 还有yundamaAPI.dll我都放到自己的百度云盘了，这是链接：
链接：https://pan.baidu.com/s/18aQsDdQPJ9n7XzJ7buCadQ 
提取码：mwuy 


