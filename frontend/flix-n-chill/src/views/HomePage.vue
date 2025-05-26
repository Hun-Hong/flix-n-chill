<template>
  <div class="home-page">
    <!-- 히어로 섹션 -->
    <div class="hero-section">
      <div class="container">
        <div class="hero-content">
          <h3 class="hero-title">
            <i class="bi bi-stars me-3"></i>
            FLIXnCHILL에 오신 것을 환영합니다
          </h3>
          <p class="hero-subtitle">
            당신만을 위한 영화 추천과 커뮤니티를 만나보세요!
          </p>
          <div class="hero-actions">
            <router-link :to="{ name: 'Search' }" class="btn btn-primary btn-lg">
              <i class="bi bi-search me-2"></i>
              영화 검색하기
            </router-link>
            <router-link :to="{ name: 'Genre' }" class="btn btn-outline-light btn-lg">
              <i class="bi bi-collection me-2"></i>
              장르별 영화
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- 인기 장르 섹션 -->
      <section class="genre-section">
        <div class="section-header">
          <h2 class="section-title">
            <i class="bi bi-fire me-2"></i>
            인기 장르
          </h2>
        </div>

        <div class="genre-grid">
          <div class="row g-3">
            <div v-for="genre in popularGenres" :key="genre.type" class="col-lg-3 col-md-4 col-sm-6 col-6">
              <router-link :to="{ name: 'Genre', query: { type: genre.type } }" class="genre-card">
                <div class="genre-icon">
                  <i :class="genre.icon"></i>
                </div>
                <h3 class="genre-name">{{ genre.name }}</h3>
                <p class="genre-description">{{ genre.description }}</p>
              </router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- 기능 소개 섹션 -->
      <section class="features-section">
        <div class="section-header">
          <h2 class="section-title">
            <i class="bi bi-heart me-2"></i>
            FLIXnCHILL의 특별한 기능들
          </h2>
        </div>

        <div class="features-grid">
          <div class="row g-4">
            <div class="col-lg-4 col-md-6">
              <div class="feature-card">
                <div class="feature-icon">
                  <i class="bi bi-search"></i>
                </div>
                <h3 class="feature-title">스마트 검색</h3>
                <p class="feature-description">원하는 영화를 빠르고 정확하게 찾아보세요</p>
                <router-link :to="{ name: 'Search' }" class="feature-link">
                  검색하기 <i class="bi bi-arrow-right"></i>
                </router-link>
              </div>
            </div>

            <div class="col-lg-4 col-md-6">
              <div class="feature-card">
                <div class="feature-icon">
                  <i class="bi bi-collection"></i>
                </div>
                <h3 class="feature-title">장르별 탐색</h3>
                <p class="feature-description">다양한 장르의 영화들을 쉽게 찾아보세요</p>
                <router-link :to="{ name: 'Genre' }" class="feature-link">
                  탐색하기 <i class="bi bi-arrow-right"></i>
                </router-link>
              </div>
            </div>

            <div class="col-lg-4 col-md-6">
              <div class="feature-card">
                <div class="feature-icon">
                  <i class="bi bi-person-circle"></i>
                </div>
                <h3 class="feature-title">개인 맞춤</h3>
                <p class="feature-description">로그인하고 나만의 영화 취향을 관리하세요</p>
                <router-link v-if="!isLoggedIn" :to="{ name: 'Login' }" class="feature-link">
                  로그인하기 <i class="bi bi-arrow-right"></i>
                </router-link>
                <router-link v-else :to="{ name: 'MyPage' }" class="feature-link">
                  마이페이지 <i class="bi bi-arrow-right"></i>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 회원가입 유도 섹션 (비로그인 시) -->
      <section v-if="!isLoggedIn" class="auth-promotion">
        <div class="promotion-content">
          <div class="promotion-icon">
            <i class="bi bi-person-heart"></i>
          </div>
          <h3>FLIXnCHILL의 모든 기능을 경험해보세요</h3>
          <ul class="promotion-features">
            <li><i class="bi bi-check-circle me-2"></i>개인화된 영화 추천</li>
            <li><i class="bi bi-check-circle me-2"></i>영화 평점 및 리뷰</li>
            <li><i class="bi bi-check-circle me-2"></i>취향 분석 서비스</li>
            <li><i class="bi bi-check-circle me-2"></i>커뮤니티 참여</li>
          </ul>
          <div class="promotion-actions">
            <router-link :to="{ name: 'Signup' }" class="btn btn-primary btn-lg">
              무료 회원가입
            </router-link>
            <router-link :to="{ name: 'Login' }" class="btn btn-outline-light btn-lg">
              로그인
            </router-link>
          </div>
        </div>
      </section>

      <!-- 로그인 사용자 환영 섹션 -->
      <section v-else class="welcome-section">
        <div class="welcome-content">
          <div class="welcome-icon">
            <i class="bi bi-emoji-smile"></i>
          </div>
          <h3>환영합니다!</h3>
          <p>다양한 영화를 탐색하고 나만의 취향을 발견해보세요.</p>
          <div class="welcome-actions">
            <router-link :to="{ name: 'Search' }" class="btn btn-primary">
              <i class="bi bi-search me-2"></i>
              영화 검색
            </router-link>
            <router-link :to="{ name: 'MyPage' }" class="btn btn-outline-light">
              <i class="bi bi-person me-2"></i>
              마이페이지
            </router-link>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 로그인 상태 확인
