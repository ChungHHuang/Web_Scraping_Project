# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RottentomatoesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movie_url = scrapy.Field()
    name =  scrapy.Field()
    critic_score = scrapy.Field()
    aud_score = scrapy.Field()
    genre = scrapy.Field()
    context = scrapy.Field()
    reviewer = scrapy.Field()
    media = scrapy.Field()
    fresh_rot = scrapy.Field()
    top_critic = scrapy.Field()