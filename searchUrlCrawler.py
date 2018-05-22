import re, math, csv, codecs, os, json
from urllib import urlencode
from urlparse import ParseResult
from collections import OrderedDict
from manta.crawler import Crawler

class SearchUrlCrawler(Crawler):

    name = u'Search Url Crawler'
    crawl_urls = []
    allowed_domains = [u'manta.com']

    def __init__(self, delay=5):
        super(SearchUrlCrawler, self).__init__(delay=delay)
        with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'keywords.csv')), u'rb', u'utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.queries = OrderedDict()
            for row in csvreader:
                query = OrderedDict([(u'city', row[1]), (u'state', row[2]), (u'kw', row[0])])
                parsed = ParseResult(u'https', u'www.manta.com', u'/api/v1/location', u'', urlencode(query), u'')
                self.queries[parsed.geturl()] = row
                self.crawl_urls.append(parsed.geturl())

    def request_proccess(self, url):
        response, html = self.session.crawl(url, headers={
            u'Accept': u'application/json, text/plain, */*',
        })
        return response, json.loads(response.content)

    def response_processor(self, response, html):
        if isinstance(html, dict):
            with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'url_list.csv')), u'ab', u'utf-8') as csvfile:
                row = self.queries[response.url]
                location = html[u'data'][u'location']
                query = OrderedDict([
                    (u'search_source', u'nav'),
                    (u'search', row[0]),
                    (u'search_location', u' '.join([location[u'city'], location[u'stateabbr']])),
                    (u'pt', u','.join([location[u'latitude'], location[u'longitude']])),
                ])
                csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csvwriter.writerow([
                    ParseResult(u'https', u'www.manta.com', u'/search', u'', urlencode(query), u'').geturl(),
                    location[u'city'], location[u'stateabbr'], location[u'latitude'], location[u'longitude']
                ])

suc = SearchUrlCrawler(delay=1.5)
suc.start()
