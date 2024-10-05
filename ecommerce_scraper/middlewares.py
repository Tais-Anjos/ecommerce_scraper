from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
import time
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import random
from io import BytesIO
from PIL import Image
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from captcha_solver import CaptchaSolver

class EcommerceScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
        

class EcommerceScraperDownloaderMiddleware:
    def __init__(self):
        # Configura o WebDriver do Selenium (Firefox com modo headless opcional)
        firefox_options = Options()
        firefox_options.add_argument('--headless')  # Rodar o navegador em modo headless

        firefox_options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        service = Service(r'D:\Tata\Projetinhos - VS CODE\ecommerce_scraper\ecommerce_scraper\ecommerce_scraper\webdriver\geckodriver.exe')

        self.driver = webdriver.Firefox(service=service, options=firefox_options)

        # Configurando o solver para usar RuCaptcha (substitua pela sua chave da API)
        self.solver = CaptchaSolver('rucaptcha', api_key='YOUR_RUCAPTCHA_API_KEY')

    def process_request(self, request, spider):
        self.driver.get(request.url)
        time.sleep(random.uniform(3, 5))  # Atraso aleatório para evitar bloqueio

        # Verifica se há CAPTCHA na página
        if "captcha" in self.driver.page_source.lower():
            spider.logger.warning(f"CAPTCHA detectado em {request.url}. Tentando resolver...")

            try:
                # Usando espera explícita para aguardar o carregamento da imagem do CAPTCHA
                captcha_image_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'img.captcha-img'))
                )

                captcha_image_base64 = captcha_image_element.get_attribute('src').split(',')[1]

                # Decodifica a imagem do CAPTCHA
                captcha_image = Image.open(BytesIO(base64.b64decode(captcha_image_base64)))
                captcha_image.save('captcha_image.png')

                # Usando o solver de CAPTCHA da RuCaptcha
                with open('captcha_image.png', 'rb') as captcha_file:
                    captcha_solution = self.solver.solve_captcha(captcha_file)

                spider.logger.info(f"CAPTCHA resolvido: {captcha_solution}")

                # Insere o texto do CAPTCHA resolvido no campo correto
                captcha_input = self.driver.find_element(By.CSS_SELECTOR, 'input.captcha-input')
                captcha_input.send_keys(captcha_solution)

                # Submete o CAPTCHA
                submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button.submit-captcha')
                submit_button.click()

                # Aguarda o carregamento da página após CAPTCHA
                time.sleep(3)

            except Exception as e:
                spider.logger.error(f"Erro ao tentar resolver o CAPTCHA: {str(e)}")
                return HtmlResponse(self.driver.current_url, body=self.driver.page_source, encoding='utf-8', request=request)

        # Captura o conteúdo da página após o CAPTCHA ser resolvido
        body = self.driver.page_source
        return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

    def spider_closed(self, spider):
        # Fecha o WebDriver quando o spider for encerrado
        spider.logger.info("Fechando o WebDriver")
        self.driver.quit()