<template>
  <div class="survey-page">
    <!-- 배경 그라데이션 -->
    <div class="background-gradient"></div>

    <!-- 헤더 -->
    <div class="survey-header">
      <div class="container">
        <div class="header-content">
          <div class="survey-info">
            <h1 class="survey-title">
              <i class="bi bi-stars"></i>
              영화 취향 설문조사
            </h1>
            <p class="survey-subtitle">
              당신의 취향을 알려주세요! 더 정확한 영화 추천을 위해 도움을 주세요.
            </p>
          </div>

          <div class="survey-progress">
            <div class="progress-info">
              <span class="progress-text">{{ currentIndex + 1 }} / {{ totalMovies }}</span>
              <span class="progress-percentage">{{ Math.round(((currentIndex + 1) / totalMovies) * 100) }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: ((currentIndex + 1) / totalMovies) * 100 + '%' }"></div>
            </div>
          </div>

          <button class="exit-btn" @click="showExitModal = true" title="설문 종료">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <div class="survey-content">
      <div class="container">
        <!-- 로딩 상태 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>영화를 불러오는 중...</p>
        </div>

        <!-- 에러 상태 -->
        <div v-else-if="error" class="error-state">
          <i class="bi bi-exclamation-triangle"></i>
          <h3>오류가 발생했습니다</h3>
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="loadMovies">다시 시도</button>
        </div>

        <!-- 설문 완료 -->
        <div v-else-if="isCompleted" class="completion-state">
          <div class="completion-content">
            <div class="completion-icon">
              <i class="bi bi-check-circle-fill"></i>
            </div>
            <h2 class="completion-title">설문이 완료되었습니다!</h2>
            <p class="completion-message">
              총 <strong>{{ ratedMovies.length }}</strong>개의 영화에 평점을 남겨주셨어요.<br>
              이제 당신만을 위한 맞춤 영화를 추천해드릴게요!
            </p>
            <div class="completion-stats">
              <div class="stat-item">
                <div class="stat-number">{{ ratedMovies.length }}</div>
                <div class="stat-label">평가한 영화</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ skippedMovies.length }}</div>
                <div class="stat-label">건너뛴 영화</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ averageRating.toFixed(1) }}</div>
                <div class="stat-label">평균 평점</div>
              </div>
            </div>
            <div class="completion-actions">
              <button class="btn btn-primary" @click="goToRecommendations">
                <i class="bi bi-magic"></i>
                추천 영화 보러가기
              </button>
              <button class="btn btn-secondary" @click="restartSurvey">
                <i class="bi bi-arrow-clockwise"></i>
                다시 설문하기
              </button>
            </div>
          </div>
        </div>

        <!-- 영화 카드 -->
        <div v-else-if="currentMovie" class="movie-survey-card">
          <div class="movie-card-container">
            <!-- 영화 포스터 -->
            <div class="movie-poster-section">
              <div class="movie-poster-wrapper">
                <img :src="currentMovie.poster" :alt="currentMovie.title" class="movie-poster"
                  @error="handlePosterError">
                <div class="movie-backdrop" :style="{ backgroundImage: `url(${currentMovie.poster})` }"></div>
              </div>
            </div>

            <!-- 영화 정보 및 평점 -->
            <div class="movie-info-section">
              <div class="movie-info">
                <h2 class="movie-title">{{ currentMovie.title }}</h2>
                <div class="movie-meta">
                  <span class="movie-year">{{ currentMovie.year }}</span>
                  <span class="movie-genres">{{ currentMovie.genre.join(', ') }}</span>
                  <span class="movie-rating">★ {{ currentMovie.rating }}/10</span>
                </div>
                <p class="movie-description" v-if="currentMovie.overview">
                  {{ truncateText(currentMovie.overview, 200) }}
                </p>
              </div>

              <!-- 별점 입력 -->
              <div class="rating-section">
                <h3 class="rating-title">이 영화를 어떻게 평가하시겠어요?</h3>

                <div class="star-rating">
                  <div class="stars-container">
                    <div v-for="star in 5" :key="star" class="star-item" @mouseenter="hoverRating = star"
                      @mouseleave="hoverRating = 0" @click="setRating(star)">
                      <!-- 전체 별 -->
                      <i class="bi star-full" :class="getStarClass(star, 'full')"></i>
                      <!-- 반쪽 별 -->
                      <i class="bi star-half" :class="getStarClass(star, 'half')"
                        @click.stop="setRating(star - 0.5)"></i>
                    </div>
                  </div>

                  <div class="rating-text" v-if="currentRating > 0">
                    <span class="rating-value">{{ currentRating }}</span>
                    <span class="rating-label">/ 5.0</span>
                  </div>
                </div>

                <!-- 액션 버튼들 -->
                <div class="action-buttons">
                  <button class="btn btn-outline skip-btn" @click="skipMovie">
                    <i class="bi bi-eye-slash"></i>
                    안 봤어요
                  </button>

                  <button class="btn btn-primary rate-btn" @click="rateMovie" :disabled="currentRating === 0">
                    <i class="bi bi-check-lg"></i>
                    평가하기
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 네비게이션 버튼 -->
          <div class="navigation-buttons">
            <button class="nav-btn prev-btn" @click="previousMovie" :disabled="currentIndex === 0"
              v-if="currentIndex > 0">
              <i class="bi bi-chevron-left"></i>
              이전
            </button>

            <button class="nav-btn next-btn" @click="nextMovie" :disabled="currentIndex >= totalMovies - 1"
              v-if="currentIndex < totalMovies - 1">
              다음
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 설문 종료 확인 모달 -->
    <div v-if="showExitModal" class="modal-overlay" @click="showExitModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">설문을 종료하시겠어요?</h3>
          <button class="modal-close-btn" @click="showExitModal = false">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>지금까지 <strong>{{ ratedMovies.length }}</strong>개의 영화를 평가해주셨어요.</p>
          <p>설문을 종료하시면 현재까지의 데이터로 영화를 추천해드립니다.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showExitModal = false">
            계속하기
          </button>
          <button class="btn btn-primary" @click="completeSurvey">
            설문 종료
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMovieStore } from '@/stores/movie'
import { useUserStore } from '@/stores/accounts'

