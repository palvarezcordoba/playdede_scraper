from scrapy_selenium import SeleniumRequest as _SeleniumRequest


class SeleniumRequest(_SeleniumRequest):
    def __init__(self, wait_time=None, wait_until=None, screenshot=False, script=None, url=None, callback=None,
                 method='GET', headers=None, body=None,
                 cookies=None, meta=None, encoding='utf-8', priority=0,
                 dont_filter=False, errback=None, flags=None, cb_kwargs=None):
        super(SeleniumRequest, self).__init__(wait_time, wait_until, screenshot, script, url, callback, method, headers,
                                              body, cookies, meta, encoding, priority, dont_filter, errback, flags,
                                              cb_kwargs)
