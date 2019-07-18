# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ThenumbersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name =  scrapy.Field()  
    release_year = scrapy.Field()
    production_budget = scrapy.Field()
    domestic = scrapy.Field()
    worldwide = scrapy.Field() 