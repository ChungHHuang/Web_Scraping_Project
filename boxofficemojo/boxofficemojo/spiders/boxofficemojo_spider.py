from scrapy import Spider , Request
from boxofficemojo.items import BoxofficemojoItem
import datetime
import re  

class BoxofficemojoSpider(Spider):
    name = 'boxofficemojo_spider'
    allowed_urls = ['https://www.boxofficemojo.com']
    start_urls = ['https://www.boxofficemojo.com/yearly/?view2=worldwide&view=releasedate&p=.htm']

    def parse(self, response):
        num_years = len(response.xpath('//table[@cellspacing="1"]//tr')) - 1
        current_year = datetime.datetime.now().year  # Use datetime module to get current year
        # Find the url of yearly boxoffice for each year
        url_list = ['https://www.boxofficemojo.com/yearly/chart/?view2=worldwide&yr={}&p=.htm'.format(i) for i in range(current_year,current_year-num_years,-1)]
        for url in url_list:
            yield Request(url = url, callback = self.parse_year_page)

    def parse_year_page(self, response):
        # Find the url of each movie
        movie_urls = response.xpath('//table[@cellpadding="5"]//tr/td[2]//a/@href').extract() 
        movie_urls = ['https://www.boxofficemojo.com' + x for x in movie_urls]

        # Check if the # of url is correct
        # print('='*50)
        # print(len(movie_urls))
        # print('='*50)

        for url in movie_urls[1:101]:
            yield Request(url=url, callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        name = response.xpath('.//font[@face="Verdana"]/b/text()').extract()
        # Some movie name is seperated into two lines
        
        if len(name) > 1:
            name = ' '.join(name)
        else:
            name = name[0]   
        
        response.xpath('//td[@width="434px"]/div[@class="mp_box"]')


        gross = response.xpath('.//div[@class="mp_box_content"]/table//tr/td[2]/b/text()').extract()
        domestic = int(''.join(gross[0][1:].split(',')))
        worldwide = int(''.join(gross[1][1:].split(',')))
        top_table = response.xpath('//table[@cellpadding="4"]') 
        distributor = top_table.xpath('.//tr[2]/td/b/a/text()').extract_first()
        release_year = top_table.xpath('.//tr[2]/td[2]//a/text()').extract_first()    
        release_year = int(release_year[-4:])
        genre = top_table.xpath('.//tr[3]/td//b/text()').extract_first() 
        MPAArating = top_table.xpath('.//tr[4]/td[1]/b/text()').extract_first()    
        production_budget = top_table.xpath('.//tr[4]/td[2]/b/text()').extract_first()  
        series_temp = response.xpath('.//table[@cellpadding="5"]//tr/td//a/b/text()').extract() 
        series = 'N/A'
        for s in series_temp:
            if s.find('Series:') != -1:
                series = s
                break
        
        item = BoxofficemojoItem()

        item['name'] = name
        item['domestic'] = domestic
        item['worldwide'] = worldwide
        item['distributor'] = distributor
        item['release_year'] = release_year
        item['genre'] = genre
        item['MPAArating'] = MPAArating
        item['production_budget'] = production_budget
        item['series'] = series
        yield item
        
