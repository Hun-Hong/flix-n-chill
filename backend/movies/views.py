from django.shortcuts import render
from django.conf import settings
import requests
from .serializer import MovieSerializer, ProviderSerilizer
from .models import Movie, Genre, MovieProvider
import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Create your views here.


## DATA COLLECT
@api_view(["POST"])
def movie_collect(request):
    # url = "https://api.themoviedb.org/3/genre/movie/list?language=ko"

    saved = 0
    for page_idx in range(1, 6):
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

                    serializer = MovieSerializer(
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
