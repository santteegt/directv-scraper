# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import logging

logger = logging.getLogger('serializerLogger')


def unicode_serialization(stream):
    logger.info(stream)
    new_stream = stream.encode('utf-8')
    logger.info(new_stream)
    return new_stream


class Program(scrapy.Item):

    show_id = scrapy.Field(serializer=str)
    channel_number = scrapy.Field(serializer=int)
    channel_name = scrapy.Field(serializer=str)
    title = scrapy.Field(serializer=unicode_serialization)
    start_time = scrapy.Field(serializer=str)
    time_length = scrapy.Field(serializer=str)
    day = scrapy.Field(serializer=unicode_serialization)
    query_date = scrapy.Field(serializer=str)


class TvShow(scrapy.Item):

    id = scrapy.Field(serializer=str)
    description = scrapy.Field(serializer=unicode_serialization)