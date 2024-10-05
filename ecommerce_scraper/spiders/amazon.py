import scrapy
from ecommerce_scraper.items import EcommerceScraperItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['www.amazon.com.br']
    start_urls = [
        'https://www.amazon.com.br/s?i=fashion-womens&rh=n%3A17682117011&fs=true'
    ]
    
    page_count = 1  # Contador de páginas

    def parse(self, response):
        # Corrige o seletor para pegar os produtos na listagem
        produtos = response.css('div.s-main-slot div.s-result-item')

        for produto in produtos:
            item = EcommerceScraperItem()  # Instanciar o item

            # Nome do produto
            item['titulo'] = produto.css('span.a-size-base-plus.a-color-base.a-text-normal::text').get(default='Título não disponível')
            
            # Preço do produto
            preco_inteiro = produto.css('span.a-price-whole::text').get(default='N/A')  # Preço inteiro
            preco_centavos = produto.css('span.a-price-fraction::text').get(default='00')  # Preço em centavos
            item['preco'] = f"{preco_inteiro},{preco_centavos}" if preco_inteiro != 'N/A' else 'Preço não disponível'
            
            # Classificação (número de estrelas)
            item['classificacao'] = produto.css('span.a-icon-alt::text').get(default='0')
            
            # Quantidade de classificações (número de reviews)
            item['qtd_classificacao'] = produto.css('span.a-size-base.s-underline-text::text').get(default='0')
            
            # Marca do produto (marca pode ser extraída de diferentes lugares dependendo da listagem)
            item['marca'] = produto.css('span.a-size-base-plus.a-color-base::text').get(default='Genérica')
            
            # Link do produto
            produto_url = produto.css('a.a-link-normal::attr(href)').get()
            if produto_url:
                item['url'] = response.urljoin(produto_url)
            else:
                item['url'] = 'URL não disponível'
            
            # Plataforma
            item['plataforma'] = 'Amazon'
            print(produtos)
            yield item
        
        # Verificar se há uma próxima página e seguir
        next_page = response.css('a.s-pagination-next::attr(href)').get()
        if next_page and self.page_count < 3:  # Limitar a 3 páginas, por exemplo
            self.page_count += 1  # Incrementa o contador de páginas
            yield response.follow(next_page, self.parse)
            
    
