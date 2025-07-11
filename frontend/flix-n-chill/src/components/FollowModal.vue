<template>
  <div v-if="isVisible" class="follow-modal-overlay" @click="closeModal">
    <div class="follow-modal" @click.stop>
      <!-- 모달 헤더 -->
      <div class="modal-header">
        <div class="header-content">
          <h2 class="modal-title">
            <i :class="modalIcon" class="title-icon"></i>
            <span>{{ modalTitle }}</span>
            <span class="count-badge">{{ filteredUsers.length }}</span>
          </h2>

          <!-- 탭 전환 -->
          <div class="tab-switches">
            <button :class="['tab-btn', { active: activeTab === 'followers' }]" @click="switchTab('followers')">
              <i class="bi bi-people-fill"></i>
              <span>팔로워</span>
              <span class="tab-count">{{ followersList.length }}</span>
            </button>
            <button :class="['tab-btn', { active: activeTab === 'following' }]" @click="switchTab('following')">
              <i class="bi bi-person-plus-fill"></i>
              <span>팔로잉</span>
              <span class="tab-count">{{ followingList.length }}</span>
            </button>
          </div>
        </div>

        <button class="close-btn" @click="closeModal">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <!-- 검색 바 -->
      <div class="search-section">
        <div class="search-input-container">
          <i class="bi bi-search search-icon"></i>
          <input v-model="searchQuery" type="text" class="search-input"
            :placeholder="`${activeTab === 'following' ? '팔로잉' : '팔로워'} 검색...`">
          <button v-if="searchQuery" @click="clearSearch" class="clear-btn">
            <i class="bi bi-x-circle-fill"></i>
          </button>
        </div>
      </div>

      <!-- 사용자 목록 -->
      <div class="users-list">
        <div v-if="isLoading" class="loading-section">
          <div class="loading-spinner"></div>
          <p>사용자 목록을 불러오는 중...</p>
        </div>

        <div v-else-if="error" class="error-section">
          <div class="error-icon">
            <i class="bi bi-exclamation-triangle"></i>
          </div>
          <h3>오류가 발생했습니다</h3>
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="loadFollowData">다시 시도</button>
        </div>

        <div v-else-if="filteredUsers.length === 0" class="empty-section">
          <div class="empty-icon">
            <i :class="emptyIcon"></i>
          </div>
          <h3>{{ emptyTitle }}</h3>
          <p>{{ emptyMessage }}</p>
        </div>

        <div v-else class="users-container">
          <div v-for="(user, index) in filteredUsers" :key="user.id" class="user-card"
            :style="{ '--delay': index * 0.05 + 's' }">
            <!-- 프로필 이미지 -->
            <div class="user-avatar-container">
              <div class="avatar-background"></div>
              <img :src="getUserAvatar(user)" :alt="user.nickname" class="user-avatar" @error="handleAvatarError">
              <div class="avatar-ring"></div>
            </div>

            <!-- 사용자 정보 -->
            <div class="user-info">
              <div class="user-main">
                <h3 class="user-nickname">{{ user.nickname || user.username || 'Unknown' }}</h3>
                <div class="user-stats">
                  <div class="stat-item">
                    <i class="bi bi-people-fill"></i>
                    <span>{{ user.followers_count || 0 }}</span>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item">
                    <i class="bi bi-person-plus-fill"></i>
                    <span>{{ user.following_count || 0 }}</span>
                  </div>
                </div>
              </div>

              <div v-if="user.profile_bio" class="user-bio">
                <p>{{ truncateBio(user.profile_bio) }}</p>
              </div>
            </div>

            <!-- 액션 버튼 -->
            <div class="user-actions">
              <!-- 🎯 router-link 대신 button으로 변경하고 클릭 이벤트 처리 -->
              <button class="profile-btn" @click="goToProfile(user)">
                <i class="bi bi-person-circle"></i>
                <span>프로필</span>
              </button>

              <button v-if="canFollowUser(user)" :class="['follow-btn', getFollowButtonClass(user)]"
                @click="toggleFollow(user)" :disabled="isFollowLoading">
                <div class="btn-content">
                  <i :class="getFollowButtonIcon(user)"></i>
                  <span>{{ getFollowButtonText(user) }}</span>
                </div>
                <div class="btn-ripple"></div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 모달 푸터 -->
      <div class="modal-footer">
        <div class="footer-info">
          <span class="result-count">
            {{ searchQuery ? `검색 결과 ${filteredUsers.length}명` : `총 ${filteredUsers.length}명` }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/accounts'
import axios from 'axios'
import { API_CONFIG, getApiUrl, getMediaUrl, API_URLS } from '@/config/api.js'

const router = useRouter()

// Props
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  initialTab: {
    type: String,
    default: 'following',
    validator: (value) => ['following', 'followers'].includes(value)
  },
  userId: {
    type: [String, Number],
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'follow', 'unfollow'])

