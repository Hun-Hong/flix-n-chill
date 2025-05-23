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
                <option value="rating">평점 높은순</option>
                <option value="rating-low">평점 낮은순</option>
                <option value="year">최신순</option>
                <option value="year-old">오래된순</option>
                <option value="title">제목순</option>
              </select>
              <select v-model="filterYear" class="form-select">
                <option value="">전체 연도</option>
                <option value="2024">2024년</option>
                <option value="2023">2023년</option>
                <option value="2022">2022년</option>
                <option value="2021">2021년</option>
                <option value="2020">2020년 이전</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="store.loading" class="loading-section">
        <div class="d-flex justify-content-center align-items-center py-5">
          <div class="spinner-border text-danger me-3" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <h5 class="mb-0">{{ currentGenre.name }} 영화를 불러오는 중...</h5>
        </div>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="store.error" class="error-section">
        <div class="text-center py-5">
          <i class="bi bi-exclamation-triangle text-warning mb-3" style="font-size: 3rem;"></i>
          <h3 class="mb-3">데이터를 불러올 수 없습니다</h3>
          <p class="text-muted mb-4">{{ store.error }}</p>
          <button @click="loadGenreMovies" class="btn btn-outline-light">
            <i class="bi bi-arrow-clockwise me-2"></i>
            다시 시도
          </button>
        </div>
      </div>

      <!-- 영화 그리드 -->
      <div v-else-if="currentMovies.length > 0" class="movies-grid">
        <div class="row g-4">
          <div v-for="movie in currentMovies" :key="movie.id" class="col-xl-2 col-lg-3 col-md-4 col-sm-6 col-6">
            <MovieCard :movie="movie" :show-details="false" @play="handlePlayMovie"
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
          <button @click="resetFilters" class="btn btn-outline-light">
            <i class="bi bi-arrow-clockwise me-2"></i>
            필터 초기화
          </button>
        </div>
      </div>
    </div>
    <!-- 영화 상세 모달 -->
    <MovieDetailModal :is-visible="showModal" :movie-id="selectedMovieId" @close="closeModal"
      @toggle-watchlist="handleModalToggleWatchlist" @toggle-like="handleModalToggleLike" @play="handleModalPlay" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MovieCard from '@/components/MovieCard.vue'
import { useMovieStore } from '@/stores/movie'
import MovieDetailModal from '@/components/MovieDetailModal.vue'

// Router 사용
const route = useRoute()
const router = useRouter()

// Store 사용
const store = useMovieStore()

// 반응형 데이터
const sortBy = ref('rating')
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

// 🎯 동기 함수를 사용해서 리액티브 데이터 가져오기
const currentMovies = computed(() => {
  let movies = store.getMoviesByGenreSync(currentGenreType.value)
  
  // 1️⃣ 연도 필터링 적용
  if (filterYear.value) {
    if (filterYear.value === '2020') {
      // 2020년 이전
      movies = movies.filter(movie => {
        const year = Number(movie.year) || 0
        return year <= 2020
      })
    } else {
      // 특정 연도
      movies = movies.filter(movie => {
        const year = Number(movie.year) || 0
        return year.toString() === filterYear.value
      })
    }
  }
  
  // 2️⃣ 정렬 적용
  const sortedMovies = [...movies].sort((a, b) => {
    switch (sortBy.value) {
      case 'rating':
        // 평점 높은순 (내림차순)
        return (b.vote_average || b.rating || b.imdbRating || 0) - (a.vote_average || a.rating || a.imdbRating || 0)
        
      case 'rating-low':
        // 평점 낮은순 (오름차순)
        return (a.vote_average || a.rating || a.imdbRating || 0) - (b.vote_average || b.rating || b.imdbRating || 0)
        
      case 'year':
        // 최신순 (내림차순)
        const yearA = Number(a.year) || 0
        const yearB = Number(b.year) || 0
        return yearB - yearA
        
      case 'year-old':
        // 오래된순 (오름차순)
        const oldYearA = Number(a.year) || 0
        const oldYearB = Number(b.year) || 0
        return oldYearA - oldYearB
        
      case 'title':
        // 제목순 (가나다순)
        const titleA = (a.title || a.name || '').toLowerCase()
        const titleB = (b.title || b.name || '').toLowerCase()
        return titleA.localeCompare(titleB, 'ko')
        
      default:
        return 0
    }
  })
  
  return sortedMovies
})

