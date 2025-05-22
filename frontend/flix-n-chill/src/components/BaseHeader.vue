<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-transparent shadow-sm fixed-top">
    <div class="container">
      <!-- 로고 -->
      <router-link class="navbar-brand fw-bold d-flex align-items-center" to="/">
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
            <router-link class="nav-link" to="/" @click="closeMobileMenu">
              <i class="bi bi-house me-1"></i>Home
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/search" @click="closeMobileMenu">
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
              <li><router-link class="dropdown-item" to="/genre/action" @click="closeAllDropdowns" style="color: lightgrey;">액션</router-link></li>
              <li><router-link class="dropdown-item" to="/genre/comedy" @click="closeAllDropdowns" style="color: lightgrey;">코미디</router-link></li>
              <li><router-link class="dropdown-item" to="/genre/drama" @click="closeAllDropdowns" style="color: lightgrey;">드라마</router-link></li>
              <li><router-link class="dropdown-item" to="/genre/horror" @click="closeAllDropdowns" style="color: lightgrey;">호러</router-link></li>
              <li><router-link class="dropdown-item" to="/genre/adventure" @click="closeAllDropdowns" style="color: lightgrey;">모험</router-link></li>
              <li><router-link class="dropdown-item" to="/genre/family" @click="closeAllDropdowns" style="color: lightgrey;">가족</router-link></li>
              <li><router-link class="dropdown-item" to="/genre/romance" @click="closeAllDropdowns" style="color: lightgrey;">로맨스</router-link></li>
            </ul>
          </li>
          <li class="nav-item" v-if="isLoggedIn">
            <router-link class="nav-link" to="/my-page" @click="closeMobileMenu">
              <i class="bi bi-person me-1"></i>My Page
            </router-link>
          </li>
        </ul>

        <!-- 사용자 영역 -->
        <div class="d-flex align-items-center">
          <!-- 비로그인 상태 -->
          <div v-if="!isLoggedIn" class="d-flex gap-2">
            <router-link to="/login" class="btn btn-sm signin-btn" @click="closeMobileMenu">
              Sign in
            </router-link>
            <router-link to="/signup" class="btn btn-sm signup-btn" @click="closeMobileMenu">
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
                :alt="userName" 
                class="rounded-circle me-2"
                width="32" 
                height="32"
              >
              <span class="text-white fw-medium d-none d-md-inline">{{ userName }}</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end" :class="{ show: isUserDropdownOpen }">
              <li>
                <router-link to="/my-page" class="dropdown-item" @click="closeAllDropdowns">
                  <i class="bi bi-person me-2"></i>My page
                </router-link>
              </li>
              <li>
                <router-link to="/settings" class="dropdown-item" @click="closeAllDropdowns">
                  <i class="bi bi-gear me-2"></i>Settings
                </router-link>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <button @click="logout" class="dropdown-item">
                  <i class="bi bi-box-arrow-right me-2"></i>Logout
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'BaseHeader',
  data() {
    return {
      isMobileMenuOpen: false,
      isGenreDropdownOpen: false,
      isUserDropdownOpen: false,
      // 임시 사용자 데이터 (실제로는 Vuex나 API에서 가져옴)
      isLoggedIn: false,
      userName: '홍혜린',
      userProfileImage: 'https://via.placeholder.com/32x32/db0000/ffffff?text=H'
    }
  },
  methods: {
    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen;
      // 모바일 메뉴 열릴 때 다른 드롭다운 닫기
      if (this.isMobileMenuOpen) {
        this.isGenreDropdownOpen = false;
        this.isUserDropdownOpen = false;
      }
    },
    closeMobileMenu() {
      this.isMobileMenuOpen = false;
    },
    toggleGenreDropdown() {
      this.isGenreDropdownOpen = !this.isGenreDropdownOpen;
      this.isUserDropdownOpen = false; // 다른 드롭다운 닫기
    },
    toggleUserDropdown() {
      this.isUserDropdownOpen = !this.isUserDropdownOpen;
      this.isGenreDropdownOpen = false; // 다른 드롭다운 닫기
    },
    closeAllDropdowns() {
      this.isGenreDropdownOpen = false;
      this.isUserDropdownOpen = false;
      this.isMobileMenuOpen = false;
    },
    logout() {
      this.isLoggedIn = false;
      this.closeAllDropdowns();
      // 실제로는 API 호출하여 로그아웃 처리
      this.$router.push('/');
    },
    // 외부 클릭 시 드롭다운 닫기
    handleClickOutside(event) {
      if (!event.target.closest('.dropdown')) {
        this.isGenreDropdownOpen = false;
        this.isUserDropdownOpen = false;
      }
    }
  },
  mounted() {
    // 외부 클릭 이벤트 리스너 추가
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    // 이벤트 리스너 제거
    document.removeEventListener('click', this.handleClickOutside);
  }
}
</script>

<style scoped>
/* 다크 테마에 맞는 네비게이션 스타일 */

/* 브랜드 로고 스타일 */
.navbar-brand {
  font-size: 1.5rem;
  color: #ffffff !important;
  font-weight: 700;
}

.navbar-brand:hover {
  color: #ffffff !important;
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

.logo-image {
  height: 40px;
  width: auto;
  max-width: 50px;
  object-fit: contain;
}
</style>