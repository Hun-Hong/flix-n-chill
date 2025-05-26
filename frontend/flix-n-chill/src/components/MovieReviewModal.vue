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
  
        <!-- 본문 -->
        <div class="review-modal-body">
          <form @submit.prevent="submitReview">
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
  
            <!-- 버튼 섹션 -->
            <div class="button-section">
              <button 
                type="button" 
                class="btn btn-secondary" 
                @click="$emit('close')"
              >
                취소
              </button>
              
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="rating === 0 || isSubmitting"
              >
                <span v-if="isSubmitting">
                  <i class="bi bi-hourglass-split"></i>
                  제출 중...
                </span>
                <span v-else>
                  <i class="bi bi-check-lg"></i>
                  평가 완료
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  
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
  
  // 반응형 데이터
  const rating = ref(0)
  const hoverRating = ref(0)
  const reviewText = ref('')
  const isSubmitting = ref(false)
  
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
      const reviewData = {
        movieId: props.movie.id,
        rating: rating.value,
        review: reviewText.value.trim(),
        createdAt: new Date().toISOString()
      }
      
      // API 호출 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      emit('submit', reviewData)
      
      // 폼 초기화
      rating.value = 0
      reviewText.value = ''
      
    } catch (error) {
      console.error('리뷰 제출 오류:', error)
      alert('리뷰 제출에 실패했습니다. 다시 시도해주세요.')
    } finally {
      isSubmitting.value = false
    }
  }
  
  // 이벤트 핸들러
  const handleBackdropClick = () => {
    emit('close')
  }
  
  // 모달이 열릴 때마다 폼 초기화
  watch(() => props.isVisible, (newValue) => {
    if (newValue) {
      rating.value = 0
      hoverRating.value = 0
      reviewText.value = ''
      isSubmitting.value = false
    }
  })
  </script>
  
  <style scoped>
  /* 모달 오버레이 */
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
    z-index: 1060; /* MovieDetailModal보다 높게 */
    padding: 1rem;
    animation: fadeIn 0.3s ease;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  /* 모달 컨테이너 */
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
  
  /* 헤더 */
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
  
  /* 본문 */
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
  
  /* 별점 섹션 */
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
  
  /* 한줄평 섹션 */
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
  
  /* 버튼 섹션 */
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
  
  /* 반응형 디자인 */
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