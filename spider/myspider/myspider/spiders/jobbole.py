# -*- coding: utf-8 -*-
import scrapy

from myspider.items import JobboleItem


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['www.jobbole.com']
    start_urls = ['http://www.jobbole.com/']

    # 若果不想从首页抓数据就使用以下方法
    def start_requests(self):
        start_urls = ['http://python.jobbole.com/all-posts/']
        for u in start_urls:
            # dont_filter:默认是False,True表示若请求url不在原始url的域名下不过滤
            # callback:默认为parse,可以自定义其它函数功能,表示请求这个url后返回的信息
            yield scrapy.Request(url=u, dont_filter=True, callback=self.parse)

    def parse(self, response):
        # 页面中这个div有两个class="post floated-thumb", 所以使用contains函数获取其中一个
        # 获取两个div[contains(@class, "floated-thumb") and contains(@class, "post")]
        lis = response.xpath('//div[@id="archive"]/div[contains(@class, "floated-thumb")]')

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').extract()
        for l in lis:
            # 引入item进行实体化
            jobbole = JobboleItem()
            # 获取数据
            title = l.xpath('./div[@class="post-thumb"]/a/@title').extract()[0]
            title_img = l.xpath('./div[@class="post-thumb"]/a/img/@src').extract()
            add_time = l.xpath('./div[@class="post-meta"]/p/text()').extract()[1].replace('·','').strip()
            desc = l.xpath('.//span[@class="excerpt"]/p/text()').extract()[0]
            tag = l.xpath('./div[@class="post-meta"]/p/a[2]/text()').extract()[0]
            # 实体
            jobbole['title'] = title
            jobbole['title_img'] = title_img
            jobbole['add_time'] = add_time
            jobbole['desc'] = desc
            jobbole['tag'] = tag

            yield jobbole
        
        # 下一页抓取
        # if next_page:
        #     yield scrapy.Request(url=next_page[0], dont_filter=True, callback=self.parse)
            
        