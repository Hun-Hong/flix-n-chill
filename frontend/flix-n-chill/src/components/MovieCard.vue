<template>
    <div class="movie-card" @click="goToMovieDetail">
      <div class="movie-poster">
        <!-- 영화 포스터 이미지 -->
        <img 
          :src="movie.poster || '/api/placeholder/300/450'" 
          :alt="movie.title" 
          class="poster-image"
          @error="handleImageError"
        >
        
        <!-- 호버 시 나타나는 오버레이 -->
        <div class="movie-overlay">
          <div class="movie-info">
            <!-- 영화 제목 -->
            <h5 class="movie-title">{{ movie.title }}</h5>
            
            <!-- 평점 -->
            <div class="movie-rating mb-2">
              <i class="bi bi-star-fill text-warning me-1"></i>
              <span>{{ movie.rating }}</span>
            </div>
            
            <!-- 출시년도 -->
            <p class="movie-year" v-if="movie.year">{{ movie.year }}년</p>
            
            <!-- 장르 -->
            <p class="movie-genre" v-if="movie.genre">{{ movie.genre }}</p>
            
            <!-- 액션 버튼들 -->
            <div class="movie-actions">
              <button 
                class="btn btn-sm btn-light me-2" 
                @click.stop="playMovie"
                title="재생"
              >
                <i class="bi bi-play-fill"></i>
              </button>
              <button 
                class="btn btn-sm btn-outline-light me-2" 
                @click.stop="toggleWatchlist"
                :class="{ 'btn-danger': movie.isInWatchlist }"
                :title="movie.isInWatchlist ? '찜 해제' : '찜하기'"
              >
                <i :class="movie.isInWatchlist ? 'bi bi-heart-fill' : 'bi bi-plus'"></i>
              </button>
              <button 
                class="btn btn-sm btn-outline-light" 
                @click.stop="toggleLike"
                :class="{ 'btn-success': movie.isLiked }"
                title="좋아요"
              >
                <i :class="movie.isLiked ? 'bi bi-hand-thumbs-up-fill' : 'bi bi-hand-thumbs-up'"></i>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 평점 배지 (오버레이 외부에 항상 표시) -->
        <div class="rating-badge">
          <i class="bi bi-star-fill"></i>
          {{ movie.rating }}
        </div>
        
        <!-- 찜하기 표시 (찜한 경우에만) -->
        <div v-if="movie.isInWatchlist" class="watchlist-badge">
          <i class="bi bi-heart-fill"></i>
        </div>
      </div>
      
      <!-- 카드 하단 정보 (항상 표시) -->
      <div class="movie-details" v-if="showDetails">
        <h6 class="movie-title-bottom">{{ movie.title }}</h6>
        <div class="movie-meta">
          <span class="movie-year-bottom">{{ movie.year }}</span>
          <span class="movie-genre-bottom">{{ movie.genre }}</span>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'MovieCard',
    props: {
      movie: {
        type: Object,
        required: true,
        default: () => ({
          id: 0,
          title: '영화 제목',
          rating: 0,
          year: 2024,
          genre: '장르',
          poster: '',
          isInWatchlist: false,
          isLiked: false
        })
      },
      showDetails: {
        type: Boolean,
        default: false
      },
      size: {
        type: String,
        default: 'medium', // 'small', 'medium', 'large'
        validator: (value) => ['small', 'medium', 'large'].includes(value)
      }
    },
    emits: ['play', 'toggle-watchlist', 'toggle-like', 'click'],
    methods: {
      // 영화 상세 페이지로 이동
      goToMovieDetail() {
        this.$emit('click', this.movie)
        // 실제로는 라우터로 이동
        // this.$router.push({ name: 'MovieDetail', params: { id: this.movie.id } })
      },
      
      // 영화 재생
      playMovie() {
        this.$emit('play', this.movie)
        console.log('영화 재생:', this.movie.title)
      },
      
      // 찜하기 토글
      toggleWatchlist() {
        this.$emit('toggle-watchlist', this.movie)
        console.log('찜하기 토글:', this.movie.title)
      },
      
      // 좋아요 토글
      toggleLike() {
        this.$emit('toggle-like', this.movie)
        console.log('좋아요 토글:', this.movie.title)
      },
      
      // 이미지 로드 실패 시 기본 이미지
      handleImageError(event) {
        event.target.src = '/api/placeholder/300/450'
      }
    }
  }
  </script>
  
  <style scoped>
  /* 기본 카드 스타일 */
  .movie-card {
    position: relative;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-radius: 12px;
    overflow: hidden;
  }
  
  .movie-card:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  }
  
  /* 포스터 컨테이너 */
  .movie-poster {
    position: relative;
    aspect-ratio: 2/3;
    overflow: hidden;
    border-radius: 12px;
    background: linear-gradient(135deg, #2c3e50, #34495e);
  }
  
  .poster-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }
  
  .movie-card:hover .poster-image {
    transform: scale(1.1);
  }
  
  /* 오버레이 */
  .movie-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      to top,
      rgba(0, 0, 0, 0.9) 0%,
      rgba(0, 0, 0, 0.7) 50%,
      rgba(0, 0, 0, 0.3) 70%,
      transparent 100%
    );
    display: flex;
    align-items: flex-end;
    padding: 1.5rem;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .movie-card:hover .movie-overlay {
    opacity: 1;
  }
  
  /* 오버레이 내 영화 정보 */
  .movie-info {
    width: 100%;
    color: white;
  }
  
  .movie-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #ffffff;
    line-height: 1.3;
  }
  
  .movie-rating {
    font-size: 0.9rem;
    color: #ffd700;
    display: flex;
    align-items: center;
  }
  
  .movie-year, .movie-genre {
    font-size: 0.8rem;
    color: #cccccc;
    margin-bottom: 0.25rem;
  }
  
  /* 액션 버튼들 */
  .movie-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
  }
  
  .movie-actions .btn {
    width: 36px;
    height: 36px;
    padding: 0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    border: 2px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
  }
  
  .movie-actions .btn:hover {
    transform: scale(1.1);
    border-color: rgba(255, 255, 255, 0.8);
  }
  
  .movie-actions .btn-light {
    background: rgba(255, 255, 255, 0.9);
    color: #333;
  }
  
  .movie-actions .btn-outline-light {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
  
  .movie-actions .btn-danger {
    background: rgba(220, 53, 69, 0.9);
    border-color: #dc3545;
    color: white;
  }
  
  .movie-actions .btn-success {
    background: rgba(25, 135, 84, 0.9);
    border-color: #198754;
    color: white;
  }
  
  /* 평점 배지 */
  .rating-badge {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    background: rgba(0, 0, 0, 0.8);
    color: #ffd700;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    backdrop-filter: blur(10px);
  }
  
  /* 찜하기 배지 */
  .watchlist-badge {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    background: rgba(220, 53, 69, 0.9);
    color: white;
    padding: 0.5rem;
    border-radius: 50%;
    font-size: 0.9rem;
    backdrop-filter: blur(10px);
  }
  
  /* 카드 하단 정보 */
  .movie-details {
    padding: 1rem 0.5rem;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 0 0 12px 12px;
  }
  
  .movie-title-bottom {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #ffffff;
    text-align: center;
  }
  
  .movie-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: #cccccc;
  }
  
  /* 카드 크기별 스타일 */
  .movie-card.size-small {
    max-width: 150px;
  }
  
  .movie-card.size-small .movie-title {
    font-size: 0.9rem;
  }
  
  .movie-card.size-small .movie-actions .btn {
    width: 30px;
    height: 30px;
    font-size: 0.8rem;
  }
  
  .movie-card.size-large {
    max-width: 300px;
  }
  
  .movie-card.size-large .movie-title {
    font-size: 1.3rem;
  }
  
  .movie-card.size-large .movie-actions .btn {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  /* 반응형 */
  @media (max-width: 768px) {
    .movie-overlay {
      padding: 1rem;
    }
    
    .movie-title {
      font-size: 1rem;
    }
    
    .movie-actions .btn {
      width: 32px;
      height: 32px;
      font-size: 0.85rem;
    }
    
    .rating-badge {
      top: 0.5rem;
      right: 0.5rem;
      font-size: 0.75rem;
      padding: 0.2rem 0.4rem;
    }
  }
  
  @media (max-width: 480px) {
    .movie-overlay {
      padding: 0.75rem;
    }
    
    .movie-actions {
      gap: 0.25rem;
    }
    
    .movie-actions .btn {
      width: 28px;
      height: 28px;
      font-size: 0.8rem;
    }
  }
  </style>