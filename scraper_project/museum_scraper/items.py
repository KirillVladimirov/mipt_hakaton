import scrapy


class CultureItem(scrapy.Item):
    title = scrapy.Field()
    authors = scrapy.Field()
    creation_time = scrapy.Field()
    size = scrapy.Field()
    technique = scrapy.Field()
    collection = scrapy.Field()
    exhibition = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
