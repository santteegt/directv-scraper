## Directv Programming Guide Scraper

Scraping the Latin America DirecTV programming guide by implementing a spider job using Scrapy.

### Software Requirements

* Python 2/3
* pip
* Scrapy
* Docker

### Setup Instructions

```
~$ pip install scrapy scrapyd scrapyd-client
```

### Spider Configuration

* TV_CHANNEL_RAGE: set the range of channels to scrape programming info Default value is `(130, 600)`. You can modify this value in [directv_spider.py](directvscraper/spiders/directv_spider.py) file

### Running Locally

```
~$ scrapy crawl directv -o directv.jl
```

### Deployment

```
~ $ docker-compose up -d scrapyd
~ $ scrapyd-deploy -p directvscraper # deployed the `eggifyed` project
```

* You can see default server conf using `scrapyd-deploy -l`, while deployed spider proyects `scrapyd-deploy -L default`

* To schedule the spider, run the following:

```
~ $ curl http://localhost:6800/schedule.json -d project=directvscraper -d spider=directv
```

* Alternatively you can use the [Directv Programing Guide - Data Cleaning.ipynb](Directv Programing Guide - Data Cleaning.ipynb) notebook to schedule and then clean the scrapped data.

* To check the progress of the spider job, visit `http://localhost:6800/jobs`

* To cancel the job, you can run the following:

```
~ $ curl http://localhost:6800/cancel.json -d project=directvscraper -d job=<JOB_ID>
```

### Debugging

If you want to debug specific pages, you can run the following code

```
~ $ scrapy shell <URL>
```

### More about Scrapyd

More info about the HTTP services available [here](https://doc.scrapy.org/en/0.12/topics/scrapyd.html)
