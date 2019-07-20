from scrapy import Spider , Request
from thenumbers.items import ThenumbersItem
import datetime
import re  

class ThenumbersSpider(Spider):
    name = 'thenumbers_spider'
    allowed_urls = ['https://www.the-numbers.com/']
    start_urls = ['https://www.the-numbers.com/movie/budgets/all']

    def parse(self, response):
        # Find the url of different pages
        url_list = ['https://www.the-numbers.com/movie/budgets/all/{}01'.format(i) for i in range(51)]
        for url in url_list:
            yield Request(url = url, callback = self.parse_rank_page)

    def parse_rank_page(self, response):
        for i in range(2,102):
            release_year = response.xpath('.//div[@id="page_filling_chart"]/center/table//tr[{}]//td/a/text()'.format(i)).extract_first()[-4:] 
            name = response.xpath('.//div[@id="page_filling_chart"]/center/table//tr[{}]//td/b/a/text()'.format(i)).extract_first()
            production_budget = response.xpath('.//div[@id="page_filling_chart"]/center/table//tr[{}]//td[4]/text()'.format(i)).extract_first()
            production_budget = int(production_budget.replace('$','').replace(',','').strip())    
            domestic = response.xpath('.//div[@id="page_filling_chart"]/center/table//tr[{}]//td[5]/text()'.format(i)).extract_first() 
            domestic = int(domestic.replace('$','').replace(',','').strip())
            worldwide = response.xpath('.//div[@id="page_filling_chart"]/center/table//tr[{}]//td[6]/text()'.format(i)).extract_first() 
            worldwide = int(worldwide.replace('$','').replace(',','').strip())

            item = ThenumbersItem()

            item['release_year'] = release_year
            item['name'] = name
            item['production_budget'] = production_budget
            item['domestic'] = domestic
            item['worldwide'] = worldwide
            
            yield item