// Store
const userStore = useUserStore()

// 반응형 데이터
const activeTab = ref(props.initialTab)
const searchQuery = ref('')
const isLoading = ref(false)
const isFollowLoading = ref(false)
const error = ref(null)
const followingList = ref([])
const followersList = ref([])

// 🎯 성능 최적화: 데이터 캐싱
const dataCache = ref(new Map())
const lastLoadedUserId = ref(null)

// Computed
const modalTitle = computed(() => {
  return activeTab.value === 'following' ? '팔로잉 목록' : '팔로워 목록'
})

const modalIcon = computed(() => {
  return activeTab.value === 'following' ? 'bi bi-person-plus-fill' : 'bi bi-people-fill'
})

const filteredUsers = computed(() => {
  const users = activeTab.value === 'following' ? followingList.value : followersList.value

  if (!searchQuery.value.trim()) {
    return users
  }

  const query = searchQuery.value.toLowerCase().trim()
  return users.filter(user =>
    user.nickname?.toLowerCase().includes(query) ||
    user.username?.toLowerCase().includes(query) ||
    user.profile_bio?.toLowerCase().includes(query)
  )
})

const emptyIcon = computed(() => {
  if (searchQuery.value) {
    return 'bi bi-search'
  }
  return activeTab.value === 'following' ? 'bi bi-person-plus' : 'bi bi-people'
})

const emptyTitle = computed(() => {
  if (searchQuery.value) {
    return '검색 결과가 없습니다'
  }
  return activeTab.value === 'following' ? '팔로잉이 없습니다' : '팔로워가 없습니다'
})

const emptyMessage = computed(() => {
  if (searchQuery.value) {
    return '다른 검색어로 시도해보세요'
  }
  return activeTab.value === 'following'
    ? '관심있는 사용자를 팔로우해보세요!'
    : '다른 사용자들이 팔로우하길 기다려보세요!'
})

// Methods
const closeModal = () => {
  emit('close')
}

const switchTab = (tab) => {
  activeTab.value = tab
  clearSearch()
}

const clearSearch = () => {
  searchQuery.value = ''
}

// 🎯 개선된 이미지 처리 함수

// 🎯 개선된 이미지 처리 함수 (기존 getUserAvatar 함수를 이것으로 교체)
const getUserAvatar = (user) => {
  console.log('🖼️ 사용자 이미지 처리:', user.nickname, user.profile_image)
  
  if (!user) {
    console.log('❌ 사용자 데이터 없음, 기본 이미지 사용')
    return '/defaultProfileImg.png'
  }
  
  // 프로필 이미지가 있는 경우
  if (user.profile_image) {
    console.log('✅ 프로필 이미지 존재:', user.profile_image)
    
    // 절대 URL인지 확인
    if (user.profile_image.startsWith('http')) {
      return user.profile_image
    }
    
    // 상대 URL인 경우 베이스 URL 추가
    if (user.profile_image.startsWith('/')) {
      const fullUrl = `${API_CONFIG.BASE_URL}${user.profile_image}`
      console.log('🔗 전체 URL 생성:', fullUrl)
      return fullUrl
    }
    
    // 경로가 media로 시작하지 않는 경우
    const mediaUrl = getMediaUrl(user.profile_image)
    console.log('📁 미디어 URL 생성:', mediaUrl)
    return mediaUrl
  }
  
  // 기본 프로필 이미지
  console.log('🎭 기본 프로필 이미지 사용')
  return '/defaultProfileImg.png'
}

// 🎯 개선된 아바타 에러 처리 (기존 handleAvatarError 함수를 이것으로 교체)
const handleAvatarError = (event) => {
  console.log('🖼️ 프로필 이미지 로드 실패:', event.target.src)
  console.log('🔄 기본 이미지로 대체')
  
  // 첫 번째 대체: 기본 프로필 이미지
  if (event.target.src !== window.location.origin + '/defaultProfileImg.png') {
    event.target.src = '/defaultProfileImg.png'
    return
  }
  
  // 두 번째 대체: placeholder
  console.log('🔄 placeholder 이미지로 대체')
  event.target.src = '/api/placeholder/64/64'
  
  // 더 이상 에러 처리하지 않음
  event.target.onerror = null
}

