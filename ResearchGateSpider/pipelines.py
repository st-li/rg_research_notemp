# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import settings
from scrapy import log
import pymongo
import MySQLdb
from scrapy.exceptions import DropItem
# from scrapy.conf import settings
import MySQLdb.cursors
from twisted.enterprise import adbapi

class ResearchgatespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoDBPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(
            settings.mongodb_server,
            settings.mongodb_port
        )
        
        db = self.client[settings.mongodb_db]
        db.authenticate(name=settings.mongodb_user, password=settings.mongodb_pwd, mechanism=settings.mongodb_mechanism)
        self.collection = db[settings.mongodb_collection]
    #def open_spider(self, spider):
    #    print spider.settings["HTTPCACHE_REDIS_HOST"]


    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            if self.collection.find_one({"_id" : item["person_key"]}):
                print "item is already in MongoDB \n"
            else:
                self.collection.insert({"_id": item["person_key"], "value" : dict(item)})
            log.msg("Question added to MongoDB database!",
                    level=log.DEBUG, spider=spider)
        return item

    def close_spider(self, spider):
        self.client.close()

# class MySQLPipeline(object):
#     def __init__(self):
#         self.dbpool = adbapi.ConnectionPool('MySQLdb',
#             host = settings.mysql_host,
#             db = settings.mysql_dbname,
#             user = settings.mysql_user,
#             passwd = settings.mysql_passwd,
#             cursorclass = MySQLdb.cursors.DictCursor,
#             charset = 'utf8',
#             use_unicode = True
#         )
#         print('Database opened')

#     def process_item(self, item, spider):
#         query = self.dbpool.runInteraction(self._conditional_insert, item)
#         query.addErrback(self.handle_error)
#         return item

#     def _conditional_insert(self, tx, item):
#         print("Check for duplication")
#         tx.execute("select * from candidate_basic where email = %s and fullname = %s", ([item['email'], item['fullname']]))
#         result = tx.fetchone()
#         if result:
#             print('Item already stored in db: %s' %item)
#         else:
#             tx.execute("""INSERT INTO candidate_basic 
#                         (
#                             fullname, country_id, discipline_id,
#                             college_id, academic_title, other_title,
#                             email, phonenumber, external_link,
#                             experience, `desc`, avatar_url, extra, url,
#                             interests, current_research, research_summary,
#                             publications, courses_desc, job_desc, edu_desc
#                         )
#                         VALUES(%s, %s, %s, %s, %s, %s, %s, 
#                                %s, %s, %s, %s, %s, %s, %s,
#                                %s, %s, %s, %s, %s, %s, %s)""", 
#                         (
#                             item['fullname'], item['country_id'], item['discipline_id'],
#                             item['college_id'], item['academic_title'], item['other_title'],
#                             item['email'], item['phonenumber'], item['external_link'],
#                             item['experience'], item['desc'], item['avatar_url'],
#                             item['extra'], item['url'], item['interests'],
#                             item['current_research'], item['research_summary'], item['publications'],
#                             item['courses_desc'], item['job_desc'], item['edu_desc']
#                         )
#                       )
    
#     def handle_error(self, e):
#         log.err(e)  

#     def close_spider(self, spider):
#         """Discard the database pool on spider close"""
#         self.dbpool.close()
