<template>
  <div class="home-page">
    <!-- 배경 효과 -->
    <div class="animated-background">
      <div class="bg-shape bg-shape-1"></div>
      <div class="bg-shape bg-shape-2"></div>
      <div class="bg-shape bg-shape-3"></div>
      <div class="gradient-mesh"></div>
    </div>

    <!-- 히어로 섹션 -->
    <div class="hero-section">
      <div class="container">
        <div class="hero-content">
          <!-- 프리미엄 배지 -->
          <div class="hero-badge animate-fade-up">
            <div class="badge-glow"></div>
            <i class="bi bi-stars"></i>
            <span>Premium Movie Experience</span>
          </div>
          
          <!-- 메인 타이틀 -->
          <h1 class="hero-title animate-fade-up">
            <div class="title-line">
              <div class="title-decoration">
                <i class="bi bi-stars"></i>
              </div>
              <span class="title-text">FLIXnCHILL</span>
              <div class="title-decoration">
                <i class="bi bi-stars"></i>
              </div>
            </div>
            <div class="subtitle-line">에 오신 것을 환영합니다</div>
          </h1>
          
          <!-- 서브타이틀 -->
          <p class="hero-subtitle animate-fade-up">
            <span class="highlight-text">AI 기반 추천 시스템</span>으로 당신만을 위한<br>
            완벽한 영화를 찾아보세요
          </p>
          
          <!-- 액션 버튼들 -->
          <div class="hero-actions animate-fade-up">
            <router-link :to="{ name: 'Search' }" class="hero-btn btn-primary">
              <div class="btn-bg"></div>
              <div class="btn-content">
                <i class="bi bi-search"></i>
                <span>영화 검색하기</span>
              </div>
              <div class="btn-ripple"></div>
            </router-link>
            
            <router-link :to="{ name: 'Genre' }" class="hero-btn btn-secondary">
              <div class="btn-bg"></div>
              <div class="btn-content">
                <i class="bi bi-collection"></i>
                <span>장르별 영화</span>
              </div>
            </router-link>
          </div>

          <!-- 통계 정보 -->
          <div class="hero-stats animate-fade-up">
            <div class="stat-item">
              <div class="stat-icon">
                <i class="bi bi-film"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">10,000+</div>
                <div class="stat-label">영화 데이터(가 목표입니다)</div>
              </div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-icon">
                <i class="bi bi-heart-fill"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">98%</div>
                <div class="stat-label">만족도(가 목표입니다)</div>
              </div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-icon">
                <i class="bi bi-people-fill"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">50,000+</div>
                <div class="stat-label">사용자(가 목표입니다)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- 인기 장르 섹션 -->
      <section class="content-section genre-section">
        <div class="section-header">
          <div class="section-badge">
            <i class="bi bi-fire"></i>
            <span>Hot Categories</span>
          </div>
          <h2 class="section-title">
            <span class="title-main">인기 장르</span>
            <span class="title-accent">Popular Genres</span>
          </h2>
          <p class="section-description">
            지금 가장 인기있는 장르들을 만나보세요
          </p>
        </div>

        <div class="genre-grid">
          <div class="row g-4">
            <div v-for="(genre, index) in popularGenres" :key="genre.type" 
                 class="col-lg-3 col-md-4 col-sm-6 col-6">
              <router-link :to="{ name: 'Genre', query: { type: genre.type } }" 
                           class="genre-card">
                <div class="card-background"></div>
                <div class="card-content">
                  <div class="genre-icon-container">
                    <div class="icon-background"></div>
                    <i :class="genre.icon" class="genre-icon"></i>
                  </div>
                  <div class="genre-info">
                    <h3 class="genre-name">{{ genre.name }}</h3>
                    <p class="genre-description">{{ genre.description }}</p>
                  </div>
                  <div class="card-arrow">
                    <i class="bi bi-arrow-right"></i>
                  </div>
                </div>
                <div class="card-glow"></div>
              </router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- 기능 소개 섹션 -->
      <section class="content-section features-section">
        <div class="section-header">
          <div class="section-badge">
            <i class="bi bi-magic"></i>
            <span>Amazing Features</span>
          </div>
          <h2 class="section-title">
            <span class="title-main">FLIXnCHILL의 특별한 기능들</span>
            <span class="title-accent">Discover What Makes Us Special</span>
          </h2>
          <p class="section-description">
            영화 탐색부터 개인화 추천까지, 모든 것이 한 곳에
          </p>
        </div>

        <div class="features-grid">             
          <div class="row g-4">
            <div class="col-lg-4 col-md-6" v-for="(feature, index) in features" :key="index">
              <div class="feature-card">
                <div class="card-background"></div>
                <div class="feature-content">
                  <div class="feature-icon-container">
                    <div class="icon-glow"></div>
                    <i :class="feature.icon" class="feature-icon"></i>
                  </div>
                  
                  <div class="feature-text">
                    <h3 class="feature-title">{{ feature.title }}</h3>
                    <p class="feature-description">{{ feature.description }}</p>
                  </div>
                  
                  <component :is="feature.linkType" :to="feature.link" class="feature-link">
                    <span>{{ feature.linkText }}</span>
                    <i class="bi bi-arrow-right"></i>
                  </component>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 회원가입 유도 섹션 (비로그인 시) -->
      <section v-if="!isLoggedIn" class="content-section promo-section">
        <div class="promo-card">
          <div class="promo-background">
            <div class="promo-pattern"></div>
            <div class="promo-glow"></div>
          </div>
          
          <div class="promo-content">
            
            <h3 class="promo-title">
              FLIXnCHILL의 <span class="text-highlight"><i class="bi bi-person-heart"></i> 모든 기능</span>을<br>
              경험해보세요
            </h3>
            
            <div class="promo-features">
              <div class="promo-feature" v-for="(item, index) in promoFeatures" :key="index">
                <div class="feature-check">
                  <i class="bi bi-check-circle-fill"></i>
                </div>
                <span>{{ item }}</span>
              </div>
            </div>
            
            <div class="promo-actions">
              <router-link :to="{ name: 'Signup' }" class="promo-btn btn-premium">
                <div class="btn-bg"></div>
                <div class="btn-content">
                  <i class="bi bi-star-fill"></i>
                  <span>무료 회원가입</span>
                </div>
              </router-link>
              
              <router-link :to="{ name: 'Login' }" class="promo-btn btn-outline">
                <div class="btn-content">
                  <i class="bi bi-box-arrow-in-right"></i>
                  <span>로그인</span>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- 로그인 사용자 환영 섹션 -->
      <section v-else class="content-section welcome-section">
        <div class="welcome-card">
          <div class="welcome-background"></div>
          
          <div class="welcome-content">
            <div class="welcome-icon">
              <i class="bi bi-emoji-smile-fill"></i>
            </div>
            
            <h3 class="welcome-title">
              환영합니다! <span class="username">
                {{ userStore.userData?.nickname || '영화 애호가' }}</span>님
            </h3>
            
            <p class="welcome-message">
              오늘도 새로운 영화와의 만남을 시작해보세요
            </p>
            
            <div class="welcome-actions">
              <router-link :to="{ name: 'Search' }" class="welcome-btn primary">
                <i class="bi bi-search"></i>
                <span>영화 검색</span>
              </router-link>
              
              <router-link :to="{ name: 'movie-survey' }" class="welcome-btn secondary">
                <i class="bi bi-stars"></i>
                <span>취향 설문</span>
              </router-link>
              
              <router-link v-if="userStore.currentUser?.id" 
                          :to="{ name: 'user-profile', params: { userId: userStore.currentUser.id } }" 
                          class="welcome-btn tertiary">
                <i class="bi bi-person"></i>
                <span>마이페이지</span>
              </router-link>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/accounts'

