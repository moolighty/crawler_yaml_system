# 通用爬虫系统 crawler_system
---
## 项目目录
---
```
src/           # 核心代码目录
---configs/         # 爬虫配置文件目录
---items/           # item特征字段定义
---loaders/         # itemloader 主要是特征字段清洗规则定义
    ---specials         # 具体网站特殊处理
---middlewares/     # 爬虫中间件定义
---misc/            # 其他(不适合放在其他目录的类或者功能法官法)
---pipelines/       # 用于item处理的pipeline
---requestfactorys/ # request对象制造工厂
---spider_yamls/    # spider 配置文件目录，对应各个网站
---spiders/         # 通用爬虫定义目录
   --- specials     # 特殊网站爬虫的定义，该目录下的爬虫不通用，很少见
---utils/           # 实用工具类或者方法
---settings.py      # 爬虫全局配置文件
---run_spider.py    # spider初始化和启动脚本
requirements.txt    # 软件所需要的依赖包
scrapy.cfg          # 该scrapy项目的全局配置文件
```

## 爬虫项目说明补充
---
1. src/run_spider.py 主要加载爬虫配置文件并启动爬虫实例进程
2. src/spiders/__init__.py 核心通用爬虫逻辑流程规范化，该类为该项目的重中之重
3. 配置中加入了depth和category的概念,说明如下：
    + depth, 层次或者深度，主要用来串起请求头部规则和链接提取规则，提取出来的链接通过src/requestfactorys/__init.py来
    depth和category来找到请求头部的参数，从而构造Ｒequest实例对象，发起请求；
    + category, 类别或者种类，一个网站可能多种特征提取方式，通过category来进行区分，串起
    request结果回来时response应该调用相应category对应的特征提取方式
4. 链接提取规则中的meta参数，可以自定义你需要的字段信息，随着request实例对象传到response对象上，
其中：
+ check_before_request_flag表示在发起请求前，去redis键值集合进行进行查询，如果存在，则
说明已经请求过，不需要再重复请求;反之，则发送网络请求.通过此机制，可以实现增量抓取;
+ next_page_flag 当前层的导航页提取链接时，存在下一页的情形，用于控制depth的变化.
5. 特征提取方式支持：xpath,css,re,直接复制常量，取response属性等方式;
6. 该项目可能还存在一些潜在的bug，还有一些网站情况可能没有处理到，欢迎扩展该项目中对应的类或者方法，从而能够处理更多的情况. 

## 项目运行
---
本地开发和测试服务器测试时，配好src/configs/dev_env.py中的redis和kafka的信息， 线上运行配置不用修改。
1. 在自己开发的时候， 可通过项目下的test.py文件手动传入爬虫配置文件名称，即可进行运行，通过打断点
的方式，进行问题调试。
2. docker方式运行
...
