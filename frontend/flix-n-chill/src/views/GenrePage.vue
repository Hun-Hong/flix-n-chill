<template>
  <div class="genre-page">
    <!-- 장르 헤더 -->
    <div class="genre-header">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-8">
            <div class="d-flex align-items-center mb-3">
              <i :class="['genre-icon', 'me-3', currentGenre.icon]" :style="{ color: currentGenre.color }"></i>
              <div>
                <h1 class="genre-title">{{ currentGenre.name }} 영화</h1>
                <p class="genre-description">{{ currentGenre.description }}</p>
              </div>
            </div>
          </div>
          <div class="col-md-4 text-md-end">
            <div class="genre-stats">
              <span class="movie-count">{{ totalMovies }}편의 영화</span>
            </div>
          </div>
        </div>

        <!-- 장르 탭 네비게이션 -->
        <div class="genre-tabs">
          <div class="genre-tabs-container">
            <button v-for="genre in genreList" :key="genre.type" @click="changeGenre(genre.type)"
              :class="['genre-tab', { 'active': currentGenreType === genre.type }]">
              <i :class="['me-2', genre.icon]" :style="{ color: genre.color }"></i>
              {{ genre.name }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 메인 컨텐츠 -->
    <div class="container">
      <!-- 필터 및 정렬 옵션 -->
      <div class="filter-section mb-4">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h5 class="results-count mb-0">
              <i class="bi bi-film me-2"></i>
              {{ currentMovies.length }}편의 {{ currentGenre.name }} 영화
            </h5>
          </div>
          <div class="col-md-6">
            <div class="filter-controls">
              <select v-model="sortBy" class="form-select me-2">
                <option value="top">평점 높은순</option>
                <option value="bottom">평점 낮은순</option>
                <option value="latest">최신순</option>
                <option value="oldest">오래된순</option>
                <option value="title">제목순</option>
              </select>
              <input class="form-input" type="number" v-model="filterYear" min="1900" max="2025" step="1"
                placeholder="전체 연도" style="max-width: 120px;"/>
            </div>
          </div>
        </div>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="store.loading" class="loading-section">
        <div class="d-flex justify-content-center align-items-center py-5">
          <div class="cyber-loader me-3"></div>
          <h5 class="mb-0">{{ currentGenre.name }} 영화를 불러오는 중...</h5>
        </div>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="store.error" class="error-section">
        <div class="text-center py-5">
          <i class="bi bi-exclamation-triangle error-icon mb-3"></i>
          <h3 class="mb-3">데이터를 불러올 수 없습니다</h3>
          <p class="text-muted mb-4">{{ store.error }}</p>
          <button @click="loadGenreMovies" class="cyber-btn">
            <i class="bi bi-arrow-clockwise me-2"></i>
            다시 시도
          </button>
        </div>
      </div>

      <!-- 영화 그리드 -->
      <div v-else-if="currentMovies.length > 0" class="movies-grid">
        <div class="row g-4">
          <div v-for="movie in currentMovies" :key="movie.id" class="col-xl-2 col-lg-3 col-md-4 col-sm-6 col-6 movie-item">
            <MovieCard :movie="movie" :is-auth="userStore.isAuthenticated" :show-details="false" @play="handlePlayMovie"
              @toggle-watchlist="handleToggleWatchlist" @toggle-like="handleToggleLike" @click="handleMovieClick" />
          </div>
        </div>
      </div>

      <!-- 영화가 없을 때 -->
      <div v-else class="empty-state">
        <div class="text-center py-5">
          <i :class="currentGenre.icon" class="empty-icon mb-4"></i>
          <h3 class="mb-3">{{ currentGenre.name }} 영화를 찾을 수 없습니다</h3>
          <p class="text-muted mb-4">다른 필터 옵션을 시도해보거나 다른 장르를 선택해보세요.</p>
          <button @click="resetFilters" class="cyber-btn">
            <i class="bi bi-arrow-clockwise me-2"></i>
            필터 초기화
          </button>
        </div>
      </div>
    </div>
    <!-- 영화 상세 모달 -->
    <MovieDetailModal :is-visible="showModal" :is-auth="userStore.isAuthenticated" :movie-id="selectedMovieId" @close="closeModal"
      @toggle-watchlist="handleModalToggleWatchlist" @toggle-like="handleModalToggleLike" @play="handleModalPlay" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MovieCard from '@/components/MovieCard.vue'
import { useMovieStore } from '@/stores/movie'
import MovieDetailModal from '@/components/MovieDetailModal.vue'
import { useUserStore } from '@/stores/accounts'

// Router 사용
const route = useRoute()
const router = useRouter()

// Store 사용
const store = useMovieStore()
const userStore = useUserStore()

// 반응형 데이터
const sortBy = ref('top')
const filterYear = ref('')

// 모달 상태
const showModal = ref(false)
const selectedMovieId = ref(null)

// 장르 정보
const genreList = ref([
  {
    type: 'action',
    name: '액션',
    icon: 'bi bi-lightning-fill',
    color: '#FFA732',
    description: '스릴 넘치는 액션과 모험이 가득한 영화들'
  },
  {
    type: 'comedy',
    name: '코미디',
    icon: 'bi bi-emoji-laughing-fill',
    color: '#C5FFF8',
    description: '유쾌하고 재미있는 웃음이 가득한 영화들'
  },
  {
    type: 'drama',
    name: '드라마',
    icon: 'bi bi-heart-fill',
    color: '#BC7FCD',
    description: '깊이 있는 스토리와 감동이 있는 영화들'
  },
  {
    type: 'horror',
    name: '호러',
    icon: 'bi bi-moon-fill',
    color: '#FABC3F',
    description: '오싹하고 스릴 넘치는 공포 영화들'
  },
  {
    type: 'adventure',
    name: '모험',
    icon: 'bi bi-compass-fill',
    color: '#A8CD9F',
    description: '신나는 모험과 탐험이 펼쳐지는 영화들'
  },
  {
    type: 'family',
    name: '가족',
    icon: 'bi bi-house-heart-fill',
    color: '#FFEADD',
    description: '온 가족이 함께 즐길 수 있는 따뜻한 영화들'
  },
  {
    type: 'romance',
    name: '로맨스',
    icon: 'bi bi-heart-fill',
    color: '#FCAEAE',
    description: '달콤하고 로맨틱한 사랑 이야기들'
  }
])

// 계산된 속성들
const currentGenreType = computed(() => {
  return route.query.type || 'action'
})

const currentGenre = computed(() => {
  return genreList.value.find(genre => genre.type === currentGenreType.value) || genreList.value[0]
})

const currentMovies = computed(() => {
  return store.getMoviesByGenreSync(currentGenreType.value, sortBy.value, filterYear.value)
})

const totalMovies = computed(() => {
  return currentMovies.value.length
})

// 장르 변경 감지해서 새로 로드
watch(() => route.query.type, (newGenre) => {
  console.log('🎬 장르 변경 감지:', newGenre)
  loadGenreMovies()
})

// 메서드들
const changeGenre = (genreType) => {
  console.log('🎬 장르 변경:', genreType)
  router.push({
    name: 'Genre',
    query: { type: genreType }
  })
}

const loadGenreMovies = async () => {
  console.log('🎬 loadGenreMovies 호출 - 장르:', currentGenreType.value)

  try {
    await store.fetchMoviesByGenre(currentGenreType.value, sortBy.value, filterYear.value)
    console.log('🎬 API 호출 완료!')
  } catch (error) {
    console.error('🚨 영화 데이터 로드 실패:', error)
  }
}

// 정렬/필터 변경 감지
watch([sortBy, filterYear], () => {
  loadGenreMovies()
}, { immediate: true })

const resetFilters = () => {
  sortBy.value = 'rating'
  filterYear.value = ''
}

// 영화 관련 이벤트 핸들러들
const handlePlayMovie = (movie) => {
  console.log('🎬 영화 재생:', movie.title)
}

const handleToggleWatchlist = (movie) => {
  console.log('🎬 찜하기 토글:', movie.title)
  store.toggleWatchlist(movie.id)
}

const handleToggleLike = (movie) => {
  console.log('🎬 좋아요 토글:', movie.title)
  store.toggleLike(movie.id)
}

const handleMovieClick = (movie) => {
  console.log('🎬 영화 클릭 이벤트:', movie)
  console.log('🎬 영화 ID:', movie.id)

  if (!movie.id) {
    console.error('🚨 영화 ID가 없습니다:', movie)
    return
  }

  selectedMovieId.value = movie.id
  showModal.value = true

  console.log('🎬 모달 열림 - 선택된 ID:', selectedMovieId.value)
}

// 모달 관련 이벤트
const closeModal = () => {
  showModal.value = false
  selectedMovieId.value = null
}

const handleModalToggleWatchlist = (movie) => {
  store.toggleWatchlist(movie.id)
}

const handleModalToggleLike = (movie) => {
  store.toggleLike(movie.id)
}

const handleModalPlay = (movie) => {
  // 재생 로직
}

// 컴포넌트 마운트 시
onMounted(() => {
  console.log('🎬 컴포넌트 마운트!')
  loadGenreMovies()
})
</script>

<style scoped>
/* 🌟 CYBERPUNK GENRE PAGE STYLES 🌟 */

/* 페이지 기본 스타일 - 사이버펑크 배경 */
.genre-page {
  min-height: 100vh;
  padding-top: 76px;
  background: 
    linear-gradient(135deg, 
      rgba(7, 55, 99, 0.9) 0%, 
      rgba(120, 9, 9, 0.9) 100%),
    radial-gradient(circle at 20% 30%, rgba(219, 0, 0, 0.1) 0%, transparent 70%),
    radial-gradient(circle at 80% 70%, rgba(7, 55, 99, 0.1) 0%, transparent 70%);
  color: #ffffff;
  position: relative;
  overflow-x: hidden;
}

/* 매트릭스 스캔라인 효과 */
.genre-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(219, 0, 0, 0.02) 25%,
    rgba(255, 255, 255, 0.01) 50%,
    rgba(219, 0, 0, 0.02) 75%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: scanline 6s linear infinite;
  pointer-events: none;
  z-index: 1;
}

