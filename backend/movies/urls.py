"""
URL configuration for flix_n_chill project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path("collect/", view=views.movie_collect),
    path("list/", view=views.MovieListView.as_view()),
    path("list/<str:genre_name>/", view=views.MovieGenreListView.as_view()),
    path("<int:pk>/", view=views.MovieDetailView.as_view()),
    path("<int:pk>/like/", view=views.movie_like),
    path("<int:pk>/review/", view=views.create_review),
    path('<int:pk>/user-review/', views.get_user_review),
    path('<int:movie_pk>/review/<int:review_pk>/', views.update_review),  
    path('<int:movie_pk>/review/<int:review_pk>/delete/', views.delete_review),  
    path("search/", view=views.MovieSearchView.as_view()),

    # path("providers/", view=views.collect_provider),
]
