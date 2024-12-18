import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings
import os
from museum_scraper.items import CultureItem
import time


class CultureSpider(scrapy.Spider):
    name = "culture_spider"
    allowed_domains = ["ar.culture.ru"]
    # Максимальная страница, которую будем скрапить
    max_page_number = 9
    start_urls = [f'https://ar.culture.ru/ru/subjects-catalog?page={i}' for i in range(301, 756 + 1)]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'FEED_URI': '../data/scraped/artefact_catalog_data.json',
        'FEED_FORMAT': 'json',
    }

    def __init__(self, *args, **kwargs):
        super(CultureSpider, self).__init__(*args, **kwargs)

        # Указываем путь к локальному chromedriver
        self.driver_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chromedriver.exe')

        # Получаем настройки браузера
        self.driver_name = get_project_settings().get('SELENIUM_DRIVER_NAME')
        self.driver_arguments = get_project_settings().get('SELENIUM_DRIVER_ARGUMENTS', [])  # Пустой список по умолчанию

        # Настроим Chrome options
        chrome_options = Options()
        for argument in self.driver_arguments:
            chrome_options.add_argument(argument)

        # Запуск Chrome WebDriver
        self.driver = webdriver.Chrome(service=Service(self.driver_path), options=chrome_options)
        self.logger.info("Selenium WebDriver initialized")

    def start_requests(self):
        # Используем Selenium для загрузки страницы\
        self.logger.info(f"Готово к загрузке {len(self.start_urls)} ссылок каталога.")
        for url in self.start_urls:
            self.logger.info(f"Run {url}")
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        url = self.get_right_page(response.url)
        self.logger.info(f"Парсинг страницы: {url}")
        # Загружаем страницу через Selenium
        self.driver.get(url)
        self.driver.refresh()
        # Ожидание 5 секунд, чтобы страница успела загрузиться
        time.sleep(5)  # Можно увеличить, если нужно больше времени

        # Используем JavaScript для ожидания полной загрузки страницы
        self.logger.info("Ожидание полной загрузки страницы с помощью JavaScript...")
        try:
            # Ожидаем, пока страница не будет полностью загружена
            self.driver.execute_script("return document.readyState == 'complete';")
            self.logger.info("Страница загружена.")
        except Exception as e:
            self.logger.error(f"Ошибка при ожидании загрузки страницы: {e}")
            self.driver.quit()

        # Получаем HTML страницы после выполнения JavaScript
        selenium_html = self.driver.page_source

        # Создаем Scrapy Response из рендеренного HTML
        response = HtmlResponse(url=response.url, body=selenium_html, encoding='utf-8')

        # Извлекаем ссылки на страницы экспонатов с текущей страницы каталога
        object_links = response.css('a.listing_block::attr(href)').getall()
        self.logger.info(f"Найдено ссылок на экспонаты: {len(object_links)}")
        self.logger.info(f"Ссылки на экспонаты: {object_links}")

        # Извлекаем ссылки на страницы экспонатов с текущей страницы каталога
        object_links = response.css('a.listing_block::attr(href)').getall()
        self.logger.info(f"Найдено ссылок на экспонаты: {len(object_links)}")

        # Фильтруем ссылки: удаляем пустые или неправильные
        object_links = [link for link in object_links if link and not link.startswith('%url%')]

        self.logger.info(f"Отфильтровано ссылок на экспонаты: {len(object_links)}")
        self.logger.info(f"Ссылки на экспонаты: {object_links}")

        # Переход к каждой странице экспоната
        for link in object_links:
            # Строим абсолютный URL для перехода к странице экспоната
            full_link = response.urljoin(link)
            yield response.follow(full_link, callback=self.parse_object)

    def parse_object(self, response):
        # Создаем item для каждого экспоната
        item = CultureItem()

        # Извлекаем информацию об экспонате
        item['title'] = response.css('h1.subject_info_block__title::text').get(default='Не указано').strip()
        if not item['title']:
            self.logger.warning(f"Заголовок не найден на странице: {response.url}")

        item['authors'] = response.css('div.subject_info_block__authors a.subject_info_block__author::text').getall()
        item['creation_time'] = self.extract_field(response, 'Время создания')
        item['size'] = self.extract_field(response, 'Размер')
        item['technique'] = self.extract_field(response, 'Техника')
        item['collection'] = self.extract_field(response, 'Коллекция')
        item['exhibition'] = self.extract_field(response, 'Выставка')

        # Извлечение описания из блока main_content
        item['description'] = self.extract_description(response)

        # Ссылка на текущую страницу экспоната
        item['url'] = response.url

        # Логируем, что данные для экспоната собраны
        self.logger.info(f"Данные для {item['title']} собраны.")

        # Возвращаем собранный item
        yield item

    def extract_description(self, response):
        """
        Извлекает текст из блока с классом 'main_content', исключая текст из элементов
        с data-placeholder='Подпись к картинке'.
        """
        main_content = response.css('div.main_content')

        # Извлекаем все текстовые части, игнорируя текст в блоках с указанным атрибутом
        description_parts = []

        for block in main_content.css('.block_wrapper'):
            if not block.css('[data-placeholder="Подпись к картинке"]'):
                # Извлекаем текст, если в блоке нет подписи к картинке
                text_content = block.css('.editable_block::text').getall()
                # \xa0 - это Unicode для NBSP
                cleaned_text = [text.replace('\xa0', ' ').strip() for text in text_content]
                description_parts.extend(cleaned_text)

        # Объединяем все извлеченные части текста в один
        description = ' '.join(part.strip() for part in description_parts if part.strip())

        return description

    def extract_field(self, response, field_name):
        # Используем XPath для извлечения информации по полю
        field_value_selector = f"//div[contains(@class, 'subject_info_block__group')][div[contains(@class, 'subject_info_block__group_label') and text()='{field_name}']]/div[contains(@class, 'subject_info_block__group_value')]//text()"
        field_value = response.xpath(field_value_selector).get(default='Не указано').strip()
        return field_value

    def get_right_page(self, current_url):
        # Проверка на наличие хеша и извлечение номера страницы
        base_url = "https://ar.culture.ru/ru/subjects-catalog"
        if 'page=' in current_url:
            page_number = int(current_url.split('page=')[-1])
        else:
            page_number = 1  # Для первой страницы
        return f"{base_url}#{page_number}"

    def closed(self, reason):
        # Закрываем WebDriver после выполнения паука
        self.driver.quit()