// UserStore 사용
const userStore = useUserStore()

// 로그인 상태 확인
const isLoggedIn = computed(() => {
  console.log('🔍 로그인 상태 확인:')
  console.log('- userStore.isAuthenticated:', userStore.isAuthenticated)
  console.log('- userStore.token:', userStore.token)
  console.log('- userStore.userData:', userStore.userData)
  console.log('- localStorage token:', localStorage.getItem('token'))
  
  const result = userStore.isAuthenticated
  console.log('🎯 최종 로그인 상태:', result)
  
  return result
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

// 기능 데이터
const features = computed(() => [
  {
    icon: 'bi bi-search',
    title: '스마트 검색',
    description: '원하는 영화를 빠르고 정확하게 찾아보세요',
    linkType: 'router-link',
    link: { name: 'Search' },
    linkText: '검색하기'
  },
  {
    icon: 'bi bi-collection',
    title: '장르별 탐색',
    description: '다양한 장르의 영화들을 쉽게 찾아보세요',
    linkType: 'router-link',
    link: { name: 'Genre' },
    linkText: '탐색하기'
  },
  {
    icon: 'bi bi-person-circle',
    title: '개인 설정',
    description: isLoggedIn.value 
      ? '취향 설문을 통해 더 정확한 영화 추천을 받으세요' 
      : '로그인하고 나만의 영화 취향을 관리하세요',
    linkType: 'router-link',
    link: isLoggedIn.value ? { name: 'movie-survey' } : { name: 'Login' },
    linkText: isLoggedIn.value ? '취향 설문하기' : '로그인하기'
  }
])

// 프로모션 기능 목록
const promoFeatures = ref([
  '개인화된 영화 추천',
  '영화 평점 및 리뷰',
  '취향 분석 서비스',
  '커뮤니티 참여'
])

onMounted(async () => {
  // 페이지 로드 시 UserStore 초기화
  try {
    console.log('🔄 UserStore 초기화 중...')
    const isInitialized = await userStore.initialize()
    console.log('✅ UserStore 초기화 완료:', isInitialized)
    
    // 세션 모니터링 시작
    if (userStore.isAuthenticated) {
      userStore.startSessionMonitoring()
    }
  } catch (error) {
    console.log('⚠️ UserStore 초기화 중 오류:', error)
  }
  
  // 페이지 로드 시 로그인 상태 확인
  console.log('📋 HomePage 로드됨 - 최종 로그인 상태:', isLoggedIn.value)
})
</script>

<style scoped>
/* 기본 애니메이션 정의 */
@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-15px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes glow {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

/* 애니메이션 클래스 */
.animate-fade-up {
  animation: fadeInUp 0.8s ease-out forwards;
}

.animate-fade-up:nth-child(1) { animation-delay: 0.1s; }
.animate-fade-up:nth-child(2) { animation-delay: 0.2s; }
.animate-fade-up:nth-child(3) { animation-delay: 0.3s; }
.animate-fade-up:nth-child(4) { animation-delay: 0.4s; }
.animate-fade-up:nth-child(5) { animation-delay: 0.5s; }

/* 페이지 기본 스타일 */
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #073763 0%, #780909 50%, #073763 100%);
  color: #ffffff;
  padding-top: 76px;
  position: relative;
  overflow-x: hidden;
}

/* 배경 효과 */
.animated-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 8s ease-in-out infinite;
}

.bg-shape-1 {
  width: 200px;
  height: 200px;
  background: linear-gradient(45deg, #db0000, #ff6b6b);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.bg-shape-2 {
  width: 150px;
  height: 150px;
  background: linear-gradient(45deg, #073763, #4dabf7);
  top: 50%;
  right: 20%;
  animation-delay: 3s;
}

.bg-shape-3 {
  width: 180px;
  height: 180px;
  background: linear-gradient(45deg, #780909, #ffa8a8);
  bottom: 20%;
  left: 30%;
  animation-delay: 1.5s;
}

.gradient-mesh {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 20% 30%, rgba(219, 0, 0, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 70% 70%, rgba(7, 55, 99, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 50% 50%, rgba(120, 9, 9, 0.05) 0%, transparent 50%);
}

/* 히어로 섹션 */
.hero-section {
  padding: 6rem 0;
  text-align: center;
  position: relative;
}

.hero-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  padding: 0.75rem 1.5rem;
  margin-bottom: 2.5rem;
  backdrop-filter: blur(10px);
  position: relative;
  opacity: 0;
}

.badge-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #db0000, #073763, #db0000);
  border-radius: 50px;
  z-index: -1;
  opacity: 0.5;
}

.hero-badge i {
  color: #ffd700;
  font-size: 1.1rem;
}

.hero-badge span {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hero-title {
  font-size: 4.5rem;
  font-weight: 800;
  margin-bottom: 2rem;
  line-height: 1.1;
  opacity: 0;
}

.title-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.title-text {
  background: linear-gradient(135deg, #ffffff 0%, #db0000 50%, #ffffff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-decoration i {
  color: #ffd700;
  font-size: 0.8em;
  animation: pulse 2s ease-in-out infinite;
}

.subtitle-line {
  font-size: 0.6em;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
}

.hero-subtitle {
  font-size: 1.4rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 3rem;
  line-height: 1.6;
  opacity: 0;
}

.highlight-text {
  color: #db0000;
  font-weight: 600;
}

.hero-actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-bottom: 4rem;
  flex-wrap: wrap;
  opacity: 0;
}

.hero-btn {
  position: relative;
  padding: 1.2rem 2.5rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  transition: all 0.3s ease;
}

.btn-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-primary .btn-bg {
  background: linear-gradient(135deg, #db0000, #c20000);
}

.btn-primary {
  color: white;
  border: 2px solid rgba(219, 0, 0, 0.3);
}

.btn-primary:hover {
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(219, 0, 0, 0.4);
}

.btn-primary:hover .btn-bg {
  background: linear-gradient(135deg, #ff0000, #db0000);
}

.btn-secondary .btn-bg {
  background: rgba(255, 255, 255, 0.1);
}

.btn-secondary {
  color: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  color: white;
  transform: translateY(-3px);
  border-color: rgba(255, 255, 255, 0.5);
}

.btn-secondary:hover .btn-bg {
  background: rgba(255, 255, 255, 0.2);
}

.btn-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s, height 0.4s;
}

.btn-primary:active .btn-ripple {
  width: 200px;
  height: 200px;
}

.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 3rem;
  opacity: 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.stat-icon {
  width: 50px;
  height: 50px;
  background: rgba(219, 0, 0, 0.2);
  border: 2px solid rgba(219, 0, 0, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #db0000;
  font-size: 1.2rem;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 700;
  color: #db0000;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.2rem;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
}

/* 콘텐츠 섹션 */
.content-section {
  margin-bottom: 6rem;
  position: relative;
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  padding: 0.5rem 1.2rem;
  margin-bottom: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-badge i {
  color: #db0000;
}

.section-title {
  margin-bottom: 1rem;
}

.title-main {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.title-accent {
  display: block;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.section-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* 장르 카드 */
.genre-grid {
  margin-top: 3rem;
}

.genre-card {
  display: block;
  text-decoration: none;
  color: inherit;
  height: 100%;
  position: relative;
  transition: all 0.3s ease;
}

.genre-card .card-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.card-content {
  position: relative;
  z-index: 2;
  padding: 2rem 1.5rem;
  text-align: center;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.genre-icon-container {
  position: relative;
  margin-bottom: 1.5rem;
}

.icon-background {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: rgba(219, 0, 0, 0.2);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.genre-icon {
  font-size: 2.5rem;
  color: #db0000;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.genre-info {
  flex: 1;
  margin-bottom: 1rem;
}

.genre-name {
  font-size: 1.3rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.genre-description {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
  margin: 0;
}

.card-arrow {
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.2rem;
  transition: all 0.3s ease;
  align-self: flex-end;
}

.card-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #db0000, transparent, #db0000);
  border-radius: 22px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.genre-card:hover {
  transform: translateY(-5px);
}

.genre-card:hover .card-background {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(219, 0, 0, 0.3);
}

.genre-card:hover .icon-background {
  background: rgba(219, 0, 0, 0.4);
  transform: translate(-50%, -50%) scale(1.1);
}

.genre-card:hover .genre-icon {
  color: #ffffff;
  transform: scale(1.1);
}

.genre-card:hover .card-arrow {
  color: #db0000;
  transform: translateX(5px);
}

.genre-card:hover .card-glow {
  opacity: 0.6;
}

/* 기능 카드 */
.features-grid {
  margin-top: 3rem;
}

.feature-card {
  height: 100%;
  position: relative;
  transition: all 0.3s ease;
}

.feature-card .card-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-content {
  position: relative;
  z-index: 2;
  padding: 2.5rem 2rem;
  text-align: center;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.feature-icon-container {
  position: relative;
  margin-bottom: 2rem;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(219, 0, 0, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.feature-icon {
  font-size: 3rem;
  color: #db0000;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.feature-text {
  flex: 1;
  margin-bottom: 2rem;
}

.feature-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 1rem;
}

.feature-description {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin: 0;
}

.feature-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #db0000;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  align-self: center;
}

.feature-link:hover {
  color: #ff4757;
  transform: translateX(5px);
}

.feature-card:hover {
  transform: translateY(-8px);
}

.feature-card:hover .card-background {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(219, 0, 0, 0.3);
  box-shadow: 0 20px 40px rgba(219, 0, 0, 0.2);
}

.feature-card:hover .icon-glow {
  opacity: 1;
}

.feature-card:hover .feature-icon {
  color: #ffffff;
  transform: scale(1.1);
}

/* 프로모션 섹션 */
.promo-section {
  margin: 8rem 0;
}

.promo-card {
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 30px;
  padding: 4rem 3rem;
  backdrop-filter: blur(10px);
  overflow: hidden;
}

.promo-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.promo-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(219, 0, 0, 0.05) 0%, transparent 50%);
}

.promo-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(219, 0, 0, 0.1) 0%, transparent 70%);
  filter: blur(100px);
}

.promo-content {
  text-align: center;
  max-width: 700px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.promo-icon {
  position: relative;
  display: inline-block;
  margin-bottom: 2rem;
}

.icon-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  border: 2px solid rgba(219, 0, 0, 0.3);
  border-radius: 50%;
  animation: rotate 10s linear infinite;
}

.promo-icon i {
  font-size: 3.5rem;
  color: #db0000;
  position: relative;
  z-index: 1;
}

.promo-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 2.5rem;
  line-height: 1.3;
}

.text-highlight {
  color: #db0000;
  position: relative;
}

.text-highlight::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #db0000, transparent);
}

.promo-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin: 3rem 0;
}

.promo-feature {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.2rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  transition: all 0.3s ease;
}

.promo-feature:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.feature-check {
  color: #27ae60;
  font-size: 1.3rem;
}

.promo-feature span {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.promo-actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-top: 3rem;
  flex-wrap: wrap;
}

.promo-btn {
  position: relative;
  padding: 1.2rem 2.5rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-premium .btn-bg {
  background: linear-gradient(135deg, #db0000, #c20000);
}

.btn-premium {
  color: white;
  border: 2px solid rgba(219, 0, 0, 0.3);
}

.btn-premium:hover {
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(219, 0, 0, 0.4);
}

.btn-outline {
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-3px);
}

/* 환영 섹션 */
.welcome-section {
  margin: 6rem 0;
}

.welcome-card {
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 25px;
  padding: 3rem 2.5rem;
  backdrop-filter: blur(10px);
  text-align: center;
}

.welcome-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(39, 174, 96, 0.05) 0%, transparent 100%);
  border-radius: 25px;
  z-index: -1;
}

.welcome-content {
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.welcome-icon {
  position: relative;
  display: inline-block;
  margin-bottom: 2rem;
}

.icon-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(39, 174, 96, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.welcome-icon i {
  font-size: 3rem;
  color: #27ae60;
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 1rem;
}

.username {
  color: #27ae60;
  font-weight: 700;
}

.welcome-message {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  margin-bottom: 2.5rem;
  line-height: 1.6;
}

.welcome-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.welcome-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.9rem 1.8rem;
  border-radius: 25px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.welcome-btn.primary {
  background: linear-gradient(135deg, #db0000, #c20000);
  color: white;
  border-color: rgba(219, 0, 0, 0.3);
}

.welcome-btn.primary:hover {
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(219, 0, 0, 0.3);
}

.welcome-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.2);
}

.welcome-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

.welcome-btn.tertiary {
  background: rgba(39, 174, 96, 0.1);
  color: #27ae60;
  border-color: rgba(39, 174, 96, 0.3);
}

.welcome-btn.tertiary:hover {
  background: rgba(39, 174, 96, 0.2);
  color: #27ae60;
  border-color: rgba(39, 174, 96, 0.5);
  transform: translateY(-2px);
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .hero-title {
    font-size: 4rem;
  }
  
  .title-main {
    font-size: 2.2rem;
  }
}

@media (max-width: 992px) {
  .home-page {
    padding-top: 70px;
  }

  .hero-section {
    padding: 5rem 0;
  }

  .hero-title {
    font-size: 3.5rem;
  }

  .title-line {
    flex-direction: column;
    gap: 0.5rem;
  }

  .hero-stats {
    flex-direction: column;
    gap: 2rem;
  }

  .stat-divider {
    width: 80%;
    height: 1px;
  }

  .title-main {
    font-size: 2rem;
  }

  .promo-features {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 4rem 0;
  }

  .hero-title {
    font-size: 3rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .content-section {
    margin-bottom: 5rem;
  }

  .title-main {
    font-size: 1.8rem;
  }

  .card-content,
  .feature-content {
    padding: 2rem 1.5rem;
  }

  .promo-card {
    padding: 3rem 2rem;
  }

  .promo-actions {
    flex-direction: column;
    align-items: center;
  }

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
    font-size: 2.5rem;
  }

  .title-main {
    font-size: 1.6rem;
  }

  .hero-btn,
  .promo-btn {
    padding: 1rem 2rem;
    font-size: 1rem;
  }

  .genre-icon,
  .feature-icon {
    font-size: 2.2rem;
  }

  .card-content,
  .feature-content {
    padding: 1.5rem 1rem;
  }

  .promo-title {
    font-size: 1.8rem;
  }

  .welcome-title {
    font-size: 1.5rem;
  }
}
</style>