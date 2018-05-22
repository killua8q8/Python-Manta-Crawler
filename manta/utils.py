import time, random, math, urllib, copy, datetime, pytz
from configs import timezone, log_time_format

class N(object):
    @staticmethod
    def ROTL(e, t): return e << t | (e % 0x100000000) >> 32 - t
    @staticmethod
    def f(e, t, r, n):
        return (t & r ^ ~t & n)        if e == 0\
          else (t ^ r ^ n)             if e == 1\
          else (t & r ^ t & n ^ r & n) if e == 2\
          else (t ^ r ^ n)
    @staticmethod
    def toHexStr(e):
        return reduce(lambda x, y: x + y, map(lambda n: unicode(hex((e % 0x100000000) >> 4 * n & 15)[2:]), xrange(7, -1, -1)), u'')

def getTimeStamp(): return int(time.time() * 1000.0)

def utf8Encode(e): return unicode(urllib.unquote(unicode(urllib.quote(e))))

def randomString(e):
    t, r, n = u'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', u'', 0
    while e > n:
        r += t[int(math.floor(random.random() * len(t)))]
        n += 1
    return r

def sha1(e):
    t = [1518500249, 1859775393, 2400959708, 3395469782]
    e = utf8Encode(e)
    e += unichr(128)
    r = len(e) / 4.0 + 2.0
    a = int(math.ceil(r / 16.0))
    i, o = [None] * a, 0
    while a > o:
        i[o] = [None] * 16
        for s in xrange(16):
            A = 64 * o + 4 * s
            B = 64 * o + 4 * s + 1
            C = 64 * o + 4 * s + 2
            D = 64 * o + 4 * s + 3
            i[o][s] = ord(e[A:A + 1] or u'\x00') << 24 | ord(e[B:B + 1] or u'\x00') << 16 | ord(e[C:C + 1] or u'\x00') << 8 | ord(e[D:D + 1] or u'\x00')
        o += 1
    i[a - 1][14] = 8.0 * (len(e) - 1) / (2.0 ** 32.0)
    i[a - 1][14] = int(math.floor(i[a - 1][14]))
    i[a - 1][15] = 8 * (len(e) - 1) & 4294967295
    h, p, f, m, v, y, o = 1732584193, 4023233417, 2562383102, 271733878, 3285377520, [None] * 80, 0
    while a > o:
        for E in xrange(16): y[E] = i[o][E]
        for E in xrange(16, 80): y[E] = N.ROTL(y[E - 3] ^ y[E - 8] ^ y[E - 14] ^ y[E - 16], 1)
        c, u, d, l, g = h, p, f, m, v
        for E in xrange(0, 80):
            T = int(math.floor(E / 20))
            S = N.ROTL(c, 5) + N.f(T, u, d, l) + g + t[T] + y[E] & 4294967295
            g, l, d, u, c = l, d, N.ROTL(u, 30), c, S
        h = h + c & 4294967295
        p = p + u & 4294967295
        f = f + d & 4294967295
        m = m + l & 4294967295
        v = v + g & 4294967295
        o += 1
    return N.toHexStr(h) + N.toHexStr(p) + N.toHexStr(f) + N.toHexStr(m) + N.toHexStr(v)

def _proof(t=8):
    n = u'{}:{}'.format(getTimeStamp(), randomString(20))
    a, i = 0, 2 ** (32 - t)
    while True:
        o, a = unicode(hex(a)[2:]) + u':' + n, a+1
        s = sha1(o)
        if int(s[0:8], 16) < i:
            return o

def proof(p):
    p[u'proof'] = _proof()
    return p

def now():
    return datetime.datetime.now(tz=pytz.timezone(timezone))

def logging(message):
    print u'[{}] {}'.format(now().strftime(log_time_format), message)
