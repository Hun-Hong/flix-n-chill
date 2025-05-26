import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useUserStore } from './accounts'

export const useMovieStore = defineStore('movie', () => {
  const moviesByGenre = ref({})  // { userKey: { cacheKey: [...] } }
  const loading = ref(false)
  const error = ref(null)

  const BE_API_PATH = "http://127.0.0.1:8000/"

  const getUserKey = () => {
    const userStore = useUserStore()
    return userStore.user?.id ? `user_${userStore.user.id}` : 'anonymous'
  }

  const getCacheKey = (genreType, ordering, year) => {
    return `${genreType}-${ordering}-${year || ''}`
  }

  const getMoviesByGenreSync = (genreType, ordering, year) => {
    const userKey = getUserKey()
    const cacheKey = getCacheKey(genreType, ordering, year)
    return moviesByGenre.value[userKey]?.[cacheKey] || []
  }

  const fetchMoviesByGenre = async (genreType, ordering = "top", year = "") => {
    const userKey = getUserKey()
    const cacheKey = getCacheKey(genreType, ordering, year)

    loading.value = true
    error.value = null

    const userStore = useUserStore()
    const headers = {}
    if (userStore.token) {
      headers['Authorization'] = `Token ${userStore.token}`
    }

    try {
      const response = await axios({
        method: 'get',
        url: `http://127.0.0.1:8000/api/v1/movies/list/${genreType}/`,
        params: { ordering, year },
        headers,
      })

      const transformedMovies = response.data.results.map(movie => ({
        id: movie.id,
        title: movie.title,
        rating: movie.vote_average,
        year: movie.release_date ? new Date(movie.release_date).getFullYear() : 2024,
        genre: movie.genres[0].name,
        genres: movie.genres.map((genre) => genre.name),
        poster: movie.poster_path
          ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
          : '/api/placeholder/300/450',
        isInWatchlist: false,
        isLiked: movie.is_liked,
        like_count: movie.like_count,
      }))

      // 유저별 캐시에 저장
      if (!moviesByGenre.value[userKey]) moviesByGenre.value[userKey] = {}
      moviesByGenre.value[userKey][cacheKey] = transformedMovies

      return transformedMovies

    } catch (err) {
      error.value = err.message
      if (!moviesByGenre.value[userKey]) moviesByGenre.value[userKey] = {}
      moviesByGenre.value[userKey][cacheKey] = []
      return []
    } finally {
      loading.value = false
    }
  }

  // 좋아요 토글
  const toggleLike = async (movieId) => {
    const userStore = useUserStore()
    if (!userStore.token) return

    const userKey = getUserKey()
    const userCache = moviesByGenre.value[userKey] || {}
    
    let currentLiked = null
    Object.values(userCache).some(arr => {
      const m = arr.find(x => x.id === movieId)
      if (m) { currentLiked = m.isLiked; return true }
    })
    if (currentLiked === null) return
    const nextLiked = !currentLiked

    try {
      await axios({
        method: nextLiked ? 'post' : 'delete',
        url: `http://127.0.0.1:8000/api/v1/movies/${movieId}/like/`,
        headers: { Authorization: `Token ${userStore.token}` }
      })

      Object.values(userCache).forEach(arr => {
        arr.forEach(movie => {
          if (movie.id === movieId) {
            movie.isLiked = nextLiked
            movie.like_count = (movie.like_count || 0) + (nextLiked ? 1 : -1)
          }
        })
      })
    }
    catch (e) {
      console.error('좋아요 토글 실패', e)
      error.value = e.message
    }
  }

  // 리뷰 생성
  const createReview = async (movieId, payload) => {
    const userStore = useUserStore()
    try {
      const response = await axios({
        method: 'post',
        url: `http://127.0.0.1:8000/api/v1/movies/${movieId}/review/`,
        data: payload,
        headers: { 
          Authorization: `Token ${userStore.token}`,
          'Content-Type': 'application/json'
        },
      })
      console.log('리뷰 생성 성공:', response.data)
      return response.data
    } catch (error) {
      console.error('리뷰 생성 실패:', error)
      throw error
    }
  }

  // 사용자 리뷰 조회
  const getUserReview = async (movieId) => {
    const userStore = useUserStore()
    try {
      const response = await axios({
        method: 'get',
        url: `http://127.0.0.1:8000/api/v1/movies/${movieId}/user-review/`,
        headers: { 
          Authorization: `Token ${userStore.token}`,
        },
      })
      console.log('기존 리뷰 조회 성공:', response.data)
      return response.data
    } catch (error) {
      if (error.response?.status === 404) {
        // 리뷰가 없는 경우 (정상적인 상황)
        console.log('기존 리뷰 없음')
        return null
      }
      console.error('리뷰 조회 실패:', error)
      throw error
    }
  }

  // 리뷰 수정
  const updateReview = async (movieId, reviewId, payload) => {
    const userStore = useUserStore()
    try {
      const response = await axios({
        method: 'put',
        url: `http://127.0.0.1:8000/api/v1/movies/${movieId}/review/${reviewId}/`,
        data: payload,
        headers: { 
          Authorization: `Token ${userStore.token}`,
          'Content-Type': 'application/json'
        },
      })
      console.log('리뷰 수정 성공:', response.data)
      return response.data
    } catch (error) {
      console.error('리뷰 수정 실패:', error)
      throw error
    }
  }

  // 리뷰 삭제
  const deleteReview = async (movieId, reviewId) => {
    const userStore = useUserStore()
    try {
      const response = await axios({
        method: 'delete',
        url: `http://127.0.0.1:8000/api/v1/movies/${movieId}/review/${reviewId}/delete/`,
        headers: { 
          Authorization: `Token ${userStore.token}`,
        },
      })
      console.log('리뷰 삭제 성공')
      return response.data
    } catch (error) {
      console.error('리뷰 삭제 실패:', error)
      throw error
    }
  }

  return {
    BE_API_PATH,
    
    moviesByGenre,
    loading,
    error,
    getMoviesByGenreSync,
    fetchMoviesByGenre,
    toggleLike,
    createReview,
    getUserReview,
    updateReview,
    deleteReview,
  }
})