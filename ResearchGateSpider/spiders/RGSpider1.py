# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider
from scrapy import Request, FormRequest
from scrapy.utils.request import request_fingerprint
from ResearchGateSpider.items import ResearchGateItem
from ResearchGateSpider.datafilter import DataFilter
from ResearchGateSpider.func import parse_text_by_multi_content
from scrapy.exceptions import CloseSpider
#from scrapy_splash import SplashRequest
#from scrapy_splash import SplashMiddleware
import time


class RGSpider1(CrawlSpider):
    name = 'RGSpider1'
    #name = "ResearchGateSpider"
    domain = 'https://www.researchgate.net'
    start_urls = ["https://www.researchgate.net/login"]
    # pub_item = []
    # finger_print = ''
    # start_urls = ['https://www.researchgate.net/profile/Anahid_A_Birjandi/contributions']

    def start_requests(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
        }
        alphabet_list = ["A", "B", "C", "D",
                         "E", "F", "G", "H",
                         "I", "J", "K", "L", 
                         "M", "N", "O", "P",
                         "Q", "R", "S", "T",
                         "U", "V", "W", "X",
                         "Y", "Z", "Other"]
        for alphabet in alphabet_list:
            url = "https://www.researchgate.net/directory/profiles/"+alphabet
            yield Request(url, headers=headers, callback=self.parse_profile_directory, dont_filter=True)
            #break

        # url = "https://www.researchgate.net/directory/profiles/" + alphabet_list[0]
        # print url
        # yield Request(url, callback=self.parse_profile_directory, dont_filter=True)

    def parse_profile_directory(self, response):
        if response.status == 429:
            lostitem_str = 'first level directory: ' + response.url + '\n'
            self.lostitem_file.write(lostitem_str)
            self.lostitem_file.close()
            raise CloseSpider(reason=u'被封了，准备切换ip')
        headers = response.request.headers
        headers["referer"] = response.url
        for url in response.xpath(
                '//ul[contains(@class, "list-directory")]/descendant::a/@href'). \
                extract():
            url = self.domain + "/" + url
            yield Request(url, headers=headers, callback=self.parse_profile_directory2, dont_filter=True)
            #break

        # urls = response.xpath('//ul[contains(@class, "list-directory")]/descendant::a/@href').extract()
        # url0 = self.domain + "/" + urls[0]
        # print url0
        # yield Request(url0, callback=self.parse_profile_directory2, dont_filter=True)

    def parse_profile_directory2(self, response):
        if response.status == 429:
            lostitem_str = 'second level directory: ' + response.url + '\n'
            self.lostitem_file.write(lostitem_str)
            self.lostitem_file.close()
            raise CloseSpider(reason='被封了，准备切换ip')
        headers = response.request.headers
        headers["referer"] = response.url
        for url in response.xpath(
                '//ul[contains(@class, "list-directory")]/descendant::a/@href'). \
                extract():
            url = self.domain + "/" + url
            yield Request(url, headers=headers, callback=self.parse_profile_directory3, dont_filter=True)
            #break
        # urls = response.xpath('//ul[contains(@class, "list-directory")]/descendant::a/@href').extract()
        # url0 = self.domain + "/" + urls[0]
        # print url0
        # yield Request(url0, callback=self.parse_profile_directory3, dont_filter=True)

    def parse_profile_directory3(self, response):
        if response.status == 429:
            lostitem_str = 'third level directory: ' + response.url + '\n'
            self.lostitem_file.write(lostitem_str)
            self.lostitem_file.close()
            raise CloseSpider(reason='被封了，准备切换ip')
        headers = response.request.headers
        headers["referer"] = response.url
        for url in response.xpath(
                '//ul[contains(@class, "list-directory")]/descendant::a/@href'). \
                extract():
            url = self.domain + "/" + url
            yield Request(url, headers=headers, callback=self.parse_candidate_overview, dont_filter=True)
             #break
        #urls = response.xpath('//ul[contains(@class, "list-directory")]/descendant::a/@href').extract()
        #url0 = self.domain + "/" + urls[1]
        #print url0
        #yield Request(url0, headers=headers, callback=self.parse_candidate_overview, dont_filter=True)

    def parse_candidate_overview(self, response):
        if response.status == 429:
            lostitem_str = 'overview page: ' + response.url + '\n'
            self.lostitem_file.write(lostitem_str)
            self.lostitem_file.close()
            raise CloseSpider(reason='被封了，准备切换ip')
        headers = response.request.headers
        headers["referer"] = response.url

        featured_researches = response.xpath('//div[contains(@class, "profile-highlights-publications")]').extract()
        if featured_researches:
            item = ResearchGateItem()

            item['person_key'] = request_fingerprint(response.request)
            item['fullname'] = DataFilter.simple_format(response.xpath('//a[@class = "ga-profile-header-name"]/text()').extract())
            item['target_sciences'] = DataFilter.simple_format(response.xpath('//*[@id="target-sciences"]/text()').extract())
            item['title'] = DataFilter.simple_format(response.xpath('//*[contains(@class,"profile-degree")]/div[@class="title"]/text()').extract())
            item['score'] = DataFilter.simple_format(response.xpath('//span[starts-with(@class, "score-link")]').extract())

            top_coauthors = response.xpath('//div[starts-with(@class, "authors-block")]//ul/li//h5[@class="ga-top-coauthor-name"]/a')
            item['co_authors'] = parse_text_by_multi_content(top_coauthors, "|")
            
            skills_expertise = response.xpath('//div[starts-with(@class, "profile-skills")]/ul/li//a[starts-with(@class, "keyword-list-token-text")]')
            item['skills'] = parse_text_by_multi_content(skills_expertise, "|")

            topics = response.xpath('//ul[@class="keyword-list clearfix"]/li//a[starts-with(@class, "keyword-list-token-text")]')
            item['topics'] = parse_text_by_multi_content(topics, "|")

            item['institution'] = DataFilter.simple_format(response.xpath('//div[starts-with(@class, "institution-name")]').extract())
            item['department'] = DataFilter.simple_format(response.xpath('//div[@class = "institution-dept"]').extract())
            address = DataFilter.simple_format(response.xpath('//div[contains(@class, "institution-location")]/text()').extract())
            add_list = address.split(',')
            add_len = len(add_list)
            if add_len == 3:
                city = add_list[0].strip()
                province = add_list[1].strip()
                country = add_list[2].strip()
            elif add_len == 2:
                city = add_list[0].strip()
                province = ''
                country = add_list[1].strip()
            elif add_len == 1:
                city = add_list[0].strip()
                province = ''
                country = ''
            else:
                city = address
                province = ''
                country = ''
            item['city'] = city
            item['province'] = province
            item['country'] = country

            url = response.url + "/publications"
            print url
            yield Request(url, headers=headers, callback=self.parse_contribution, dont_filter=True, meta={"item":item})
        # yield Request(url, callback=self.parse_contribution, dont_filter=True, meta={"item":item})

    def parse_contribution(self, response):
        item = response.meta["item"]
        if response.status == 429:
            lostitem_str = item['fullname'] + ':' + ' contribution page: ' + response.url + '\n'
            self.lostitem_file.write(lostitem_str)
            self.lostitem_file.close()
            raise CloseSpider(reason=u'被封了，准备切换ip')
        headers = response.request.headers
        headers["referer"] = response.url
        # Parse articles, each article has a seperate page

        item['publications'] = []

        headers = response.request.headers
        headers["referer"] = response.url
        article_urls = response.xpath(
                '//li[contains(@class, "li-publication")]/descendant::a[contains(@class, "js-publication-title-link")]/@href').extract()
        article_count = len(article_urls)
        if article_count == 0:
            yield item
        for article_url in article_urls:
            article_url = self.domain + "/" + article_url
            yield Request(article_url, headers=headers, callback=self.parse_article, dont_filter=True, meta={'item':item, 'count':article_count})
        # for url in = article_urls[:3]:
        #     url = self.domain + "/" + url
        #     yield Request(url, headers=headers, callback=self.parse_article, dont_filter=True, meta={'item':item, 'last':'no'})
        
        
        # urls = response.xpath('//li[contains(@class, "li-publication")]/descendant::a[contains(@class, "js-publication-title-link")]/@href').extract()
        # url0 = self.domain + "/" + urls[0]
        # yield Request(url0, headers=headers, callback=self.parse_article, dont_filter=True)

    def parse_article(self, response):
        item = response.meta['item']
        if response.status == 429:
            lostitem_str = item['fullname'] + ':' + ' article page: ' + response.url + '\n'
            self.lostitem_file.write(lostitem_str)
            self.lostitem_file.close()
            raise CloseSpider(reason='被封了，准备切换ip')
        print response.url
        # item = ResearchGateItem()
        item = response.meta['item']
        pub_count = response.meta['count']
        
        article_item = {}
        article_name = DataFilter.simple_format(response.xpath('//div[@class="publication-header"]//h1[@class="publication-title"]/text()').extract())
        article_item['article_name'] = article_name
        article_abstract = DataFilter.simple_format(response.xpath('//div[@class="publication-abstract"]/div[2]').extract())
        article_item['artical_abstract'] = article_abstract
        article_journal = DataFilter.simple_format(response.xpath('//span[@class="publication-meta-journal"]/a').extract())
        article_date = DataFilter.simple_format(response.xpath('//span[@class="publication-meta-date"]').extract())
        article_item['article_journal'] = article_journal + ", " + article_date
        item['publications'].append(article_item)
        if len(item['publications']) == pub_count:
            return item
    
    def __init__(self, **kwargs):
        super(RGSpider1, self).__init__(**kwargs)
        self.lostitem_file = open('/data/lostitem_notempt.out', 'a+')
        pass

    def close(self, reason):
        self.lostitem_file.close()
        super(RGSpider1, self).close(self, reason)
