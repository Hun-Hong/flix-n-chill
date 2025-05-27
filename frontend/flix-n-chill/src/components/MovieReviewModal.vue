<template>
    <div v-if="isVisible" class="review-modal-overlay" @click="handleBackdropClick">
      <div class="review-modal-container" @click.stop>
        <!-- 헤더 -->
        <div class="review-modal-header">
          <div class="movie-info">
            <img 
              :src="movie?.poster || '/api/placeholder/60/90'" 
              :alt="movie?.title"
              class="movie-poster-small"
            />
            <div class="movie-details">
              <h3 class="movie-title">{{ movie?.title }}</h3>
              <p class="movie-year">{{ movie?.year }}</p>
            </div>
          </div>
          
          <button class="close-btn" @click="$emit('close')" aria-label="닫기">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- 로딩 상태 -->
        <div v-if="isLoadingReview" class="loading-content">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3">기존 리뷰를 확인하는 중...</p>
        </div>

        <!-- 본문 -->
        <div v-else class="review-modal-body">
          <form @submit.prevent="submitReview">
            <!-- 모드 표시 -->
            <div class="mode-indicator" v-if="isEditMode">
              <i class="bi bi-pencil-square"></i>
              <span>기존 리뷰 수정</span>
            </div>

            <!-- 별점 섹션 -->
            <div class="rating-section">
              <h4 class="section-title">이 영화를 평가해주세요</h4>
              
              <div class="star-rating">
                <div class="stars-container">
                  <div 
                    v-for="star in 5" 
                    :key="star"
                    class="star-item"
                    @mouseenter="hoverRating = star"
                    @mouseleave="hoverRating = 0"
                    @click="setRating(star)"
                  >
                    <!-- 전체 별 -->
                    <i 
                      class="bi star-full"
                      :class="getStarClass(star, 'full')"
                    ></i>
                    <!-- 반쪽 별 -->
                    <i 
                      class="bi star-half"
                      :class="getStarClass(star, 'half')"
                      @click.stop="setRating(star - 0.5)"
                    ></i>
                  </div>
                </div>
                
                <div class="rating-text" v-if="rating > 0">
                  <span class="rating-value">{{ rating }}</span>
                  <span class="rating-label">/ 5.0</span>
                  <span class="rating-description">{{ getRatingDescription(rating) }}</span>
                </div>
              </div>
            </div>

            <!-- 한줄평 섹션 -->
            <div class="review-section">
              <h4 class="section-title">한줄평을 남겨주세요 (선택사항)</h4>
              
              <div class="review-input-container">
                <textarea
                  v-model="reviewText"
                  class="review-textarea"
                  placeholder="이 영화에 대한 솔직한 감상을 남겨주세요..."
                  maxlength="200"
                  rows="4"
                ></textarea>
                <div class="character-count">
                  {{ reviewText.length }}/200
                </div>
              </div>
            </div>

            <!-- 기존 리뷰 정보 (수정 모드일 때만) -->
            <div v-if="isEditMode && existingReview" class="existing-review-info">
              <div class="info-item">
                <i class="bi bi-calendar3"></i>
                <span>작성일: {{ formatDate(existingReview.created_at) }}</span>
              </div>
            </div>

            <!-- 버튼 섹션 -->
            <div class="button-section">
              <button 
                type="button" 
                class="btn btn-secondary" 
                @click="$emit('close')"
              >
                취소
              </button>

              <!-- 삭제 버튼 (수정 모드일 때만 표시) -->
              <button 
                v-if="isEditMode"
                type="button" 
                class="btn btn-danger" 
                @click="deleteReview"
                :disabled="isSubmitting"
              >
                <i class="bi bi-trash"></i>
                삭제
              </button>
              
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="rating === 0 || isSubmitting"
              >
                <span v-if="isSubmitting">
                  <i class="bi bi-hourglass-split"></i>
                  {{ isEditMode ? '수정 중...' : '제출 중...' }}
                </span>
                <span v-else>
                  <i :class="isEditMode ? 'bi bi-check2-square' : 'bi bi-check-lg'"></i>
                  {{ isEditMode ? '리뷰 수정' : '평가 완료' }}
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useMovieStore } from '@/stores/movie'

