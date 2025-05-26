<template>
  <div v-if="isVisible" class="modal-overlay" @click="handleBackdropClick">
    <div class="modal-container" @click.stop>
      <!-- 닫기 버튼 -->
      <button class="close-btn" @click="$emit('close')" aria-label="닫기">
        <i class="bi bi-x-lg"></i>
      </button>

      <!-- 로딩 상태 -->
      <div v-if="loading" class="loading-content">
        <div class="spinner-border text-danger" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3">영화 정보를 불러오는 중...</p>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="error" class="error-content">
        <i class="bi bi-exclamation-triangle error-icon"></i>
        <h4>정보를 불러올 수 없습니다</h4>
        <p>{{ error }}</p>
        <button @click="fetchMovieDetail" class="btn btn-outline-light btn-sm">
          <i class="bi bi-arrow-clockwise me-2"></i>
          다시 시도
        </button>
      </div>

      <!-- 영화 상세 정보 -->
      <div v-else-if="movieDetail" class="modal-content">
        <!-- 헤더 섹션 -->
        <div class="modal-header">
          <div class="movie-backdrop" v-if="movieDetail.backdrop_path">
            <img :src="`https://image.tmdb.org/t/p/w1280${movieDetail.backdrop_path}`" 
                 :alt="movieDetail.title" />
            <div class="backdrop-overlay"></div>
          </div>
          
          <div class="movie-header-content">
            <div class="movie-poster-section">
              <img :src="movieDetail.poster || '/api/placeholder/300/450'" 
                   :alt="movieDetail.title" 
                   class="movie-poster" />
            </div>
            
            <div class="movie-info-section">
              <h1 class="movie-title">{{ movieDetail.title }}</h1>
              <div class="movie-meta">
                <span class="movie-year">{{ movieDetail.year }}</span>
                <span class="separator">•</span>
                <span class="movie-rating">
                  <i class="bi bi-star-fill"></i>
                  {{ movieDetail.rating }}
                </span>
                <span class="separator" v-if="movieDetail.runtime">•</span>
                <span class="movie-runtime" v-if="movieDetail.runtime">{{ movieDetail.runtime }}분</span>
              </div>
              
              <!-- 장르 -->
              <div class="movie-genres" v-if="movieDetail.genres && movieDetail.genres.length">
                <span v-for="genre in movieDetail.genres" :key="genre" class="genre-tag">
                  {{ genre }}
                </span>
              </div>

              <!-- 액션 버튼들 -->
              <div class="action-buttons">
                <button @click="handlePlay" class="btn btn-primary play-btn">
                  <i class="bi bi-play-fill me-2"></i>
                  재생
                </button>
                
                <button v-if="isAuth"
                        @click="handleToggleLike" 
                        class="btn btn-outline-light action-btn"
                        :class="{ 'active': movieDetail.isLiked }">
                  <i class="bi" :class="movieDetail.isLiked ? 'bi-heart-fill' : 'bi-heart'"></i>
                </button>

                <!-- 평가하기 버튼 추가 -->
                <button v-if="isAuth"
                        @click.stop="openReviewModal" 
                        class="btn btn-outline-light action-btn"
                        title="평가하기">
                  <i class="bi bi-star"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 본문 섹션 -->
        <div class="modal-body">
          <!-- 줄거리 -->
          <div class="section" v-if="movieDetail.overview">
            <h3 class="section-title">줄거리</h3>
            <p class="overview">{{ movieDetail.overview }}</p>
          </div>

          <!-- 감상 가능한 플랫폼 -->
          <div class="section" v-if="movieDetail.providers && movieDetail.providers.length">
            <h3 class="section-title">감상 가능한 플랫폼</h3>
            <div class="providers-container">
              <div 
                v-for="provider in movieDetail.providers" 
                :key="provider.id" 
                class="provider-item"
              >
                <div class="provider-logo">
                  <img 
                    :src="provider.logo_path ? `https://image.tmdb.org/t/p/w92${provider.logo_path}` : '/api/placeholder/40/40'" 
                    :alt="provider.name"
                    @error="handleImageError"
                  />
                </div>
                <span class="provider-name">{{ provider.name }}</span>
              </div>
            </div>
          </div>

          <!-- 상세 정보 -->
          <div class="section">
            <h3 class="section-title">상세 정보</h3>
            <div class="details-grid">
              <div class="detail-item" v-if="movieDetail.release_date">
                <span class="label">개봉일</span>
                <span class="value">{{ formatDate(movieDetail.release_date) }}</span>
              </div>
              <div class="detail-item" v-if="movieDetail.original_language">
                <span class="label">원어</span>
                <span class="value">{{ getLanguageName(movieDetail.original_language) }}</span>
              </div>
              <div class="detail-item" v-if="movieDetail.vote_count">
                <span class="label">평점 참여</span>
                <span class="value">{{ movieDetail.vote_count.toLocaleString() }}명</span>
              </div>
              <div class="detail-item" v-if="movieDetail.budget && movieDetail.budget > 0">
                <span class="label">제작비</span>
                <span class="value">${{ (movieDetail.budget / 1000000).toFixed(1) }}M</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 평가 모달을 modal-container 외부로 이동 -->
    <MovieReviewModal 
      :is-visible="showReviewModal"
      :movie="movieDetail"
      @close="closeReviewModal"
      @submit="handleReviewSubmit"
    />
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import axios from 'axios'
import MovieReviewModal from './MovieReviewModal.vue'