@keyframes scanline {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* 🎭 장르 헤더 - 글래스모피즘 */
.genre-header {
  background: 
    linear-gradient(135deg,
      rgba(0, 0, 0, 0.6) 0%,
      rgba(219, 0, 0, 0.1) 30%,
      rgba(0, 0, 0, 0.6) 100%);
  backdrop-filter: blur(20px) saturate(150%);
  border-bottom: 1px solid rgba(219, 0, 0, 0.3);
  padding: 2rem 0;
  margin-bottom: 2rem;
  position: relative;
  z-index: 2;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.genre-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(219, 0, 0, 0.8) 50%, 
    transparent 100%);
}

/* 🚀 장르 아이콘 - 홀로그래픽 효과 */
.genre-icon {
  font-size: 4rem;
  filter: 
    drop-shadow(0 0 20px currentColor)
    drop-shadow(0 0 40px rgba(219, 0, 0, 0.3));
  animation: iconFloat 4s ease-in-out infinite;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.genre-icon:hover {
  transform: scale(1.1) rotate(5deg);
  filter: 
    drop-shadow(0 0 30px currentColor)
    drop-shadow(0 0 60px rgba(219, 0, 0, 0.5));
}

@keyframes iconFloat {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(2deg); }
}

/* ⚡ 장르 제목 - 네온 효과 */
.genre-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(
    45deg,
    #ffffff,
    #ff6b6b,
    #ffffff,
    #ff4757,
    #ffffff
  );
  background-size: 400% 400%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: holographicText 3s ease-in-out infinite;
  text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
  position: relative;
}

