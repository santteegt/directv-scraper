#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import re
import itertools
from sys import version
from directvscraper.items import Program, TvShow

if version[0] == '2':
    itertools.zip_longest = itertools.izip_longest

URL_SCROLLING = 'https://www.directv.com.ec/movil/ProgramGuide/ProgramGuide?isForwardPress=true&isBackPress=false'
TV_CHANNEL_RAGE = (130, 600)


class DirectvSpider(scrapy.Spider):
    """

    Crawl Directv programming guide. Schedule is available for the following 7 days (from the first request)

    """
    name = "directv"

    # Datetime information related to shown programming schedule
    form_controller = "//form[@id='dateForm']/div[@id='guide-scroller']/div[@class='Contenedor-controladores-guia']"
    calendar_form = "/div[@class='Box-GuiaProgramacion']"
    cf_date = "/input[@class='dayJump']/@value"  # should be extracted by attribute name
    cf_day = "/label[@class='day']/text()"
    cf_start_time = "/div[@class='TiempoComienzo']/text()"
    cf_end_time = "/div[@class='TiempoFin']/text()"

    # Programming guide data
    channel_list_xpath = "//table[@id='program-guide']/tbody/tr/td[@class='channel']/a/p/text()"
    channel_content_anchor = "//table[@id='program-guide']/tbody/tr/td[not(contains(@class,'channel'))]/a"
    channel_content_title = '/div/dl/dt/strong/text()'
    channel_content_time = '/div/dl/dd'  # return two values per record: 'Comienza:' & 'Duracion:'
    content_start_time_regex = r'\<dd\>\s+\<strong>Comienza\:\<\/strong>\s+(.{5})\s+'
    # content_time_length_regex = r'\<dd\>\<strong\>Duración\:\<\/strong\>\s+(.*)\r\s+'
    content_time_length_regex = r'\<dd\>\<strong\>Duraci.*n\:\<\/strong\>\r\s+(.*)\smin\r\s+'

    item_detail_url = "//table[@id='program-guide']/tbody/tr/td[not(contains(@class, 'channel'))]/a/@href"
    item_content_detail = "//div[@id='main']/div[@data-role='content']/p[@class='desc']/text()"
    init_data = None

    national_tv_channels = None

    limit_query = None

    def append_dummy(self, item):
        """
        Functon to append a dummy parameter to URL request, in order to avoid scrapy duplicate requests filtering
        :param item: dict with schedule information
        :return: dummy parameter as string
        """
        return '&dummy=%s%s' % (item['init_day'], item['end_time'])

    def parse_channel_list(self, response):
        nat_tv_range = TV_CHANNEL_RAGE
        channel_list = response.xpath(self.channel_list_xpath).extract()
        channel_list_numbers = [int(channel_list[i]) for i in range(0, len(channel_list), 2)]
        channel_list_names = [channel_list[i] for i in range(1, len(channel_list), 2)]
        channel_list = zip(channel_list_names, channel_list_numbers)

        self.national_tv_channels = [channel for channel in list(channel_list) if channel[1] < nat_tv_range[1]]
        self.limit_query = len(self.national_tv_channels)

        # print(self.national_tv_channels)

    def parse_programming_guide_items(self, response):
        titles = response.xpath(self.channel_content_anchor + self.channel_content_title).extract()[:self.limit_query]
        start_times = response.xpath(self.channel_content_anchor + self.channel_content_time)\
            .re(self.content_start_time_regex)[:self.limit_query]
        time_lengths = response.xpath(self.channel_content_anchor + self.channel_content_time)\
            .re(self.content_time_length_regex)[:self.limit_query]

        return titles, start_times, time_lengths

    def parse_programming_guide_table(self, response, calendar_item):

        titles, start_times, time_lengths = self.parse_programming_guide_items(response)

        query_dates = [calendar_item['date']] * len(titles)
        days = [calendar_item['init_day']] * len(titles)

        print("LENGTHS ===> %s %s %s %s " %
              (len(self.national_tv_channels), len(titles), len(start_times), len(time_lengths)))

        program_list = [Program(channel_number=channel[1], channel_name=channel[0], title=title, start_time=start_time,
                                time_length=time_length, day=day, query_date=query_date)
                        for channel, title, start_time, time_length, query_date, day
                        in itertools.zip_longest(self.national_tv_channels, titles, start_times, time_lengths,
                                                 query_dates, days)]

        return program_list

    def get_programming_guide_linkages(self, response):

        return response.xpath(self.item_detail_url).extract()[:self.limit_query]

    def start_requests(self):
        """
        Entrance function that returns an iterable of requests to the scrapper
        :return:
        """
        start_urls = [
            'https://www.directv.com.ec/movil/ProgramGuide/ProgramGuide'
        ]
        for url in start_urls:
            yield scrapy.Request(url=url,
                                 meta={'dont_redirect': True},
                                 callback=self.parse)

    def parse(self, response):
        """
        Callback function to crawl web responses
        :param response: HTMl Document entity
        :return:
        """

        item = None
        for calendar in response.xpath(self.form_controller + self.calendar_form):
            item = {
                'date': calendar.xpath('/' + self.cf_date).extract_first(),
                'init_day': re.search('.*\-', calendar.xpath('/' + self.cf_day).extract_first()).group(0)[:-1],
                'start_time': re.search('.*\s', calendar.xpath('/' + self.cf_start_time).extract_first()).group(0)[:-1],
                'end_time': calendar.xpath('/' + self.cf_end_time).extract_first()
            }

        if self.init_data is None:

            self.init_data = item
            self.parse_channel_list(response)

        programs = self.parse_programming_guide_table(response, item)

        program_det_urls = self.get_programming_guide_linkages(response)

        for i in range(len(programs)):
            programs[i]['show_id'] = program_det_urls[i][(program_det_urls[i].find('=') + 1):]
            yield programs[i]

        for url in program_det_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_programming_detail)

        # iterates until finding a repeated URL: reaches the end of a programming guide availability (1 week)
        yield scrapy.Request(URL_SCROLLING + self.append_dummy(item), meta={'dont_redirect': True}, callback=self.parse)

    def parse_programming_detail(self, response):

        yield TvShow(id=(response.url[(response.url.find('=') + 1):]),
                     description=response.xpath(self.item_content_detail).extract_first())