// Props
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  movieId: {
    type: [Number, String],
    required: true
  },
  isAuth: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'toggle-watchlist', 'toggle-like', 'play', 'review-submitted'])

// 반응형 데이터
const movieDetail = ref(null)
const loading = ref(false)
const error = ref(null)
const showReviewModal = ref(false)

// 영화 상세 정보 가져오기
const fetchMovieDetail = async () => {
  if (!props.movieId) return
  
  loading.value = true
  error.value = null
  
  try {
    // Django API 호출
    const response = await axios.get(`http://127.0.0.1:8000/api/v1/movies/${props.movieId}/`)
    
    const genreList = {
      "1": "액션",
      "2": "모험",
      "3": "애니메이션",
      "4": "코미디",
      "5": "범죄",
      "6": "다큐멘터리",
      "7": "드라마",
      "8": "가족",
      "9": "판타지",
      "10": "역사",
      "11": "공포",
      "12": "음악",
      "13": "미스터리",
      "14": "로맨스",
      "15": "SF",
      "16": "TV 영화",
      "17": "스릴러",
      "18": "전쟁",
      "19": "서부"
    }

    // 데이터 변환
    const movie = response.data
    movieDetail.value = {
      id: movie.id,
      title: movie.title,
      overview: movie.overview,
      poster: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : null,
      backdrop_path: movie.backdrop_path,
      rating: movie.vote_average,
      year: movie.release_date ? new Date(movie.release_date).getFullYear() : null,
      release_date: movie.release_date,
      runtime: movie.runtime,
      genres: movie.genres.map((genreCode) => genreList[genreCode]) || [],
      original_language: movie.original_language,
      vote_count: movie.vote_count,
      budget: movie.budget,
      isLiked: false, // 실제로는 사용자 상태에 따라
      providers: movie.providers
    }
    
  } catch (err) {
    console.error('🚨 영화 상세 정보 로딩 오류:', err)
    error.value = '영화 정보를 불러오는데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// Watchers
watch(() => props.isVisible, (newValue) => {
  if (newValue && props.movieId) {
    fetchMovieDetail()
  }
  
  // 모달이 열릴 때 스크롤 방지
  if (newValue) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = 'auto'
  }
})

watch(() => props.movieId, (newValue) => {
  if (newValue && props.isVisible) {
    fetchMovieDetail()
  }
})

// 이벤트 핸들러들
const handleBackdropClick = () => {
  emit('close')
}

const handlePlay = () => {
  emit('play', movieDetail.value)
}

const handleToggleLike = () => {
  movieDetail.value.isLiked = !movieDetail.value.isLiked
  emit('toggle-like', movieDetail.value)
}

const handleReviewSubmit = (reviewData) => {
  console.log('리뷰 제출:', reviewData)
  emit('review-submitted', reviewData)
  closeReviewModal()
}

const openReviewModal = () => {
  showReviewModal.value = true
}

const closeReviewModal = () => {
  showReviewModal.value = false
}

// 이미지 로딩 실패 시 처리
const handleImageError = (event) => {
  event.target.style.display = 'none'
  event.target.parentElement.style.background = 'linear-gradient(135deg, #666, #888)'
  event.target.parentElement.innerHTML = '<i class="bi bi-play-circle" style="color: white; font-size: 20px;"></i>'
}

// 언어 코드를 한국어로 변환
const getLanguageName = (code) => {
  const languages = {
    'ko': '한국어',
    'en': '영어',
    'ja': '일본어',
    'zh': '중국어',
    'fr': '프랑스어',
    'de': '독일어',
    'es': '스페인어',
    'it': '이탈리아어',
    'ru': '러시아어'
  }
  return languages[code] || code.toUpperCase()
}

// 유틸리티 함수들
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 컴포넌트 제거 시 스크롤 복원
onBeforeUnmount(() => {
  document.body.style.overflow = 'auto'
})
</script>

<style scoped>
/* 모달 오버레이 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1rem;
  overflow-y: auto;
}

/* 모달 컨테이너 */
.modal-container {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 20px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  position: relative;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 닫기 버튼 */
.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.7);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(219, 0, 0, 0.8);
  transform: scale(1.1);
}