// Stores
const movieStore = useMovieStore()
const userStore = useUserStore()
const router = useRouter()

// 반응형 데이터
const isLoading = ref(false)
const error = ref(null)
const movies = ref([])
const currentIndex = ref(0)
const currentRating = ref(0)
const hoverRating = ref(0)
const ratedMovies = ref([])
const skippedMovies = ref([])
const isCompleted = ref(false)
const showExitModal = ref(false)

// Computed
const totalMovies = computed(() => movies.value.length)
const currentMovie = computed(() => movies.value[currentIndex.value] || null)

const averageRating = computed(() => {
  if (ratedMovies.value.length === 0) return 0
  const sum = ratedMovies.value.reduce((acc, movie) => acc + movie.rating, 0)
  return sum / ratedMovies.value.length
})

// 별점 관련 메서드
const getStarClass = (starNumber, type) => {
  const rating = hoverRating.value || currentRating.value

  if (type === 'full') {
    if (rating >= starNumber) {
      return 'bi-star-fill active'
    } else if (rating >= starNumber - 0.5) {
      return 'bi-star-half active'
    } else {
      return 'bi-star'
    }
  } else if (type === 'half') {
    return 'star-half-overlay'
  }
}

const setRating = (rating) => {
  currentRating.value = rating
}

// 영화 관련 메서드
const loadMovies = async () => {
  isLoading.value = true
  error.value = null

  try {
    // 다양한 장르의 영화들을 가져오기
    const genres = ['popular', 'action', 'comedy', 'drama', 'horror', 'romance']
    const moviePromises = genres.map(genre =>
      movieStore.fetchMoviesByGenre(genre, 'top', '')
    )

    const results = await Promise.all(moviePromises)

    // 모든 영화를 합치고 중복 제거
    const allMovies = results.flat()
    const uniqueMovies = allMovies.filter((movie, index, self) =>
      index === self.findIndex(m => m.id === movie.id)
    )

    // 랜덤하게 섞고 30개만 선택
    movies.value = shuffleArray(uniqueMovies).slice(0, 30)

    if (movies.value.length === 0) {
      throw new Error('영화 데이터를 불러올 수 없습니다.')
    }

  } catch (err) {
    console.error('영화 로드 실패:', err)
    error.value = err.message || '영화를 불러오는 중 오류가 발생했습니다.'
  } finally {
    isLoading.value = false
  }
}