// 정렬/필터 변경 감지
watch([sortBy, filterYear], () => {
  // 정렬/필터 변경 시 자동으로 computed가 재실행됨
}, { immediate: true })

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
    // 🚀 비동기 API 호출!
    await store.fetchMoviesByGenre(currentGenreType.value)
    console.log('🎬 API 호출 완료!')

  } catch (error) {
    console.error('🚨 영화 데이터 로드 실패:', error)
  }
}

const resetFilters = () => {
  sortBy.value = 'rating'
  filterYear.value = ''
}

// 영화 관련 이벤트 핸들러들
const handlePlayMovie = (movie) => {
  console.log('🎬 영화 재생:', movie.title)
  // 실제로는 영화 재생 로직 구현
}

const handleToggleWatchlist = (movie) => {
  console.log('🎬 찜하기 토글:', movie.title)
  store.toggleWatchlist(movie.id)
}

const handleToggleLike = (movie) => {
  console.log('🎬 좋아요 토글:', movie.title)
  store.toggleLike(movie.id)
}

// 영화 클릭 이벤트 - 모달 열기
const handleMovieClick = (movie) => {
  console.log('🎬 영화 클릭 이벤트:', movie)  // 전체 movie 객체 확인
  console.log('🎬 영화 ID:', movie.id)        // id 값 확인
  
  // id가 없으면 경고하고 리턴
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
/* 페이지 기본 스타일 */
.genre-page {
  min-height: 100vh;
  padding-top: 76px;
  background: linear-gradient(135deg, #073763 0%, #780909 100%);
  color: #ffffff;
}

/* 장르 헤더 */
.genre-header {
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.genre-icon {
  font-size: 4rem;
}

.genre-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #ffffff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.genre-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0;
}

.genre-stats {
  text-align: right;
}

.movie-count {
  font-size: 1.2rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(219, 0, 0, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  border: 1px solid rgba(219, 0, 0, 0.3);
}

/* 장르 탭 */
.genre-tabs {
  margin-top: 2rem;
}

.genre-tabs-container {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.genre-tab {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.genre-tab:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
  transform: translateY(-2px);
}

.genre-tab.active {
  background: linear-gradient(135deg, #db0000, #ff4757);
  border-color: #db0000;
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(219, 0, 0, 0.4);
}

/* 필터 섹션 */
.filter-section {
  background: rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.results-count {
  color: #ffffff;
  font-weight: 600;
}

.filter-controls {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.form-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  backdrop-filter: blur(10px);
  width: auto;
  min-width: 140px;
}

.form-select:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #db0000;
  color: #ffffff;
  box-shadow: 0 0 0 0.2rem rgba(219, 0, 0, 0.25);
}

.form-select option {
  background: #2c3e50;
  color: #ffffff;
}

/* 로딩 & 에러 섹션 */
.loading-section,
.error-section {
  text-align: center;
  padding: 3rem 0;
}

/* 영화 그리드 */
.movies-grid {
  margin-bottom: 2rem;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 4rem 0;
}

.empty-icon {
  font-size: 5rem;
  color: rgba(255, 255, 255, 0.3);
}

.empty-state h3 {
  color: #ffffff;
  margin-bottom: 1rem;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
}

/* 반응형 디자인 */
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
  }

  .genre-tab {
    font-size: 0.9rem;
    padding: 0.6rem 1.2rem;
  }
}

@media (max-width: 768px) {
  .genre-header {
    padding: 1rem 0;
  }

  .genre-title {
    font-size: 1.75rem;
  }

  .genre-icon {
    font-size: 2.5rem;
  }

  .movie-count {
    font-size: 1rem;
    padding: 0.4rem 0.8rem;
  }

  .filter-section {
    padding: 1rem;
  }

  .filter-controls {
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-select {
    min-width: auto;
  }

  .genre-tabs-container {
    gap: 0.3rem;
  }

  .genre-tab {
    font-size: 0.8rem;
    padding: 0.5rem 1rem;
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
}
</style>