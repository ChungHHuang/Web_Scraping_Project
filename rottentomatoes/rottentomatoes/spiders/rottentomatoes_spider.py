from scrapy import Spider , Request
from rottentomatoes.items import RottentomatoesItem
import datetime
import re  

class RottentomatoesSpider(Spider):
    name = 'rottentomatoes_spider'
    allowed_urls = ['https://www.rottentomatoes.com/']
    start_urls = ['https://www.rottentomatoes.com/']

    def parse(self, response):
        with open('urls.txt', 'r') as f:
            url_list = f.read()
            url_list = url_list.split(',')
            url_list = [x.strip() for x in url_list]
            for url in url_list:
                yield Request(url = url, 
                    meta={'movie_url': url},
                    callback = self.parse_movie_page)

    def parse_movie_page(self, response):
        movie_url = response.meta['movie_url']
        name = response.xpath('.//div[@class="mop-ratings-wrap score_panel js-mop-ratings-wrap"]/h1/text()').extract_first() 
        critic_score = response.xpath('.//div[@class="mop-ratings-wrap__half"]/h2/a/span[2]/text()').extract_first().strip() 
        aud_score = response.xpath('.//div[@class="mop-ratings-wrap__half audience-score"]/h2/a/span[2]/text()').extract_first().strip()
        genre = response.xpath('.//ul[@class="content-meta info"]/li[2]/div[2]/a/text()').extract()
        review_url = response.xpath('//div[@class="panel-body content_body"]/p[1]/a[1]/@href').extract_first()  
        review_url = 'https://www.rottentomatoes.com' + review_url
        yield Request(url = review_url,
                meta={'movie_url': movie_url,'name': name,'critic_score':critic_score,
                    'aud_score':aud_score,'genre':genre,'review_url':review_url},
                callback = self.parse_review_page)

    def parse_review_page(self, response):
        movie_url = response.meta['movie_url']
        name = response.meta['name']
        critic_score = response.meta['critic_score']
        aud_score = response.meta['aud_score']
        genre = response.meta['genre']
        review_url = response.meta['review_url']
        pages = response.xpath('//div[@style="display:inline-block; float:right; padding-bottom:10px"]/span/text()').extract_first()
        pages = int(re.findall('\d+',pages)[1])
        review_urls = [review_url + '?page={}'.format(i) for i in range(1,pages+1)]

        for url in review_urls:
            yield Request(url = url,
                    meta={'movie_url': movie_url,'name': name,'critic_score':critic_score,
                        'aud_score':aud_score,'genre':genre},
                    callback=self.parse_critic_page)

    def parse_critic_page(self, response):
        movie_url = response.meta['movie_url']
        name = response.meta['name']
        critic_score = response.meta['critic_score']
        aud_score = response.meta['aud_score']
        genre = response.meta['genre']
        reviews = response.xpath('//div[@class="row review_table_row"]')

        for review in reviews:
            reviewer = review.xpath('.//div[@class="col-sm-13 col-xs-24 col-sm-pull-4 critic_name"]/a/text()').extract_first().strip() 
            media = review.xpath('.//div[@class="col-sm-13 col-xs-24 col-sm-pull-4 critic_name"]//em/text()').extract_first().strip() 
            context = review.xpath('.//div[@class="the_review"]/text()').extract_first().strip() 
            if review.xpath('./div[2]/div').extract_first().find('fresh') != -1: 
                fresh_rot = 'fresh'
            else:
                fresh_rot = 'rotten'
            if review.xpath('.//div[@class="small"]/text()').extract_first(): 
                top_critic = True
            else:
                top_critic = False

            item = RottentomatoesItem()
            item['movie_url'] = movie_url
            item['name'] = name
            item['critic_score'] = critic_score
            item['aud_score'] = aud_score
            item['genre'] = genre
            item['context'] = context
            item['reviewer'] = reviewer
            item['media'] = media
            item['fresh_rot'] = fresh_rot
            item['top_critic'] = top_critic
            yield item




