BOT_NAME = "museum_scraper"

# Укажите User-Agent, чтобы ваш спайдер выглядел как браузер
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

# Настройки, чтобы избежать блокировок
DOWNLOAD_DELAY = 1  # Задержка между запросами в секундах
#DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True

SPIDER_MODULES = ["museum_scraper.spiders"]
NEWSPIDER_MODULE = "museum_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Для логирования
LOG_LEVEL = 'INFO'

# Сохранение в JSON или CSV
FEED_FORMAT = 'json'  # Для сохранения в формате JSON
FEED_URI = 'output.json'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# # Для настройки браузера можно использовать настройки Selenium, например:
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = '/chromedriver.exe'  # Убедитесь, что путь правильный
SELENIUM_DRIVER_ARGUMENTS = ['--enable-unsafe-swiftshader', '--disable-extensions', '--disable-gpu', '--no-sandbox']  # Добавьте нужные аргументы

TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = "utf-8"

# DOWNLOADER_MIDDLEWARES = {
#     "museum_scraper.middlewares.MuseumScraperDownloaderMiddleware": 543,
#     "museum_scraper.middlewares.SeleniumMiddleware": 800
# }

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "museum_scraper.middlewares.MuseumScraperSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "museum_scraper.middlewares.MuseumScraperDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "museum_scraper.pipelines.MuseumScraperPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

