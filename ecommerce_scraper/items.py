# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EcommerceScraperItem(scrapy.Item):
    # define the fields for your item here like:
     titulo = scrapy.Field()
     preco = scrapy.Field()
     classificacao = scrapy.Field()
     qtd_classificacao = scrapy.Field()
     marca = scrapy.Field()
     url = scrapy.Field()
     plataforma = scrapy.Field()
