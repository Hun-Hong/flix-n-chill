<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-transparent shadow-sm fixed-top">
    <div class="container">
      <!-- 로고 -->
      <router-link class="navbar-brand fw-bold d-flex align-items-center" :to="{ name: 'Home' }">
        <img src="/flixnchill.png" alt="FLIX n CHILL" class="logo-image me-2">
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
            <ul class="dropdown-menu" :class="{ show: isGenreDropdownOpen }" style="background-color: black;">
              <li v-for="genre in genreList" :key="genre.type">
                <router-link 
                  class="dropdown-item" 
                  :to="{ name: 'Genre', query: { type: genre.type } }" 
                  @click="closeAllDropdowns" 
                  style="color: #FAF8F1;"
                >
                  {{ genre.name }}
                </router-link>
              </li>
            </ul>
          </li>
          <li class="nav-item" v-if="userStore.isAuthenticated">
            <router-link class="nav-link" :to="{ name: 'MyPage' }" @click="closeMobileMenu">
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
              >
              <span class="text-white fw-medium d-none d-md-inline">{{ userStore.userName }}</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end" :class="{ show: isUserDropdownOpen }">
              <li>
                <router-link :to="{ name: 'MyPage' }" class="dropdown-item" @click="closeAllDropdowns">
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

// 사용자 프로필 이미지 계산
const userProfileImage = computed(() => {
  if (userStore.currentUser?.profile_image) {
    return userStore.currentUser.profile_image
  }
  // 기본 프로필 이미지 (사용자 이름 첫 글자 사용)
  const firstLetter = userStore.userName ? userStore.userName.charAt(0).toUpperCase() : 'U'
  return `https://via.placeholder.com/32x32/db0000/ffffff?text=${firstLetter}`
})

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
  
  // 사용자 활동 업데이트
  if (userStore.isAuthenticated) {
    userStore.updateLastActivity()
  }
})

onUnmounted(() => {
  // 이벤트 리스너 제거
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* 기존 네비게이션 스타일 유지 */

/* 브랜드 로고 스타일 */
.navbar-brand {
  font-size: 1.5rem;
  color: #ffffff !important;
  font-weight: 700;
}

.navbar-brand:hover {
  color: #ffffff !important;
}

/* 로고 이미지 스타일 */
.logo-image {
  height: 40px;
  width: auto;
  max-width: 50px;
  object-fit: contain;
}

/* 모든 네비게이션 링크를 흰색으로 */
.navbar-nav .nav-link {
  color: #ffffff !important;
  font-weight: 500;
}

.navbar-nav .nav-link:hover {
  color: #db0000 !important; /* FLIX n CHILL 브랜드 컬러로 호버 */
}

/* active 링크 스타일 */
.nav-link.router-link-active {
  color: #db0000 !important; /* 브랜드 컬러로 활성 상태 표시 */
  font-weight: 600;
}

/* 드롭다운 버튼 스타일 */
.nav-link.dropdown-toggle {
  cursor: pointer;
  color: #ffffff !important;
}

.nav-link.dropdown-toggle:hover {
  color: #db0000 !important;
}

/* 사용자 인증 버튼 스타일 */
.signin-btn {
  background-color: white;
  color: #333333;
  border: 1px solid #ffffff;
  font-weight: 500;
}

.signin-btn:hover {
  background-color: #f8f9fa;
  color: #333333;
}

.signup-btn {
  background-color: #db0000;
  color: white;
  border: 1px solid #db0000;
  font-weight: 500;
}

.signup-btn:hover {
  background-color: #c20000;
  border-color: #c20000;
}

/* 사용자 프로필 버튼 */
.user-profile-btn {
  color: #ffffff !important;
}

.user-profile-btn:hover {
  color: #db0000 !important;
}

/* 사용자 프로필 드롭다운 버튼 */
.dropdown-toggle:focus {
  box-shadow: none;
}

/* 드롭다운 메뉴 스타일 */
.dropdown-menu {
  z-index: 1050;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
}

.dropdown-item {
  color: #333333;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
  color: #db0000;
}

/* 로그아웃 버튼 특별 스타일 */
.logout-btn {
  color: #dc3545 !important;
}

.logout-btn:hover {
  background-color: rgba(220, 53, 69, 0.1) !important;
  color: #dc3545 !important;
}

/* 네비게이션 바 투명도 */
.navbar {
  background: rgba(0, 0, 0, 0.8) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 모바일 토글 버튼 스타일 */
.navbar-toggler {
  border-color: rgba(255, 255, 255, 0.3);
}

.navbar-toggler:focus {
  box-shadow: 0 0 0 0.25rem rgba(255, 255, 255, 0.25);
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba%28255, 255, 255, 0.75%29' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
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

/* 모바일에서 네비게이션 간격 조정 */
@media (max-width: 991.98px) {
  .navbar-nav {
    padding-top: 1rem;
    background-color: rgba(0, 0, 0, 0.9);
    border-radius: 8px;
    margin-top: 1rem;
    padding: 1rem;
  }
  
  .nav-item {
    margin-bottom: 0.5rem;
  }
  
  .d-flex.gap-2 {
    gap: 0.5rem !important;
    margin-top: 1rem;
  }

  /* 모바일에서 드롭다운 메뉴 스타일 */
  .dropdown-menu {
    position: static !important;
    transform: none !important;
    box-shadow: none;
    border: none;
    background-color: rgba(255, 255, 255, 0.1);
    margin-left: 1rem;
  }

  .dropdown-item {
    color: #ffffff;
  }

  .dropdown-item:hover {
    background-color: rgba(219, 0, 0, 0.2);
    color: #ffffff;
  }

  .logout-btn:hover {
    background-color: rgba(220, 53, 69, 0.2) !important;
    color: #dc3545 !important;
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
}

@media (max-width: 480px) {
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