<template>
  <div class="recommendations-page">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <h1 class="page-title">🎬 맞춤 영화 추천</h1>
      <p class="page-subtitle">당신의 취향을 분석해서 완벽한 영화를 추천해드려요!</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>당신만을 위한 추천 영화를 찾고 있어요...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>추천 시스템에 문제가 발생했어요</h3>
      <p>{{ error }}</p>
      <button @click="refreshRecommendations" class="retry-btn">
        다시 시도하기
      </button>
    </div>

    <!-- 추천 없음 (첫 사용자) -->
    <div v-else-if="!hasRecommendations && !loading" class="empty-state">
      <div class="empty-icon">🎭</div>
      <h3>아직 추천할 영화가 없어요</h3>
      <p>몇 편의 영화를 평가해주시면 완벽한 추천을 해드릴게요!</p>
      <router-link to="/genre" class="explore-btn">
        영화 둘러보기
      </router-link>
    </div>

    <!-- 메인 콘텐츠 -->
    <div v-else class="main-content">
      <!-- 장르 선호도 분석 섹션 -->
      <section v-if="userGenreAnalysis" class="genre-analysis-section">
        <h2 class="section-title">📊 당신의 취향 분석</h2>
        <div class="genre-preferences">
          <div class="preference-item" v-for="({ genre, score }, index) in topGenres" :key="genre"
            :class="`rank-${index + 1}`">
            <div class="genre-info">
              <span class="genre-name">{{ genre }}</span>
              <span class="genre-score">{{ score.toFixed(1) }}/5</span>
            </div>
            <div class="score-bar">
              <div class="score-fill" :style="{ width: `${(score / 5) * 100}%` }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 추천 설정 컨트롤 -->
      <section class="controls-section">
        <div class="controls">
          <div class="control-group">
            <label for="recommendation-count">추천 개수:</label>
            <select id="recommendation-count" v-model="recommendationCount" @change="applyFilters">
              <option value="5">5개</option>
              <option value="10">10개</option>
              <option value="15">15개</option>
              <option value="20">20개</option>
            </select>
          </div>

          <div class="control-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="excludeRated" @change="applyFilters">
              <span class="checkmark"></span>
              이미 평가한 영화 제외
            </label>
          </div>

          <button @click="refreshRecommendations" class="refresh-btn" :disabled="loading">
            🔄 새로고침
          </button>
        </div>
      </section>

      <!-- 추천 영화 목록 -->
      <section class="recommendations-section">
        <h2 class="section-title">🌟 당신을 위한 추천 영화</h2>

        <div class="recommendations-grid">
          <div v-for="(movie, index) in recommendations" :key="movie.id" class="movie-card"
            :class="{ 'top-pick': index < 3 }" @click="goToMovieDetail(movie.id)">
            <!-- 상위 추천 배지 -->
            <div v-if="index < 3" class="top-badge">
              {{ index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉' }}
              TOP {{ index + 1 }}
            </div>

            <!-- 영화 포스터 -->
            <div class="poster-container">
              <img :src="getMoviePosterUrl(movie.poster_path)" :alt="`${movie.title} 포스터`" class="movie-poster"
                @error="handleImageError">
              <div class="similarity-badge">
                {{ Math.round(movie.similarity_score * 100) }}% 매치
              </div>
            </div>

            <!-- 영화 정보 -->
            <div class="movie-info">
              <h3 class="movie-title">{{ movie.title }}</h3>
              <p class="movie-original-title">{{ movie.original_title }}</p>

              <!-- 장르 태그 -->
              <div class="genre-tags">
                <span v-for="genre in movie.genres" :key="genre.name" class="genre-tag"
                  :class="{ 'matched-genre': isMatchedGenre(genre.name, movie.genre_matches) }">
                  {{ genre.name }}
                </span>
              </div>

              <!-- 매칭 장르 정보 -->
              <div v-if="movie.genre_matches?.length" class="match-info">
                <p class="match-text">
                  <span class="match-icon">💝</span>
                  당신이 좋아하는
                  <strong>{{movie.genre_matches.map(m => m.genre).join(', ')}}</strong>
                  장르예요!
                </p>
              </div>

              <!-- 영화 메타 정보 -->
              <div class="movie-meta">
                <span class="release-date">{{ formatDate(movie.release_date) }}</span>
                <span class="vote-average">⭐ {{ movie.vote_average }}/10</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 추가 액션 버튼들 -->
      <section class="actions-section">
        <button @click="loadMoreRecommendations" class="load-more-btn" :disabled="loading">
          더 많은 추천 보기
        </button>
        <button @click="analyzeAgain" class="analyze-btn">
          취향 다시 분석하기
        </button>
      </section>
    </div>
  </div>

  <!-- 영화 상세 모달 - 모든 이벤트 핸들러 연결 -->
  <MovieDetailModal :is-visible="showDetailModal" :movie-id="selectedMovieId" :is-auth="isAuth"
    @close="closeDetailModal" @play="handleMoviePlay" @toggle-like="handleToggleLikeWithStatusCheck"
    @review-submitted="handleReviewSubmitted" />


</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useRecommendationStore } from '@/stores/recommendation'
import { useUserStore } from '@/stores/accounts'
import { storeToRefs } from 'pinia'
import MovieDetailModal from '@/components/MovieDetailModal.vue'
import axios from 'axios'

// 라우터
const router = useRouter()

// 스토어 사용
const recommendationStore = useRecommendationStore()
const userStore = useUserStore()

// 스토어에서 반응형 상태 가져오기
const {
  recommendations,
  userGenreAnalysis,
  loading,
  error,
  hasRecommendations,
  topGenres
} = storeToRefs(recommendationStore)

// 로컬 반응형 상태
const recommendationCount = ref(10)
const excludeRated = ref(true)
const isInitialized = ref(false)

// 모달 상태
const showDetailModal = ref(false)
const selectedMovieId = ref(null)

// 로그인 상태
const isAuth = computed(() => userStore.isAuthenticated)

// Computed 속성들
const debugData = computed(() => ({
  recommendationsLength: recommendations.value?.length || 0,
  hasRecommendations: hasRecommendations.value,
  loading: loading.value,
  error: error.value,
  genreAnalysis: !!userGenreAnalysis.value,
  topGenresCount: topGenres.value?.length || 0
}))

// 메서드들
const loadInitialData = async () => {
  if (isInitialized.value) return
  
  try {
    console.log('🚀 초기 데이터 로드 시작...')
    
    // 장르 분석 먼저 로드
    await recommendationStore.getUserGenreAnalysis()
    console.log('✅ 장르 분석 완료:', userGenreAnalysis.value)
    
    // 추천 데이터 로드
    await recommendationStore.getMovieRecommendations({
      count: recommendationCount.value,
      excludeRated: excludeRated.value
    })
    console.log('✅ 추천 데이터 완료:', recommendations.value?.length)
    
    isInitialized.value = true
    
    // 다음 틱에서 렌더링 확인
    await nextTick()
    console.log('🔄 렌더링 완료, 최종 상태:', debugData.value)
    
  } catch (error) {
    console.error('❌ 초기 데이터 로드 실패:', error)
    isInitialized.value = true
  }
}

const refreshRecommendations = async () => {
  try {
    console.log('🔄 추천 새로고침:', {
      count: recommendationCount.value,
      excludeRated: excludeRated.value
    })
    
    await recommendationStore.getMovieRecommendations({
      count: recommendationCount.value,
      excludeRated: excludeRated.value
    })
    
    console.log('✅ 새로고침 완료:', recommendations.value?.length)
    
  } catch (error) {
    console.error('❌ 새로고침 실패:', error)
  }
}

const applyFilters = async () => {
  console.log('🎛️ 필터 적용...')
  await refreshRecommendations()
}

const loadMoreRecommendations = async () => {
  const newCount = recommendationCount.value + 10
  console.log('📈 더 많은 추천 로드:', newCount)
  
  recommendationCount.value = newCount
  await refreshRecommendations()
}

const analyzeAgain = async () => {
  try {
    console.log('🔍 취향 재분석...')
    
    await recommendationStore.getUserGenreAnalysis()
    await refreshRecommendations()
    
    console.log('✅ 재분석 완료')
  } catch (error) {
    console.error('❌ 재분석 실패:', error)
  }
}

const goToMovieDetail = (movieId) => {
  console.log('🎬 영화 카드 클릭:', movieId)
  selectedMovieId.value = movieId
  showDetailModal.value = true
}

// 영화 좋아요 상태를 확인하는 헬퍼 함수
const checkMovieLikeStatus = async (movieId) => {
  try {
    console.log('🔍 API로 좋아요 상태 확인:', movieId)
    const response = await axios.get(
      `http://34.47.106.179/api/v1/movies/${movieId}/`,
      {
        headers: {
          'Authorization': `Token ${userStore.token}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    const likeStatus = response.data.isLiked || false
    console.log('📊 API 응답 좋아요 상태:', likeStatus)
    return likeStatus
    
  } catch (error) {
    console.error('❌ 좋아요 상태 확인 실패:', error)
    
    // API 실패시 기본값 false 반환
    return false
  }
}

// 개선된 좋아요 토글 함수 (상태 확인 포함)
const handleToggleLikeWithStatusCheck = async (movie) => {
  if (!userStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }

  if (likeProcessing.value.has(movie.id)) {
    console.log('⏳ 이미 좋아요 처리 중입니다:', movie.id)
    return
  }

  try {
    console.log('❤️ 좋아요 토글 시작:', movie.id)
    likeProcessing.value.add(movie.id)
    
    // 🔥 핵심 수정: 현재 좋아요 상태를 API로 정확히 확인
    console.log('🔍 현재 좋아요 상태 확인 중...')
    const isCurrentlyLiked = await checkMovieLikeStatus(movie.id)
    console.log('📊 현재 좋아요 상태:', isCurrentlyLiked)
    
    let response
    const url = `http://34.47.106.179/api/v1/movies/${movie.id}/like/`
    const config = {
      headers: {
        'Authorization': `Token ${userStore.token}`,
        'Content-Type': 'application/json'  
      }
    }

    if (isCurrentlyLiked) {
      console.log('💔 좋아요 취소 요청 (DELETE)')
      response = await axios.delete(url, config)
    } else {
      console.log('💖 좋아요 추가 요청 (POST)')
      response = await axios.post(url, {}, config)
    }

    console.log('✅ 좋아요 API 응답:', response.data)
    
    // 성공 메시지 표시
    if (response.data.liked) {
      console.log('💖 영화를 좋아요에 추가했습니다!')
    } else {
      console.log('💔 영화를 좋아요에서 제거했습니다!')
    }


  } catch (error) {
    console.error('❌ 좋아요 처리 실패:', error)
    
    if (error.response?.status === 401) {
      alert('로그인이 만료되었습니다. 다시 로그인해주세요.')
      userStore.logout()
    } else if (error.response?.status === 404) {
      alert('해당 영화를 찾을 수 없습니다.')
    } else {
      alert('좋아요 처리 중 오류가 발생했습니다.')
    }
  } finally {
    likeProcessing.value.delete(movie.id)
  }
}


// 모달 닫을 때 처리 중인 상태도 정리
const closeDetailModal = () => {
  console.log('🚪 모달 닫기')
  showDetailModal.value = false
  selectedMovieId.value = null
  
  // 혹시 모를 처리 중인 상태들 정리
  setTimeout(() => {
    likeProcessing.value.clear()
  }, 1000)
}

const handleMoviePlay = (movie) => {
  console.log('▶️ 영화 재생:', movie)
  // 재생 로직 구현 (필요시 외부 플레이어나 스트리밍 서비스 연동)
}

// 좋아요 처리 상태 관리
const likeProcessing = ref(new Set()) // 현재 처리 중인 영화 ID들

const handleToggleLike = async (movie) => {
  if (!userStore.isAuthenticated) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }

  // 중복 호출 방지
  if (likeProcessing.value.has(movie.id)) {
    console.log('⏳ 이미 좋아요 처리 중입니다:', movie.id)
    return
  }

  try {
    console.log('❤️ 좋아요 토글 시작:', movie.id)
    
    // 처리 중 상태로 설정
    likeProcessing.value.add(movie.id)
    
    // 현재 좋아요 상태를 먼저 확인해야 함
    // movie 객체에서 isLiked 정보를 가져오거나, 별도 API로 확인
    const isCurrentlyLiked = movie.isLiked || false
    
    let response
    const url = `http://34.47.106.179/api/v1/movies/${movie.id}/like/`
    const config = {
      headers: {
        'Authorization': `Token ${userStore.token}`,
        'Content-Type': 'application/json'
      }
    }

    if (isCurrentlyLiked) {
      // 이미 좋아요 상태 → DELETE 요청으로 좋아요 취소
      console.log('💔 좋아요 취소 요청 (DELETE)')
      response = await axios.delete(url, config)
    } else {
      // 좋아요 안된 상태 → POST 요청으로 좋아요 추가
      console.log('💖 좋아요 추가 요청 (POST)')
      response = await axios.post(url, {}, config)
    }

    console.log('✅ 좋아요 API 응답:', response.data)
    
    // 성공 메시지 표시
    if (response.data.liked) {
      console.log('💖 영화를 좋아요에 추가했습니다!')
    } else {
      console.log('💔 영화를 좋아요에서 제거했습니다!')
    }

    // movie 객체의 isLiked 상태 업데이트 (로컬 상태 동기화)
    if (movie.isLiked !== undefined) {
      movie.isLiked = response.data.liked
    }

  } catch (error) {
    console.error('❌ 좋아요 처리 실패:', error)
    
    if (error.response?.status === 401) {
      alert('로그인이 만료되었습니다. 다시 로그인해주세요.')
      userStore.logout()
    } else if (error.response?.status === 404) {
      alert('해당 영화를 찾을 수 없습니다.')
    } else if (error.response?.status === 400) {
      alert('잘못된 요청입니다.')
    } else {
      alert('좋아요 처리 중 오류가 발생했습니다.')
    }
  } finally {
    // 처리 완료 후 상태 해제
    likeProcessing.value.delete(movie.id)
  }
}

const handleReviewSubmitted = async (data) => {
  console.log('⭐ 리뷰 제출 이벤트:', data)
  
  try {
    if (data.success) {
      let message = ''
      
      if (data.isDelete) {
        message = '리뷰가 삭제되었습니다!'
        console.log('🗑️ 리뷰 삭제 성공!')
      } else if (data.isEdit) {
        message = '리뷰가 수정되었습니다!'
        console.log('✏️ 리뷰 수정 성공!')
      } else {
        message = '리뷰가 등록되었습니다!'
        console.log('📝 리뷰 생성 성공!')
      }

      // 성공 메시지 표시
      alert(message)

      // 필요시 추천 데이터 새로고침
      // await refreshRecommendations()
      
    } else if (data.error) {
      console.error('❌ 리뷰 처리 실패:', data.message)
      alert('리뷰 처리 중 오류가 발생했습니다.')
    }
  } catch (error) {
    console.error('❌ 리뷰 제출 처리 중 오류:', error)
  }
}

// 유틸리티 함수들
const getMoviePosterUrl = (posterPath) => {
  if (!posterPath) return '/images/no-poster.jpg'
  return `https://image.tmdb.org/t/p/w500${posterPath}`
}

const handleImageError = (event) => {
  console.log('🖼️ 이미지 로드 실패')
  event.target.src = '/images/no-poster.jpg'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.getFullYear()
  } catch (e) {
    console.warn('날짜 파싱 오류:', dateString)
    return ''
  }
}

const isMatchedGenre = (genreName, genreMatches) => {
  if (!genreMatches || !Array.isArray(genreMatches)) return false
  return genreMatches.some(match => match.genre === genreName)
}

// 데이터 변화 감시 (디버깅용)
watch(recommendations, (newVal, oldVal) => {
  console.log('📊 추천 데이터 변화:', {
    이전: oldVal?.length || 0,
    현재: newVal?.length || 0,
    데이터: newVal
  })
}, { deep: true })

watch(loading, (newVal) => {
  console.log('⏳ 로딩 상태:', newVal)
})

watch(error, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    console.log('❌ 에러 상태:', newVal)
  }
})

