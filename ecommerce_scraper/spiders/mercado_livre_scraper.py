import scrapy
from ecommerce_scraper.items import EcommerceScraperItem

class MercadoLivre(scrapy.Spider):
    name = 'mercadolivre'
    allowed_domains = ['mercadolivre.com.br']
    start_urls = [
        'https://lista.mercadolivre.com.br/_Container_moda-jeans_AGE*GROUP_6725189'
    ]
    
    page_count = 1
    max_pages = 10  # Define o número máximo de páginas a ser raspado
    
    def parse(self, response):
        # Extrai todos os produtos na página de listagem
        produtos = response.css('li.ui-search-layout__item')
        
        for produto in produtos:
            # Extrai a URL do produto
            produto_url = produto.css('a.ui-search-link::attr(href)').get()
            
            # Segue o link do produto para pegar os dados da página de detalhes
            if produto_url:
                yield response.follow(produto_url, self.parse_product)
        
        # Paginação: encontra a URL da próxima página e segue
        if self.page_count < self.max_pages:
            next_page = response.css('a.andes-pagination__link.ui-search-link::attr(href)').get()
            if next_page:
                self.page_count += 1
                yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        # Extrair dados da página de detalhes do produto
        item = EcommerceScraperItem()

        # Título do produto
        item['titulo'] = response.css('h1.ui-pdp-title::text').get()

        # Preço do produto
        preco_inteiro = response.css('span.andes-money-amount__fraction::text').get(default='00')
        preco_centavos = response.css('span.andes-money-amount__cents::text').get(default='00')
        item['preco'] = f"{preco_inteiro},{preco_centavos}"
        
        # Classificação
        item['classificacao'] = response.css('span.ui-pdp-review__rating::text').get(default='N/A') #ex 4.6
        
        # Quantidade de classificações
        item['qtd_classificacao'] = response.css('span.ui-pdp-review__amount::text').get(default='0') #ex -->4000<-- de 4.6
        
        # Marca do produto
        #item['marca'] = response.css('span.ui-pdp-color--BLACK.ui-pdp-size--XSMALL.ui-pdp-family--SEMIBOLD::text').getall(default='Genérica') #ex: Nike
        item['marca'] = response.xpath('//span[contains(text(), "Marca:")]/following-sibling::span/text()').get(default='Marca não encontrada')

        # URL do produto
        item['url'] = response.url

        # Plataforma (Site do produto)
        item['plataforma'] = 'Mercado Livre'

        # Retorna o item raspado
        yield item