const shuffleArray = (array) => {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

const rateMovie = async () => {
  if (currentRating.value === 0) return

  const ratedMovie = {
    ...currentMovie.value,
    rating: currentRating.value,
    ratedAt: new Date().toISOString()
  }

  ratedMovies.value.push(ratedMovie)

  // 서버에 평점 저장 (실제 API 구현 필요)
  try {
    // TODO: API 호출
    console.log('평점 저장:', ratedMovie)
  } catch (err) {
    console.error('평점 저장 실패:', err)
  }

  // 다음 영화로 이동
  nextMovie()
}

const skipMovie = () => {
  const skippedMovie = {
    ...currentMovie.value,
    skippedAt: new Date().toISOString()
  }

  skippedMovies.value.push(skippedMovie)

  // 다음 영화로 이동
  nextMovie()
}

const nextMovie = () => {
  currentRating.value = 0
  hoverRating.value = 0

  if (currentIndex.value < totalMovies.value - 1) {
    currentIndex.value++
  } else {
    // 마지막 영화면 설문 완료
    completeSurvey()
  }
}

const previousMovie = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    currentRating.value = 0
    hoverRating.value = 0
  }
}

const completeSurvey = async () => {
  showExitModal.value = false

  // 서버에 설문 결과 전송
  try {
    const surveyData = {
      ratedMovies: ratedMovies.value,
      skippedMovies: skippedMovies.value,
      completedAt: new Date().toISOString(),
      totalMoviesShown: totalMovies.value
    }

    // TODO: 실제 API 호출
    console.log('설문 결과 저장:', surveyData)

    // 설문 완료 상태로 변경
    isCompleted.value = true

  } catch (err) {
    console.error('설문 결과 저장 실패:', err)
    // 에러가 있어도 완료 상태로 변경
    isCompleted.value = true
  }
}

const restartSurvey = () => {
  // 설문 초기화
  currentIndex.value = 0
  currentRating.value = 0
  hoverRating.value = 0
  ratedMovies.value = []
  skippedMovies.value = []
  isCompleted.value = false

  // 영화 다시 섞기
  movies.value = shuffleArray(movies.value)
}

const goToRecommendations = () => {
  // 추천 페이지로 이동
  router.push('/recommendations')
}

// 유틸리티 함수들
const handlePosterError = (event) => {
  event.target.src = '/api/placeholder/300/450'
}

const truncateText = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

// 키보드 이벤트 핸들러
const handleKeydown = (event) => {
  if (isCompleted.value || showExitModal.value) return

  switch (event.key) {
    case 'ArrowLeft':
      if (currentIndex.value > 0) previousMovie()
      break
    case 'ArrowRight':
      if (currentRating.value > 0) rateMovie()
      else skipMovie()
      break
    case 'Escape':
      showExitModal.value = true
      break
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
      setRating(parseInt(event.key))
      break
  }
}

// 생명주기
onMounted(async () => {
  await loadMovies()

  // 키보드 이벤트 리스너 추가
  document.addEventListener('keydown', handleKeydown)
})