// 라이프사이클
onMounted(async () => {
  console.log('🏁 RecommendationsPage 마운트')
  await loadInitialData()
})
</script>


<style scoped>
/* 기본 애니메이션 (최소화) */
@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 페이지 기본 레이아웃 */
.recommendations-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #073763 0%, #780909 50%, #073763 100%);
  color: #ffffff;
  padding-top: 100px;
  position: relative;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* 페이지 헤더 */
.page-header {
  text-align: center;
  padding: 3rem 0 2rem;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #ffffff;
}

.page-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  max-width: 600px;
  margin: 0 auto;
}

/* 로딩 상태 */
.loading-container {
  text-align: center;
  padding: 4rem 2rem;
  color: white;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top: 3px solid #db0000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

.loading-container p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
}

/* 에러 상태 */
.error-container {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 15px;
  color: white;
  max-width: 600px;
  margin: 0 auto;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #ff6b6b;
}

.error-container h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #ff6b6b;
}

.error-container p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2rem;
}

.retry-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.retry-btn:hover {
  background: #ff5252;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  color: white;
  max-width: 600px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.empty-state p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 2rem;
}

.explore-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #db0000;
  color: white;
  padding: 1rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.explore-btn:hover {
  color: white;
  background: #c20000;
}

/* 메인 콘텐츠 */
.main-content {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 2.5rem;
}

