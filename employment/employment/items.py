# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EmploymentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class LiepinItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    city = scrapy.Field()
    edu = scrapy.Field()
    work = scrapy.Field()