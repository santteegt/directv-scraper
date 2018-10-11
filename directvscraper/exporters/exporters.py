# -*- coding: UTF-8 -*-
from scrapy.exporters import BaseItemExporter
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.utils.python import to_bytes
import logging


class UnicodeJsonLinesItemExporter(BaseItemExporter):

    logger = logging.getLogger('UnicodeJsonLinesLogging')

    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file
        self.encoder = ScrapyJSONEncoder(ensure_ascii=False, encoding='UTF-8', **kwargs)

    def export_item(self, item):
        itemdict = dict(self._get_serialized_fields(item))
        data = self.encoder.encode(itemdict) + '\n'
        self.logger.info('==============')
        self.file.write(to_bytes(data, self.encoding))

    def finish_exporting(self):
        pass