@keyframes holographicText {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.genre-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* 📊 영화 카운트 - 사이버 배지 */
.movie-count {
  font-size: 1.2rem;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, 
    rgba(219, 0, 0, 0.8), 
    rgba(255, 68, 68, 0.6));
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  border: 2px solid rgba(219, 0, 0, 0.5);
}


/* 🎯 장르 탭 - 네온 버튼 */
.genre-tabs {
  margin-top: 2rem;
  position: relative;
  z-index: 2;
}

.genre-tabs-container {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
  justify-content: center;
}

.genre-tab {
  background: rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.8rem 1.8rem;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  backdrop-filter: blur(15px);
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.9rem;
}

.genre-tab::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.1), 
    transparent);
  transition: left 0.5s ease;
}

.genre-tab:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(219, 0, 0, 0.5);
  color: #ffffff;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 25px rgba(219, 0, 0, 0.2);
}

.genre-tab:hover::before {
  left: 100%;
}

.genre-tab.active {
  background: linear-gradient(135deg, #db0000, #ff4757);
  border-color: #ff6b6b;
  color: #ffffff;
  box-shadow: 
    0 8px 25px rgba(219, 0, 0, 0.5),
    0 0 30px rgba(219, 0, 0, 0.3);
  transform: translateY(-2px);
}

.genre-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 2px;
  background: linear-gradient(90deg, #ff0000, #ff6666, #ff0000);
  animation: activeGlow 2s ease-in-out infinite alternate;
}

@keyframes activeGlow {
  0% { box-shadow: 0 0 5px rgba(219, 0, 0, 0.8); }
  100% { box-shadow: 0 0 15px rgba(219, 0, 0, 1); }
}

/* 🔧 필터 섹션 - 사이버 컨트롤 */
.filter-section {
  background: 
    linear-gradient(135deg, 
      rgba(0, 0, 0, 0.6) 0%, 
      rgba(219, 0, 0, 0.1) 50%,
      rgba(0, 0, 0, 0.6) 100%);
  padding: 1.8rem;
  border-radius: 15px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(219, 0, 0, 0.3);
  position: relative;
  z-index: 2;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.results-count {
  color: #ffffff;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  font-size: 1.1rem;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

/* 🎨 폼 컨트롤 - 사이버 스타일 */
.form-select, .form-input {
  background: rgba(0, 0, 0, 0.6);
  border: 2px solid rgba(219, 0, 0, 0.3);
  color: #ffffff;
  backdrop-filter: blur(15px);
  border-radius: 10px;
  padding: 0.8rem 1rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.2);
}

.form-select:focus, .form-input:focus {
  background: rgba(0, 0, 0, 0.8);
  border-color: #db0000;
  color: #ffffff;
  box-shadow: 
    0 0 0 0.2rem rgba(219, 0, 0, 0.25),
    0 0 15px rgba(219, 0, 0, 0.3);
  transform: translateY(-1px);
}

.form-select option {
  background: #1a1a1a;
  color: #ffffff;
  border: none;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
  opacity: 1;
}

/* 🎭 사이버 로더 */
.cyber-loader {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(219, 0, 0, 0.3);
  border-top: 3px solid #db0000;
  border-radius: 50%;
  animation: cyberSpin 1s linear infinite;
  position: relative;
}

.cyber-loader::after {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  border: 2px solid transparent;
  border-top: 2px solid rgba(255, 68, 68, 0.5);
  border-radius: 50%;
  animation: cyberSpin 2s linear infinite reverse;
}

@keyframes cyberSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 🚨 에러 아이콘 */
.error-icon {
  font-size: 4rem;
  color: #ff6b6b;
  filter: drop-shadow(0 0 20px rgba(255, 107, 107, 0.5));
  animation: pulse 2s ease-in-out infinite alternate;
}

/* 🎮 사이버 버튼 */
.cyber-btn {
  background: linear-gradient(135deg, 
    rgba(219, 0, 0, 0.8), 
    rgba(255, 68, 68, 0.6));
  border: 2px solid rgba(219, 0, 0, 0.6);
  color: #ffffff;
  padding: 0.8rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 15px rgba(219, 0, 0, 0.3);
}

.cyber-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.2), 
    transparent);
  transition: left 0.5s ease;
}

