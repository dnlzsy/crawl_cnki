# -*- coding: utf-8 -*-
from scrapy import cmdline

cmdline.execute("scrapy crawl cnki".split())
# 全部爬虫启动
# cmdline.execute("scrapy crawlall".split())