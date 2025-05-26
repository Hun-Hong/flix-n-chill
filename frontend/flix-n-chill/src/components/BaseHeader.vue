<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-transparent shadow-sm fixed-top" :class="{ scrolled: isScrolled }">
    <div class="container">
      <!-- 로고 -->
      <router-link class="navbar-brand fw-bold d-flex align-items-center" :to="{ name: 'Home' }">
        <img src="/flixnchill.png" alt="FLIX n CHILL" class="logo-image me-2" @error="handleImageError">
        <span style="color: #db0000;">FLIXnCHILL</span>
      </router-link>

      <!-- 모바일 토글 버튼 -->
      <button 
        class="navbar-toggler" 
        type="button" 
        @click="toggleMobileMenu"
        :class="{ collapsed: !isMobileMenuOpen }"
        aria-expanded="false" 
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- 메뉴 -->
      <div class="collapse navbar-collapse" :class="{ show: isMobileMenuOpen }">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link" :to="{ name: 'Home' }" @click="closeMobileMenu">
              <i class="bi bi-house me-1"></i>Home
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" :to="{ name: 'Search' }" @click="closeMobileMenu">
              <i class="bi bi-search me-1"></i>Search
            </router-link>
          </li>
          <li class="nav-item dropdown">
            <a 
              class="nav-link dropdown-toggle" 
              href="#"
              @click.prevent="toggleGenreDropdown"
              :aria-expanded="isGenreDropdownOpen"
              role="button"
            >
              <i class="bi bi-collection me-1"></i>Genre
            </a>
            <ul class="dropdown-menu" :class="{ show: isGenreDropdownOpen }">
              <li v-for="genre in genreList" :key="genre.type">
                <router-link 
                  class="dropdown-item" 
                  :to="{ name: 'Genre', query: { type: genre.type } }" 
                  @click="closeAllDropdowns"
                >
                  {{ genre.name }}
                </router-link>
              </li>
            </ul>
          </li>
          <li class="nav-item" v-if="userStore.isAuthenticated">
            <router-link class="nav-link" :to="{ name: 'user-profile', params: {userId: 1} }" @click="closeMobileMenu">
              <i class="bi bi-person me-1"></i>My Page
            </router-link>
          </li>
        </ul>

        <!-- 사용자 영역 -->
        <div class="d-flex align-items-center">
          <!-- 비로그인 상태 -->
          <div v-if="!userStore.isAuthenticated" class="d-flex gap-2">
            <router-link :to="{ name: 'Login' }" class="btn btn-sm signin-btn" @click="closeMobileMenu">
              Sign in
            </router-link>
            <router-link :to="{ name: 'Signup' }" class="btn btn-sm signup-btn" @click="closeMobileMenu">
              Sign up
            </router-link>
          </div>

          <!-- 로그인 상태 -->
          <div v-else class="dropdown">
            <button 
              class="btn btn-link dropdown-toggle d-flex align-items-center text-decoration-none p-0 border-0 user-profile-btn"
              @click="toggleUserDropdown"
              :aria-expanded="isUserDropdownOpen"
            >
              <img 
                :src="userProfileImage" 
                :alt="userStore.userName" 
                class="rounded-circle me-2"
                width="32" 
                height="32"
                @error="handleImageError"
              >
              <span class="text-white fw-medium d-none d-md-inline">{{ userStore.userName }}</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end" :class="{ show: isUserDropdownOpen }">
              <li>
                <router-link :to="{ name: 'user-profile', params: {userId: 1} }" class="dropdown-item" @click="closeAllDropdowns">
                  <i class="bi bi-person me-2"></i>My page
                </router-link>
              </li>
              <li>
                <router-link :to="{ name: 'Settings' }" class="dropdown-item" @click="closeAllDropdowns">
                  <i class="bi bi-gear me-2"></i>Settings
                </router-link>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <button @click="showLogoutModal = true" class="dropdown-item logout-btn">
                  <i class="bi bi-box-arrow-right me-2"></i>Logout
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 로그아웃 확인 모달 -->
    <div v-if="showLogoutModal" class="modal-overlay" @click="showLogoutModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">로그아웃 확인</h2>
          <button class="modal-close-btn" @click="showLogoutModal = false">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="logout-icon">
            <i class="bi bi-box-arrow-right"></i>
          </div>
          <p class="modal-description">
            정말로 로그아웃 하시겠습니까?<br>
            현재 작업 중인 내용이 저장되지 않을 수 있습니다.
          </p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn secondary" @click="showLogoutModal = false">
            취소
          </button>
          <button class="modal-btn primary" @click="handleLogout" :disabled="isLoggingOut">
            <span v-if="isLoggingOut" class="loading-spinner small"></span>
            {{ isLoggingOut ? '로그아웃 중...' : '로그아웃' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 로그아웃 성공 팝업 -->
    <div v-if="showLogoutSuccess" class="popup-overlay" @click="closeSuccessPopup">
      <div class="popup-content" @click.stop>
        <div class="popup-header">
          <div class="success-icon">
            <i class="bi bi-check-circle-fill"></i>
          </div>
          <h2 class="popup-title">로그아웃 완료!</h2>
          <p class="popup-message">
            안전하게 로그아웃되었습니다.<br>
            이용해 주셔서 감사합니다.
          </p>
        </div>
        <div class="popup-actions">
          <button class="popup-btn primary" @click="goToLogin">로그인 페이지로</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/accounts'

// 라우터와 스토어
const router = useRouter()
const userStore = useUserStore()

// 반응형 상태 관리
const isMobileMenuOpen = ref(false)
const isGenreDropdownOpen = ref(false)
const isUserDropdownOpen = ref(false)

// 로그아웃 관련 상태
const showLogoutModal = ref(false)
const showLogoutSuccess = ref(false)
const isLoggingOut = ref(false)

// 스크롤 효과 상태
const isScrolled = ref(false)

// 사용자 프로필 이미지 계산
const userProfileImage = computed(() => {
  // 1. 사용자가 업로드한 프로필 이미지가 있는 경우
  if (userStore.currentUser?.profile_image) {
    // 상대 경로인 경우 절대 경로로 변환
    if (userStore.currentUser.profile_image.startsWith('/')) {
      return `http://127.0.0.1:8000${userStore.currentUser.profile_image}`
    }
    // 이미 절대 경로인 경우 그대로 사용
    if (userStore.currentUser.profile_image.startsWith('http')) {
      return userStore.currentUser.profile_image
    }
    // 상대 경로인 경우 미디어 URL과 결합
    return `http://127.0.0.1:8000/media/${userStore.currentUser.profile_image}`
  }

  const firstLetter = userStore.userName ? userStore.userName.charAt(0).toUpperCase() : 'U'
  const colors = [
    { bg: 'db0000', text: 'ffffff' }, // 브랜드 레드
    { bg: '2563eb', text: 'ffffff' }, // 블루
    { bg: '7c3aed', text: 'ffffff' }, // 바이올렛
    { bg: 'dc2626', text: 'ffffff' }, // 레드
    { bg: 'ea580c', text: 'ffffff' }, // 오렌지
    { bg: '16a34a', text: 'ffffff' }, // 그린
  ]
  
  // 사용자 이름 기반으로 색상 선택 (일관성 유지)
  const userName = userStore.userName || 'User'
  const colorIndex = userName.charCodeAt(0) % colors.length
  const selectedColor = colors[colorIndex]
  
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(firstLetter)}&background=${selectedColor.bg}&color=${selectedColor.text}&size=128&font-size=0.6&bold=true`
})

// 이미지 로드 에러 처리를 위한 함수 추가
const handleImageError = (event) => {
  console.log('프로필 이미지 로드 실패, 기본 이미지로 교체')
  const firstLetter = userStore.userName ? userStore.userName.charAt(0).toUpperCase() : 'U'
  const userName = userStore.userName || 'User'
  const colorIndex = userName.charCodeAt(0) % 6
  const colors = ['db0000', '2563eb', '7c3aed', 'dc2626', 'ea580c', '16a34a']
  const selectedColor = colors[colorIndex]
  
  event.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(firstLetter)}&background=${selectedColor}&color=ffffff&size=128&font-size=0.6&bold=true`
}

// 프로필 이미지 관련 유틸리티 함수들 추가
const getInitials = (name) => {
  if (!name) return 'U'
  
  const words = name.trim().split(' ')
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }
  
  // 두 단어 이상인 경우 첫 글자들 조합
  return words.slice(0, 2).map(word => word.charAt(0).toUpperCase()).join('')
}

const generateAvatarUrl = (name, size = 128) => {
  const initials = getInitials(name)
  const userName = name || 'User'
  const colors = [
    { bg: 'db0000', text: 'ffffff' }, // 브랜드 컬러
    { bg: '2563eb', text: 'ffffff' },
    { bg: '7c3aed', text: 'ffffff' },
    { bg: 'dc2626', text: 'ffffff' },
    { bg: 'ea580c', text: 'ffffff' },
    { bg: '16a34a', text: 'ffffff' },
  ]
  
  const colorIndex = userName.charCodeAt(0) % colors.length
  const selectedColor = colors[colorIndex]
  
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=${selectedColor.bg}&color=${selectedColor.text}&size=${size}&font-size=0.6&bold=true&rounded=true`
}

// 장르 목록
const genreList = [
  { type: 'action', name: '액션' },
  { type: 'comedy', name: '코미디' },
  { type: 'drama', name: '드라마' },
  { type: 'horror', name: '호러' },
  { type: 'adventure', name: '모험' },
  { type: 'family', name: '가족' },
  { type: 'romance', name: '로맨스' }
]

// 스크롤 효과 핸들러
const handleScroll = () => {
  isScrolled.value = window.scrollY > 100
}

// 메뉴 토글 함수들
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
  // 모바일 메뉴 열릴 때 다른 드롭다운 닫기
  if (isMobileMenuOpen.value) {
    isGenreDropdownOpen.value = false
    isUserDropdownOpen.value = false
  }
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

const toggleGenreDropdown = () => {
  isGenreDropdownOpen.value = !isGenreDropdownOpen.value
  isUserDropdownOpen.value = false // 다른 드롭다운 닫기
}

const toggleUserDropdown = () => {
  isUserDropdownOpen.value = !isUserDropdownOpen.value
  isGenreDropdownOpen.value = false // 다른 드롭다운 닫기
}

const closeAllDropdowns = () => {
  isGenreDropdownOpen.value = false
  isUserDropdownOpen.value = false
  isMobileMenuOpen.value = false
}

// 로그아웃 처리 함수
const handleLogout = async () => {
  isLoggingOut.value = true
  closeAllDropdowns()
  
  try {
    // 서버에 로그아웃 요청
    const result = await userStore.logout()
    
    if (result.success) {
      // 모달 닫고 성공 팝업 표시
      showLogoutModal.value = false
      showLogoutSuccess.value = true
      
      if (result.warning) {
        console.warn(result.warning)
      }
    } else {
      console.error('로그아웃 실패:', result.error)
      // 실패해도 클라이언트 정리는 완료된 상태이므로 성공 팝업 표시
      showLogoutModal.value = false
      showLogoutSuccess.value = true
    }
  } catch (error) {
    console.error('로그아웃 처리 중 오류:', error)
    // 오류가 발생해도 사용자에게는 성공 메시지 표시
    showLogoutModal.value = false
    showLogoutSuccess.value = true
  } finally {
    isLoggingOut.value = false
  }
}

// 성공 팝업 닫기
const closeSuccessPopup = () => {
  showLogoutSuccess.value = false
  goToLogin()
}

// 로그인 페이지로 이동
const goToLogin = () => {
  showLogoutSuccess.value = false
  router.push({ name: 'Login' })
}

// 외부 클릭 시 드롭다운 닫기
const handleClickOutside = (event) => {
  if (!event.target.closest('.dropdown')) {
    isGenreDropdownOpen.value = false
    isUserDropdownOpen.value = false
  }
}

// 라이프사이클 훅
onMounted(() => {
  // 외부 클릭 이벤트 리스너 추가
  document.addEventListener('click', handleClickOutside)
  // 스크롤 이벤트 리스너 추가
  window.addEventListener('scroll', handleScroll)
  
  // 사용자 활동 업데이트
  if (userStore.isAuthenticated) {
    userStore.updateLastActivity()
  }
})

onUnmounted(() => {
  // 이벤트 리스너 제거
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 🌟 GLASS MORPHISM NAVBAR WITH EPIC ANIMATIONS 🌟 */
.navbar {
  background: linear-gradient(135deg, 
    rgba(0, 0, 0, 0.9) 0%, 
    rgba(219, 0, 0, 0.15) 30%, 
    rgba(0, 0, 0, 0.9) 100%) !important;
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(219, 0, 0, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.37),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: visible !important;
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: 1050 !important;
}

/* 🎭 FLOATING PARTICLES BACKGROUND */
.navbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(219, 0, 0, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(219, 0, 0, 0.08) 0%, transparent 50%);
  /* animation: particleFloat 8s ease-in-out infinite alternate; */
  pointer-events: none;
}

@keyframes particleFloat {
  0% { 
    opacity: 0.6;
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: translateY(-10px) rotate(180deg);
  }
  100% { 
    opacity: 0.8;
    transform: translateY(-5px) rotate(360deg);
  }
}

/* 🚀 BRAND LOGO WITH HOLOGRAPHIC EFFECT */
.navbar-brand {
  font-size: 1.8rem !important;
  font-weight: 800 !important;
  background: linear-gradient(
    45deg,
    #ff0000,
    #ff4444,
    #ff0000,
    #cc0000,
    #ff0000
  );
  background-size: 400% 400%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: holographicShine 3s ease-in-out infinite;
  text-shadow: 0 0 30px rgba(219, 0, 0, 0.5);
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.navbar-brand:hover {
  transform: scale(1.05) rotateY(5deg);
  filter: brightness(1.2) saturate(1.3);
}

@keyframes holographicShine {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* 💎 LOGO IMAGE WITH CYBER GLOW */
.logo-image {
  height: 45px;
  width: auto;
  max-width: 55px;
  filter: 
    drop-shadow(0 0 10px rgba(219, 0, 0, 0.6))
    drop-shadow(0 0 20px rgba(219, 0, 0, 0.4))
    brightness(1.1)
    contrast(1.2);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: logoFloat 4s ease-in-out infinite;
}

.navbar-brand:hover .logo-image {
  transform: rotate(5deg) scale(1.1);
  filter: 
    drop-shadow(0 0 15px rgba(219, 0, 0, 0.8))
    drop-shadow(0 0 30px rgba(219, 0, 0, 0.6))
    brightness(1.3)
    contrast(1.4);
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-3px) rotate(2deg); }
}

/* ⚡ CYBER NAV LINKS WITH NEON EFFECTS - 간격 넓히기 */
.navbar-nav {
  gap: 2rem; /* 메뉴 간격을 2rem으로 넓힘 */
  display: flex; 
  overflow: visible;
}

.navbar-nav .nav-link {
  color: #ffffff !important;
  font-weight: 600 !important;
  position: relative;
  padding: 0.8rem 1.5rem !important; /* 클릭 영역도 넓게 */
  border-radius: 25px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
  overflow: hidden;
  white-space: nowrap; /* 텍스트 줄바꿈 방지 */
}

.navbar-nav .nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(219, 0, 0, 0.3),
    transparent
  );
  transition: left 0.5s ease;
}

.navbar-nav .nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #ff0000, #ff4444, #ff0000);
  transform: translateX(-50%);
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.navbar-nav .nav-link:hover {
  color: #ffffff !important;
  background: rgba(219, 0, 0, 0.2);
  box-shadow: 
    0 0 20px rgba(219, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transform: translateY(-2px) scale(1.05);
}

.navbar-nav .nav-link:hover::before {
  left: 100%;
}

.navbar-nav .nav-link:hover::after {
  width: 80%;
}

/* 🎯 ACTIVE LINK WITH SPECIAL GLOW */
.nav-link.router-link-active {
  background: linear-gradient(135deg, 
    rgba(219, 0, 0, 0.3), 
    rgba(255, 68, 68, 0.2)) !important;
  box-shadow: 
    0 0 25px rgba(219, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(219, 0, 0, 0.5);
  color: #ffffff !important;
  font-weight: 700 !important;
}

.nav-link.router-link-active::after {
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #ff0000, #ff6666, #ff0000);
  animation: activeGlow 2s ease-in-out infinite alternate;
}

@keyframes activeGlow {
  0% { box-shadow: 0 0 5px rgba(219, 0, 0, 0.8); }
  100% { box-shadow: 0 0 20px rgba(219, 0, 0, 1); }
}

/* 🔧 드롭다운 컨테이너 기본 설정 */
.nav-item.dropdown {
  position: relative; /* 매우 중요! 부모 위치 기준점 */
}

/* 🎭 EPIC DROPDOWN WITH MATRIX EFFECTS - 가려짐 문제 해결 */
.dropdown-menu {
  background: linear-gradient(135deg, 
    rgba(0, 0, 0, 0.89) 0%,    /* 🎯 0.95 → 0.98로 변경 (더 불투명) */
    rgba(61, 24, 65, 0.9) 50%,  /* 🎯 0.1 → 0.2로 변경 (빨간색 더 진하게) */
    rgba(0, 0, 0, 0.95) 100%   /* 🎯 0.95 → 0.98로 변경 (더 불투명) */
  ) !important;
  backdrop-filter: blur(20px) saturate(150%);
  border: 1px solid rgba(219, 0, 0, 0.5) !important; /* 🎯 테두리도 더 진하게 */
  border-radius: 15px !important;
  box-shadow: 
    0 15px 35px rgba(0, 0, 0, 0.7),    /* 🎯 그림자도 더 진하게 */
    0 5px 15px rgba(219, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.15); /* 🎯 내부 하이라이트도 더 밝게 */
  padding: 1rem !important;
  animation: dropdownSlide 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  
  position: absolute !important;
  z-index: 9999 !important;
  top: calc(100% + 0.25rem) !important;
  left: 0 !important;
  min-width: 200px !important;
  max-width: 300px !important;
  margin: 0 !important;
  overflow: visible !important;
  transform: none !important;
  will-change: transform, opacity;
}

.dropdown-menu::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(219, 0, 0, 0.8) 50%, 
    transparent 100%);
}

/* 드롭다운이 보이는 상태일 때 강제 표시 */
.dropdown-menu.show {
  display: block !important;
  opacity: 1 !important;
  visibility: visible !important;
  pointer-events: auto !important;
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
    visibility: hidden;
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
    visibility: visible;
  }
}

.dropdown-item {
  color: rgba(255, 255, 255, 0.9) !important;
  padding: 0.8rem 1.2rem !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  position: relative;
  overflow: hidden;
  white-space: nowrap; /* 텍스트 줄바꿈 방지 */
}

.dropdown-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(219, 0, 0, 0.2), 
    transparent);
  transition: left 0.4s ease;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, 
    rgba(219, 0, 0, 0.2), 
    rgba(255, 68, 68, 0.1)) !important;
  color: #ffffff !important;
  transform: translateX(5px) scale(1.02);
  box-shadow: 0 5px 15px rgba(219, 0, 0, 0.3);
}

.dropdown-item:hover::before {
  left: 100%;
}

/* 드롭다운 토글 버튼 개선 */
.nav-link.dropdown-toggle {
  position: relative;
}

.nav-link.dropdown-toggle::after {
  transition: transform 0.3s ease;
  margin-left: 0.5rem;
}

.nav-link.dropdown-toggle[aria-expanded="true"]::after {
  transform: rotate(180deg);
}

/* 🔥 CYBER BUTTONS WITH HOLOGRAPHIC EFFECTS */
.signin-btn {
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.9), 
    rgba(255, 255, 255, 0.8)) !important;
  color: #000000 !important;
  border: 2px solid rgba(255, 255, 255, 0.8) !important;
  font-weight: 600 !important;
  border-radius: 25px !important;
  padding: 0.6rem 1.5rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.signin-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.3), 
    transparent);
  transition: left 0.5s ease;
}

.signin-btn:hover {
  background: linear-gradient(135deg, #ffffff, #f8f9fa) !important;
  color: #000000 !important;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 
    0 10px 25px rgba(255, 255, 255, 0.2),
    0 0 20px rgba(255, 255, 255, 0.1);
}

.signin-btn:hover::before {
  left: 100%;
}

.signup-btn {
  background: linear-gradient(135deg, #ff0000, #cc0000) !important;
  color: white !important;
  border: 2px solid rgba(219, 0, 0, 0.8) !important;
  font-weight: 600 !important;
  border-radius: 25px !important;
  padding: 0.6rem 1.5rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(219, 0, 0, 0.3);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.signup-btn::before {
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

.signup-btn:hover {
  background: linear-gradient(135deg, #ff2222, #e60000) !important;
  border-color: rgba(255, 68, 68, 0.9) !important;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 
    0 15px 35px rgba(219, 0, 0, 0.4),
    0 0 30px rgba(219, 0, 0, 0.6);
}

.signup-btn:hover::before {
  left: 100%;
}

/* 👤 CYBER USER PROFILE WITH MATRIX VIBES */
.user-profile-btn {
  color: #ffffff !important;
  padding: 0.5rem 1rem !important;
  border-radius: 50px !important;
  background: rgba(255, 255, 255, 0.05) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.user-profile-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgba(219, 0, 0, 0.1), 
    transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.user-profile-btn:hover {
  background: rgba(219, 0, 0, 0.2) !important;
  border-color: rgba(219, 0, 0, 0.5) !important;
  transform: scale(1.05);
  box-shadow: 0 0 25px rgba(219, 0, 0, 0.3);
}

.user-profile-btn:hover::before {
  opacity: 1;
}

/* 🖼️ PROFILE IMAGE WITH CYBER RING */
.user-profile-btn img {
  border: 2px solid rgba(219, 0, 0, 0.5);
  transition: all 0.3s ease;
  box-shadow: 0 0 15px rgba(219, 0, 0, 0.3);
}

.user-profile-btn:hover img {
  border-color: rgba(219, 0, 0, 0.8);
  box-shadow: 
    0 0 25px rgba(219, 0, 0, 0.6),
    inset 0 0 10px rgba(219, 0, 0, 0.2);
  transform: scale(1.1);
}

/* 🌟 MOBILE TOGGLER WITH CYBER EFFECTS */
.navbar-toggler {
  border: 2px solid rgba(219, 0, 0, 0.5) !important;
  border-radius: 8px !important;
  padding: 0.5rem !important;
  background: rgba(0, 0, 0, 0.5) !important;
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.navbar-toggler:hover {
  border-color: rgba(219, 0, 0, 0.8) !important;
  background: rgba(219, 0, 0, 0.2) !important;
  box-shadow: 0 0 20px rgba(219, 0, 0, 0.4);
  transform: scale(1.1);
}

.navbar-toggler:focus {
  box-shadow: 0 0 0 0.25rem rgba(219, 0, 0, 0.5) !important;
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba%28255, 255, 255, 0.85%29' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

/* 🎯 SCROLL EFFECTS */
.navbar.scrolled {
  background: linear-gradient(135deg, 
    rgba(0, 0, 0, 0.98) 0%, 
    rgba(219, 0, 0, 0.08) 30%, 
    rgba(0, 0, 0, 0.98) 100%) !important;
  backdrop-filter: blur(25px) saturate(200%);
  box-shadow: 
    0 12px 40px rgba(0, 0, 0, 0.5),
    0 0 60px rgba(219, 0, 0, 0.2);
}

/* ✨ SPECIAL EFFECTS FOR EPIC FEEL */
.navbar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(219, 0, 0, 0.03) 25%,
    rgba(255, 255, 255, 0.02) 50%,
    rgba(219, 0, 0, 0.03) 75%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: scanline 4s linear infinite;
  pointer-events: none;
}

@keyframes scanline {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* 컨테이너 오버플로우 방지 */
.navbar .container {
  overflow: visible;
}

/* 화면 경계 처리 - 드롭다운이 화면 밖으로 나가지 않도록 */
@media (max-width: 1200px) {
  .navbar-nav {
    gap: 1.5rem; /* 중간 크기 화면에서는 간격 줄임 */
  }
  
  .dropdown-menu {
    right: 0 !important;
    left: auto !important;
  }
}

/* 🎨 ENHANCED MOBILE STYLES */
@media (max-width: 991.98px) {
  .navbar-nav {
    background: linear-gradient(135deg, 
      rgba(0, 0, 0, 0.95) 0%, 
      rgba(219, 0, 0, 0.1) 50%,
      rgba(0, 0, 0, 0.95) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(219, 0, 0, 0.3);
    border-radius: 15px;
    margin-top: 1rem;
    padding: 2rem 1.5rem;
    box-shadow: 
      0 15px 35px rgba(0, 0, 0, 0.5),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    animation: mobileMenuSlide 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    gap: 1rem; /* 모바일에서는 간격 줄임 */
  }

  @keyframes mobileMenuSlide {
    from {
      opacity: 0;
      transform: translateY(-30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .nav-item {
    margin-bottom: 1rem;
    flex-shrink: 0;
  }

  .navbar-nav .nav-link {
    padding: 1rem 1.5rem !important;
    margin-bottom: 0.5rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .navbar-nav .nav-link:hover {
    background: rgba(219, 0, 0, 0.3);
    border-color: rgba(219, 0, 0, 0.5);
  }

  /* 모바일에서 드롭다운 메뉴 스타일 */
  .dropdown-menu {
    position: static !important;
    transform: none !important;
    box-shadow: 
      0 10px 25px rgba(0, 0, 0, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(219, 0, 0, 0.3) !important;
    background: linear-gradient(135deg, 
      rgba(0, 0, 0, 0.9) 0%, 
      rgba(219, 0, 0, 0.15) 50%,
      rgba(0, 0, 0, 0.9) 100%) !important;
    margin-left: 1rem;
    margin-top: 0.5rem;
    border-radius: 10px !important;
    z-index: auto;
  }

  .dropdown-item {
    color: #ffffff !important;
  }

  .dropdown-item:hover {
    background: rgba(219, 0, 0, 0.2) !important;
    color: #ffffff !important;
  }

  .d-flex.gap-2 {
    gap: 0.5rem !important;
    margin-top: 1rem;
  }
}

/* 로그아웃 버튼 특별 스타일 */
.logout-btn {
  color: #dc3545 !important;
}

.logout-btn:hover {
  background-color: rgba(220, 53, 69, 0.1) !important;
  color: #dc3545 !important;
}

/* 로그아웃 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(15px);
  animation: fadeIn 0.3s ease-out;
  padding: 2rem 1rem;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  max-width: 450px;
  width: 100%;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(30px);
  box-shadow:
    0 30px 80px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  position: relative;
  animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
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

.modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(219, 0, 0, 0.8) 50%,
    transparent 100%);
  border-radius: 20px 20px 0 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2.5rem 1rem 2.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.modal-title {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #ffffff 0%, #e8e8e8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.modal-close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2rem;
}

.modal-close-btn:hover {
  background: rgba(219, 0, 0, 0.2);
  color: rgba(219, 0, 0, 0.9);
  transform: scale(1.1);
}

.modal-body {
  padding: 1.5rem 2.5rem;
  text-align: center;
}

.logout-icon {
  font-size: 3rem;
  color: rgba(219, 0, 0, 0.8);
  margin-bottom: 1.5rem;
  animation: pulse 2s ease-in-out infinite alternate;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(1.05); opacity: 1; }
}

.modal-description {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0;
  font-size: 0.95rem;
}

.modal-footer {
  padding: 1rem 2.5rem 2rem 2.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  flex-shrink: 0;
}

.modal-btn {
  padding: 0.8rem 1.8rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.modal-btn.primary {
  background: linear-gradient(135deg, #db0000, #c20000);
  color: white;
}

.modal-btn.primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.modal-btn.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #e60000, #d40000);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(219, 0, 0, 0.4);
}

.modal-btn.primary:hover:not(:disabled)::before {
  left: 100%;
}

.modal-btn.primary:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.4);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.modal-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner.small {
  width: 14px;
  height: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 성공 팝업 스타일 */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(15px);
  animation: fadeIn 0.3s ease-out;
}

.popup-content {
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 3rem 2.5rem;
  max-width: 400px;
  width: 90%;
  text-align: center;
  backdrop-filter: blur(30px);
  box-shadow:
    0 30px 80px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  position: relative;
  animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.popup-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(75, 192, 192, 0.8) 50%,
    transparent 100%);
  border-radius: 20px 20px 0 0;
}

.popup-header {
  margin-bottom: 2rem;
}

.success-icon {
  font-size: 4rem;
  color: #2ed573;
  margin-bottom: 1.5rem;
  animation: bounce 0.6s ease-out;
}

@keyframes bounce {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.popup-title {
  color: #ffffff;
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #ffffff 0%, #e8e8e8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.popup-message {
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
  margin: 0;
  font-size: 1rem;
}

.popup-actions {
  display: flex;
  justify-content: center;
}

.popup-btn {
  padding: 0.9rem 2rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  min-width: 120px;
}

.popup-btn.primary {
  background: linear-gradient(135deg, #db0000, #c20000);
  color: white;
}

.popup-btn.primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.popup-btn.primary:hover {
  background: linear-gradient(135deg, #e60000, #d40000);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(219, 0, 0, 0.4);
}

.popup-btn.primary:hover::before {
  left: 100%;
}

/* 🎪 ULTRA RESPONSIVE DESIGN */
@media (max-width: 768px) {
  .navbar-brand {
    font-size: 1.5rem !important;
  }
  
  .logo-image {
    height: 35px;
  }
  
  .signin-btn, .signup-btn {
    padding: 0.5rem 1rem !important;
    font-size: 0.8rem;
  }

  /* 모바일에서 모달 조정 */
  .modal-content {
    margin: 1rem;
    max-width: none;
  }

  .modal-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }

  .modal-body {
    padding: 1rem 1.5rem;
  }

  .modal-footer {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
    flex-direction: column;
  }

  .modal-btn {
    width: 100%;
  }

  .popup-content {
    padding: 2rem 1.5rem;
  }

  .logout-btn:hover {
    background-color: rgba(220, 53, 69, 0.2) !important;
    color: #dc3545 !important;
  }
}

@media (max-width: 480px) {
  .navbar-brand {
    font-size: 1.3rem !important;
  }
  
  .logo-image {
    height: 30px;
  }
  
  .navbar-nav .nav-link {
    font-size: 0.8rem;
    padding: 0.8rem 1rem !important;
  }

  .modal-content {
    margin: 0.5rem;
  }

  .logout-icon {
    font-size: 2.5rem;
  }

  .success-icon {
    font-size: 3.5rem;
  }

  .popup-title {
    font-size: 1.4rem;
  }

  .modal-title {
    font-size: 1.3rem;
  }
}

/* 🌈 ACCESSIBILITY WITH STYLE */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.5s !important;
    transition-duration: 0.3s !important;
  }
}

/* 🎨 HIGH CONTRAST MODE */
@media (prefers-contrast: high) {
  .navbar {
    background: rgba(0, 0, 0, 1) !important;
    border-bottom: 3px solid #ff0000;
  }
  
  .navbar-nav .nav-link {
    border: 2px solid rgba(255, 255, 255, 0.3);
  }
  
  .navbar-nav .nav-link:hover {
    border-color: #ff0000;
  }
}

/* 포커스 스타일 */
.modal-btn:focus-visible,
.popup-btn:focus-visible,
.modal-close-btn:focus-visible {
  outline: 2px solid rgba(219, 0, 0, 0.8);
  outline-offset: 2px;
}

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>