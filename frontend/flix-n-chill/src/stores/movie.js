import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useUserStore } from './accounts'

export const useMovieStore = defineStore('movie', () => {
  const moviesByGenre = ref({})  // { userKey: { cacheKey: [...] } }
  const loading = ref(false)
  const error = ref(null)


  // const userStore = useUserStore()
  // watch(
  //   () => userStore.user?.id, // userId가 바뀌면(로그인/로그아웃)
  //   () => {
  //     moviesByGenre.value = {} // 캐시 초기화!
  //   }
  // )


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

    // if (
    //   moviesByGenre.value[userKey] &&
    //   moviesByGenre.value[userKey][cacheKey] &&
    //   moviesByGenre.value[userKey][cacheKey].length > 0
    // ) {
    //   return moviesByGenre.value[userKey][cacheKey]
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
        params: { ordering, year },
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

  // 좋아요 토글 후엔 캐시 지우고 새로 fetch
  const toggleLike = async (movieId) => {
  const userStore = useUserStore()
  if (!userStore.token) return

  // 1) 캐시에서 모든 배열 참조 가져오기
  const userKey   = getUserKey()
  const userCache = moviesByGenre.value[userKey] || {}
  // 2) 현재 토글할 값 계산
  //    (어차피 모든 배열의 movieRef.isLiked 값은 동일하다고 가정)
  let currentLiked = null
  Object.values(userCache).some(arr => {
    const m = arr.find(x => x.id === movieId)
    if (m) { currentLiked = m.isLiked; return true }
  })
  if (currentLiked === null) return
  const nextLiked = !currentLiked

  // 3) 서버에 요청 (POST/DELETE 분기)
  try {
    await axios({
      method: nextLiked ? 'post' : 'delete',
      url:   `http://127.0.0.1:8000/api/v1/movies/${movieId}/like/`,
      headers: { Authorization: `Token ${userStore.token}` }
    })

    // 4) 모든 캐시 배열 안에서 해당 영화만 업데이트
    Object.values(userCache).forEach(arr => {
      arr.forEach(movie => {
        if (movie.id === movieId) {
          movie.isLiked    = nextLiked
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


  // ... (찜 토글도 같은 방식 적용)

  return {
    moviesByGenre,
    loading,
    error,
    getMoviesByGenreSync,
    fetchMoviesByGenre,
    toggleLike,
  }
})
