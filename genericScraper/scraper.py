import scrapy
import re
from scrapy.crawler import CrawlerProcess
import logging
from es_operate import ElasticSearchOperate

es_ops = None

class IonicSpider(scrapy.Spider):
    name = "ionic_spider"
    start_urls = ['https://en.wikipedia.org/wiki/Ionic_(mobile_app_framework)']
    line_count = -1
    with open('genericScraper/input_format.txt') as f:
        lines = [line.strip() for line in f]

    def parse(self, response):
        global es_ops
        IonicSpider.line_count += 1

        while(True):
            if 'next' in IonicSpider.lines[IonicSpider.line_count]:
                IonicSpider.line_count += 1
                break
            else:
                selector = IonicSpider.lines[IonicSpider.line_count]
                IonicSpider.line_count += 1

                content = response.xpath(selector).extract_first()
                content = content.replace('\n',' ')
                content = re.sub('<[^>]*>', '', content) # remove tags from the extracted text
                content = re.sub('[\[].*?[\]]', '', content) # remove square brackets and text contained in them
                # res = es_ops.insert_fact(content)

                content = content.split(". ")
                for sentence in content:
                    res = es_ops.insert_fact(sentence + ".")

                # yield {
                #     "content" : content,
                # }s

                # print("Content : \n",content,"\n")

        if 'exit' in IonicSpider.lines[IonicSpider.line_count]:
            pass
        else:
            yield scrapy.Request(
                response.urljoin(IonicSpider.lines[IonicSpider.line_count]),
                callback=self.parse
                )

def crawlPages():
    global es_ops
    es_ops = ElasticSearchOperate()
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('elasticsearch').propagate = False
    logging.getLogger('urllib3').propagate = False
    process = CrawlerProcess()
    process.crawl(IonicSpider)
    process.start()
