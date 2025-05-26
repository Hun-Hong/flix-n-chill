import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useUserStore } from './accounts'

export const useMovieStore = defineStore('movie', () => {
  const moviesByGenre = ref({})  // { userKey: { cacheKey: { movies: [...], totalCount: 0, currentPage: 1 } } }
  const loading = ref(false)
  const error = ref(null)

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

    // 이미 해당 페이지를 로드했다면 리턴 (이 로직 제거!)
    // if (cacheData.currentPage >= page) {
    //   return {
    //     movies: cacheData.movies,
    //     total: cacheData.totalCount,
    //     hasMore: cacheData.movies.length < cacheData.totalCount
    //   }
    // }

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
        genre: movie.genres.map((genre) => genre.name),
        poster: movie.poster_path
          ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
          : '/api/placeholder/300/450',
        isInWatchlist: false,
        isLiked: movie.is_liked,
        like_count: movie.like_count,
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

  // 좋아요 토글 후엔 캐시 지우고 새로 fetch
  const toggleLike = async (movieId) => {
    const userStore = useUserStore()
    if (!userStore.token) return

    // 1) 캐시에서 모든 배열 참조 가져오기
    const userKey = getUserKey()
    const userCache = moviesByGenre.value[userKey] || {}
    
    // 2) 현재 토글할 값 계산
    let currentLiked = null
    Object.values(userCache).some(cacheData => {
      const m = cacheData.movies?.find(x => x.id === movieId)
      if (m) { currentLiked = m.isLiked; return true }
    })
    if (currentLiked === null) return
    const nextLiked = !currentLiked

    // 3) 서버에 요청 (POST/DELETE 분기)
    try {
      await axios({
        method: nextLiked ? 'post' : 'delete',
        url: `http://127.0.0.1:8000/api/v1/movies/${movieId}/like/`,
        headers: { Authorization: `Token ${userStore.token}` }
      })

      // 4) 모든 캐시 배열 안에서 해당 영화만 업데이트
      Object.values(userCache).forEach(cacheData => {
        if (cacheData.movies) {
          cacheData.movies.forEach(movie => {
            if (movie.id === movieId) {
              movie.isLiked = nextLiked
              movie.like_count = (movie.like_count || 0) + (nextLiked ? 1 : -1)
            }
          })
        }
      })
    } catch (e) {
      console.error('좋아요 토글 실패', e)
      error.value = e.message
    }
  }

  // 찜 토글 (필요시 구현)
  const toggleWatchlist = async (movieId) => {
    // 찜 토글 로직 구현
    console.log('찜 토글:', movieId)
  }

  return {
    moviesByGenre,
    loading,
    error,
    getMoviesByGenreSync,
    fetchMoviesByGenre,
    clearGenreMovies,
    toggleLike,
    toggleWatchlist,
  }
})