const isLoggedIn = computed(() => {
  return localStorage.getItem('isLoggedIn') === 'true'
})

// 인기 장르 데이터
const popularGenres = ref([
  {
    type: 'action',
    name: '액션',
    description: '스릴 넘치는 액션 영화',
    icon: 'bi bi-lightning-charge'
  },
  {
    type: 'comedy',
    name: '코미디',
    description: '재미있는 코미디 영화',
    icon: 'bi bi-emoji-laughing'
  },
  {
    type: 'drama',
    name: '드라마',
    description: '감동적인 드라마 영화',
    icon: 'bi bi-heart'
  },
  {
    type: 'horror',
    name: '호러',
    description: '무서운 호러 영화',
    icon: 'bi bi-moon'
  },
  {
    type: 'romance',
    name: '로맨스',
    description: '달콤한 로맨스 영화',
    icon: 'bi bi-heart-fill'
  },
  {
    type: 'adventure',
    name: '모험',
    description: '흥미진진한 모험 영화',
    icon: 'bi bi-compass'
  },
  {
    type: 'family',
    name: '가족',
    description: '온 가족이 함께 볼 수 있는 영화',
    icon: 'bi bi-house-heart'
  },
])

onMounted(() => {
  // 페이지 로드 시 필요한 초기화 작업
  console.log('HomePage 로드됨')
})
</script>

<style scoped>
/* 페이지 기본 스타일 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-title,
.hero-subtitle,
.hero-actions {
  animation: fadeInUp 1s ease forwards;
  opacity: 0;
}

.hero-title {
  animation-delay: 0.2s;
}

.hero-subtitle {
  animation-delay: 0.4s;
}

.hero-actions {
  animation-delay: 0.6s;
}

.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #073763 0%, #780909 100%);
  color: #ffffff;
  padding-top: 76px;
}

/* 히어로 섹션 */
.hero-section {
  background: linear-gradient(135deg,
      rgba(7, 55, 99, 0.9) 0%,
      rgba(120, 9, 9, 0.9) 100%),
    url('/api/placeholder/1920/600') center/cover;
  padding: 4rem 0;
  margin-bottom: 4rem;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #ffffff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2.5rem;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* 섹션 공통 스타일 */
.genre-section,
.features-section {
  margin-bottom: 4rem;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 장르 그리드 */
.genre-grid {
  margin-bottom: 2rem;
}

.genre-card {
  display: block;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 2rem 1rem;
  text-align: center;
  text-decoration: none;
  color: #ffffff;
  transition: all 0.3s ease;
  height: 100%;
}

.genre-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-5px);
  color: #ffffff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.genre-icon {
  font-size: 3rem;
  color: #db0000;
  margin-bottom: 1rem;
}

.genre-name {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #ffffff;
}

.genre-description {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 기능 소개 섹션 */
.features-grid {
  margin-bottom: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  height: 100%;
  transition: all 0.3s ease;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  color: #db0000;
  margin-bottom: 1.5rem;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #ffffff;
}

.feature-description {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.feature-link {
  color: #db0000;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.feature-link:hover {
  color: #ff4757;
  transform: translateX(5px);
}

/* 회원가입 유도 섹션 */
.auth-promotion {
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 100%);
  border-radius: 20px;
  padding: 4rem 2rem;
  text-align: center;
  margin: 4rem 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.promotion-content {
  max-width: 600px;
  margin: 0 auto;
}

.promotion-icon i {
  font-size: 4rem;
  color: #db0000;
  margin-bottom: 2rem;
}

.promotion-content h3 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: #ffffff;
}

.promotion-features {
  list-style: none;
  padding: 0;
  margin: 2rem 0;
  text-align: left;
  display: inline-block;
}

.promotion-features li {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
}

.promotion-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 2rem;
}

/* 환영 섹션 */
.welcome-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 3rem 2rem;
  text-align: center;
  margin: 4rem 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.welcome-content {
  max-width: 500px;
  margin: 0 auto;
}

.welcome-icon i {
  font-size: 3rem;
  color: #27ae60;
  margin-bottom: 1.5rem;
}

.welcome-content h3 {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #ffffff;
}

.welcome-content p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2rem;
}

.welcome-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* 버튼 스타일 */
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #db0000, #c20000);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #e60000, #d40000);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(219, 0, 0, 0.4);
  color: white;
}

.btn-outline-light {
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
  transform: translateY(-2px);
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

/* 반응형 디자인 */
@media (max-width: 992px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .section-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .home-page {
    padding-top: 70px;
  }

  .hero-section {
    padding: 3rem 0;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1.1rem;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .section-title {
    font-size: 1.75rem;
    flex-direction: column;
    gap: 0.5rem;
  }

  .genre-card,
  .feature-card {
    padding: 1.5rem 1rem;
  }

  .promotion-features {
    text-align: center;
  }

  .promotion-actions,
  .welcome-actions {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .hero-content {
    padding: 0 1rem;
  }

  .hero-title {
    font-size: 1.75rem;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .genre-icon,
  .feature-icon {
    font-size: 2.5rem;
  }
}
</style>