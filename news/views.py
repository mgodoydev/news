from django.shortcuts import render
from django.utils import timezone
from .models import News
import requests
from django.conf import settings
from django.core.paginator import Paginator

# Create your views here.

def home(request):
    return render(request, 'home.html')

def get_news(request):
    category = request.GET.get('category', 'sports')  # Obtén la categoría de los parámetros GET
    api_key = settings.NEWS_API_KEY
    url = f'https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={api_key}'
    response = requests.get(url)
    data = response.json()
    news_articles = data.get('articles', [])

    # Guarda o actualiza las noticias en la base de datos
    for article in news_articles:
        News.objects.update_or_create(
            title=article.get('title'),
            defaults={
                'description': article.get('description', 'No description available'),
                'url': article.get('url'),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'url_to_image': article.get('urlToImage'),
                'published_at': article.get('publishedAt', None),
                'category': category
            }
        )

    # Obtén todas las noticias de la base de datos filtradas por categoría
    news_from_db = News.objects.filter(category=category).order_by('-published_at')

    # Configura la paginación
    paginator = Paginator(news_from_db, 6)  # Muestra 6 noticias por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pasa las noticias y la página actual a la plantilla
    return render(request, 'news.html', {
        'news': page_obj,
        'current_category': category,
        'page_obj': page_obj
    })

