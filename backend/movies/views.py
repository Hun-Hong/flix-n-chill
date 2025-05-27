from django.shortcuts import render, get_object_or_404
from django.conf import settings
import requests
from .serializers import (
    MovieListSerializer, MovieCreateSerializer, MovieDetailSerializer, 
    ReviewSerializer, ReviewCreateSerializer, 
    CommentSerializer, CommentCreateSerializer
)
from .models import Movie, Genre, MovieProvider, Review, Comment
import json
from .models import Genre
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db.models import Q
from datetime import datetime
from accounts.models import MovieLike, ReviewLike

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
        MovieLike.objects.create(user=user, movie=movie)
        return Response({"detail": "liked"},status=status.HTTP_201_CREATED)
    elif request.method == "DELETE":
        MovieLike.objects.filter(user=user, movie=movie).delete()
        return Response({"detail": "unliked"},status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_review(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    # 해당 사용자가 이미 이 영화에 리뷰를 작성했는지 확인 (선택사항)
    existing_review = Review.objects.filter(user=request.user, movie=movie).first()
    if existing_review:
        return Response(
            {"error": "이미 이 영화에 대한 리뷰를 작성하셨습니다."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ReviewCreateSerializer(data=request.data)
    if serializer.is_valid():
        # user와 movie를 자동으로 설정
        review = serializer.save(user=request.user, movie=movie)

        # 생성된 리뷰를 다시 직렬화해서 반환 (모든 필드 포함)
        response_serializer = ReviewCreateSerializer(review)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_review(request, pk):
    """현재 사용자의 특정 영화에 대한 리뷰 조회"""
    movie = get_object_or_404(Movie, pk=pk)

    try:
        review = Review.objects.get(user=request.user, movie=movie)
        serializer = ReviewSerializer(review)  # 적절한 serializer 사용
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Review.DoesNotExist:
        return Response(
            {"detail": "리뷰가 존재하지 않습니다."}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_review(request, movie_pk, review_pk):
    """리뷰 수정"""
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk, user=request.user, movie=movie)

    serializer = ReviewCreateSerializer(review, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_review(request, movie_pk, review_pk):
    """리뷰 삭제"""
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk, user=request.user, movie=movie)

    review.delete()
    return Response(
        {"detail": "리뷰가 삭제되었습니다."}, 
        status=status.HTTP_204_NO_CONTENT
    )


## Comment API Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_comment(request, review_pk):
    """리뷰에 댓글 작성"""
    review = get_object_or_404(Review, pk=review_pk)

    serializer = CommentCreateSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(user=request.user, review=review, parent_comment=None)
        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_reply(request, comment_pk):
    """댓글에 대댓글 작성"""
    parent_comment = get_object_or_404(Comment, pk=comment_pk)

    serializer = CommentCreateSerializer(data=request.data)
    if serializer.is_valid():
        # 대댓글은 parent_comment를 설정하고, review는 부모 댓글의 review를 사용
        comment = serializer.save(
            user=request.user, 
            parent_comment=parent_comment,
            review=parent_comment.review
        )
        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_review_comments(request, review_pk):
    """리뷰의 모든 댓글 조회 (대댓글 포함)"""
    review = get_object_or_404(Review, pk=review_pk)

    # 최상위 댓글만 가져옴 (대댓글은 CommentSerializer에서 처리)
    comments = Comment.objects.filter(review=review, parent_comment=None).order_by('created_at')
    serializer = CommentSerializer(comments, many=True, context={'request': request})

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_comment(request, comment_pk):
    """댓글 수정"""
    comment = get_object_or_404(Comment, pk=comment_pk, user=request.user)

    serializer = CommentCreateSerializer(comment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_comment(request, comment_pk):
    """댓글 삭제"""
    comment = get_object_or_404(Comment, pk=comment_pk, user=request.user)

    comment.delete()
    return Response(
        {"detail": "댓글이 삭제되었습니다."}, 
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def comment_like(request, comment_pk):
    """댓글 좋아요/좋아요 취소"""
    comment = get_object_or_404(Comment, pk=comment_pk)
    user = request.user

    if request.method == 'POST':
        # 좋아요 추가
        comment.likes.add(user)
        return Response(
            {"detail": "댓글에 좋아요를 표시했습니다.", "like_count": comment.like_count}, 
            status=status.HTTP_200_OK
        )
    elif request.method == 'DELETE':
        # 좋아요 취소
        comment.likes.remove(user)
        return Response(
            {"detail": "댓글 좋아요를 취소했습니다.", "like_count": comment.like_count}, 
            status=status.HTTP_200_OK
        )

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def review_like(request, review_pk):
    """리뷰 좋아요/좋아요 취소"""
    review = get_object_or_404(Review, pk=review_pk)
    user = request.user

    if request.method == 'POST':
        # 이미 좋아요 했는지 확인
        review_like, created = ReviewLike.objects.get_or_create(
            user=user, 
            review=review
        )
        
        if created:
            return Response({
                "detail": "리뷰에 좋아요를 표시했습니다.",
                "is_liked": True,
                "like_count": review.like_count
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "detail": "이미 좋아요를 누른 리뷰입니다.",
                "is_liked": True,
                "like_count": review.like_count
            }, status=status.HTTP_200_OK)
            
    elif request.method == 'DELETE':
        # 좋아요 취소
        deleted_count, _ = ReviewLike.objects.filter(
            user=user, 
            review=review
        ).delete()
        
        if deleted_count > 0:
            return Response({
                "detail": "리뷰 좋아요를 취소했습니다.",
                "is_liked": False,
                "like_count": review.like_count
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "detail": "좋아요를 누르지 않은 리뷰입니다.",
                "is_liked": False,
                "like_count": review.like_count
            }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_review_detail(request, review_pk):
    """리뷰 상세 정보 조회 (좋아요 정보 포함)"""
    review = get_object_or_404(Review, pk=review_pk)
    
    # 현재 사용자의 좋아요 여부 확인
    is_liked = False
    if request.user.is_authenticated:
        is_liked = ReviewLike.objects.filter(
            user=request.user, 
            review=review
        ).exists()
    
    # 리뷰 데이터 구성
    review_data = {
        'id': review.id,
        'user': {
            'id': review.user.id,
            'nickname': review.user.nickname or review.user.username,
            'profile_image': review.user.profile_image.url if review.user.profile_image else None
        },
        'movie': {
            'id': review.movie.id,
            'title': review.movie.title,
            'poster_path': review.movie.poster_path
        },
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at,
        'updated_at': review.updated_at,
        'like_count': review.like_count,
        'is_liked': is_liked
    }
    
    return Response(review_data, status=status.HTTP_200_OK)


from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from collections import defaultdict

from .models import Movie, Review, Genre
from .serializers import MovieListSerializer

class MovieRecommendationService:
    """
    코사인 유사도 기반 영화 추천 서비스
    """
    
    @staticmethod
    def get_user_genre_preferences(user):
        """
        사용자의 장르별 선호도 계산 
        (사용자가 평가한 영화들의 장르별 평점 가중 평균)
        """
        print(f"👤 사용자 {user.id}의 장르 선호도 계산 중...")
        
        # 사용자의 모든 리뷰 가져오기
        user_reviews = Review.objects.filter(user=user).select_related('movie').prefetch_related('movie__genres')
        
        if not user_reviews.exists():
            print("❌ 사용자 리뷰가 없어 추천할 수 없습니다.")
            return None
        
        # 장르별 점수 누적
        genre_scores = defaultdict(list)
        
        for review in user_reviews:
            movie_genres = review.movie.genres.all()
            rating = review.rating
            
            for genre in movie_genres:
                genre_scores[genre.name].append(rating)
        
        # 장르별 평균 평점 계산 (선호도)
        genre_preferences = {}
        for genre_name, ratings in genre_scores.items():
            genre_preferences[genre_name] = np.mean(ratings)
        
        print(f"✅ 장르 선호도 계산 완료: {len(genre_preferences)}개 장르")
        return genre_preferences
    
    @staticmethod
    def create_movie_genre_vector(movie, all_genres):
        """
        영화의 장르 벡터 생성 (원핫 인코딩 방식)
        """
        movie_genres = set(genre.name for genre in movie.genres.all())
        return [1 if genre in movie_genres else 0 for genre in all_genres]
    
    @staticmethod
    def create_user_preference_vector(user_preferences, all_genres):
        """
        사용자 선호도 벡터 생성
        """
        # 선호도가 없는 장르는 0으로 설정
        return [user_preferences.get(genre, 0) for genre in all_genres]
    
    @classmethod
    def get_movie_recommendations(cls, user, exclude_rated=True, top_k=10):
        """
        코사인 유사도를 이용한 영화 추천
        
        Args:
            user: 추천을 받을 사용자
            exclude_rated: 이미 평가한 영화 제외 여부
            top_k: 추천할 영화 개수
        
        Returns:
            추천 영화 리스트 (유사도 점수 포함)
        """
        print(f"🎯 사용자 {user.username}에게 영화 추천 시작...")
        
        # 1. 사용자 장르 선호도 계산
        user_preferences = cls.get_user_genre_preferences(user)
        if not user_preferences:
            return []
        
        # 2. 모든 장르 목록 가져오기
        all_genres = list(Genre.objects.values_list('name', flat=True).distinct())
        print(f"🎬 전체 장르 수: {len(all_genres)}")
        
        # 3. 후보 영화 선택
        candidate_movies = Movie.objects.prefetch_related('genres').all()
        
        if exclude_rated:
            # 이미 평가한 영화 제외
            rated_movie_ids = Review.objects.filter(user=user).values_list('movie_id', flat=True)
            candidate_movies = candidate_movies.exclude(id__in=rated_movie_ids)
        
        print(f"📝 후보 영화 수: {candidate_movies.count()}")
        
        # 4. 사용자 선호도 벡터 생성
        user_vector = cls.create_user_preference_vector(user_preferences, all_genres)
        user_vector = np.array(user_vector).reshape(1, -1)
        
        # 5. 각 영화와의 코사인 유사도 계산
        recommendations = []
        
        for movie in candidate_movies:
            # 영화 장르 벡터 생성
            movie_vector = cls.create_movie_genre_vector(movie, all_genres)
            movie_vector = np.array(movie_vector).reshape(1, -1)
            
            # 코사인 유사도 계산
            if np.sum(movie_vector) > 0:  # 장르 정보가 있는 영화만
                similarity = cosine_similarity(user_vector, movie_vector)[0][0]
                
                recommendations.append({
                    'movie': movie,
                    'similarity_score': similarity,
                    'user_genre_match': cls.get_genre_match_info(movie, user_preferences)
                })
        
        # 6. 유사도 점수로 정렬
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        print(f"✅ 추천 완료: {len(recommendations)}개 영화 중 상위 {top_k}개 선택")
        
        return recommendations[:top_k]
    
    @staticmethod
    def get_genre_match_info(movie, user_preferences):
        """
        영화와 사용자 선호도의 장르 매칭 정보
        """
        movie_genres = [genre.name for genre in movie.genres.all()]
        matched_genres = []
        
        for genre in movie_genres:
            if genre in user_preferences:
                matched_genres.append({
                    'genre': genre,
                    'user_preference': user_preferences[genre]
                })
        
        return matched_genres

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_movie_recommendations(request):
    """
    현재 로그인한 사용자에게 영화 추천
    """
    try:
        # 쿼리 파라미터
        top_k = int(request.GET.get('count', 10))  # 추천 개수 (기본 10개)
        exclude_rated = request.GET.get('exclude_rated', 'true').lower() == 'true'
        
        # 추천 실행
        recommendations = MovieRecommendationService.get_movie_recommendations(
            user=request.user,
            exclude_rated=exclude_rated,
            top_k=top_k
        )
        
        if not recommendations:
            return Response({
                'message': '추천할 영화가 없습니다. 먼저 몇 편의 영화를 평가해주세요!',
                'recommendations': []
            }, status=status.HTTP_200_OK)
        
        # 추천 결과 직렬화
        recommendation_data = []
        for rec in recommendations:
            movie_data = MovieListSerializer(rec['movie']).data
            movie_data['similarity_score'] = round(rec['similarity_score'], 4)
            movie_data['genre_matches'] = rec['user_genre_match']
            recommendation_data.append(movie_data)
        
        return Response({
            'message': f'{len(recommendations)}개의 추천 영화를 찾았습니다!',
            'user_id': request.user.id,
            'user_name': request.user.username,
            'recommendations': recommendation_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ 추천 시스템 오류: {str(e)}")
        return Response({
            'error': '영화 추천 중 오류가 발생했습니다.',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_genre_analysis(request):
    """
    사용자의 장르 선호도 분석 결과 반환
    """
    try:
        user_preferences = MovieRecommendationService.get_user_genre_preferences(request.user)
        
        if not user_preferences:
            return Response({
                'message': '분석할 데이터가 없습니다. 영화를 평가해주세요!',
                'genre_preferences': {}
            }, status=status.HTTP_200_OK)
        
        # 선호도 순으로 정렬
        sorted_preferences = dict(sorted(user_preferences.items(), 
                                       key=lambda x: x[1], reverse=True))
        
        return Response({
            'user_id': request.user.id,
            'user_name': request.user.username,
            'genre_preferences': sorted_preferences,
            'top_genres': list(sorted_preferences.keys())[:5],  # 상위 5개 장르
            'total_genres_rated': len(sorted_preferences)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': '장르 분석 중 오류가 발생했습니다.',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 추가적인 유틸리티 함수들
@api_view(['GET'])
def get_similar_movies(request, movie_id):
    """
    특정 영화와 유사한 영화들 추천 (장르 기반)
    """
    try:
        target_movie = Movie.objects.get(id=movie_id)
        target_genres = set(genre.name for genre in target_movie.genres.all())
        
        if not target_genres:
            return Response({
                'message': '해당 영화의 장르 정보가 없습니다.',
                'similar_movies': []
            }, status=status.HTTP_200_OK)
        
        # 모든 장르 목록
        all_genres = list(Genre.objects.values_list('name', flat=True).distinct())
        
        # 타겟 영화 장르 벡터
        target_vector = np.array([1 if genre in target_genres else 0 for genre in all_genres]).reshape(1, -1)
        
        # 다른 영화들과 비교
        similar_movies = []
        other_movies = Movie.objects.exclude(id=movie_id).prefetch_related('genres')
        
        for movie in other_movies:
            movie_genres = set(genre.name for genre in movie.genres.all())
            if movie_genres:  # 장르 정보가 있는 경우만
                movie_vector = np.array([1 if genre in movie_genres else 0 for genre in all_genres]).reshape(1, -1)
                similarity = cosine_similarity(target_vector, movie_vector)[0][0]
                
                if similarity > 0:  # 유사도가 0보다 큰 경우만
                    similar_movies.append({
                        'movie': movie,
                        'similarity_score': similarity,
                        'common_genres': list(target_genres.intersection(movie_genres))
                    })
        
        # 유사도순 정렬
        similar_movies.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # 상위 10개만 반환
        top_similar = similar_movies[:10]
        
        result_data = []
        for sim_movie in top_similar:
            movie_data = MovieListSerializer(sim_movie['movie']).data
            movie_data['similarity_score'] = round(sim_movie['similarity_score'], 4)
            movie_data['common_genres'] = sim_movie['common_genres']
            result_data.append(movie_data)
        
        return Response({
            'target_movie': MovieListSerializer(target_movie).data,
            'similar_movies': result_data,
            'total_found': len(similar_movies)
        }, status=status.HTTP_200_OK)
        
    except Movie.DoesNotExist:
        return Response({
            'error': '해당 영화를 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': '유사 영화 검색 중 오류가 발생했습니다.',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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