.cyber-btn:hover {
  background: linear-gradient(135deg, #db0000, #ff4757);
  border-color: #ff6b6b;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 
    0 15px 35px rgba(219, 0, 0, 0.4),
    0 0 30px rgba(219, 0, 0, 0.3);
}

.cyber-btn:hover::before {
  left: 100%;
}

/* 🎬 영화 그리드 - 스태거 애니메이션 */
.movies-grid {
  margin-bottom: 2rem;
  position: relative;
  z-index: 2;
}

.movie-item {
  animation: movieItemFadeIn 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(30px);
}

.movie-item:nth-child(1) { animation-delay: 0.1s; }
.movie-item:nth-child(2) { animation-delay: 0.2s; }
.movie-item:nth-child(3) { animation-delay: 0.3s; }
.movie-item:nth-child(4) { animation-delay: 0.4s; }
.movie-item:nth-child(5) { animation-delay: 0.5s; }
.movie-item:nth-child(6) { animation-delay: 0.6s; }
.movie-item:nth-child(n+7) { animation-delay: 0.7s; }

@keyframes movieItemFadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 💫 빈 상태 스타일 */
.empty-state {
  text-align: center;
  padding: 4rem 0;
  position: relative;
  z-index: 2;
}

.empty-icon {
  font-size: 6rem;
  color: rgba(255, 255, 255, 0.3);
  filter: drop-shadow(0 0 30px rgba(255, 255, 255, 0.1));
  animation: emptyFloat 3s ease-in-out infinite;
}

@keyframes emptyFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
}

