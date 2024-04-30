from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
import json
from django.shortcuts import get_object_or_404, redirect

from .models import Movie, Review

from .forms import ReviewForm

from django.contrib.auth.decorators import login_required

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

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
    matplotlib.use('Agg')
    # Gráfica de películas por año
    all_movies = Movie.objects.all()
    movie_counts_by_year = {}
    for movie in all_movies:
        year = movie.year if movie.year else "None"
        if year in movie_counts_by_year:
            movie_counts_by_year[year] += 1
        else:
            movie_counts_by_year[year] = 1

    year_graphic = generate_bar_chart(movie_counts_by_year, 'Year', 'Number of movies')

    # Gráfica de películas por género
    movie_counts_by_genre = {}
    for movie in all_movies:
        # Obtener el primer género
        genres = movie.genre.split(',')[0].strip() if movie.genre else "None"
        if genres in movie_counts_by_genre:
            movie_counts_by_genre[genres] += 1
        else:
            movie_counts_by_genre[genres] = 1

    genre_graphic = generate_bar_chart(movie_counts_by_genre, 'Genre', 'Number of movies')

    return render(request, 'statistics.html', {'year_graphic': year_graphic, 'genre_graphic': genre_graphic})


def generate_bar_chart(data, xlabel, ylabel):
    keys = [str(key) for key in data.keys()]
    plt.bar(keys, data.values())
    plt.title('Movies Distribution')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=90)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')
    return graphic

def detail(request, movie_id): 
    movie = get_object_or_404(Movie,pk=movie_id) 
    reviews = Review.objects.filter(movie = movie)
    return render(request, 'detail.html', {'movie':movie, 'reviews': reviews})

@login_required
def createreview(request, movie_id): 
    movie = get_object_or_404(Movie,pk=movie_id) 
    if request.method == 'GET': 
        return render(request, 'createreview.html', {'form':ReviewForm(), 'movie': movie}) 
    else: 
        try: 
            form = ReviewForm(request.POST) 
            newReview = form.save(commit=False) 
            newReview.user = request.user 
            newReview.movie = movie 
            newReview.save() 
            return redirect('detail', newReview.movie.id) 
        except ValueError: 
            return render(request, 'createreview.html', {'form':ReviewForm(),'error':'bad data passed in'})

@login_required      
def updatereview(request, review_id): 
    review = get_object_or_404(Review,pk=review_id,user=request.user) 
    if request.method =='GET': 
        form = ReviewForm(instance=review) 
        return render(request, 'updatereview.html', {'review': review,'form':form}) 
    else: 
        try: 
            form = ReviewForm(request.POST, instance=review) 
            form.save() 
            return redirect('detail', review.movie.id) 
        except ValueError: 
            return render(request, 'updatereview.html', {'review': review,'form':form,'error':'Bad data in form'})

@login_required      
def deletereview(request, review_id): 
    review = get_object_or_404(Review, pk=review_id, user=request.user) 
    review.delete() 
    return redirect('detail', review.movie.id)