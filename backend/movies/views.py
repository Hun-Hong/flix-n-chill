from django.shortcuts import render, get_object_or_404
from django.conf import settings
import requests
from .serializers import MovieListSerializer, MovieCreateSerializer, MovieDetailSerializer, ReviewSerializer 
from .models import Movie, Genre, MovieProvider
import json
from .models import Genre
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db.models import Q
from datetime import datetime

# Create your views here.


## DATA COLLECT
@api_view(["POST"])
def movie_collect(request):
    # url = "https://api.themoviedb.org/3/genre/movie/list?language=ko"

    saved = 0
    for page_idx in range(1, 26):
        list_url = f"https://api.themoviedb.org/3/movie/top_rated?language=ko-KR&page={page_idx}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_API_KEY}",
        }
        response = requests.get(list_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            movies = data.get("results", [])

            for movie in movies:
                tmdb_id = movie["id"]

                if not Movie.objects.filter(tmdb_id=tmdb_id).exists():
                    detail_url = (
                        f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=ko-KR"
                    )
                    detail_response = requests.get(detail_url, headers=headers)

                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                    else:
                        continue

                    provider_url = (
                        f"https://api.themoviedb.org/3/movie/{tmdb_id}/watch/providers"
                    )
                    provider_response = requests.get(provider_url, headers=headers)
                    if provider_response.status_code == 200:
                        provider_data = provider_response.json()
                    else:
                        provider_data = {}

                    serializer = MovieCreateSerializer(
                        data={
                            "tmdb_id": tmdb_id,
                            "title": detail_data.get("title", ""),
                            "original_title": detail_data.get("original_title", ""),
                            "overview": detail_data.get("overview", ""),
                            "adult": detail_data.get("adult", False),
                            "budget": detail_data.get("budget", 0),
                            "origin_country": detail_data.get(
                                "origin_country", "UNKNOWN"
                            )[0],
                            "runtime": detail_data.get("runtime", 0),
                            "release_date": detail_data.get(
                                "release_date", "1900-01-01"
                            ),
                            "tagline": detail_data.get("tagline", ""),
                            "vote_average": detail_data.get("vote_average", 0.0),
                            "poster_path": detail_data.get("poster_path", ""),
                        }
                    )
                    if serializer.is_valid():
                        cur_movie = serializer.save()
                        saved += 1
                        for option_type in ["buy", "flatrate", "rent"]:
                            provider_list = (
                                provider_data.get("results")
                                .get("KR", {})
                                .get(option_type, [])
                            )
                            for provider in provider_list:
                                cur_movie.providers.add(
                                    MovieProvider.objects.get(
                                        tmdb_id=provider["provider_id"]
                                    )
                                )
                        for genre in detail_data.get("genres", []):
                            cur_movie.genres.add(Genre.objects.get(tmdb_id=genre["id"]))
                    else:
                        print(serializer.errors)

    context = {
        "result": f"{saved} movies saved",
        "message": serializer.errors,
        "data": provider_data,
    }
    return Response(context, status.HTTP_200_OK)


# 함수 방식
# @api_view(["GET"])
# def movie_list(request):
#     top_movies = Movie.objects.order_by('-vote_average')

#     serializer = MovieSerializer(top_movies, many=True)

#     return Response(serializer.data)

# 클래스 방식
class MovieListView(ListAPIView):
    serializer_class = MovieListSerializer
    
    def get_queryset(self):
        ordering = self.request.query_params.get('ordering', 'latest')
        year = self.request.query_params.get('year', None)

        queryset = Movie.objects.all()

        # 연도 필터
        if year:
            try:
                year = int(year)
                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 12, 31)
                queryset = queryset.filter(release_date__range=(start_date, end_date))
            except ValueError:
                pass  # year가 숫자가 아닌 경우 무시

        if ordering == 'top':
            queryset = queryset.order_by("-vote_average")
        elif ordering == 'bottom':
            queryset = queryset.order_by("vote_average")
        elif ordering == 'oldest':
            queryset = queryset.order_by("release_date")
        elif ordering == 'title':
            queryset = queryset.order_by("title")
        else:
            queryset = queryset.order_by("-release_date")

        return queryset


