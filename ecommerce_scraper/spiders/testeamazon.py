import scrapy
from ecommerce_scraper.items import EcommerceScraperItem

class AmazonSpider(scrapy.Spider):
    name = 'amazonna'
    allowed_domains = ['amazon.com.br']
    start_urls = [
        'https://www.amazon.com.br/s?k=jeans+feminino'
    ]

    page_count = 1

    def parse(self, response):
        # Extrai todos os produtos na página de listagem
        produtos = response.css('div.s-main-slot div.s-result-item')

        for produto in produtos:
            # Tenta pegar a URL do produto
            produto_url = produto.css('a.a-link-normal.s-no-outline::attr(href)').get()
            
            # Extrai a classificação (estrelas) diretamente da listagem
            classificacao = produto.css('span.a-icon-alt::text').get(default='N/A')

            # Segue o link do produto para pegar os dados da página de detalhes
            if produto_url:
                produto_url = response.urljoin(produto_url)
                yield response.follow(produto_url, self.parse_product, meta={'classificacao': classificacao})
        
        # Paginação: encontra a URL da próxima página e segue
        if self.page_count < 5:  # Define um limite para o número de páginas a serem raspadas
            next_page = response.css('ul.a-pagination li.a-last a::attr(href)').get()
            if next_page:
                self.page_count += 1
                next_page = response.urljoin(next_page)
                yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        # Cria um item para armazenar os dados do produto
        item = EcommerceScraperItem()

        # Título do produto
        item['titulo'] = response.css('span#productTitle::text').get().strip()

        # Preço do produto
        preco_inteiro = response.css('span.a-price-whole::text').get(default='00')
        preco_centavos = response.css('span.a-price-fraction::text').get(default='00')
        item['preco'] = f"{preco_inteiro},{preco_centavos}"

        # Classificação (passada da página de listagem)
        item['classificacao'] = response.meta.get('classificacao', 'N/A')

        # Quantidade de avaliações
        item['qtd_classificacao'] = response.css('span#acrCustomerReviewText::text').get(default='0').strip()

        # Marca do produto (Amazon pode não ter uma marca definida claramente)
        item['marca'] = response.css('a#bylineInfo::text').get(default='Desconhecida').strip()

        # URL do produto
        item['url'] = response.url

        # Plataforma (pode ser um valor fixo como "Amazon")
        item['plataforma'] = 'Amazon'

        # Retorna o item raspado
        yield item
