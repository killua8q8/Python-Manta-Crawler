import time
from session import Session
from utils import logging, now
from urlparse import urlparse

class Crawler(object):

    name = u'Crawler'
    crawl_urls, allowed_domains = [], []
    delay = 5

    def __init__(self, delay=5):
        logging(u'Initializing {} . . .'.format(self.name))
        self.delay = delay
        self.session = Session()

    def _validate_domains(self, url):
        parsed = urlparse(url)
        domain = u'.'.join(parsed.netloc.split(u'.')[-2:])
        if any(map(lambda ad: domain.lower() == ad.lower(), self.allowed_domains)):
            return True
        else:
            logging(u'"{}" is not an allowed domain.'.format(domain))
            return False

    def pre_request_proccess(self, url):
        return url

    def post_request_proccess(self, response, html):
        return response, html

    def request_proccess(self, url):
        url = self.pre_request_proccess(url)
        response, html = self.session.crawl(url)
        return self.post_request_proccess(response, html)

    def pre_response_processor(self, response, html):
        return response, html

    def post_response_processor(self, response, html):
        return response, html

    def response_processor(self, response, html):
        response, html = self.pre_response_processor(response, html)
        # Do Sth
        response, html = self.post_response_processor(response, html)
        return response, html

    def start(self):
        self._success, self._failed, self._ngad = 0, 0, 0
        self._startTime = now()
        if len(self.crawl_urls):
            logging(u'Total {} urls waiting to be crawled.'.format(len(self.crawl_urls)))
            try:
                for url in self.crawl_urls:
                    if self._validate_domains(url):
                        time.sleep(self.delay)
                        response, html = self.request_proccess(url)
                        if response is not None:
                            self._success += 1
                            self.response_processor(response, html)
                        else:
                            self._failed += 1
                    else:
                        self._ngad += 1
            except Exception, e:
                self._failed += 1
                logging(u'Crawling has been interrupted by exception.')
            self._endTime = now()
            self.stats()
        else:
            logging(u'Nothing needs to be crawled.')

    def stats(self):
        delta = self._endTime - self._startTime
        logging(u'Crawling finished.')
        logging(unicode(
            'This Run:\n'
            '{space}[Start At]\t{startTime}\n'
            '{space}[Finish At]\t{endTime}\n'
            '{space}[Total Runtime]\t{seconds} Seconds\n'
            '{space}[Success]\t{success}\n'
            '{space}[Failed]\t{failed}\n'
            '{space}[NG Domain]\t{ngad}'
        ).format(space=u' ' * 26
                ,success=self._success
                ,failed=self._failed
                ,ngad=self._ngad
                ,startTime=self._startTime.strftime(u'%Y-%m-%d %H:%M:%S %Z')
                ,endTime=self._endTime.strftime(u'%Y-%m-%d %H:%M:%S %Z')
                ,seconds=delta.total_seconds()
        ))
