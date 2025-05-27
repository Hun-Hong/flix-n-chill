// stores/recommendation.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useUserStore } from './accounts'

const useRecommendationStore = defineStore('recommendation', () => {
  // State - 반응형 상태
  const recommendations = ref([])
  const userGenreAnalysis = ref(null)
  const similarMovies = ref([])
  const loading = ref(false)
  const error = ref(null)



  // API 설정
  const API_BASE_URL = 'http://localhost:8000/api/v1/movies'


  // Axios 설정
  const getAuthHeaders = (() => {
    const userStore = useUserStore()

    return {
      'Authorization': `Token ${userStore.token}`,
      'Content-Type': 'application/json'
    }
  })

  // Getters
  const hasRecommendations = computed(() => {
    return Array.isArray(recommendations.value) && recommendations.value.length > 0
  })

  const topGenres = computed(() => {
    if (!userGenreAnalysis.value?.genre_preferences) return []

    return Object.entries(userGenreAnalysis.value.genre_preferences)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([genre, score]) => ({ genre, score: Number(score) }))
  })

  const recommendationCount = computed(() => recommendations.value.length)

  // Actions
  const getMovieRecommendations = async (options = {}) => {
    loading.value = true
    error.value = null

    try {
      console.log('🎬 영화 추천 API 요청:', options)

      const params = {
        count: options.count || 10,
        exclude_rated: options.excludeRated !== false ? 'true' : 'false'
      }

      const response = await axios.get(`${API_BASE_URL}/recommendations/`, {
        params,
        headers: getAuthHeaders()
      })

      console.log('✅ 추천 API 응답:', response.data)

      if (response.data.recommendations && Array.isArray(response.data.recommendations)) {
        recommendations.value = response.data.recommendations
        console.log(`📝 ${recommendations.value.length}개 추천 저장됨`)
      } else {
        recommendations.value = []
        console.warn('⚠️ 추천 데이터가 없음')
      }

      return response.data

    } catch (err) {
      console.error('❌ 추천 API 오류:', err)

      if (err.response?.status === 401) {
        error.value = '로그인이 필요합니다.'
        localStorage.removeItem('access_token')
      } else if (err.response?.data?.error) {
        error.value = err.response.data.error
      } else if (err.response?.data?.detail) {
        error.value = err.response.data.detail
      } else {
        error.value = '추천 데이터를 불러오는데 실패했습니다.'
      }

      recommendations.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  const getUserGenreAnalysis = async () => {
    loading.value = true
    error.value = null

    try {
      console.log('📊 장르 분석 API 요청')

      const response = await axios.get(`${API_BASE_URL}/user/genre-analysis/`, {
        headers: getAuthHeaders()
      })

      console.log('✅ 장르 분석 응답:', response.data)
      userGenreAnalysis.value = response.data

      return response.data

    } catch (err) {
      console.error('❌ 장르 분석 오류:', err)

      if (err.response?.status === 401) {
        error.value = '로그인이 필요합니다.'
      } else if (err.response?.data?.error) {
        error.value = err.response.data.error
      } else {
        error.value = '장르 분석을 불러오는데 실패했습니다.'
      }

      userGenreAnalysis.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSimilarMovies = async (movieId) => {
    loading.value = true
    error.value = null

    try {
      console.log('🔍 유사 영화 API 요청:', movieId)

      const response = await axios.get(`${API_BASE_URL}/movies/${movieId}/similar/`, {
        headers: getAuthHeaders()
      })

      console.log('✅ 유사 영화 응답:', response.data)

      if (response.data.similar_movies && Array.isArray(response.data.similar_movies)) {
        similarMovies.value = response.data.similar_movies
      } else {
        similarMovies.value = []
      }

      return response.data

    } catch (err) {
      console.error('❌ 유사 영화 오류:', err)

      if (err.response?.data?.error) {
        error.value = err.response.data.error
      } else {
        error.value = '유사 영화를 불러오는데 실패했습니다.'
      }

      similarMovies.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearRecommendations = () => {
    recommendations.value = []
    userGenreAnalysis.value = null
    similarMovies.value = []
    error.value = null
    console.log('🧹 추천 데이터 초기화')
  }

  const appendRecommendations = (newRecommendations) => {
    if (Array.isArray(newRecommendations)) {
      recommendations.value.push(...newRecommendations)
      console.log(`➕ ${newRecommendations.length}개 추천 추가, 총: ${recommendations.value.length}개`)
    }
  }

  return {
    // State
    recommendations,
    userGenreAnalysis,
    similarMovies,
    loading,
    error,

    // Getters
    hasRecommendations,
    topGenres,
    recommendationCount,

    // Actions
    getMovieRecommendations,
    getUserGenreAnalysis,
    getSimilarMovies,
    clearRecommendations,
    appendRecommendations
  }
})

// 기본 내보내기 (Vue3 스타일)
export { useRecommendationStore }