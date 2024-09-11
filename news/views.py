from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import News
import requests
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html',{
            'form': UserCreationForm()
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            #register user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                login(request, user)
                return redirect('news')
            except IntegrityError:
                return render(request, 'signup.html',{
                    'form': UserCreationForm,
                    'error': 'User already exists'
                })
        return render(request, 'signup.html',{
            'form': UserCreationForm,
            'error': 'Password do not match'
        })

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html',{
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request,
            username=request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error':'Username or Password is incorrect'
            })
        else:
            login(request, user)
            return redirect('news')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

@login_required
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