// 🎯 성능 최적화된 팔로우 데이터 로드
const loadFollowData = async () => {
  const cacheKey = `user_${props.userId}`
  
  // 🎯 캐시된 데이터가 있고, 같은 사용자라면 재사용
  if (dataCache.value.has(cacheKey) && lastLoadedUserId.value === props.userId) {
    console.log('📦 캐시된 데이터 사용:', props.userId)
    const cachedData = dataCache.value.get(cacheKey)
    followingList.value = cachedData.following
    followersList.value = cachedData.followers
    return
  }

  isLoading.value = true
  error.value = null

  try {
    console.log('🔄 팔로우 데이터 로딩 시작:', props.userId)

    const response = await axios({
      method: 'get',
      url: API_URLS.USER_DETAIL(props.userId),
      headers: {
        'Content-Type': 'application/json',
        ...(userStore.token && { 'Authorization': `Token ${userStore.token}` })
      }
    })

    const userData = response.data
    console.log('📊 받은 사용자 데이터:', userData)

    // 🎯 데이터 정규화 (이미지 처리 개선)
    const processedFollowing = (userData.following || []).map(user => ({
      id: user.id,
      username: user.username,
      nickname: user.nickname || user.username,
      profile_image: user.profile_image,
      profile_bio: user.profile_bio || '',
      following_count: user.following_count || 0,
      followers_count: user.followers_count || 0,
      is_following: user.is_following || false
    }))

    const processedFollowers = (userData.followers || []).map(user => ({
      id: user.id,
      username: user.username,
      nickname: user.nickname || user.username,
      profile_image: user.profile_image,
      profile_bio: user.profile_bio || '',
      following_count: user.following_count || 0,
      followers_count: user.followers_count || 0,
      is_following: user.is_following || false
    }))

    // 상태 업데이트
    followingList.value = processedFollowing
    followersList.value = processedFollowers

    // 🎯 캐시에 저장
    dataCache.value.set(cacheKey, {
      following: processedFollowing,
      followers: processedFollowers,
      timestamp: Date.now()
    })
    lastLoadedUserId.value = props.userId

    console.log('✅ 팔로우 데이터 로딩 완료:', {
      following: processedFollowing.length,
      followers: processedFollowers.length
    })

  } catch (error) {
    console.error('❌ 팔로우 데이터 로드 실패:', error)

    let errorMessage = '팔로우 데이터를 불러오는데 실패했습니다.'

    if (error.response?.status === 404) {
      errorMessage = '사용자를 찾을 수 없습니다.'
    } else if (error.response?.status === 401) {
      errorMessage = '로그인이 필요합니다.'
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    }

    error.value = errorMessage
    followingList.value = []
    followersList.value = []

  } finally {
    isLoading.value = false
  }
}

const truncateBio = (bio) => {
  if (!bio) return ''
  return bio.length > 80 ? bio.substring(0, 80) + '...' : bio
}

const canFollowUser = (user) => {
  return user.id !== userStore.currentUser?.id
}

const getFollowButtonClass = (user) => {
  return user.is_following ? 'following' : 'not-following'
}

const getFollowButtonIcon = (user) => {
  return user.is_following ? 'bi bi-person-check-fill' : 'bi bi-person-plus-fill'
}

const getFollowButtonText = (user) => {
  return user.is_following ? '팔로잉' : '팔로우'
}

const goToProfile = (user) => {
  console.log('🔗 프로필 페이지로 이동:', user.nickname, 'userId:', user.id)
  
  // 모달 닫기
  closeModal()
  
  // 프로필 페이지로 이동
  router.push({ 
    name: 'user-profile', 
    params: { userId: user.id } 
  })
}

// 🎯 최적화된 팔로우/언팔로우 (불필요한 데이터 재로딩 제거)
const toggleFollow = async (user) => {
  if (isFollowLoading.value) return

  isFollowLoading.value = true

  try {
    console.log('🔄 팔로우 토글 시작:', user.nickname)

    const result = await userStore.toggleFollow(user.id)

    // 🎯 UI만 업데이트, 전체 데이터 재로딩 안함
    user.is_following = result.is_following
    user.followers_count = result.followers_count || user.followers_count

    // 🎯 캐시 업데이트
    const cacheKey = `user_${props.userId}`
    if (dataCache.value.has(cacheKey)) {
      const cachedData = dataCache.value.get(cacheKey)
      
      // following 목록에서 업데이트
      const followingIndex = cachedData.following.findIndex(u => u.id === user.id)
      if (followingIndex !== -1) {
        cachedData.following[followingIndex] = { ...user }
      }
      
      // followers 목록에서 업데이트
      const followersIndex = cachedData.followers.findIndex(u => u.id === user.id)
      if (followersIndex !== -1) {
        cachedData.followers[followersIndex] = { ...user }
      }
      
      dataCache.value.set(cacheKey, cachedData)
    }

    const message = result.is_following ? `${user.nickname}님을 팔로우했습니다!` : `${user.nickname}님을 언팔로우했습니다!`
    console.log('✅', message)

    // 부모 컴포넌트에 이벤트 전달
    if (result.is_following) {
      emit('follow', user)
    } else {
      emit('unfollow', user)
    }

  } catch (error) {
    console.error('❌ 팔로우 토글 실패:', error)

    let errorMessage = '팔로우 처리에 실패했습니다.'
    if (error.message) {
      errorMessage = error.message
    }

    alert(errorMessage)

  } finally {
    isFollowLoading.value = false
  }
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    closeModal()
  }
}

