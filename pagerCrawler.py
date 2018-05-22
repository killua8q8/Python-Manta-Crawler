import re, math, csv, codecs, os
from collections import OrderedDict
from manta.crawler import Crawler

class PagerCrawler(Crawler):

    name = u'Pager Crawler'
    crawl_urls = []
    allowed_domains = [u'manta.com']

    def __init__(self, delay=5):
        super(PagerCrawler, self).__init__(delay=delay)
        with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'url_list.csv')), u'rb', u'utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.queries = OrderedDict()
            for row in csvreader:
                self.queries[row[0]] = row
                self.crawl_urls.append(row[0])

    def pre_request_proccess(self, url):
        row = self.queries[url]
        self.session.session.headers.update({ u'Accept': u'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' })
        self.session.session.cookies.update({
            u'city': row[1],
            u'state': row[2],
            u'lat': row[3],
            u'lon': row[4],
        })
        return url

    def response_processor(self, response, html):
        pager = next(iter(html.cssselect(u'[ng-controller="SearchPaginationController"]')), None)
        if pager is not None:
            total = float(re.search(r'^totalCount\=(\d+)\;', pager.get(u'ng-init')).group(1))
            itemPerPage = len(html.cssselect(u'[rel="searchResults"] .organic-result'))
            pages = int(math.ceil(total / itemPerPage))
        else:
            pages = 1
        with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'url_list_pagenum.csv')), u'ab', u'utf-8') as csvfile:
            row = self.queries[response.url]
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow([response.url, pages] + row[1:5])

pc = PagerCrawler(delay=1.5)
pc.start()