// Props
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  movie: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'submit'])

// Store
const movieStore = useMovieStore()

// 반응형 데이터
const rating = ref(0)
const hoverRating = ref(0)
const reviewText = ref('')
const isSubmitting = ref(false)
const isLoadingReview = ref(false)
const existingReview = ref(null)

// 계산된 속성
const isEditMode = computed(() => !!existingReview.value)

// 기존 리뷰 조회
const loadExistingReview = async () => {
  if (!props.movie?.id) return
  
  isLoadingReview.value = true
  try {
    const review = await movieStore.getUserReview(props.movie.id)
    if (review) {
      existingReview.value = review
      rating.value = review.rating
      reviewText.value = review.comment || ''
      console.log('기존 리뷰 로드:', review)
    } else {
      existingReview.value = null
      console.log('기존 리뷰 없음')
    }
  } catch (error) {
    console.error('기존 리뷰 조회 실패:', error)
    existingReview.value = null
  } finally {
    isLoadingReview.value = false
  }
}

// 별점 관련 메서드
const getStarClass = (starNumber, type) => {
  const currentRating = hoverRating.value || rating.value
  
  if (type === 'full') {
    if (currentRating >= starNumber) {
      return 'bi-star-fill active'
    } else if (currentRating >= starNumber - 0.5) {
      return 'bi-star-half active'
    } else {
      return 'bi-star'
    }
  } else if (type === 'half') {
    return 'star-half-overlay'
  }
}

const setRating = (newRating) => {
  rating.value = newRating
}

const getRatingDescription = (rating) => {
  if (rating <= 1) return '별로예요'
  if (rating <= 2) return '아쉬워요'
  if (rating <= 3) return '보통이에요'
  if (rating <= 4) return '좋아요'
  return '최고예요!'
}

// 폼 제출
const submitReview = async () => {
  if (rating.value === 0) return
  
  isSubmitting.value = true
  
  try {
    const movieId = props.movie.id
    const reviewData = {
      rating: rating.value,
      comment: reviewText.value.trim()
    }
    
    console.log('리뷰 제출 데이터:', reviewData)
    
    let result
    if (isEditMode.value) {
      // 수정 모드
      result = await movieStore.updateReview(movieId, existingReview.value.id, reviewData)
    } else {
      // 새 리뷰 생성
      result = await movieStore.createReview(movieId, reviewData)
    }
    
    console.log('리뷰 처리 완료:', result)
    
    // 성공 시 부모 컴포넌트에 알림
    emit('submit', {
      ...reviewData,
      movie: props.movie,
      success: true,
      isEdit: isEditMode.value,
      reviewId: result.id
    })
    
    // 폼 초기화 (다음 열기를 위해)
    resetForm()
    
  } catch (error) {
    console.error('리뷰 제출 오류:', error)
    
    let errorMessage = `리뷰 ${isEditMode.value ? '수정' : '제출'}에 실패했습니다. 다시 시도해주세요.`
    
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = '로그인이 필요합니다.'
      } else if (error.response.status === 400) {
        errorMessage = error.response.data?.error || '입력 정보를 확인해주세요.'
      } else if (error.response.status === 404) {
        errorMessage = '영화를 찾을 수 없습니다.'
      }
    }
    
    alert(errorMessage)
    
    emit('submit', {
      error: true,
      message: errorMessage
    })
    
  } finally {
    isSubmitting.value = false
  }
}