.empty-state h3 {
  color: #ffffff;
  margin-bottom: 1rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.empty-state p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* 🌟 반응형 디자인 */
@media (max-width: 1200px) {
  .genre-tabs-container {
    gap: 0.6rem;
  }
  
  .genre-tab {
    padding: 0.7rem 1.5rem;
    font-size: 0.85rem;
  }
}

@media (max-width: 992px) {
  .genre-title {
    font-size: 2rem;
  }

  .genre-icon {
    font-size: 3rem;
  }

  .filter-controls {
    justify-content: center;
    margin-top: 1rem;
  }

  .genre-tabs-container {
    justify-content: flex-start;
    gap: 0.5rem;
  }

  .genre-tab {
    font-size: 0.8rem;
    padding: 0.6rem 1.2rem;
  }

  .movie-count {
    font-size: 1rem;
    padding: 0.6rem 1.2rem;
  }
}

@media (max-width: 768px) {
  .genre-header {
    padding: 1.5rem 0;
  }

  .genre-title {
    font-size: 1.8rem;
  }

  .genre-icon {
    font-size: 2.5rem;
  }

  .filter-section {
    padding: 1.5rem;
  }

  .filter-controls {
    flex-direction: column;
    gap: 0.8rem;
  }

  .form-select, .form-input {
    width: 100%;
  }

  .genre-tabs-container {
    gap: 0.4rem;
  }

  .genre-tab {
    font-size: 0.75rem;
    padding: 0.5rem 1rem;
  }

  /* 모바일에서 영화 아이템 애니메이션 단순화 */
  .movie-item {
    animation-delay: 0.1s !important;
  }
}

@media (max-width: 576px) {
  .genre-page {
    padding-top: 76px;
  }

  .genre-header .row {
    text-align: center;
  }

  .genre-stats {
    text-align: center;
    margin-top: 1rem;
  }

  .results-count {
    font-size: 1rem;
    text-align: center;
    margin-bottom: 1rem;
  }

  .empty-icon {
    font-size: 4rem;
  }

  .genre-title {
    font-size: 1.6rem;
  }

  .genre-icon {
    font-size: 2rem;
  }

  .cyber-btn {
    padding: 0.7rem 1.5rem;
    font-size: 0.9rem;
  }

  /* 모바일에서 스캔라인 효과 줄이기 */
  .genre-page::before {
    animation-duration: 8s;
    opacity: 0.5;
  }
}

/* 🎨 고대비 모드 지원 */
@media (prefers-contrast: high) {
  .genre-header {
    background: rgba(0, 0, 0, 0.9);
    border-bottom: 3px solid #ff0000;
  }
  
  .genre-tab {
    border-width: 3px;
  }
  
  .filter-section {
    background: rgba(0, 0, 0, 0.8);
    border-width: 2px;
  }
}

/* 🌈 모션 감소 설정 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.3s !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.2s !important;
  }
  
  .genre-page::before {
    animation: none;
  }
  
  .genre-icon {
    animation: none;
  }
  
  .movie-item {
    animation: none;
    opacity: 1;
    transform: none;
  }
}

/* 🎯 포커스 접근성 */
.genre-tab:focus-visible,
.cyber-btn:focus-visible,
.form-select:focus-visible,
.form-input:focus-visible {
  outline: 3px solid rgba(219, 0, 0, 0.8);
  outline-offset: 2px;
}

/* ✨ 추가 글로우 효과 */
.filter-section:hover {
  box-shadow: 
    0 15px 35px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(219, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.genre-header:hover .genre-icon {
  transform: scale(1.05);
  filter: 
    drop-shadow(0 0 25px currentColor)
    drop-shadow(0 0 50px rgba(219, 0, 0, 0.4));
}

/* 🚀 로딩 상태 개선 */
.loading-section {
  text-align: center;
  padding: 4rem 0;
  position: relative;
  z-index: 2;
}

.loading-section h5 {
  color: #ffffff;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  animation: pulse 2s ease-in-out infinite alternate;
}

/* 🎪 최종 터치 - 페이지 전체 글로우 */
.genre-page {
  box-shadow: inset 0 0 100px rgba(219, 0, 0, 0.05);
}
</style>