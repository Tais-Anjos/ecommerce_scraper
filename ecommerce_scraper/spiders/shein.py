import scrapy
import time
import random
from ecommerce_scraper.items import EcommerceScraperItem

class SheinSpider(scrapy.Spider):
    name = 'shein'
    allowed_domains = ['br.shein.com']
    start_urls = [
        'https://br.shein.com/Women-Denim-c-1930.html?adp=2633787&categoryJump=true&ici=br_tab04navbar04menu01dir10&src_identifier=fc%3DWomen%20Clothing%60sc%3DWomen%20Clothing%60tc%3DShop%20by%20category%60oc%3DDenim%60ps%3Dtab04navbar04menu01dir10%60jc%3Dreal_1930&src_module=topcat&src_tab_page_id=page_goods_detail1728087196571'
    ]
    
    page_count = 1
    max_pages = 5  # Limite de páginas a serem raspadas

    def parse(self, response):
        # Verificar se houve bloqueio por CAPTCHA
        if "captcha" in response.text.lower():
            self.logger.warning(f"CAPTCHA detectado na página {response.url}. O middleware está tentando resolver.")
            return

        # Extrai os produtos da página
        produtos = response.css('section.product-list__item')

        if not produtos:
            self.logger.warning(f"Nenhum produto encontrado na página {response.url}")

        for produto in produtos:
            # Extrai a URL do produto
            produto_url = produto.css('a::attr(href)').get()
            if produto_url:
                yield response.follow(produto_url, self.parse_product)
            else:
                self.logger.warning(f"URL do produto ausente em {response.url}")

        # Implementa a paginação
        if self.page_count < self.max_pages:
            next_page = response.css('a.she-pager__next::attr(href)').get()  # Verifique o seletor correto
            if next_page:
                self.page_count += 1
                self.logger.info(f"Indo para a próxima página: {next_page}")

                # Atraso aleatório para evitar comportamento suspeito
                time.sleep(random.uniform(2, 5))

                yield response.follow(next_page, self.parse)
            else:
                self.logger.info(f"Não foi encontrada a próxima página em {response.url}, terminando a paginação.")
        else:
            self.logger.info("Limite máximo de páginas atingido, encerrando spider.")

    def parse_product(self, response):
        # Cria o objeto item
        item = EcommerceScraperItem()

        # Extrai os detalhes do produto
        item['titulo'] = response.xpath('//*[@id="goods-detail-v3"]/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/h1/text()').get(default='Título não disponível')

        # Extrai o preço do produto
        preco_inteiro = response.xpath('//*[@id="productIntroPrice"]/div/div/div/div/div/span/text()').get()
        item['preco'] = preco_inteiro.strip() if preco_inteiro else 'Preço não disponível'

        # Classificação do produto
        item['classificacao'] = response.xpath('//*[@id="goods-detail-v3"]/div/div[1]/div/div[2]/div[1]/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]').get(default='N/A')
        
        # Quantidade de classificações (reviews)
        item['qtd_classificacao'] = response.css('span.product-intro__head-rate-num::text').get(default='0')
        
        # Marca do produto
        item['marca'] = response.xpath('//*[@id="goods-detail-v3"]/div/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[9]/div[3]/div[2]/div/div[1]/div[3]/div[1]/div/text()').get(default='Genérica')

        # URL do produto
        item['url'] = response.url

        # Plataforma (nome do site)
        item['plataforma'] = 'Shein'

        # Retorna o item raspado
        yield item
