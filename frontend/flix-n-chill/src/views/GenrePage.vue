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
            <MovieCard :movie="movie" :is-auth="userStore.isAuthenticated" :show-details="false" @play="handlePlayMovie"
              @toggle-watchlist="handleToggleWatchlist" @toggle-like="handleToggleLike" @click="handleMovieClick" />
          </div>
        </div>

        <!-- 더보기 또는 완료 섹션 -->
        <div class="pagination-section">
          <!-- 더보기 섹션 -->
          <div v-if="hasMoreMovies" class="text-center mt-5 mb-4">
            <button 
              @click="loadMoreMovies" 
              :disabled="isLoadingMore"
              class="btn btn-load-more"
              ref="loadMoreButton"
            >
              <div v-if="isLoadingMore" class="d-flex align-items-center justify-content-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                더 많은 영화를 불러오는 중...
              </div>
              <div v-else class="d-flex align-items-center justify-content-center">
                <i class="bi bi-plus-circle me-2"></i>
                더 많은 영화 보기 ({{ remainingMoviesCount }}개 더)
              </div>
            </button>
          </div>

          <!-- 모든 영화를 다 본 경우 -->
          <div v-else-if="totalMoviesFromAPI > 0 && !hasMoreMovies" class="text-center mt-5 mb-4">
            <div class="all-movies-loaded">
              <i class="bi bi-check-circle-fill text-success mb-2" style="font-size: 2rem;"></i>
              <p class="text-white mb-0">모든 {{ currentGenre.name }} 영화를 확인했습니다! 🎬</p>
            </div>
          </div>
        </div>

        <!-- 새로 로드된 영화들의 시작점을 표시하는 마커 -->
        <div ref="newMoviesMarker" class="new-movies-marker"></div>
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
    <MovieDetailModal :is-visible="showModal" :is-auth="userStore.isAuthenticated" :movie-id="selectedMovieId" @close="closeModal"
      @toggle-watchlist="handleModalToggleWatchlist" @toggle-like="handleModalToggleLike" @play="handleModalPlay" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MovieCard from '@/components/MovieCard.vue'
import { useMovieStore } from '@/stores/movie'
import MovieDetailModal from '@/components/MovieDetailModal.vue'
import { useUserStore } from '@/stores/accounts'

const route = useRoute()
const router = useRouter()
const store = useMovieStore()
const userStore = useUserStore()

const sortBy = ref('top')
const filterYear = ref('')
const currentPage = ref(1)
const isLoadingMore = ref(false)
const totalMoviesFromAPI = ref(0)
const loadMoreButton = ref(null)
const newMoviesMarker = ref(null)
const showModal = ref(false)
const selectedMovieId = ref(null)

const genreList = ref([
  { type: 'action', name: '액션', icon: 'bi bi-lightning-fill', color: '#FFA732', description: '스릴 넘치는 액션과 모험이 가득한 영화들' },
  { type: 'comedy', name: '코미디', icon: 'bi bi-emoji-laughing-fill', color: '#C5FFF8', description: '유쾌하고 재미있는 웃음이 가득한 영화들' },
  { type: 'drama', name: '드라마', icon: 'bi bi-heart-fill', color: '#BC7FCD', description: '깊이 있는 스토리와 감동이 있는 영화들' },
  { type: 'horror', name: '호러', icon: 'bi bi-moon-fill', color: '#FABC3F', description: '오싹하고 스릴 넘치는 공포 영화들' },
  { type: 'adventure', name: '모험', icon: 'bi bi-compass-fill', color: '#A8CD9F', description: '신나는 모험과 탐험이 펼쳐지는 영화들' },
  { type: 'family', name: '가족', icon: 'bi bi-house-heart-fill', color: '#FFEADD', description: '온 가족이 함께 즐길 수 있는 따뜻한 영화들' },
  { type: 'romance', name: '로맨스', icon: 'bi bi-heart-fill', color: '#FCAEAE', description: '달콤하고 로맨틱한 사랑 이야기들' }
])

