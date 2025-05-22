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
              <!-- <i :class="genre.icon" class="me-2"></i> -->
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
              {{ filteredMovies.length }}편의 {{ currentGenre.name }} 영화
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
      <div v-if="loading" class="loading-section">
        <div class="d-flex justify-content-center align-items-center py-5">
          <div class="spinner-border text-danger me-3" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <h5 class="mb-0">{{ currentGenre.name }} 영화를 불러오는 중...</h5>
        </div>
      </div>

      <!-- 영화 그리드 -->
      <div v-else-if="paginatedMovies.length > 0" class="movies-grid">
        <div class="row g-4">
          <div v-for="movie in paginatedMovies" :key="movie.id" class="col-xl-2 col-lg-3 col-md-4 col-sm-6 col-6">
            <MovieCard :movie="movie" :show-details="false" @play="handlePlayMovie"
              @toggle-watchlist="handleToggleWatchlist" @toggle-like="handleToggleLike" @click="handleMovieClick" />
          </div>
        </div>

        <!-- 더 보기 버튼 -->
        <div class="load-more-section" v-if="hasMoreMovies">
          <div class="text-center mt-5">
            <button @click="loadMore" class="btn btn-outline-light btn-lg load-more-btn">
              <i class="bi bi-arrow-down-circle me-2"></i>
              더 많은 {{ currentGenre.name }} 영화 보기
              <span class="badge bg-danger ms-2">{{ remainingMoviesCount }}</span>
            </button>
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
  </div>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue'

