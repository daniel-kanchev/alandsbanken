import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from alandsbanken.items import Article


class AlandsbankenSpider(scrapy.Spider):
    name = 'alandsbanken'
    start_urls = ['https://www.alandsbanken.se/blog/all']

    def parse(self, response):
        links = response.xpath('//a[@class="latest-blog__card"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//a[@class="heading-6"]/@href)[last()]').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="heading-2 single-article__heading readthis "]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="single-article__date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="single-article__content readthis"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