// cleanup
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* 페이지 기본 스타일 */
.survey-page {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

.background-gradient {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg,
      #0a0a0a 0%,
      #1a0f1f 20%,
      #2d1b69 40%,
      #8e2de2 60%,
      #4a00e0 80%,
      #000000 100%);
  z-index: -1;
}

.background-gradient::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 20%, rgba(138, 43, 226, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 70% 80%, rgba(74, 0, 224, 0.3) 0%, transparent 50%);
  animation: gradientShift 8s ease-in-out infinite alternate;
}

@keyframes gradientShift {
  0% {
    opacity: 0.7;
  }

  100% {
    opacity: 1;
  }
}

/* 헤더 */
.survey-header {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem 0;
  position: sticky;
  top: 65px;
  z-index: 50;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.survey-info {
  flex: 1;
}

.survey-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #ffffff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.survey-subtitle {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 1rem;
}

.survey-progress {
  flex: 1;
  max-width: 300px;
  text-align: center;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8e2de2, #4a00e0);
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.exit-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.8);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
}

.exit-btn:hover {
  background: rgba(255, 99, 132, 0.2);
  border-color: rgba(255, 99, 132, 0.5);
  color: rgba(255, 99, 132, 0.9);
  transform: scale(1.1);
}

/* 메인 콘텐츠 */
.survey-content {
  padding: 3rem 0;
  min-height: calc(100vh - 140px);
  display: flex;
  align-items: center;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #8e2de2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 2rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.loading-state p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  margin: 0;
}

/* 에러 상태 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.error-state i {
  font-size: 4rem;
  color: rgba(255, 99, 132, 0.8);
  margin-bottom: 2rem;
}

.error-state h3 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: white;
}

.error-state p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

/* 완료 상태 */
.completion-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.completion-content {
  text-align: center;
  max-width: 600px;
}

.completion-icon {
  font-size: 6rem;
  color: #27ae60;
  margin-bottom: 2rem;
  animation: bounce 0.6s ease-out;
}

@keyframes bounce {
  0% {
    transform: scale(0);
  }

  50% {
    transform: scale(1.2);
  }

  100% {
    transform: scale(1);
  }
}

.completion-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #ffffff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.completion-message {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin-bottom: 3rem;
}

.completion-stats {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-bottom: 3rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #8e2de2;
  display: block;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
}

.completion-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* 영화 카드 */
.movie-survey-card {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
}

.movie-card-container {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  overflow: hidden;
  display: flex;
  min-height: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.movie-poster-section {
  flex: 0 0 300px;
  position: relative;
  overflow: hidden;
}

.movie-poster-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: relative;
  z-index: 2;
}

.movie-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-size: cover;
  background-position: center;
  filter: blur(10px) brightness(0.3);
  transform: scale(1.1);
  z-index: 1;
}

.movie-info-section {
  flex: 1;
  padding: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.movie-info {
  margin-bottom: 2rem;
}

.movie-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  line-height: 1.2;
  background: linear-gradient(135deg, #ffffff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.movie-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.movie-year,
.movie-genres,
.movie-rating {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.movie-rating {
  color: #ffd700;
}

.movie-description {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 0;
}

/* 별점 섹션 */
.rating-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.rating-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1.5rem;
  text-align: center;
}

.star-rating {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.stars-container {
  display: flex;
  gap: 0.5rem;
}

.star-item {
  position: relative;
  cursor: pointer;
  font-size: 2.5rem;
  transition: transform 0.2s ease;
}

.star-item:hover {
  transform: scale(1.2);
}

.star-full {
  color: rgba(255, 255, 255, 0.3);
  transition: color 0.2s ease;
}

.star-full.active {
  color: #ffd700;
  filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.6));
}

.star-half-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  overflow: hidden;
  cursor: pointer;
}

.star-half-overlay::before {
  content: '★';
  position: absolute;
  top: 0;
  left: 0;
  color: #ffd700;
  filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.6));
  transition: opacity 0.2s ease;
  opacity: 0;
}

