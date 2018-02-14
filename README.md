# mm131_spider_wordpress
本脚本只支持python3，需要将系统语言设置成utf8

演示站：https://luoli.se

# 需要安装的库

```bash
pip3 install pymysql
pip3 install requests
```
# 关于使用
需要打开脚本文件设置连接的mysql信息，在代码第10行
还有要修改第25行的图床key，和图床url，只支持chevereto
# 已知BUG
1.下载后会在temp生成下载图片，不过并不会移除旧的图片（会直接替换），可能代码逻辑有问题，但不影响使用
2.脚本中，如果图床已有一篇文章图片，会自动跳过，不会发布
3.在上传中有限制隔1秒上传，如果不需要请自行删除，在代码第29行
4.在执行目录会生成文章名.txt文件，这是用于脚本判断是否更新的文件，文件内容为文章内容
# 运行
```bash
mkdir temp
python3 spider.py
```
# 联系作者
QQ：47313013
邮箱：sys@t667.com
