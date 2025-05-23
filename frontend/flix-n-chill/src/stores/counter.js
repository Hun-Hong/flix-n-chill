import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useMovieStore = defineStore('movie', () => {
  // 🎯 상태 관리
  const movies = ref([])
  const moviesByGenre = ref({}) // 장르별로 영화 저장
  const loading = ref(false)
  const error = ref(null)

  // 🎯 동기적으로 특정 장르 영화 가져오기 (computed에서 사용)
  const getMoviesByGenreSync = (genreType) => {
    console.log('🎬 동기 함수 호출 - genreType:', genreType)
    console.log('🎬 현재 moviesByGenre 상태:', moviesByGenre.value)
    return moviesByGenre.value[genreType] || []
  }

  // 🎯 비동기 API 호출 - 장르별 영화 가져오기 (메서드에서 호출)
  const fetchMoviesByGenre = async (genreType) => {
    console.log('🎬 비동기 함수 호출 - genreType:', genreType)
    
    // 이미 해당 장르 데이터가 있으면 API 호출 안 함
    if (moviesByGenre.value[genreType] && moviesByGenre.value[genreType].length > 0) {
      console.log('🎬 캐시된 데이터 사용:', moviesByGenre.value[genreType])
      return moviesByGenre.value[genreType]
    }

    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/v1/movies/list/${genreType}/`)
      console.log('🎬 API 응답:', response.data)
      
      // Django 데이터를 MovieCard에 맞게 변환
      const transformedMovies = response.data.results.map(movie => ({
        id: movie.id,
        title: movie.title,
        rating: movie.vote_average,
        year: movie.release_date ? new Date(movie.release_date).getFullYear() : 2024,
        genre: genreType, // 실제 장르명 사용
        poster: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/api/placeholder/300/450',
        isInWatchlist: false,
        isLiked: false
      }))
      
      console.log('🎬 변환된 데이터:', transformedMovies)
      
      // 장르별로 데이터 저장
      moviesByGenre.value[genreType] = transformedMovies
      
      return transformedMovies
      
    } catch (err) {
      console.error('🚨 API 에러:', err)
      error.value = err.message
      moviesByGenre.value[genreType] = []
      return []
    } finally {
      loading.value = false
    }
  }

  // 🎯 찜하기 토글
  const toggleWatchlist = (movieId) => {
    // 모든 장르에서 해당 영화 찾아서 업데이트
    Object.keys(moviesByGenre.value).forEach(genre => {
      const movie = moviesByGenre.value[genre].find(m => m.id === movieId)
      if (movie) {
        movie.isInWatchlist = !movie.isInWatchlist
        console.log('🎬 찜하기 토글:', movie.title, movie.isInWatchlist)
      }
    })
  }

  // 🎯 좋아요 토글
  const toggleLike = (movieId) => {
    // 모든 장르에서 해당 영화 찾아서 업데이트
    Object.keys(moviesByGenre.value).forEach(genre => {
      const movie = moviesByGenre.value[genre].find(m => m.id === movieId)
      if (movie) {
        movie.isLiked = !movie.isLiked
        console.log('🎬 좋아요 토글:', movie.title, movie.isLiked)
      }
    })
  }

  return {
    // 상태
    movies,
    moviesByGenre,
    loading,
    error,
    // 메서드
    getMoviesByGenreSync,
    fetchMoviesByGenre,
    toggleWatchlist,
    toggleLike
  }
})