.rating-text {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.rating-value {
  color: #ffd700;
  font-size: 2rem;
}

.rating-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.2rem;
}

/* 액션 버튼들 */
.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  position: relative;
  overflow: hidden;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.btn-primary {
  background: linear-gradient(135deg, #8e2de2, #4a00e0);
  color: white;
  min-width: 140px;
  justify-content: center;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #a653e8, #5d15e6);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(138, 43, 226, 0.4);
}

.btn-primary:hover:not(:disabled)::before {
  left: 100%;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
  transform: translateY(-2px);
}

.skip-btn {
  min-width: 140px;
  justify-content: center;
}

.rate-btn {
  min-width: 140px;
  justify-content: center;
}

/* 네비게이션 버튼 */
.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  padding: 0 1rem;
}

.nav-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.75rem 1.5rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  color: white;
  transform: translateY(-2px);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.modal-content {
  background: rgba(20, 20, 20, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
  animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px) scale(0.9);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2rem 1rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.modal-close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close-btn:hover {
  background: rgba(255, 99, 132, 0.2);
  color: rgba(255, 99, 132, 0.9);
  transform: scale(1.1);
}

.modal-body {
  padding: 2rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.modal-body p {
  margin: 0 0 1rem 0;
}

.modal-body strong {
  color: #8e2de2;
  font-weight: 600;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1rem 2rem 2rem 2rem;
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .movie-card-container {
    max-width: 900px;
  }

  .movie-poster-section {
    flex: 0 0 250px;
  }

  .movie-info-section {
    padding: 2rem;
  }
}

@media (max-width: 992px) {
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }

  .survey-header {
    top: 66px;
  }

  .survey-progress {
    max-width: 100%;
  }

  .movie-card-container {
    flex-direction: column;
    min-height: auto;
    max-width: 700px;
    margin: 0 auto;
  }

  .movie-poster-section {
    flex: none;
    width: 100%;
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .movie-poster {
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    object-fit: contain;
  }

  .movie-poster-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
  }

  .movie-info-section {
    padding: 2rem 1.5rem;
  }

  .movie-title {
    font-size: 2rem;
  }

  .completion-stats {
    flex-direction: column;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .survey-header {
    padding: 1rem 0;
    top: 60px;
    padding: 1rem 0;
  }

  .survey-title {
    font-size: 1.5rem;
  }

  .survey-subtitle {
    font-size: 0.9rem;
  }

  .survey-content {
    padding: 2rem 0;
  }

  .movie-info-section {
    padding: 1.5rem 1rem;
  }

  .movie-title {
    font-size: 1.8rem;
  }

  .movie-meta {
    flex-direction: column;
    gap: 0.5rem;
  }

  .rating-section {
    padding: 1.5rem;
  }

  .star-item {
    font-size: 2rem;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
  }

  .btn {
    width: 100%;
    max-width: 200px;
  }

  .completion-title {
    font-size: 2rem;
  }

  .completion-actions {
    flex-direction: column;
    align-items: center;
  }

  .modal-content {
    margin: 1rem;
    width: calc(100% - 2rem);
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .modal-footer {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .movie-poster-section {
    height: 250px;
  }

  .movie-info-section {
    padding: 1rem;
  }

  .movie-title {
    font-size: 1.5rem;
  }

  .rating-title {
    font-size: 1.1rem;
  }

  .star-item {
    font-size: 1.8rem;
  }

  .stars-container {
    gap: 0.25rem;
  }

  .btn {
    padding: 0.8rem 1.5rem;
    font-size: 0.9rem;
  }

  .completion-icon {
    font-size: 4rem;
  }

  .completion-title {
    font-size: 1.8rem;
  }

  .stat-number {
    font-size: 2rem;
  }

  .survey-header {
    top: 55px;
  }
}
</style>