// 🎯 캐시 정리 함수
const clearCache = () => {
  dataCache.value.clear()
  lastLoadedUserId.value = null
}

// Watchers
watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    console.log('🚀 FollowModal 열림:', props.initialTab)
    activeTab.value = props.initialTab
    loadFollowData()
    document.addEventListener('keydown', handleKeydown)
    document.body.style.overflow = 'hidden'
  } else {
    console.log('❌ FollowModal 닫힘')
    document.removeEventListener('keydown', handleKeydown)
    document.body.style.overflow = ''
    searchQuery.value = ''
    error.value = null
  }
})

watch(() => props.initialTab, (newValue) => {
  activeTab.value = newValue
})

// 🎯 사용자 ID 변경 시에만 새 데이터 로드
watch(() => props.userId, (newValue, oldValue) => {
  if (newValue && newValue !== oldValue && props.isVisible) {
    console.log('👤 사용자 변경:', oldValue, '->', newValue)
    loadFollowData()
  }
})

// Lifecycle
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
  // 🎯 메모리 정리
  clearCache()
})
</script>

<style scoped>
/* 기본 애니메이션 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.05);
  }
}

@keyframes ripple {
  from {
    transform: scale(0);
    opacity: 1;
  }

  to {
    transform: scale(2);
    opacity: 0;
  }
}

/* 모달 오버레이 */
.follow-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
  padding: 2rem;
}

/* 모달 컨테이너 */
.follow-modal {
  background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 25px;
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.4s ease;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6);
}

/* 모달 헤더 */
.modal-header {
  padding: 2rem 2rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.header-content {
  flex: 1;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.8rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 1.5rem;
}

.title-icon {
  color: #db0000;
  font-size: 1.5rem;
}

.count-badge {
  background: rgba(219, 0, 0, 0.2);
  color: #db0000;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 600;
  border: 1px solid rgba(219, 0, 0, 0.3);
}

.tab-switches {
  display: flex;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.3rem;
  border-radius: 15px;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
}

.tab-btn.active {
  background: rgba(219, 0, 0, 0.2);
  color: #db0000;
  border: 1px solid rgba(219, 0, 0, 0.3);
}

.tab-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.tab-count {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 600;
}

.tab-btn.active .tab-count {
  background: rgba(219, 0, 0, 0.3);
  color: #ffffff;
}

.close-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.close-btn:hover {
  background: rgba(219, 0, 0, 0.2);
  color: #db0000;
  transform: scale(1.1);
}

/* 검색 섹션 */
.search-section {
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.1rem;
  z-index: 2;
}

.search-input {
  width: 100%;
  padding: 0.9rem 1rem 0.9rem 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.search-input:focus {
  outline: none;
  border-color: rgba(219, 0, 0, 0.5);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 3px rgba(219, 0, 0, 0.1);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.clear-btn {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  font-size: 1.1rem;
  transition: color 0.3s ease;
}

.clear-btn:hover {
  color: #db0000;
}

/* 사용자 목록 */
.users-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.loading-section,
.error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid #db0000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

.loading-section p,
.error-section p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin: 0;
}

.error-icon {
  font-size: 4rem;
  color: rgba(255, 99, 132, 0.8);
  margin-bottom: 1.5rem;
}

.error-section h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 1rem;
}

.error-section .btn {
  margin-top: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #db0000, #c20000);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.error-section .btn:hover {
  background: linear-gradient(135deg, #ff0000, #db0000);
  transform: translateY(-2px);
}

.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 1.5rem;
}

.empty-section h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.5rem;
}

.empty-section p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 1rem;
  margin: 0;
}

.users-container {
  padding: 0 2rem;
}

/* 사용자 카드 */
.user-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  margin-bottom: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 18px;
  transition: all 0.3s ease;
  animation: slideUp 0.4s ease calc(var(--delay)) both;
}

