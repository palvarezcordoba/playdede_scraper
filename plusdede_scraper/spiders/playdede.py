from typing import List

from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from plusdede_scraper.requests.selenium_request import SeleniumRequest


class PlaydedeSpider(CrawlSpider):
    name = 'playdede'
    allowed_domains = ['playdede.com']
    rules = (
        Rule(LinkExtractor(allow=(r'pelicula/',)), callback='parse_moovie', follow=True),
    )

    base_url = "https://playdede.com/"
    login_url = f"{base_url}/login/"
    url_regex = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    def start_requests(self):
        yield SeleniumRequest(url=self.login_url, callback=self.login, wait_time=14,
                              wait_until=EC.presence_of_element_located((By.XPATH, "//form")))

    def login(self, response: Response):
        driver: WebDriver = response.meta["driver"]
        user = self.settings["PLAYDEDE_LOGIN_USER"]
        password = self.settings["PLAYDEDE_LOGIN_PASSWORD"]
        driver.find_element_by_css_selector("div.form-C:nth-child(3) > input:nth-child(2)").send_keys(user)
        driver.find_element_by_css_selector("div.form-C:nth-child(4) > input:nth-child(2)").send_keys(password)
        driver.find_element_by_css_selector("div.FormAcept > input:nth-child(1)").click()
        WebDriverWait(driver, 14).until(EC.visibility_of_element_located((By.XPATH, "//article[1]")))
        yield SeleniumRequest(url=self.base_url)

    def parse_moovie(self, response: Response):
        # inspect_response(response, self)
        title: str = response.css("div.data:nth-child(2) > h1:nth-child(1)::text").get()
        genres: List[str] = response.css(".sgeneros > a::text").getall()
        date: str = response.css(".date::text").get()
        wallpaper: str = response.css(".wallpaper::attr(style)").re(self.url_regex)[0]
        description: str = response.css(".overview > p::text").get()
        rating = float(response.css(".nota > span::text").get())

        # driver: WebDriver = response.meta["driver"]
        # driver.find_element_by_css_selector(".act_N").click()
        download_links = response.css(".linksUsers > li")
        parsed_download_links = list(map(self.parse_download_link, download_links))
        yield dict(
            title=title,
            genres=genres,
            date=date,
            wallpaper=wallpaper,
            description=description,
            rating=rating,
            download_links=parsed_download_links
        )

    @staticmethod
    def parse_download_link(link):
        return dict(
            download_link=link.css("a::attr(href)").get(),
            download_provider_icon=link.css("span:nth-child(1) > img::attr(src)").get(),
            download_provider_name=link.css("span:nth-child(1)::text").get(),
            language_flag_icon=link.css("span:nth-child(2) > img::attr(src)").get(),
            i_dont_know_whats_this_wtf=link.css("span:nth-child(1) > b::text").get(),
        )

    def _build_request(self, rule_index, link):
        return SeleniumRequest(
            url=link.url,
            callback=self._callback,
            errback=self._errback,
            meta=dict(rule=rule_index, link_text=link.text),
        )
