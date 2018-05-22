# Manta Crawler  
> Simple tool to crawl from manta.com

## Install
---
* Clone this repo and have [virtualenv](https://virtualenv.pypa.io/en/stable/) ready if possible.
* `$ cd /path/to/repo`
* `$ virtualenv env && source env/bin/activate`
* `(env)$ pip install -r requirements.txt`

## Configurations
---
> Not much to configs, but proxy is required.  
> Change timezone accordingly.  
> Read configs.py for details.

## Get Started
---
* Create _keywords.csv_ file  
  `$ touch keywords.csv`
* Put something into _keywords.csv_ in this format: keyword,city,state  
  `$ echo 'burger,new york,ny' >> keywords.csv`
* Run Crawler `searchUrlCrawler.py`  
  `$ python searchUrlCrawler.py`
* If success, then run Crawler `pagerCrawler.py`  
  `$ python pagerCrawler.py`
* If success, then run Crawler `detailListCrawler.py`  
  `$ python detailListCrawler.py`
* If success, then run Crawler `detailCrawler.py` or your own crawler to crawl page details  
  `$ python detailCrawler.py`
* Done! Then you results will be outputted to details.csv @ the root of repo

## P.S.
* Manta only accepts SSL requests, make sure your proxies have SSL access.
* Don't change the delay too short, just in case.
* Change proxies if encountered HTTP 405 error.
* Make your own _Detail Crawler_ for customized crawled result.
* All crawled results will be appending to the existing output file, delete or truncate the files if you want a clean results.
