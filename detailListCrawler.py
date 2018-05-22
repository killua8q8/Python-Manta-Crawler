import csv, codecs, os
from collections import OrderedDict
from urllib import urlencode
from urlparse import urlparse, parse_qsl, ParseResult
from collections import OrderedDict
from manta.crawler import Crawler
from manta.utils import logging

class DetailListCrawler(Crawler):

    name = u'Detail List Crawler'
    crawl_urls = []
    allowed_domains = [u'manta.com']

    def __init__(self, delay=5):
        super(DetailListCrawler, self).__init__(delay=delay)
        with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'url_list_pagenum.csv')), u'rb', u'utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.queries = OrderedDict()
            for row in csvreader:
                parsed = urlparse(row[0])
                query = OrderedDict(parse_qsl(parsed.query))
                for page in xrange(int(row[1])):
                    query[u'pg'] = page + 1
                    newParsed = ParseResult(parsed.scheme, parsed.netloc, parsed.path, u'', urlencode(query), u'')
                    self.queries[newParsed.geturl()] = row
                    self.crawl_urls.append(newParsed.geturl())

    def pre_request_proccess(self, url):
        row = self.queries[url]
        self.session.session.cookies.update({
            u'city': row[2],
            u'state': row[3],
            u'lat': row[4],
            u'lon': row[5],
        })
        return url

    def response_processor(self, response, html):
        with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'detail_url_list.csv')), u'ab', u'utf-8') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            parsed = urlparse(response.url)
            query = OrderedDict(parse_qsl(parsed.query))
            anchors = html.xpath(u'//div[@role="main"]//ul[@rel="searchResults"]/li[@itemtype="http://schema.org/LocalBusiness"]//a[@class="pull-left"]/@href')
            for anchor in anchors:
                csvwriter.writerow([
                    ParseResult(parsed.scheme, parsed.netloc, anchor, u'', u'', u'').geturl(),
                    query[u'search'],
                ])

dlc = DetailListCrawler(delay=1.5)
dlc.start()
