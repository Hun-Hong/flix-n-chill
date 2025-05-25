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
  const toggleLike = async (movieId, genreType, ordering, year) => {
    const userStore = useUserStore()
    const headers = {}
    if (userStore.token) {
      headers['Authorization'] = `Token ${userStore.token}`
    }
    try {
      // 현재 영화 상태 찾기 (캐시 구조상 모든 캐시에서 찾아도 됨)
      const userKey = getUserKey()
      // (여기서는 메인 리스트 파라미터만 새로고침)
      await axios({
        method: "post", // or "delete"는 FE에서 판단 or 서버에서 토글 지원
        url: `http://127.0.0.1:8000/api/v1/movies/${movieId}/like/`,
        headers,
      })
      // **관련 캐시 무효화**
      if (moviesByGenre.value[userKey]) {
        // 캐시 전체 삭제(또는 일부만 삭제)
        Object.keys(moviesByGenre.value[userKey]).forEach(cacheKey => {
          // 캐시 무효화 기준을 더 세밀하게 하고 싶으면 cacheKey에 movieId 포함 여부 판단 가능
          delete moviesByGenre.value[userKey][cacheKey]
        })
      }
      // **현재 파라미터에 맞는 리스트만 새로 받아오기**
      await fetchMoviesByGenre(genreType, ordering, year)
    } catch (err) {
      // 실패시 에러 핸들링
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
