# -*- coding: utf-8 -*-
import scrapy


class MyspiderItem(scrapy.Item):
    pass


class JobboleItem(scrapy.Item):
    title = scrapy.Field()      # 标题
    title_img = scrapy.Field()  # 标题图片
    add_time = scrapy.Field()   # 发表日期
    desc = scrapy.Field()       # 简介
    tag = scrapy.Field()        # 标签
    title_img_path = scrapy.Field()   # 图片本地路径