const currentGenreType = computed(() => route.query.type || 'action')
const currentGenre = computed(() => genreList.value.find(genre => genre.type === currentGenreType.value) || genreList.value[0])
const currentMovies = computed(() => store.getMoviesByGenreSync(currentGenreType.value, sortBy.value, filterYear.value) || [])
const totalMovies = computed(() => totalMoviesFromAPI.value || currentMovies.value.length)
const hasMoreMovies = computed(() => totalMoviesFromAPI.value > currentMovies.value.length)
const remainingMoviesCount = computed(() => Math.min(20, totalMoviesFromAPI.value - currentMovies.value.length))

watch(() => route.query.type, () => resetAndLoadMovies())
watch([sortBy, filterYear], () => resetAndLoadMovies())

const changeGenre = (genreType) => {
  router.push({ name: 'Genre', query: { type: genreType } })
}

const resetAndLoadMovies = async () => {
  currentPage.value = 1
  totalMoviesFromAPI.value = 0
  if (store.clearGenreMovies) {
    store.clearGenreMovies(currentGenreType.value, sortBy.value, filterYear.value)
  }
  await loadGenreMovies()
}

const loadGenreMovies = async () => {
  try {
    const response = await store.fetchMoviesByGenre(currentGenreType.value, sortBy.value, filterYear.value, currentPage.value)
    if (response && response.total) {
      totalMoviesFromAPI.value = response.total
    }
  } catch (error) {
    console.error('🚨 영화 데이터 로드 실패:', error)
  }
}

const loadMoreMovies = async () => {
  if (isLoadingMore.value) return

  // ✅ 현재 스크롤 위치 기억
  const savedScrollTop = window.scrollY || window.pageYOffset

  isLoadingMore.value = true

  try {
    currentPage.value += 1
    await loadGenreMovies()

    await nextTick()

    // ✅ 저장된 위치로 다시 스크롤 복원
    window.scrollTo({ top: savedScrollTop, behavior: 'auto' })

  } catch (error) {
    currentPage.value -= 1
    console.error('🚨 추가 영화 로드 실패:', error)
  } finally {
    isLoadingMore.value = false
  }
}


const resetFilters = () => {
  sortBy.value = 'top'
  filterYear.value = ''
}

const handlePlayMovie = (movie) => console.log('🎬 영화 재생:', movie.title)
const handleToggleWatchlist = (movie) => store.toggleWatchlist(movie.id)
const handleToggleLike = (movie) => store.toggleLike(movie.id)
const handleMovieClick = (movie) => {
  if (!movie.id) return
  selectedMovieId.value = movie.id
  showModal.value = true
}
const closeModal = () => {
  showModal.value = false
  selectedMovieId.value = null
}
const handleModalToggleWatchlist = (movie) => store.toggleWatchlist(movie.id)
const handleModalToggleLike = (movie) => store.toggleLike(movie.id)
const handleModalPlay = (movie) => {}

onMounted(() => {
  loadGenreMovies()
})
</script>


<style scoped>
/* 기존 스타일 그대로 유지 */
.genre-page {
  min-height: 100vh;
  padding-top: 76px;
  background: linear-gradient(135deg, #073763 0%, #780909 100%);
  color: #ffffff;
}

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

.form-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  border-radius: 0.375rem;
  backdrop-filter: blur(10px);
  width: auto;
  min-width: 140px;
}

.form-input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #db0000;
  color: #ffffff;
  box-shadow: 0 0 0 0.2rem rgba(219, 0, 0, 0.25);
}

.form-input::placeholder {
  color: #dddddd;
  opacity: 1;
}

.loading-section,
.error-section {
  text-align: center;
  padding: 3rem 0;
}

.movies-grid {
  margin-bottom: 2rem;
}

/* 더보기 버튼 스타일 - 기존 디자인과 조화롭게 */
.btn-load-more {
  background: linear-gradient(135deg, #db0000, #ff4757);
  border: none;
  color: #ffffff;
  padding: 1rem 2rem;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(219, 0, 0, 0.3);
  min-width: 280px;
}

.btn-load-more:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff4757, #ff6b7a);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(219, 0, 0, 0.4);
  color: #ffffff;
}

.btn-load-more:disabled {
  background: linear-gradient(135deg, #666, #888);
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.all-movies-loaded {
  background: rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 새로운 영화 마커 (보이지 않음) */
.new-movies-marker {
  height: 1px;
  width: 1px;
  opacity: 0;
  pointer-events: none;
}

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

  .btn-load-more {
    min-width: auto;
    width: 100%;
    max-width: 350px;
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