import csv, codecs, os, re
from collections import OrderedDict
from manta.crawler import Crawler
from manta.utils import logging

class DetailCrawler(Crawler):

    name = u'Detail Crawler'
    crawl_urls = []
    allowed_domains = [u'manta.com']

    def __init__(self, delay=5):
        super(DetailCrawler, self).__init__(delay=delay)
        self.result = OrderedDict([
            (u'company',       None),
            (u'url',           None),
            (u'keywords',      None),
            (u'score',         None),
            (u'num_of_review', None),
            (u'address',       None),
            (u'city',          None),
            (u'state',         None),
            (u'zip',           None),
            (u'phone',         None),
            (u'weburl',        None),
            (u'email',         None),
        ])
        with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'detail_url_list.csv')), u'rb', u'utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.queries = OrderedDict()
            for row in csvreader:
                self.queries[row[0]] = row
                self.crawl_urls.append(row[0])

        with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'details.csv')), u'rb', u'utf-8') as csvfileR:
            csvreader = csv.reader(csvfileR, delimiter=',', quotechar='"')
            try:
                csvreader.next()
            except Exception, e:
                with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'details.csv')), u'ab', u'utf-8') as csvfileA:
                    csvwriter = csv.writer(csvfileA, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csvwriter.writerow(self.result.keys())

    def post_request_proccess(self, response, html):
        if response:
            self.session.lastReferer = response.url
        return response, html

    def _clean(self, xpath, delimiter=u'|'):
        _sanitized = map(lambda x: x.strip(), xpath)
        return delimiter.join(sorted(set(_sanitized), key=_sanitized.index))

    def _cleanEmail(self, email, delimiter=u';'):
        _r = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
        return delimiter.join(set(re.findall(_r, email)))

    def _cleanUrl(self, url, delimiter=u'|'):
        return delimiter.join(set(map(lambda x: x.lower(), url.split(u'|'))))

    def _cleanPhone(self, phone, delimiter=u'|'):
        _r = r'(\d{3})[\)\ \-]*(\d{3})[\ \-]*(\d{4})'
        return delimiter.join(set(map(lambda p: u''.join(p), re.findall(_r, phone))))

    def response_processor(self, response, html):
        if response:
            row = self.queries.get(response.url)
            if row:
                self.result[u'company']       = self._clean(html.xpath(u'//*[@itemprop="name"]//a/text()'))
                self.result[u'url']           = response.url
                self.result[u'keywords']      = row[1]
                self.result[u'score']         = u'-'
                self.result[u'num_of_review'] = u'-'
                self.result[u'address']       = self._clean(html.xpath(u'//*[@itemprop="streetAddress"]/text()'), u'; ')
                self.result[u'city']          = self._clean(html.xpath(u'//*[@itemprop="addressLocality"]/text()'))
                self.result[u'state']         = self._clean(html.xpath(u'//*[@itemprop="addressRegion"]/text()'))
                self.result[u'zip']           = self._clean(html.xpath(u'//*[@itemprop="postalCode"]/text()'))
                self.result[u'phone']         = self._cleanPhone(self._clean(html.xpath(u'//*[@itemprop="telephone"]/text()')))
                self.result[u'weburl']        = self._cleanUrl(self._clean(html.xpath(u'//*[@rel="contact"]/*[@class="napu"]//*[@itemprop="url"]/text()')))
                self.result[u'email']         = self._cleanEmail(self._clean(html.xpath(u'//*[@itemprop="email"]/text()')))

                with codecs.open(os.path.realpath(os.path.join(os.getcwd(), u'details.csv')), u'ab', u'utf-8') as csvfile:
                    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csvwriter.writerow(self.result.values())
            else:
                logging(u'Failed to get back "{}", maybe url got changed.'.format(response.url))

dc = DetailCrawler(delay=5.0)
dc.start()