export default {
  name: 'GenrePage',
  components: {
    MovieCard
  },
  data() {
    return {
      loading: false,
      sortBy: 'rating',
      filterYear: '',
      currentPage: 1,
      moviesPerPage: 24,

      // 장르 정보
      genreList: [
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
      ],

      // 임시 영화 데이터
      moviesByGenre: {
        action: [
          { id: 1, title: '존 윅', rating: 8.5, year: 2014, genre: '액션', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: false },
          { id: 2, title: '미션 임파서블', rating: 8.3, year: 2018, genre: '액션', poster: '/api/placeholder/300/450', isInWatchlist: true, isLiked: false },
          { id: 3, title: '분노의 질주', rating: 8.1, year: 2021, genre: '액션', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: true },
          { id: 4, title: '매드 맥스', rating: 8.4, year: 2015, genre: '액션', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: false },
          { id: 5, title: '어벤져스', rating: 9.0, year: 2012, genre: '액션', poster: '/api/placeholder/300/450', isInWatchlist: true, isLiked: true },
          { id: 6, title: '아이언맨', rating: 8.7, year: 2008, genre: '액션', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: false }
        ],
        comedy: [
          { id: 11, title: '극한직업', rating: 8.2, year: 2019, genre: '코미디', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: false },
          { id: 12, title: '베테랑', rating: 8.1, year: 2015, genre: '코미디', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: true },
          { id: 13, title: '해운대', rating: 7.8, year: 2009, genre: '코미디', poster: '/api/placeholder/300/450', isInWatchlist: true, isLiked: false }
        ],
        drama: [
          { id: 21, title: '기생충', rating: 9.2, year: 2019, genre: '드라마', poster: '/api/placeholder/300/450', isInWatchlist: true, isLiked: true },
          { id: 22, title: '인터스텔라', rating: 8.9, year: 2014, genre: '드라마', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: true },
          { id: 23, title: '쇼생크 탈출', rating: 9.3, year: 1994, genre: '드라마', poster: '/api/placeholder/300/450', isInWatchlist: true, isLiked: false }
        ],
        horror: [
          { id: 31, title: '컨져링', rating: 8.1, year: 2013, genre: '호러', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: false },
          { id: 32, title: 'IT', rating: 7.8, year: 2017, genre: '호러', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: false }
        ],
        adventure: [
          { id: 41, title: '인디아나 존스', rating: 8.6, year: 1981, genre: '모험', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: false },
          { id: 42, title: '쥬라기 공원', rating: 8.7, year: 1993, genre: '모험', poster: '/api/placeholder/300/450', isInWatchlist: true, isLiked: false }
        ],
        family: [
          { id: 51, title: '토이 스토리', rating: 8.5, year: 1995, genre: '가족', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: true },
          { id: 52, title: '겨울왕국', rating: 8.3, year: 2013, genre: '가족', poster: '/api/placeholder/300/450', isInWatchlist: true, isLiked: false }
        ],
        romance: [
          { id: 61, title: '라라랜드', rating: 8.6, year: 2016, genre: '로맨스', poster: '/api/placeholder/300/450', isInWatchlist: false, isLiked: false },
          { id: 62, title: '타이타닉', rating: 8.7, year: 1997, genre: '로맨스', poster: '/api/placeholder/300/450', isInWatchlist: true, isLiked: true }
        ]
      }
    }
  },
  computed: {
    // 현재 선택된 장르 타입
    currentGenreType() {
      return this.$route.query.type || 'action'
    },

    // 현재 장르 정보
    currentGenre() {
      return this.genreList.find(genre => genre.type === this.currentGenreType) || this.genreList[0]
    },

    // 현재 장르의 영화들
    currentMovies() {
      return this.moviesByGenre[this.currentGenreType] || []
    },

    // 필터링된 영화들
    filteredMovies() {
      let movies = [...this.currentMovies]

      // 연도 필터
      if (this.filterYear) {
        if (this.filterYear === '2020') {
          movies = movies.filter(movie => movie.year <= 2020)
        } else {
          movies = movies.filter(movie => movie.year.toString() === this.filterYear)
        }
      }

      // 정렬
      movies.sort((a, b) => {
        switch (this.sortBy) {
          case 'rating':
            return b.rating - a.rating
          case 'rating-low':
            return a.rating - b.rating
          case 'year':
            return b.year - a.year
          case 'year-old':
            return a.year - b.year
          case 'title':
            return a.title.localeCompare(b.title)
          default:
            return 0
        }
      })

      return movies
    },

    // 페이지네이션된 영화들
    paginatedMovies() {
      const endIndex = this.currentPage * this.moviesPerPage
      return this.filteredMovies.slice(0, endIndex)
    },

    // 더 보기 버튼 표시 여부
    hasMoreMovies() {
      return this.filteredMovies.length > this.paginatedMovies.length
    },

    // 남은 영화 수
    remainingMoviesCount() {
      return this.filteredMovies.length - this.paginatedMovies.length
    },

    // 전체 영화 수
    totalMovies() {
      return this.currentMovies.length
    }
  },
  watch: {
    // 라우트 쿼리가 변경될 때
    '$route.query.type'() {
      this.loadGenreMovies()
    },

    // 정렬/필터가 변경될 때 페이지 리셋
    sortBy() {
      this.currentPage = 1
    },
    filterYear() {
      this.currentPage = 1
    }
  },
  mounted() {
    this.loadGenreMovies()
  },
  methods: {
    // 장르 변경
    changeGenre(genreType) {
      this.$router.push({
        name: 'Genre',
        query: { type: genreType }
      })
    },

    // 장르별 영화 데이터 로드
    async loadGenreMovies() {
      this.loading = true

      try {
        // 실제로는 API 호출
        await new Promise(resolve => setTimeout(resolve, 500))

        // 데이터는 이미 moviesByGenre에 있음

      } catch (error) {
        console.error('영화 데이터 로드 실패:', error)
      } finally {
        this.loading = false
        this.currentPage = 1
      }
    },

    // 더 보기
    loadMore() {
      this.currentPage += 1
    },

    // 필터 초기화
    resetFilters() {
      this.sortBy = 'rating'
      this.filterYear = ''
      this.currentPage = 1
    },

    // 영화 관련 이벤트 핸들러들
    handlePlayMovie(movie) {
      console.log('영화 재생:', movie.title)
      // 실제로는 영화 재생 로직 구현
    },

    handleToggleWatchlist(movie) {
      console.log('찜하기 토글:', movie.title)
      // 실제로는 API 호출하여 찜하기 상태 변경
      movie.isInWatchlist = !movie.isInWatchlist
    },

    handleToggleLike(movie) {
      console.log('좋아요 토글:', movie.title)
      // 실제로는 API 호출하여 좋아요 상태 변경
      movie.isLiked = !movie.isLiked
    },

    handleMovieClick(movie) {
      console.log('영화 클릭:', movie.title)
      // 실제로는 영화 상세 페이지로 이동
      // this.$router.push({ name: 'MovieDetail', params: { id: movie.id } })
    }
  }
}
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

/* 로딩 섹션 */
.loading-section {
  text-align: center;
  padding: 3rem 0;
}

/* 영화 그리드 */
.movies-grid {
  margin-bottom: 2rem;
}

/* 더 보기 섹션 */
.load-more-section {
  text-align: center;
  padding: 2rem 0;
}

.load-more-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 50px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.load-more-btn:hover {
  background: rgba(219, 0, 0, 0.8);
  border-color: #db0000;
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(219, 0, 0, 0.3);
}

.load-more-btn .badge {
  font-size: 0.9rem;
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

  .load-more-btn {
    font-size: 1rem;
    padding: 0.75rem 1.5rem;
  }

  .empty-icon {
    font-size: 4rem;
  }
}
</style>