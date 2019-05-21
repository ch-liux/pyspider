# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
import pymysql
import pymongo


class MyspiderPipeline(object):
    def process_item(self, item, spider):
        return item


# mysql
class JobboleMysqlPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8',
            use_unicode=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        # dbpool = adbapi.ConnectionPool("pymysql", host = settings["MYSQL_HOST"], db = settings["MYSQL_DBNAME"],...)
        dbpool = adbapi.ConnectionPool("pymysql", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twsisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)   #处理异常
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
            insert into jobbole(title, add_time, title_img, title_img_path, `desc`, tag) 
             values(%s, %s, %s, %s, %s, %s)
        """
        params = (item['title'], item['add_time'], item['title_img'], item['title_img_path'], item['desc'], item['tag'])
        cursor.execute(insert_sql, params)


# mongo
class JobboleMongoPipeline(object):
    collection_name = 'scrapy_items'
    def __init__(self, mongo_uri, mongo_db):
         self.mongo_uri = mongo_uri
         self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGODB_DBNAME')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        d = dict(item)
        tableName = spider.name
        # 爬虫名为表名
        table = self.db[tableName]
        # 去重验证
        validate = {
            'title': d['title'],
            'add_time': d['add_time']
        }
        # 去重插入
        table.update(validate, {'$set':d}, True)
        # 直接插入
        # table.insert_one(d)
        return item


# 图片处理
class JobboleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "title_img" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["title_img_path"] = image_file_path
        return item
