import requests
import os

from dotenv import load_dotenv
load_dotenv()

from dataclasses import dataclass

@dataclass
class Article:
    description: str
    image_url: str
    link: str
    source_name: str
    title: str

    def get_hashtags(self):
        return "#noticias #ultimaHora #guayaquil #ecuador #formateo #laptops #windows10 #office"

    def get_ads(self):
        return "El formateador: Servicio de formateo de laptops windows 7, 10 e instalación de office, word, excel. Cambio de disco duro y memoria ram."
    
    def as_post(self):
        result = "Noticia: "
        result+= '"' + self.title +'"' + "\n\n"
        result+= self.description +"\n.\n.\n.\n"
        result+= self.get_ads() + "\n\n"
        result+= self.get_hashtags()
        return result

def get_news():
    newsdata_apikey = os.getenv('NEWSDATA_APIKEY')
    country = 'ec'
    query_terms = 'guayaquil'

    base_url = f'https://newsdata.io/api/1/news?apikey={newsdata_apikey}&q={query_terms}&country={country}'

    response = requests.get(base_url)
    articles = response.json()["results"]

    results = []
    for item in articles:
        a = Article(
            description=item["description"],
            image_url=item["image_url"],
            link=item["link"],
            source_name=item["source_name"],
            title=item["title"]
        )
        results.append(a)
    
    return results
