import requests, json, re, time, random, configs as cfg
from lxml import html
from pprint import pprint
from urllib2 import urlopen
from urlparse import urlparse, urljoin, urlunparse, ParseResult
from utils import logging, proof

class Session(object):

    _ip = None

    def __init__(self):
        logging(u'Starting new manta session . . .')
        self.session = requests.Session()
        self.session.proxies = cfg.proxies
        self.session.headers = cfg.base_headers
        self._getMyIp()
        self._testSessionProxy()
        logging(u'Initializing request session . . .')
        self._buildCookiedSession(cfg.manta_base_url)

    def _getMyIp(self):
        self._ip = json.load(urlopen(cfg.ip_url))[u'origin']
        logging(u'Current Public IP: {}'.format(self._ip))

    def _testSessionProxy(self):
        logging(u'Testing proxies . . .')
        try:
            r = self.session.get(cfg.ip_url, timeout=5)
            r.raise_for_status()
            r_json = json.loads(r.content)
            if self._ip in r_json[u'origin']:
                raise ValueError(u'Proxied IP same as original IP')
        except Exception, e:
            logging(u'Proxy test failed: {}'.format(unicode(e)))
            logging(u'Exiting process . . .')
            exit()
        logging(u'Proxy test passed! Current proxied IP: {}'.format(r_json[u'origin']))

    def _get(self, url, params={}, headers=None, referer=u''):
        logging(u'<GET> "{}"'.format(url))
        if headers:
            self.session.headers.update(headers)
        if referer:
            self.session.headers.update({ u'Referer': referer })
        res = self.session.get(url, params=params)
        logging(u'<GET> "{}" - {}'.format(url, res.status_code))
        return res

    def _post(self, url, data={}, headers=None, referer=u''):
        logging(u'<POST> "{}"'.format(url))
        if headers:
            self.session.headers.update(headers)
        if referer:
            self.session.headers.update({ u'Referer': referer })
        res = self.session.post(url, data=data)
        logging(u'<POST> "{}" - {}'.format(url, res.status_code))
        return res

    def _buildCookiedSession(self, base_url, referer=u''):
        parsed = urlparse(base_url)

        # First request
        logging(u'Build Cookies Request #1:')
        res = self._get(parsed.geturl(), headers={
            u'Accept': u'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            u'Upgrade-Insecure-Requests': u'1',
            u'Host': parsed.netloc,
        }, referer=referer)
        self.lastReferer = res.url
        # print res.content + '\n'

        # Second request to get js content
        JS = re.search(r'src\=\"\/(ser\-.*\.js)\"', res.content).group(1)
        url_2 = ParseResult(parsed.scheme, parsed.netloc, JS, u'', u'', u'').geturl()
        time.sleep(random.random())
        logging(u'Build Cookies Request #2:')
        res = self._get(url_2, referer=self.lastReferer)
        # print res.content + '\n'

        # Third request to post js to get cookies
        PID = re.search(r'FingerprintWrapper\(\{path\:\"\/.*?\?(PID\=.*?)\"\,', res.content).group(1)
        AJAX = re.search(r'FingerprintWrapper.*?ajax_header\:\"(.*?)\"\,interval', res.content).group(1)
        url_3 = ParseResult(parsed.scheme, parsed.netloc, JS, '', PID, '').geturl()
        time.sleep(random.random())
        logging(u'Build Cookies Request #3:')
        res = self._post(url_3, data={ u'p': proof(cfg.p) }, headers={ u'Accept': u'*/*', u'X-Distil-Ajax': AJAX }, referer=self.lastReferer)
        # print res.__dict__
        return res

    def crawl(self, url, **kwargs):
        parsed = urlparse(url)
        logging(u'Preparing crawler for "{}"'.format(parsed.geturl()))
        params = {
            u'httpReferrer': u'?'.join([parsed.path, parsed.query]),
            u'uid': self.session.cookies[u'D_ZUID'],
        }
        url_4 = ParseResult(parsed.scheme, parsed.netloc, u'distil_identify_cookie.html', u'', u'', u'').geturl()
        try:
            res = self._get(url_4, params=params, referer=self.lastReferer, **kwargs)
            if res.status_code == 200:
                logging(u'"{}" - Crawled'.format(parsed.geturl()))
                return res, html.fromstring(res.content)
            elif res.status_code == 405:
                logging(u'HTTP 405 detected, looks like Captcha is stopping us! Change proxy and try again . . .')
                res.raise_for_status()
            elif res.status_code == 409:
                logging(u'HTTP 409 detected, try rebuilding cookies . . .')
                self.session.headers = cfg.base_headers
                self._buildCookiedSession(cfg.manta_base_url)
                return self.crawl(url)
            else:
                logging(u'HTTP {} detected, not sure how to handle this . . .'.format(res.status_code))
                res.raise_for_status()
        except Exception, e:
            logging(u'"{}" - Error: {}'.format(parsed.geturl(), unicode(e)))
            raise