.user-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(219, 0, 0, 0.2);
  transform: translateY(-2px);
}

.user-card:last-child {
  margin-bottom: 0;
}

/* 아바타 */
.user-avatar-container {
  position: relative;
  flex-shrink: 0;
}

.avatar-background {
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  background: linear-gradient(45deg, #db0000, #073763);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.user-card:hover .avatar-background {
  opacity: 0.6;
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  position: relative;
  z-index: 2;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.avatar-ring {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border: 2px solid transparent;
  border-radius: 50%;
  background: linear-gradient(45deg, #db0000, #073763) border-box;
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.user-card:hover .avatar-ring {
  opacity: 1;
}

/* 사용자 정보 */
.user-info {
  flex: 1;
  min-width: 0;
}

.user-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.user-nickname {
  font-size: 1.2rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  flex-shrink: 0;
}

.user-stats {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.stat-item i {
  color: #db0000;
  font-size: 0.8rem;
}

.stat-divider {
  width: 1px;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
}

.user-bio {
  margin-top: 0.5rem;
}

.user-bio p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}

/* 액션 버튼 */
.user-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

.profile-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.profile-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.follow-btn {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  overflow: hidden;
}

.btn-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  transition: width 0.3s, height 0.3s;
}

.follow-btn:active .btn-ripple {
  width: 100px;
  height: 100px;
}

.follow-btn.not-following {
  background: linear-gradient(135deg, #db0000, #c20000);
  color: white;
}

.follow-btn.not-following:hover {
  background: linear-gradient(135deg, #ff0000, #db0000);
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(219, 0, 0, 0.3);
}

.follow-btn.following {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.follow-btn.following:hover {
  background: rgba(219, 0, 0, 0.1);
  color: #db0000;
  border-color: rgba(219, 0, 0, 0.3);
  transform: translateY(-1px);
}

.follow-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* 모달 푸터 */
.modal-footer {
  padding: 1rem 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.footer-info {
  text-align: center;
}

.result-count {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  font-weight: 500;
}

/* 스크롤바 스타일 */
.users-list::-webkit-scrollbar {
  width: 6px;
}

.users-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.users-list::-webkit-scrollbar-thumb {
  background: rgba(219, 0, 0, 0.3);
  border-radius: 3px;
}

.users-list::-webkit-scrollbar-thumb:hover {
  background: rgba(219, 0, 0, 0.5);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .follow-modal-overlay {
    padding: 1rem;
  }

  .follow-modal {
    max-width: 100%;
    max-height: 90vh;
    border-radius: 20px;
  }

  .modal-header {
    padding: 1.5rem 1.5rem 1rem;
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .header-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .modal-title {
    font-size: 1.5rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0;
  }

  .tab-switches {
    flex-direction: row;
  }

  .tab-btn {
    flex-direction: column;
    gap: 0.3rem;
    padding: 0.8rem 0.5rem;
  }

  .tab-btn span:first-of-type {
    font-size: 0.9rem;
  }

  .close-btn {
    align-self: flex-end;
    margin-top: -3rem;
  }

  .search-section {
    padding: 1rem 1.5rem;
  }

  .users-container {
    padding: 0 1.5rem;
  }

  .user-card {
    padding: 1.2rem;
    gap: 1rem;
  }

  .user-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .user-stats {
    gap: 0.75rem;
  }

  .user-actions {
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }

  .profile-btn,
  .follow-btn {
    justify-content: center;
    padding: 0.7rem;
  }

  .modal-footer {
    padding: 1rem 1.5rem;
  }
}

@media (max-width: 480px) {
  .follow-modal-overlay {
    padding: 0.5rem;
  }

  .modal-header {
    padding: 1rem;
  }

  .modal-title {
    font-size: 1.3rem;
  }

  .search-section,
  .users-container,
  .modal-footer {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .user-card {
    padding: 1rem;
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }

  .user-avatar-container {
    align-self: center;
  }

  .user-info {
    width: 100%;
  }

  .user-actions {
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }

  .profile-btn,
  .follow-btn {
    flex: 1;
  }
}

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 다크모드 최적화 */
@media (prefers-color-scheme: dark) {
  .follow-modal {
    background: linear-gradient(145deg, #0f0f23 0%, #1a1a2e 100%);
  }

  .search-input {
    background: rgba(0, 0, 0, 0.3);
  }

  .user-card {
    background: rgba(0, 0, 0, 0.2);
  }

  .user-card:hover {
    background: rgba(0, 0, 0, 0.4);
  }
}
</style>