/* 섹션 타이틀 */
.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.section-title::before {
  content: '';
  width: 3px;
  height: 30px;
  background: #db0000;
  border-radius: 2px;
}

/* 장르 분석 섹션 */
.genre-analysis-section {
  margin-bottom: 3rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.genre-preferences {
  display: grid;
  gap: 1rem;
}

.preference-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  transition: background-color 0.2s ease;
  border-left: 3px solid transparent;
}

.preference-item.rank-1 {
  border-left-color: #ffd700;
}

.preference-item.rank-2 {
  border-left-color: #c0c0c0;
}

.preference-item.rank-3 {
  border-left-color: #cd7f32;
}

.preference-item:hover {
  background: rgba(255, 255, 255, 0.12);
}

.genre-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 200px;
}

.genre-name {
  font-weight: 600;
  color: #ffffff;
}

.genre-score {
  font-weight: 600;
  color: #ffd700;
}

.score-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  margin-left: 1.5rem;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #db0000, #ff6b6b);
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* 컨트롤 섹션 */
.controls-section {
  margin-bottom: 2.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.controls {
  display: flex;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.control-group label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.control-group select {
  padding: 0.6rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-weight: 500;
}

.control-group select option {
  background: #2c2c54;
  color: #ffffff;
}

.control-group select:focus {
  outline: none;
  border-color: #db0000;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 0.6rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #db0000;
}

.refresh-btn {
  background: #db0000;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #c20000;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 추천 영화 그리드 */
.recommendations-section {
  margin-bottom: 3rem;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.movie-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.movie-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(219, 0, 0, 0.3);
}

.movie-card.top-pick {
  border: 2px solid #ffd700;
}

.top-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #ffd700;
  color: #333;
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.8rem;
  z-index: 2;
}

.poster-container {
  position: relative;
  height: 400px;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .movie-poster {
  transform: scale(1.05);
}

.similarity-badge {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: #27ae60;
  color: white;
  padding: 0.4rem 1rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.85rem;
}

.movie-info {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.movie-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #ffffff;
  line-height: 1.3;
}

.movie-original-title {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.genre-tag {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.genre-tag.matched-genre {
  background: #db0000;
  color: white;
}

.match-info {
  background: rgba(219, 0, 0, 0.1);
  border: 1px solid rgba(219, 0, 0, 0.2);
  padding: 0.8rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.match-text {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.match-icon {
  margin-right: 0.5rem;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.release-date {
  font-weight: 500;
}

.vote-average {
  font-weight: 600;
  color: #ffd700;
}

/* 액션 섹션 */
.actions-section {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  flex-wrap: wrap;
}

.load-more-btn,
.analyze-btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more-btn {
  background: #4ecdc4;
  color: white;
}

.load-more-btn:hover:not(:disabled) {
  background: #45b7aa;
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.analyze-btn {
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.analyze-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

/* 반응형 디자인 */
@media (max-width: 992px) {
  .recommendations-page {
    padding-top: 90px;
  }

  .page-title {
    font-size: 3rem;
  }

  .main-content {
    padding: 2rem;
  }

  .recommendations-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .controls {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .actions-section {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }

  .page-title {
    font-size: 2.5rem;
  }

  .main-content {
    padding: 1.5rem;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .movie-info {
    padding: 1.2rem;
  }

  .poster-container {
    height: 350px;
  }

  .genre-analysis-section {
    padding: 1.5rem;
  }

  .preference-item {
    flex-direction: column;
    gap: 0.8rem;
    align-items: flex-start;
  }

  .genre-info {
    width: 100%;
  }

  .score-bar {
    margin-left: 0;
    margin-top: 0.5rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 2rem;
  }

  .main-content {
    padding: 1rem;
  }

  .load-more-btn,
  .analyze-btn {
    width: 100%;
  }

  .poster-container {
    height: 300px;
  }
}
</style>
