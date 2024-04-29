from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
import json
from django.shortcuts import get_object_or_404

from .models import Movie

def home(request):
    #return HttpResponse('<h1>Welcome to Home Page</h1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html', {'name':'Paola Vallejo'})
    searchTerm = request.GET.get('searchMovie') # GET se usa para solicitar recursos de un servidor
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies':movies})


def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email') 
    return render(request, 'signup.html', {'email':email})

def statistics(request):
    # Consulta para obtener películas agrupadas por año
    movies_by_year = Movie.objects.values('year').annotate(total=Count('id')).order_by('year')
    
    # Convertir los resultados de la consulta a una lista de diccionarios
    movies_by_year_list = [{'year': item['year'], 'total': item['total']} for item in movies_by_year]
    
    # Serializar la lista de diccionarios a JSON
    movies_by_year_json = json.dumps(movies_by_year_list)
    
    return render(request, 'statistics.html', {'movies_by_year_json': movies_by_year_json})

def detail(request, movie_id):
    movie = get_object_or_404(Movie,pk=movie_id)
    return render(request, 'detail.html', {'movie':movie})