// 리뷰 삭제
const deleteReview = async () => {
  if (!confirm('정말로 이 리뷰를 삭제하시겠습니까?')) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    const movieId = props.movie.id
    const reviewId = existingReview.value.id
    
    await movieStore.deleteReview(movieId, reviewId)
    
    console.log('리뷰 삭제 완료')
    
    // 성공 시 부모 컴포넌트에 알림
    emit('submit', {
      movie: props.movie,
      success: true,
      isDelete: true,
      reviewId: reviewId
    })
    
    // 폼 초기화
    resetForm()
    
  } catch (error) {
    console.error('리뷰 삭제 오류:', error)
    
    let errorMessage = '리뷰 삭제에 실패했습니다. 다시 시도해주세요.'
    
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = '로그인이 필요합니다.'
      } else if (error.response.status === 404) {
        errorMessage = '삭제할 리뷰를 찾을 수 없습니다.'
      }
    }
    
    alert(errorMessage)
    
  } finally {
    isSubmitting.value = false
  }
}

// 폼 초기화
const resetForm = () => {
  rating.value = 0
  hoverRating.value = 0
  reviewText.value = ''
  existingReview.value = null
  isSubmitting.value = false
}

// 이벤트 핸들러
const handleBackdropClick = () => {
  emit('close')
}

// 날짜 포맷팅
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 모달이 열릴 때마다 기존 리뷰 확인
watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    resetForm()
    loadExistingReview()
  }
})
</script>

<style scoped>
/* 기존 스타일에 추가할 스타일들 */

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  color: white;
  text-align: center;
}

.mode-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.2), rgba(41, 128, 185, 0.1));
  border: 1px solid rgba(52, 152, 219, 0.3);
  border-radius: 10px;
  color: #3498db;
  font-weight: 600;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.existing-review-info {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item i {
  color: rgba(255, 255, 255, 0.5);
}

/* 기존 모든 스타일을 여기에 포함 */
.review-modal-overlay {
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
  z-index: 1060;
  padding: 1rem;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.review-modal-container {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  position: relative;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
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

.review-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
}

.movie-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.movie-poster-small {
  width: 60px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.movie-details {
  color: white;
}

.movie-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  line-height: 1.3;
}

.movie-year {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.8);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 99, 132, 0.2);
  color: rgba(255, 99, 132, 0.9);
  transform: scale(1.1);
}

.review-modal-body {
  padding: 2rem;
  color: white;
  max-height: calc(90vh - 120px);
  overflow-y: auto;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: white;
}

.rating-section {
  margin-bottom: 2rem;
}

.star-rating {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
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
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.rating-value {
  font-size: 2rem;
  font-weight: 700;
  color: #ffd700;
}

.rating-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
}

.rating-description {
  font-size: 1.1rem;
  font-weight: 600;
  color: #ffd700;
  margin-top: 0.5rem;
}

.review-section {
  margin-bottom: 2rem;
}

.review-input-container {
  position: relative;
}

.review-textarea {
  width: 100%;
  background: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  color: white;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  min-height: 100px;
  transition: all 0.3s ease;
}

.review-textarea:focus {
  outline: none;
  border-color: #8e2de2;
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 3px rgba(142, 45, 226, 0.2);
}

.review-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.character-count {
  position: absolute;
  bottom: 0.5rem;
  right: 1rem;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  pointer-events: none;
}

.button-section {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  min-width: 120px;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-danger {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  position: relative;
  overflow: hidden;
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #c0392b, #a93226);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(231, 76, 60, 0.4);
}

.btn-primary {
  background: linear-gradient(135deg, #8e2de2, #4a00e0);
  color: white;
  position: relative;
  overflow: hidden;
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
  color: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
  transform: translateY(-2px);
}

@media (max-width: 600px) {
  .review-modal-container {
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
  }
  
  .review-modal-header {
    padding: 1rem;
  }
  
  .review-modal-body {
    padding: 1.5rem;
  }
  
  .movie-info {
    gap: 0.75rem;
  }
  
  .movie-poster-small {
    width: 50px;
    height: 75px;
  }
  
  .movie-title {
    font-size: 1.1rem;
  }
  
  .star-item {
    font-size: 2rem;
  }
  
  .stars-container {
    gap: 0.25rem;
  }
  
  .button-section {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .review-modal-body {
    padding: 1rem;
  }
  
  .star-item {
    font-size: 1.8rem;
  }
  
  .rating-value {
    font-size: 1.8rem;
  }
}
</style>