class MovieDetailView(RetrieveAPIView):
    serializer_class = MovieDetailSerializer
    queryset = Movie.objects.all()


class MovieGenreListView(ListAPIView):
    serializer_class = MovieListSerializer

    def get_queryset(self):
        name_to_id = {
            "action": 1,
            "comedy": 4,
            "drama": 7,
            "horror": 11,
            "adventure": 2,
            "family": 8,
            "romance": 14,
        }

        genre_name = self.kwargs.get("genre_name")
        ordering = self.request.query_params.get('ordering', 'latest')
        year = self.request.query_params.get('year', None)

        # 장르 존재 확인
        genre_id = name_to_id.get(genre_name)
        if genre_id is None:
            return Movie.objects.none()

        genre = Genre.objects.get(id=genre_id)

        queryset = Movie.objects.filter(genres=genre)

        # 연도 필터링
        if year:
            try:
                year = int(year)
                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 12, 31)
                queryset = queryset.filter(release_date__range=(start_date, end_date))
            except ValueError:
                pass  # 숫자가 아닌 경우 무시

        # 정렬
        if ordering == 'top':
            queryset = queryset.order_by("-vote_average")
        elif ordering == 'bottom':
            queryset = queryset.order_by("vote_average")
        elif ordering == 'oldest':
            queryset = queryset.order_by("release_date")
        elif ordering == 'title':
            queryset = queryset.order_by("title")
        else:
            queryset = queryset.order_by("-release_date")

        return queryset


class MovieSearchView(ListAPIView):
    serializer_class = MovieListSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', '').strip()

        if not query:
            return Movie.objects.none()
        
        if len(query) < 2:
            raise ValidationError("검색어는 최소 2자 이상이어야 합니다.")

        return Movie.objects.filter(
            Q(title__icontains=query) | Q(original_title__icontains=query) | Q(overview__icontains=query) | Q(tagline__icontains=query)
            ).order_by('-release_date')

@api_view(["POST", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def movie_like(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    user = request.user

    if request.method == "POST":
        movie.liked_user.add(user)
        return Response({"detail": "liked"},status=status.HTTP_201_CREATED)
    elif request.method == "DELETE":
        movie.liked_user.remove(user)
        return Response({"detail": "unliked"},status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_review(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, movie=movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



## provider DB 수집을 위해 작동하였습니다.
## basic fixture에 해당 DB를 dump하여 해당 코드를 비활성화 합니다.
# @api_view(["POST"])
# def collect_provider(request):
#     url = "https://api.themoviedb.org/3/watch/providers/tv?language=en-US"
#     headers = {
#         "accept": "application/json",
#         "Authorization": f"Bearer {settings.TMDB_API_KEY}",
#     }

#     response = requests.get(url, headers=headers)

#     filtered_providers = []
#     response_json = response.json()

#     # print(response_json)
#     for provider in response_json.get("results", []):
#         display_priorities = provider.get("display_priorities", {})
#         if "KR" in display_priorities:
#             filtered_providers.append(
#                 {
#                     "provider_id": provider.get("provider_id"),
#                     "provider_name": provider.get("provider_name"),
#                     "logo_path": provider.get("logo_path"),
#                     "display_priority": display_priorities["KR"],
#                 }
#             )

#     # 결과 출력 또는 저장
#     for p in filtered_providers:

#         serializer = ProviderSerilizer(
#             data={
#                 "name": p["provider_name"],
#                 "tmdb_id": p["provider_id"],
#                 "logo_path": p["logo_path"],
#             }
#         )
#         if serializer.is_valid():
#             serializer.save()

#     return Response(filtered_providers, status.HTTP_200_OK)