/* 로딩 및 에러 상태 */
.loading-content, .error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: white;
  text-align: center;
}

.error-icon {
  font-size: 3rem;
  color: #ff6b7a;
  margin-bottom: 1rem;
}

/* 모달 콘텐츠 */
.modal-content {
  height: 100%;
  max-height: 90vh;
  overflow-y: auto;
  color: white;
}

/* 헤더 섹션 */
.modal-header {
  position: relative;
  min-height: 400px;
}

.movie-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  overflow: hidden;
}

.movie-backdrop img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}

.backdrop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(26, 26, 46, 0.3) 0%,
    rgba(26, 26, 46, 0.8) 70%,
    rgba(26, 26, 46, 1) 100%
  );
}

.movie-header-content {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 2rem;
  padding: 2rem;
  align-items: flex-end;
  min-height: 400px;
}

.movie-poster-section {
  flex-shrink: 0;
}

.movie-poster {
  width: 200px;
  height: 300px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.movie-info-section {
  flex: 1;
  min-width: 0;
}

.movie-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.2;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}

.movie-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
}

.separator {
  color: rgba(255, 255, 255, 0.5);
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #ffc107;
  font-weight: 600;
}

.movie-genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.genre-tag {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

/* 액션 버튼들 */
.action-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.play-btn {
  background: linear-gradient(135deg, #db0000, #ff4757);
  border: none;
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.play-btn:hover {
  background: linear-gradient(135deg, #ff4757, #ff6b7a);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(219, 0, 0, 0.4);
}

.action-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

.action-btn.active {
  background: rgba(219, 0, 0, 0.8);
  border-color: #db0000;
  color: white;
}

/* 본문 섹션 */
.modal-body {
  padding: 2rem;
}

.section {
  margin-bottom: 2.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #ffffff;
  border-bottom: 2px solid rgba(219, 0, 0, 0.5);
  padding-bottom: 0.5rem;
}

.overview {
  font-size: 1rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
}

/* 감상 플랫폼 스타일 */
.providers-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.provider-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.04));
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  cursor: pointer;
  min-width: 140px;
}

.provider-item:hover {
  background: linear-gradient(135deg, rgba(219, 0, 0, 0.15), rgba(255, 71, 87, 0.1));
  border-color: rgba(219, 0, 0, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(219, 0, 0, 0.2);
}

.provider-logo {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.provider-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.provider-name {
  font-weight: 600;
  color: #ffffff;
  font-size: 0.95rem;
}

/* 상세 정보 그리드 */
.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.value {
  font-weight: 500;
  color: #ffffff;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .modal-container {
    margin: 0.5rem;
    max-height: 95vh;
  }
  
  .movie-header-content {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }
  
  .movie-poster {
    width: 150px;
    height: 225px;
  }
  
  .movie-title {
    font-size: 2rem;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .provider-item {
    min-width: 120px;
    padding: 0.6rem 0.8rem;
  }
  
  .provider-logo {
    width: 32px;
    height: 32px;
  }
  
  .provider-name {
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .movie-header-content {
    padding: 1rem;
  }
  
  .movie-title {
    font-size: 1.75rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
}
</style>