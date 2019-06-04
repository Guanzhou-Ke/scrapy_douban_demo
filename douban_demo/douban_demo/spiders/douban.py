# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.request import Request
from douban_demo.settings import Cookies


class DoubanSpider(scrapy.Spider):
    name = 'douban'

    def start_requests(self):
        yield Request(url='https://movie.douban.com/chart', callback=self.parse_rank)

    def parse_rank(self, response):
        for item in response.css('tr.item'):
            detail_url = item.css('a.nbg::attr(href)').extract_first()
            img_url = item.css('a.nbg > img::attr(src)').extract_first()
            main_name = item.css('div.pl2 > a::text').extract_first()
            other_name = item.css('div.pl2 > a > span::text').extract_first()
            brief = item.css('p.pl::text').extract_first()
            main_name = main_name.replace('\n', '').replace(' ', '')

            yield {
                'detail_url': detail_url,
                'img_url': img_url,
                'name': main_name+other_name,
                'brief': brief
            }

            yield Request(url=detail_url+'comments?status=P',
                          callback=self.parse_comments,
                          cookies=Cookies,
                          meta={'movie': main_name})

    def parse_comments(self, response):
        for comments in response.css('.comment-item'):
            username = comments.css('span.comment-info > a::text').extract_first()
            comment = comments.css('span.short::text').extract_first()

            yield {
                'movie': response.meta['movie'],
                'username': username,
                'comment': comment
            }
        nexturl = response.css('a.next::attr(href)').extract_first()
        if nexturl:
            yield Request(url=response.url[:response.url.find('?')]+nexturl,
                          callback=self.parse_comments,
                          cookies=Cookies,
                          meta=response.meta)
