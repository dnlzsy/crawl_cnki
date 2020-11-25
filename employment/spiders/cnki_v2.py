#!/usr/bin/env python3
# coding: utf-8 -*-
# Time: 2020/11/5 11:35
# Author: xd
import json
import re

import scrapy
from scrapy_redis.spiders import RedisSpider
from employment.settings import CNKI_HEADERS

class CnkiSpider(scrapy.Spider):
    name = 'cnki'
    allowed_domains = ['cnki.net']
    start_urls = ['https://wap.cnki.net/touch/web']

    # redis_key = 'cnki:start_urls'  # redis_key,用于在redis 添加起始url
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": CNKI_HEADERS
    }

    subject_url = 'https://wap.cnki.net/touch/web/Article/SearchBySubject/'

    def parse(self, response, **kwargs):

        subject_list = response.xpath('/html/body/header/nav/ul/li/a')
        for subject in subject_list:

            kw = subject.xpath('./@href').extract_first().split('.')[-2][-1]
            xkdl = subject.xpath('./text()').extract_first()
            data = {
                'keyword': kw,
                'xkdl': xkdl,
                'fieldtype': '1001',
                'pagesize': '30'
            }
            item = {}
            item['学科大类'] = xkdl
            url = f'https://wap.cnki.net/touch/web/Home/Album/{kw}.html'
            yield scrapy.FormRequest(url=url,
                                     callback=self.parse_subject,
                                     method='POST',
                                     meta={'item': item},
                                     formdata=data, dont_filter=True)

    def parse_subject(self, response):
        item = response.meta.get('item')
        script = response.xpath('/html/body/script[3]').extract_first()
        json_str = re.findall("\'\[([^\[\]]+)\]\'", script)[0]
        json_list = re.findall("\{[^\{\}]+?\}", json_str)
        for xk_json in json_list:
            xk_json = xk_json.replace('&quot;', '\"')
            xk_data = json.loads(xk_json)
            xkkw = xk_data.get('Type')
            xk = xk_data.get('Name')
            item['学科'] = xk

            data = {
                'keyword': xkkw,
                'fieldtype': '1002',
                'pagesize': '30'
            }
            articletype = {
                '博士论文': '21',
                '硕士论文': '22',
                '期刊': '10',
                '会议论文': '30',
                '报纸': '40'
            }
            for i, j in articletype.items():
                data['articletype'] = j
                item['文献类型'] = i
                yield scrapy.FormRequest(url=self.subject_url,
                                         callback=self.parse_list,
                                         method='POST',
                                         meta={'item': item , 'metadata': data},
                                         formdata=data, dont_filter=True)

    def parse_list(self, response):
        text = response.text
        item = response.meta.get('item')
        metadata = response.meta.get('metadata')
        info = json.loads(text)
        total = info.get('total')
        page = total // 30 + 1
        data = {
            'keyword': metadata.get('keyword'),
            'fieldtype': metadata.get('fieldtype'),
            'pagesize': metadata.get('pagesize'),
            'articletype':metadata.get('articletype')
        }
        for p in range(1, page+1):
            data['pageindex'] = str(p)
            yield scrapy.FormRequest(url=self.subject_url,
                                     callback=self.parse_info,
                                     method='POST',
                                     meta={'item': item},
                                     formdata=data, dont_filter=True)

    def parse_info(self, response):
        text = response.text
        item = response.meta.get('item')
        info = json.loads(text).get('rows')
        for i in info:
            item['文章来源'] = i.get('ArticleSource')
            item['标题'] = i.get('Title')
            item['作者'] = i.get('Author')
            item['目录'] = i.get('Catalog')
            item['内容'] = i.get('Content')
            item['下载次数'] = i.get('DownloadCount')
            item['关键字'] = i.get('Keyword')
            item['关键字CN'] = i.get('KeywordCN')
            item['关键字JB'] = i.get('KeywordJB')
            item['时期'] = i.get('Period')
            item['发表时间'] = i.get('PublicationTime')
            item['发表机构'] = i.get('PublishName')
            item['发表机构PY'] = i.get('PublishPYName')
            item['引用频率'] = i.get('QuoteFrequency')
            item['摘要'] = i.get('Summary')
            item['导师'] = i.get('Tutor')
            item['年份'] = i.get('Year')
            item['页码'] = i.get('Page')
            item['页数'] = i.get('PageCount')
            item['文件名'] = i.get('FileName')
            item['文件类型'] = i.get('FileType')
            item['数据库名'] = i.get('DBName')
            item['类型'] = i.get('Type')
            item['内容'] = i.get('Content')
            item['区间'] = i.get('Range')
            item['区间数'] = i.get('RangeCount')
            item['文献标记'] = i.get('ArticleMark')
            item['期刊标记'] = i.get('QKMark')
            item['AuthorInstitution'] = i.get('AuthorInstitution')
            item['AuthorInstitutionCode'] = i.get('AuthorInstitutionCode')
            item['DiscN0'] = i.get('DiscN0')
            item['Priority'] = i.get('Priority')
            item['UnitCode'] = i.get('UnitCode')
            item['CoreCode'] = i.get('CoreCode')
            item['SCICode'] = i.get('SCICode')
            item['EICode'] = i.get('EICode')
            item['CSSCICode'] = i.get('CSSCICode')
            item['NetMark'] = i.get('NetMark')
            item['PriorityFileName'] = i.get('PriorityFileName')
            item['状态'] = i.get('Status')
            item['状态内容'] = i.get('StatusContent')
            item['AssignType'] = i.get('AssignType')
            detail_url = 'https:' + i.get('Url')
            item['url'] = detail_url
            item['封面url'] = i.get('CoverUrl')
            item['数据库url'] = i.get('DbUrl')
            item['发表url'] = i.get('PublishUrl')
            item['下载url'] = i.get('DownloadUrl')
            item['SYS_VSM'] = i.get('SYS_VSM')
            item['ZjCode'] = i.get('ZjCode')
            item['ZtCode'] = i.get('ZtCode')
            item['ZtChildCode'] = i.get('ZtChildCode')
            item['ZtCodeName'] = i.get('ZtCodeName')
            yield scrapy.Request(url=detail_url,
                                     callback=self.parse_detail,
                                     meta={'item': item},dont_filter=True)

    def parse_detail(self, response):
        item = response.meta.get("item")
        domains = response.xpath('//div[contains(text(),"领　域")]/following-sibling::*/a/text()').extract()
        if domains:
            domain=','.join(domains)
            item['领域'] = domain
        else:
            item['领域'] =''
        item['from'] = 'cnki'
        return item