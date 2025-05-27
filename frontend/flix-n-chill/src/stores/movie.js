import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useUserStore } from './accounts'

export const useMovieStore = defineStore('movie', () => {
  const moviesByGenre = ref({})  // { userKey: { cacheKey: { movies: [...], totalCount: 0, currentPage: 1 } } }
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

  const getMoviesByGenreSync = (genreType, ordering = 'top', year = '') => {
    const userKey = getUserKey()
    const cacheKey = getCacheKey(genreType, ordering, year)
    const cacheData = moviesByGenre.value[userKey]?.[cacheKey]
    return cacheData?.movies || []
  }

  const fetchMoviesByGenre = async (genreType, ordering = "top", year = "", page = 1) => {
    const userKey = getUserKey()
    const cacheKey = getCacheKey(genreType, ordering, year)

    // 캐시 초기화 여부 확인
    if (!moviesByGenre.value[userKey]) {
      moviesByGenre.value[userKey] = {}
    }
    if (!moviesByGenre.value[userKey][cacheKey]) {
      moviesByGenre.value[userKey][cacheKey] = {
        movies: [],
        totalCount: 0,
        currentPage: 0
      }
    }

    const cacheData = moviesByGenre.value[userKey][cacheKey]

    // 첫 페이지 요청이면 캐시 초기화
    if (page === 1) {
      cacheData.movies = []
      cacheData.totalCount = 0
      cacheData.currentPage = 0
    }

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
        params: { 
          ordering, 
          year,
          page: page,
          page_size: 20  // 백엔드에서 사용하는 파라미터명에 맞게 조정
        },
        headers,
      })

      const transformedMovies = response.data.results.map(movie => ({
        id: movie.id,
        title: movie.title,
        rating: movie.vote_average,
        year: movie.release_date ? new Date(movie.release_date).getFullYear() : 2024,
        genre: movie.genres[0]?.name || 'Unknown', // 안전한 접근
        genres: movie.genres?.map((genre) => genre.name) || [],
        poster: movie.poster_path
          ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
          : '/api/placeholder/300/450',
        isInWatchlist: false,
        isLiked: movie.is_liked || false, // 기본값 설정
        like_count: movie.like_count || 0, // 기본값 설정
      }))

      // 기존 영화 목록에 새로운 영화들 추가
      cacheData.movies.push(...transformedMovies)
      cacheData.totalCount = response.data.count || response.data.total || 0
      cacheData.currentPage = page

      console.log(`🎬 페이지 ${page} 로드 완료 - 현재 영화 수: ${cacheData.movies.length}, 전체: ${cacheData.totalCount}`)

      return {
        movies: transformedMovies, // 새로 로드된 영화들만 반환
        total: cacheData.totalCount,
        hasMore: cacheData.movies.length < cacheData.totalCount // 현재 로드된 영화 수 < 전체 영화 수
      }

    } catch (err) {
      console.error('🚨 API 호출 실패:', err)
      error.value = err.message
      return {
        movies: [],
        total: 0,
        hasMore: false
      }
    } finally {
      loading.value = false
    }
  }

  // 캐시 초기화 메서드 추가
  const clearGenreMovies = (genreType, ordering = 'top', year = '') => {
    const userKey = getUserKey()
    const cacheKey = getCacheKey(genreType, ordering, year)
    
    if (moviesByGenre.value[userKey]?.[cacheKey]) {
      moviesByGenre.value[userKey][cacheKey] = {
        movies: [],
        totalCount: 0,
        currentPage: 0
      }
    }
  }

  // 좋아요 토글 - 수정된 버전
  const toggleLike = async (movieId) => {
    const userStore = useUserStore()
    if (!userStore.token) {
      console.warn('로그인이 필요합니다.')
      return
    }

    // 1) 캐시에서 모든 데이터 참조 가져오기
    const userKey = getUserKey()
    const userCache = moviesByGenre.value[userKey] || {}
    
    // 2) 현재 토글할 값 계산
    let currentLiked = null
    let targetMovie = null
    
    // 올바른 데이터 구조로 접근 - cacheData.movies 배열에서 찾기
    Object.values(userCache).some(cacheData => {
      if (cacheData.movies) {
        const movie = cacheData.movies.find(m => m.id === movieId)
        if (movie) {
          currentLiked = movie.isLiked
          targetMovie = movie
          return true
        }
      }
      return false
    })
    
    if (currentLiked === null || !targetMovie) {
      console.warn('해당 영화를 찾을 수 없습니다.')
      return
    }
    
    const nextLiked = !currentLiked

    // 3) 서버에 요청 (POST/DELETE 분기)
    try {
      await axios({
        method: nextLiked ? 'post' : 'delete',
        url: `http://127.0.0.1:8000/api/v1/movies/${movieId}/like/`,
        headers: { Authorization: `Token ${userStore.token}` }
      })

      // 4) 모든 캐시 데이터에서 해당 영화 업데이트
      Object.values(userCache).forEach(cacheData => {
        if (cacheData.movies) {
          cacheData.movies.forEach(movie => {
            if (movie.id === movieId) {
              movie.isLiked = nextLiked
              movie.like_count = Math.max(0, (movie.like_count || 0) + (nextLiked ? 1 : -1))
            }
          })
        }
      })
      
      console.log(`✅ 좋아요 ${nextLiked ? '추가' : '제거'} 성공: ${movieId}`)
      
    } catch (e) {
      console.error('❌ 좋아요 토글 실패:', e)
      error.value = e.message || '좋아요 처리 중 오류가 발생했습니다.'
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