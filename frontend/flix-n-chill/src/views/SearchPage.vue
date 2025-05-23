<template>
    <div class="search-page">
      <!-- 검색 헤더 -->
      <div class="search-header">
        <div class="container">
          <!-- 페이지 타이틀 (검색 전에만 표시) -->
          <div class="search-title-section" v-if="!hasSearched">
            <h1 class="search-title" style="margin-top: 30px;">
              <i class="bi bi-search me-3"></i>
              영화 검색
            </h1>
            <p class="search-subtitle" style="margin-left: 20px;">찾고 싶은 영화 제목을 입력하세요!</p>
          </div>
  
          <!-- 검색창 -->
          <div class="search-input-section" :class="{ 'compact': hasSearched }">
            <SearchInput
              ref="searchInput"
              :initial-value="searchQuery"
              @search="handleSearch"
            />
          </div>
  
          <!-- 검색 결과 헤더 -->
          <div v-if="hasSearched && searchResults.length > 0" class="search-results-header">
            <h2 class="results-title">
              <i class="bi bi-film me-2"></i>
              "{{ searchQuery }}" 검색 결과
            </h2>
            <div class="results-count">
              {{ searchResults.length }}개의 영화를 찾았습니다!
            </div>
          </div>
        </div>
      </div>
  
      <!-- 메인 컨텐츠 -->
      <div class="container">
        <!-- 검색 전 상태 -->
        <div v-if="!hasSearched && !loading" class="search-welcome" style="margin-left: 20px;">
          <div class="welcome-content">
            <div class="welcome-icon">
              <i class="bi bi-camera-reels"></i>
            </div>
            <h3>어떤 영화를 찾고 계신가요?</h3>
            <p>영화 제목을 입력해서 검색해보세요!</p>
          </div>
        </div>
  
        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-section">
          <div class="d-flex justify-content-center align-items-center py-5">
            <div class="spinner-border text-danger me-3" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <h5 class="mb-0">"{{ searchQuery }}" 검색 중...</h5>
          </div>
        </div>
  
        <!-- 검색 에러 -->
        <div v-else-if="searchError" class="error-section">
          <div class="text-center py-5">
            <i class="bi bi-exclamation-triangle error-icon mb-4"></i>
            <h3 class="mb-3">검색 중 오류가 발생했습니다</h3>
            <p class="mb-4" style="color: gray;">잠시 후 다시 시도해주세요</p>
            <button @click="retrySearch" class="btn btn-outline-light">
              <i class="bi bi-arrow-clockwise me-2"></i>
              다시 시도
            </button>
          </div>
        </div>
  
        <!-- 검색 결과 -->
        <div v-else-if="hasSearched && searchResults.length > 0" class="search-results">
          <div class="movies-grid">
            <div class="row g-4">
              <div v-for="movie in searchResults" :key="movie.id" class="col-xl-2 col-lg-3 col-md-4 col-sm-6 col-6">
                <div class="movie-card" @click="handleMovieClick(movie)">
                  <div class="movie-poster">
                    <img :src="movie.poster || '/api/placeholder/300/450'" :alt="movie.title" />
                  </div>
                  <div class="movie-info">
                    <h5 class="movie-title">{{ movie.title }}</h5>
                    <p class="movie-year">{{ movie.year }}</p>
                    <div class="movie-rating" v-if="movie.rating">
                      <i class="bi bi-star-fill"></i>
                      {{ movie.rating }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- 검색 결과 없음 -->
        <div v-else-if="hasSearched && searchResults.length === 0" class="no-results">
          <div class="text-center py-5">
            <i class="bi bi-search no-results-icon mb-4"></i>
            <h3 class="mb-3">"{{ searchQuery }}"에 대한 검색 결과가 없습니다 :(</h3>
            <p class="mb-4" style="color: gray;">다른 영화 제목으로 검색해보세요</p>
            <button @click="clearSearch" class="btn btn-outline-light">
              <i class="bi bi-arrow-clockwise me-2"></i>
              새로 검색하기
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import SearchInput from '@/components/SearchInput.vue'
  import MovieCard from '@/components/MovieCard.vue'
  import { useMovieStore } from '@/stores/movie'
  import axios from 'axios'
  
  // Router & Store
  const route = useRoute()
  const router = useRouter()
  const store = useMovieStore()
  
  // 반응형 데이터
  const searchQuery = ref('')
  const searchResults = ref([])
  const loading = ref(false)
  const hasSearched = ref(false)
  const searchError = ref(false)
  
  // API 설정 - 백엔드 URL (Django 주소)
  const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'
  
  // 백엔드 API 호출 함수
  const searchMoviesFromAPI = async (query) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/movies/search/`, {
        params: {
          title: query  // 제목으로만 검색
        }
      })
      
      // Django 데이터를 MovieCard에 맞게 변환
      const transformedMovies = response.data.results.map(movie => ({
        id: movie.id,
        title: movie.title,
        rating: movie.vote_average,
        year: movie.release_date ? new Date(movie.release_date).getFullYear() : 2024,
        genre: 'search', // 검색 결과로 표시
        poster: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/api/placeholder/300/450',
        isInWatchlist: false,
        isLiked: false
      }))
      
      return transformedMovies
    } catch (error) {
      console.error('🚨 API 검색 오류:', error)
      throw error
    }
  }
  
  // 메서드들
  const handleSearch = (query) => {
    searchQuery.value = query
    performSearch(query)
    
    // URL 쿼리 파라미터 업데이트
    router.push({ 
      name: 'Search', 
      query: { q: query } 
    })
  }
  
  const performSearch = async (query) => {
    if (!query.trim()) return
    
    loading.value = true
    hasSearched.value = true
    searchError.value = false
    
    try {
      console.log('🔍 백엔드 검색 실행:', query)
      
      // 백엔드 API 호출
      const results = await searchMoviesFromAPI(query)
      
      searchResults.value = results || []
      
      console.log('✅ 검색 완료:', searchResults.value.length, '개 결과')
      
    } catch (error) {
      console.error('🚨 검색 오류:', error)
      searchError.value = true
      searchResults.value = []
    } finally {
      loading.value = false
    }
  }
  
  const clearSearch = () => {
    searchQuery.value = ''
    searchResults.value = []
    hasSearched.value = false
    searchError.value = false
    
    // URL 쿼리 파라미터 제거
    router.push({ name: 'Search' })
    
    // 검색창에 포커스
    setTimeout(() => {
      const searchInput = document.querySelector('.search-input')
      if (searchInput) {
        searchInput.focus()
      }
    }, 100)
  }
  
  const retrySearch = () => {
    if (searchQuery.value.trim()) {
      performSearch(searchQuery.value)
    }
  }
  
  // 영화 이벤트 핸들러들
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
  
  // 영화 클릭 이벤트
  const handleMovieClick = (movie) => {
    console.log('🎬 영화 클릭:', movie.title)
    // 실제로는 영화 상세 페이지로 이동
    // router.push({ name: 'MovieDetail', params: { id: movie.id } })
  }
  
  // URL 쿼리에서 검색어 가져오기
  onMounted(() => {
    const query = route.query.q
    if (query) {
      searchQuery.value = query
      performSearch(query)
    }
  })
  </script>
  
  <style scoped>
  /* 페이지 기본 스타일 */
  .search-page {
    min-height: 100vh;
    padding-top: 76px;
    background: linear-gradient(135deg, #073763 0%, #780909 100%);
    color: #ffffff;
  }
  
  /* 검색 헤더 */
  .search-header {
    background: linear-gradient(135deg,
        rgba(255, 255, 255, 0.1) 0%,
        rgba(255, 255, 255, 0.05) 100%);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2rem 0;
    margin-bottom: 2rem;
  }
  
  /* 검색 타이틀 섹션 */
  .search-title-section {
    text-align: center;
    margin-bottom: 3rem;
  }
  
  .search-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #ffffff, #e0e0e0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .search-subtitle {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 0;
  }
  
  /* 검색 입력 섹션 */
  .search-input-section {
    transition: all 0.3s ease;
  }
  
  .search-input-section.compact {
    margin-bottom: 2rem;
  }
  
  /* 검색 결과 헤더 */
  .search-results-header {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .results-title {
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #ffffff;
  }
  
  .results-count {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.8);
  }
  
  /* 검색 전 환영 화면 */
  .search-welcome {
    text-align: center;
    padding: 4rem 0;
  }
  
  .welcome-content {
    max-width: 500px;
    margin: 0 auto;
  }
  
  .welcome-icon {
    font-size: 5rem;
    color: rgba(255, 255, 255, 0.3);
    margin-bottom: 2rem;
  }
  
  .search-welcome h3 {
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #ffffff;
  }
  
  .search-welcome p {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
  }
  
  /* 로딩 섹션 */
  .loading-section {
    text-align: center;
    padding: 3rem 0;
  }
  
  /* 에러 섹션 */
  .error-section {
    text-align: center;
    padding: 4rem 0;
  }
  
  .error-icon {
    font-size: 5rem;
    color: #ff6b7a;
  }
  
  /* 검색 결과 그리드 */
  .movies-grid {
    margin-bottom: 2rem;
  }
  
  /* 검색 결과 없음 */
  .no-results {
    text-align: center;
    padding: 4rem 0;
  }
  
  .no-results-icon {
    font-size: 5rem;
    color: rgba(255, 255, 255, 0.3);
  }
  
  .no-results h3 {
    color: #ffffff;
    margin-bottom: 1rem;
  }
  
  .no-results p {
    color: rgba(255, 255, 255, 0.7);
    font-size: 1.1rem;
  }
  
  /* 버튼 스타일 */
  .btn-outline-light {
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: #ffffff;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    border-radius: 25px;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
  }
  
  .btn-outline-light:hover {
    background: rgba(219, 0, 0, 0.8);
    border-color: #db0000;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(219, 0, 0, 0.3);
  }
  
  /* 반응형 디자인 */
  @media (max-width: 992px) {
    .search-title {
      font-size: 2.5rem;
    }
    
    .results-title {
      font-size: 1.75rem;
    }
  }
  
  @media (max-width: 768px) {
    .search-header {
      padding: 1.5rem 0;
    }
    
    .search-title {
      font-size: 2rem;
    }
    
    .search-subtitle {
      font-size: 1rem;
    }
    
    .search-title-section {
      margin-bottom: 2rem;
    }
    
    .results-title {
      font-size: 1.5rem;
    }
    
    .welcome-icon {
      font-size: 4rem;
    }
    
    .search-welcome h3 {
      font-size: 1.5rem;
    }
  }
  
  @media (max-width: 576px) {
    .search-page {
      padding-top: 76px;
    }
    
    .search-title {
      font-size: 1.75rem;
    }
    
    .search-welcome {
      padding: 2rem 0;
    }
    
    .no-results {
      padding: 2rem 0;
    }
    
    .no-results-icon {
      font-size: 4rem;
    }
  }
  </style>