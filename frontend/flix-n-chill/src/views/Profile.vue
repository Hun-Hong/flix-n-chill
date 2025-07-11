<template>
  <div class="profile-page" v-if="userProfile">
    <!-- 프로필 헤더 -->
    <div class="profile-header">
      <div class="container">
        <div class="profile-hero">
          <!-- 프로필 이미지 & 기본 정보 -->
          <div class="profile-main-info">
            <div class="profile-avatar-section">
              <div class="avatar-container" @click="handleAvatarClick">
                <img :src="userProfile.profile_image || `/defaultProfileImg.png`" :alt="userProfile.nickname"
                  class="profile-avatar" @error="handleAvatarError">
                <div class="avatar-overlay">
                  <i class="bi bi-camera"></i>
                </div>
              </div>
            </div>

            <div class="profile-info">
              <div class="profile-header-top">
                <h1 class="profile-nickname">{{ userProfile.nickname }}</h1>
              </div>

              <p class="profile-email">{{ userProfile.email }}</p>
              <p v-if="userProfile.profile_bio" class="profile-bio">{{ userProfile.profile_bio }}</p>

              <!-- 팔로우 정보 -->
              <div class="follow-stats">
                <div class="stat-item" @click="openFollowModal('followers')">
                  <span class="stat-number">{{ formatNumber(userProfile.followers_count) }}</span>
                  <span class="stat-label">팔로워</span>
                </div>
                <div class="stat-item" @click="openFollowModal('following')">
                  <span class="stat-number">{{ formatNumber(userProfile.following_count) }}</span>
                  <span class="stat-label">팔로잉</span>
                </div>
                <!-- <div class="stat-item">
                                    <span class="stat-number">{{ formatNumber(userProfile.reviews_count) }}</span>
                                    <span class="stat-label">리뷰</span>
                                </div> -->
              </div>
            </div>
          </div>

          <!-- 프로필 액션 버튼들 -->
          <div class="profile-actions">
            <button v-if="!isOwnProfile" class="btn follow-btn" :class="{ 'following': userProfile.isFollowing }"
              @click="toggleFollow" :disabled="followLoading">
              <div class="btn-content">
                <i :class="userProfile.isFollowing ? 'bi bi-person-check-fill' : 'bi bi-person-plus-fill'"></i>
                <span>{{ userProfile.isFollowing ? '팔로잉' : '팔로우' }}</span>
              </div>
              <div class="btn-hover-content">
                <i class="bi bi-person-dash-fill"></i>
                <span>언팔로우</span>
              </div>
            </button>

            <button v-if="!isOwnProfile" class="btn chat-btn" @click="startChat">
              <i class="bi bi-chat-dots-fill"></i>
              <span>채팅하기</span>
            </button>

            <div class="dropdown">
              <button class="btn btn-outline" @click="toggleDropdown">
                <i class="bi bi-three-dots"></i>
              </button>
              <div class="dropdown-menu" :class="{ 'show': showDropdown }">
                <button class="dropdown-item" @click="reportUser" v-if="!isOwnProfile">
                  <i class="bi bi-flag"></i>
                  신고하기
                </button>
                <button class="dropdown-item" @click="blockUser" v-if="!isOwnProfile">
                  <i class="bi bi-person-slash"></i>
                  차단하기
                </button>
                <button class="dropdown-item" @click="editProfile" v-if="isOwnProfile">
                  <i class="bi bi-pencil"></i>
                  프로필 편집
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 프로필 탭 네비게이션 -->
    <div class="profile-nav">
      <div class="container">
        <div class="nav-tabs">
          <button v-for="tab in tabs" :key="tab.id" class="nav-tab" :class="{ 'active': activeTab === tab.id }"
            @click="setActiveTab(tab.id)">
            <i :class="tab.icon"></i>
            <span>{{ tab.label }}</span>
            <span class="tab-count">{{ tab.count }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 프로필 컨텐츠 -->
    <div class="profile-content">
      <div class="container">
        <!-- 리뷰 탭 -->
        <div v-if="activeTab === 'reviews'" class="tab-content">
          <div class="content-header">
            <h3>
              <i class="bi bi-chat-quote"></i>
              {{ userReviews.length }}개의 리뷰를 남겼어요!
            </h3>
            <div class="sort-options">
              <select v-model="reviewSortBy" class="sort-select">
                <option value="recent">최신순</option>
                <option value="rating">평점순</option>
                <option value="popular">인기순</option>
              </select>
            </div>
          </div>

          <div class="reviews-grid" v-if="userReviews.length > 0">
            <div v-for="review in sortedReviews" :key="review.id" class="review-card" @click="viewReview(review)">
              <div class="review-movie-info">
                <img :src="review.moviePoster || '/api/placeholder/60/90'" :alt="review.movieTitle"
                  class="review-movie-poster">
                <div class="review-movie-details">
                  <h5 class="review-movie-title">{{ review.movieTitle }}</h5>
                  <div class="review-rating">
                    <div class="stars">
                      <i v-for="star in 5" :key="star" class="bi" :class="review.rating >= star
                        ? 'bi-star-fill'                    // 꽉 찬 별
                        : review.rating >= star - 0.5
                          ? 'bi-star-half'                    // 반쪽 별
                          : 'bi-star'                          // 빈 별
                        "></i>
                    </div>
                    <span class="rating-text">{{ review.rating }}/5</span>
                  </div>
                </div>
              </div>

              <div class="review-content">
                <p class="review-text">{{ truncateText(review.content, 150) }}</p>
                <div class="review-meta">
                  <span class="review-date">{{ formatDate(review.createdAt) }}</span>
                  <div class="review-actions">
                    <span class="review-likes">
                      <i class="bi bi-heart"></i>
                      {{ review.likesCount }}
                    </span>
                    <span class="review-comments">
                      <i class="bi bi-chat"></i>
                      {{ review.commentsCount }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <i class="bi bi-chat-quote empty-icon"></i>
            <h4>아직 작성한 리뷰가 없어요</h4>
            <p>좋아하는 영화에 대한 리뷰를 작성해보세요!</p>
          </div>
        </div>

        <!-- 좋아요 탭 -->
        <div v-if="activeTab === 'likes'" class="tab-content">
          <div class="content-header">
            <h3>
              <i class="bi bi-heart-fill"></i>
              {{ likedMovies.length }}개의 영화를 좋아해요!
            </h3>
            <div class="view-options">
              <button class="view-btn" :class="{ 'active': viewMode === 'grid' }" @click="viewMode = 'grid'">
                <i class="bi bi-grid-3x3-gap"></i>
              </button>
              <button class="view-btn" :class="{ 'active': viewMode === 'list' }" @click="viewMode = 'list'">
                <i class="bi bi-list"></i>
              </button>
            </div>
          </div>

          <div v-if="likedMovies.length > 0" class="liked-movies">
            <div class="movies-grid" :class="{ 'list-view': viewMode === 'list' }">
              <div class="row g-4">
                <div v-for="movie in likedMovies" :key="movie.id"
                  :class="viewMode === 'grid' ? 'col-xl-2 col-lg-3 col-md-4 col-sm-6 col-6' : 'col-12'">
                  <MovieCard :movie="movie" :show-details="viewMode === 'list'" @play="handlePlayMovie"
                    @toggle-watchlist="handleToggleWatchlist" @toggle-like="handleToggleLike"
                    @click="handleMovieClick" />
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <i class="bi bi-heart empty-icon"></i>
            <h4>아직 좋아하는 영화가 없어요</h4>
            <p>마음에 드는 영화에 하트를 눌러보세요!</p>
          </div>
        </div>

        <!-- 장르 선호도 탭 -->
        <div v-if="activeTab === 'genres'" class="tab-content">
          <div class="content-header">
            <h3>
              <i class="bi bi-pie-chart-fill"></i>
              나의 장르 선호도
            </h3>
          </div>

          <div v-if="genrePreferences.length > 0" class="genre-preferences">
            <div class="genre-chart">
              <div class="chart-container">
                <div class="genre-bars">
                  <div v-for="genre in genrePreferences" :key="genre.id" class="genre-bar">
                    <div class="genre-info">
                      <span class="genre-name">{{ genre.name }}</span>
                      
                    </div>
                    <div class="bar-container">
                      <div class="bar-fill" :style="{
                        width: genre.percentage + '%',
                        backgroundColor: genre.color
                      }"></div>
                    </div>
                    <span class="genre-percentage">{{ genre.percentage }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="genre-summary">
              <div class="summary-card">
                <i class="bi bi-award-fill"></i>
                <h4>가장 좋아하는 장르</h4>
                <p>{{ genrePreferences[0]?.name || '데이터 없음' }}</p>
              </div>
              <div class="summary-card">
                <i class="bi bi-graph-up"></i>
                <h4>리뷰한 장르 수</h4>
                <p>{{ genrePreferences.length }}개</p>
              </div>
              <div class="summary-card">
                <i class="bi bi-star-fill"></i>
                <h4>평균 평점</h4>
                <p>{{ calculateAverageRating() }}/5</p>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <i class="bi bi-pie-chart empty-icon"></i>
            <h4>장르 선호도 데이터가 없어요</h4>
            <p>더 많은 영화를 좋아요하고 리뷰해서 취향을 분석해보세요!</p>
          </div>
        </div>

        <!-- 추천 유저 탭 -->
        <div v-if="activeTab === 'recommendations'" class="tab-content">
          <div class="content-header">
            <h3>
              <i class="bi bi-people-fill"></i>
              비슷한 취향의 유저들
            </h3>
            <p class="header-subtitle">당신과 비슷한 영화 취향을 가진 사용자들을 추천해드려요!</p>
          </div>

          <div v-if="recommendedUsers.length > 0" class="recommended-users">
            <div class="users-grid">
              <div v-for="user in recommendedUsers" :key="user.id" class="user-recommendation-card">
                <div class="user-header">
                  <div class="user-avatar" @click="goToUserProfile(user.id)">
                    <img :src="user.profile_image || '/defaultProfileImg.png'" :alt="user.nickname" class="avatar-image"
                      @error="handleAvatarError">
                  </div>
                  <div class="user-info">
                    <h4 class="user-nickname" @click="goToUserProfile(user.id)">
                      {{ user.nickname }}
                    </h4>
                    <div class="similarity-score">
                      <i class="bi bi-heart-fill"></i>
                      <span>{{ Math.round(user.similarity_score) }}% 유사</span>
                    </div>
                  </div>
                  <button class="follow-btn-small" :class="{ 'following': user.isFollowing }"
                    @click="toggleRecommendedUserFollow(user.id)">
                    <i :class="user.isFollowing ? 'bi bi-person-check-fill' : 'bi bi-person-plus-fill'"></i>
                    {{ user.isFollowing ? '팔로잉' : '팔로우' }}
                  </button>
                </div>

                <div class="user-stats">
                  <div class="stat">
                    <i class="bi bi-people"></i>
                    <span>{{ formatNumber(user.followers_count) }} 팔로워</span>
                  </div>
                  <div class="stat">
                    <i class="bi bi-chat-quote"></i>
                    <span>{{ formatNumber(user.reviews_count) }} 리뷰</span>
                  </div>
                </div>

                <div class="common-genres">
                  <h5>공통 관심 장르</h5>
                  <div class="genre-tags">
                    <span v-for="genre in user.common_genres.slice(0, 3)" :key="genre" class="genre-tag"
                      :style="{ backgroundColor: getGenreColor(genre) }">
                      {{ genre }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <i class="bi bi-people empty-icon"></i>
            <h4>추천할 유저가 없어요</h4>
            <p>더 많은 영화 활동을 하시면 비슷한 취향의 유저를 찾아드릴게요!</p>
          </div>
        </div>



        <!-- 활동 탭 -->
        <div v-if="activeTab === 'activity'" class="tab-content">
          <div class="content-header">
            <h3>
              <i class="bi bi-activity"></i>
              최근 활동
            </h3>
          </div>

          <div class="activity-timeline">
            <div v-for="activity in userActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="activity.type">
                <i :class="getActivityIcon(activity.type)"></i>
              </div>
              <div class="activity-content">
                <div class="activity-text">{{ activity.text }}</div>
                <div class="activity-time">{{ formatRelativeTime(activity.createdAt) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 모달들 -->
    <EditProfileModal :show="showEditModal" :user-profile="userProfile" @close="showEditModal = false"
      @save="handleProfileSave" />

    <ReviewDetailModal :show="showReviewModal" :review="selectedReview" @close="closeReviewModal"
      @like-toggled="handleReviewLikeToggled" @comment-added="handleCommentAdded" />

    <!-- 🎯 FollowModal 추가 -->
    <FollowModal :is-visible="isFollowModalVisible" :initial-tab="selectedFollowTab" :user-id="userProfile.id"
      @close="closeFollowModal" @follow="handleFollowFromModal" @unfollow="handleUnfollowFromModal" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMovieStore } from '@/stores/movie'
import { useUserStore } from '@/stores/accounts'
import MovieCard from '@/components/MovieCard.vue'
import EditProfileModal from '@/components/EditProfileModal.vue'
import ReviewDetailModal from '@/components/ReviewDetailModal.vue'
import FollowModal from '@/components/FollowModal.vue' // 🎯 FollowModal import
import axios from 'axios'
import { API_CONFIG, getApiUrl, getMediaUrl, API_URLS } from '@/config/api.js'

// 모달 상태
const showEditModal = ref(false)
const showReviewModal = ref(false)
const selectedReview = ref(null)

// 🎯 FollowModal 관련 상태 추가
const isFollowModalVisible = ref(false)
const selectedFollowTab = ref('followers')

// Stores
const movieStore = useMovieStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

// 반응형 데이터
const activeTab = ref('reviews')
const viewMode = ref('grid')
const reviewSortBy = ref('recent')
const followLoading = ref(false)
const showDropdown = ref(false)
const isLoading = ref(false)

const setActiveTab = (tabId) => {
  activeTab.value = tabId
}

// 사용자 프로필 데이터 (실제로는 API에서 가져올 데이터)
const userProfile = ref("")

const setUserData = (data) => {
  userProfile.value = data
}

const fetchRecommendedUsers = async () => {
  try {
    console.log('👥 추천 유저 API 호출 시작...')
    
    const response = await axios({
      method: 'get',
      url: API_URLS.SIMILAR_USERS,
      headers: {
        'Authorization': `Token ${userStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('👥 추천 유저 API 응답:', response.data)
    
    if (response.data.similar_users && response.data.similar_users.length > 0) {
      return response.data.similar_users.map(user => ({
        id: user.id,
        nickname: user.nickname,
        profile_image: user.profile_image,
        similarity_score: user.similarity_score,
        common_genres: user.common_genres || [],
        followers_count: user.followers_count || 0,
        reviews_count: user.reviews_count || 0,
        isFollowing: user.is_following || false
      }))
    }
    
    return []
  } catch (error) {
    console.error('❌ 추천 유저 조회 실패:', error)
    
    return []
  }
}

// Actions - 사용자 정보 가져오기
const fetchUserData = async () => {
  isLoading.value = true
  try {
    console.log('유저 조회 요청 보냄')
    const response = await axios({
      method: 'get',
      url: API_URLS.USER_DETAIL(route.params.userId),
      headers: {
        'Content-Type': 'application/json'
      }
    })

    setUserData(response.data)

    // 🎯 장르 선호도와 추천 유저 데이터 가져오기 (본인 프로필일 때만)
    if (isOwnProfile.value && userStore.token) {
      try {
        console.log('🎯 장르 선호도 및 추천 유저 데이터 로딩 시작...')

        const [genreData, recommendedData] = await Promise.all([
          fetchGenrePreferences(),
          fetchRecommendedUsers()
        ])

        console.log('🎬 장르 선호도 데이터:', genreData)
        console.log('👥 추천 유저 데이터:', recommendedData)

        // 사용자 프로필에 추가 데이터 설정
        userProfile.value.genre_preferences = genreData
        userProfile.value.recommended_users = recommendedData

        console.log('✅ 장르 선호도 및 추천 유저 데이터 로딩 완료')
      } catch (error) {
        console.warn('⚠️ 추가 데이터 로딩 실패:', error)
        // 기본값 설정
        userProfile.value.genre_preferences = []
        userProfile.value.recommended_users = []
      }
    } else {
      // 다른 사용자의 프로필이거나 토큰이 없는 경우 빈 배열 설정
      userProfile.value.genre_preferences = []
      userProfile.value.recommended_users = []
    }

  } catch (error) {
    console.error('사용자 정보 가져오기 실패:', error)
  } finally {
    isLoading.value = false
  }
}

const fetchGenrePreferences = async () => {
  try {
    console.log('🎬 장르 선호도 API 호출 시작...')

    const response = await axios({
      method: 'get',
      url: API_URLS.GENRE_ANALYSIS,
      headers: {
        'Authorization': `Token ${userStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    console.log('🎬 장르 선호도 API 응답:', response.data)

    if (response.data.genre_preferences) {
      // 백엔드 응답을 프론트엔드 형식으로 변환
      const preferences = Object.entries(response.data.genre_preferences).map(([name, rating], index) => ({
        id: index + 1,
        name: name,
        count: Math.round(rating * 10), // 가중치를 개수처럼 표시
        percentage: Math.round((rating / 5) * 100), // 5점 만점을 100%로 변환
        color: getGenreColor(name)
      }))

      console.log('🎬 변환된 장르 선호도:', preferences)

      // 상위 10개만 선택하고 퍼센티지 순으로 정렬
      return preferences
        .sort((a, b) => b.percentage - a.percentage)
        .slice(0, 10)
    }

    return []
  } catch (error) {
    console.error('❌ 장르 선호도 조회 실패:', error)

    // 실패 시 더미 데이터 반환 (테스트용)
    return [
      {
        id: 1,
        name: '액션',
        count: 15,
        percentage: 85,
        color: getGenreColor('액션')
      },
      {
        id: 2,
        name: '드라마',
        count: 12,
        percentage: 70,
        color: getGenreColor('드라마')
      },
      {
        id: 3,
        name: '코미디',
        count: 8,
        percentage: 60,
        color: getGenreColor('코미디')
      }
    ]
  }
}

// 탭 설정
const tabs = computed(() => {
  const baseTabs = [
    {
      id: 'reviews',
      label: '리뷰',
      icon: 'bi bi-chat-quote',
      count: userReviews.value.length
    },
    {
      id: 'likes',
      label: '좋아요',
      icon: 'bi bi-heart-fill',
      count: likedMovies.value.length
    }
  ]

  // 🎯 본인 프로필일 때만 장르 선호도와 추천 유저 탭 추가
  if (isOwnProfile.value) {
    baseTabs.push(
      {
        id: 'genres',
        label: '장르 선호도',
        icon: 'bi bi-pie-chart-fill',
        count: genrePreferences.value.length
      },
      {
        id: 'recommendations',
        label: '추천 유저',
        icon: 'bi bi-people-fill',
        count: recommendedUsers.value.length
      }
    )
  }

  // 활동 탭은 항상 마지막에 추가
  baseTabs.push({
    id: 'activity',
    label: '활동',
    icon: 'bi bi-activity',
    count: userActivities.value.length
  })

  return baseTabs
})


const calculateAverageRating = () => {
  if (userReviews.value.length === 0) return '0.0'

  const total = userReviews.value.reduce((sum, review) => sum + review.rating, 0)
  return (total / userReviews.value.length).toFixed(1)
}


const genrePreferences = computed(() => {
  if (!userProfile.value?.genre_preferences) return []

  return userProfile.value.genre_preferences.map(genre => ({
    id: genre.id,
    name: genre.name,
    percentage: genre.percentage,
    color: getGenreColor(genre.name)
  }))
})

const recommendedUsers = computed(() => {
  if (!userProfile.value?.recommended_users) return []

  return userProfile.value.recommended_users.map(user => ({
    id: user.id,
    nickname: user.nickname,
    profile_image: user.profile_image,
    similarity_score: user.similarity_score,
    common_genres: user.common_genres || [],
    followers_count: user.followers_count || 0,
    reviews_count: user.reviews_count || 0,
    isFollowing: user.isFollowing || user.is_following || false // 두 형식 모두 체크
  }))
})

// 장르별 색상 매핑
const getGenreColor = (genreName) => {
  const colors = {
    // 한국어 장르명
    '액션': '#e74c3c',
    '모험': '#ff5722',
    '애니메이션': '#ff9800',
    '코미디': '#f39c12',
    '범죄': '#95a5a6',
    '다큐멘터리': '#607d8b',
    '드라마': '#3498db',
    '가족': '#4caf50',
    '판타지': '#9b59b6',
    '역사': '#ffc107',
    '공포': '#8e44ad',
    '음악': '#673ab7',
    '미스터리': '#9c27b0',
    '로맨스': '#e91e63',
    'SF': '#1abc9c',
    'TV 영화': '#34495e',
    '스릴러': '#34495e',
    '전쟁': '#795548',
    '서부': '#8bc34a',

    // 영어 장르명 (백엔드에서 영어로 올 수도 있음)
    'Action': '#e74c3c',
    'Adventure': '#ff5722',
    'Animation': '#ff9800',
    'Comedy': '#f39c12',
    'Crime': '#95a5a6',
    'Documentary': '#607d8b',
    'Drama': '#3498db',
    'Family': '#4caf50',
    'Fantasy': '#9b59b6',
    'History': '#ffc107',
    'Horror': '#8e44ad',
    'Music': '#673ab7',
    'Mystery': '#9c27b0',
    'Romance': '#e91e63',
    'Science Fiction': '#1abc9c',
    'TV Movie': '#34495e',
    'Thriller': '#34495e',
    'War': '#795548',
    'Western': '#8bc34a'
  }
  return colors[genreName] || '#6c757d'
}

// 추천 유저 팔로우 토글
const toggleRecommendedUserFollow = async (userId) => {
  try {
    console.log('👥 추천 유저 팔로우 토글 시작:', userId)
    
    const result = await userStore.toggleFollow(userId)
    
    console.log('👥 팔로우 결과:', result)

    // 🎯 userProfile의 recommended_users 배열에서 해당 유저 찾아서 업데이트
    if (userProfile.value.recommended_users) {
      const userIndex = userProfile.value.recommended_users.findIndex(u => u.id === userId)
      if (userIndex !== -1) {
        // 원본 배열 직접 수정
        userProfile.value.recommended_users[userIndex] = {
          ...userProfile.value.recommended_users[userIndex],
          isFollowing: result.is_following,
          is_following: result.is_following, // 백엔드 형식도 함께 업데이트
          followers_count: result.followers_count || userProfile.value.recommended_users[userIndex].followers_count
        }
        
        console.log('✅ 추천 유저 상태 업데이트 완료:', {
          userId,
          isFollowing: result.is_following,
          userIndex
        })
      }
    }

    // 메시지 표시
    const message = result.is_following ? '팔로우했습니다!' : '언팔로우했습니다!'
    console.log(message)

  } catch (error) {
    console.error('❌ 팔로우 오류:', error)
    
    let errorMessage = '팔로우 처리에 실패했습니다.'
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.message) {
      errorMessage = error.message
    }
    
    alert(errorMessage)
  }
}

// 추천 유저 프로필로 이동
const goToUserProfile = (userId) => {
  router.push(`/profile/${userId}`)
}



// 현재 사용자 본인 프로필인지 확인
const isOwnProfile = computed(() => {
  // 실제로는 로그인한 사용자 ID와 비교
  return route.params.userId == userStore.userData.id
})

computed(() => {
  return userProfile.value.reviews
})

// 리뷰 데이터
const userReviews = computed(() => {
  if (!userProfile.value?.reviews) return []

  return userProfile.value.reviews.map(review => ({
    id: review.id,
    movieID: review.movie_id,
    movieTitle: review.movie_title,
    moviePoster: review.poster_path ? `https://image.tmdb.org/t/p/w500${review.poster_path}` : '/api/placeholder/300/450',
    rating: review.rating,
    content: review.comment,
    createdAt: review.created_at,
    commentsCount: 0,
    likesCount: 0,
  }))
})

const handleCommentAdded = (commentData) => {
  try {
    const { reviewId, commentCount } = commentData

    console.log('📝 댓글 개수 업데이트:', { reviewId, commentCount })

    // 🎯 selectedReview 업데이트 (모달이 열려있는 경우)
    if (selectedReview.value && selectedReview.value.id === reviewId) {
      selectedReview.value.commentsCount = commentCount
    }

    // 🎯 userReviews 배열에서도 해당 리뷰의 댓글 개수 업데이트
    const reviewIndex = userReviews.value.findIndex(r => r.id === reviewId)
    if (reviewIndex !== -1) {
      userReviews.value[reviewIndex].commentsCount = commentCount
    }

    console.log('✅ 댓글 개수 업데이트 완료:', commentCount)

  } catch (error) {
    console.error('❌ 댓글 개수 업데이트 실패:', error)
  }
}

const likedMovies = computed(() => {
  if (!userProfile.value?.like_movies) return []

  return userProfile.value.like_movies.map(movie => ({
    id: movie.id,
    title: movie.title || movie.original_title,
    original_title: movie.original_title,
    rating: movie.vote_average || movie.average_rating,
    vote_average: movie.vote_average,
    average_rating: movie.average_rating,
    year: movie.release_date ? new Date(movie.release_date).getFullYear() : null,
    release_date: movie.release_date,
    genre: movie.genres?.[0]?.name || 'Unknown',
    genres: movie.genres || [],
    activities: movie.activities,
    poster: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/api/placeholder/300/450',
    poster_path: movie.poster_path,
    isInWatchlist: false,
    isLiked: movie.is_liked !== undefined ? movie.is_liked : true
  }))
})

const userActivities = computed(() => {
  if (!userProfile.value?.activities) return []

  return userProfile.value.activities.map(activity => ({
    id: activity.id,
    type: activity.action,
    text: activity.text,
    createdAt: activity.created_at,
  }))
})

// 계산된 속성들
const sortedReviews = computed(() => {
  const reviews = [...userReviews.value]

  switch (reviewSortBy.value) {
    case 'rating':
      return reviews.sort((a, b) => b.rating - a.rating)
    case 'popular':
      return reviews.sort((a, b) => b.likesCount - a.likesCount)
    case 'recent':
    default:
      return reviews.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  }
})

// 🎯 FollowModal 관련 메서드들
const openFollowModal = (tab) => {
  console.log('🚀 팔로우 모달 열기:', tab)
  selectedFollowTab.value = tab
  isFollowModalVisible.value = true
}

const closeFollowModal = () => {
  console.log('❌ 팔로우 모달 닫기')
  isFollowModalVisible.value = false
}

const handleFollowFromModal = (user) => {
  console.log('👥 모달에서 팔로우:', user)
  // 팔로우 성공 시 프로필 정보 업데이트
  if (userProfile.value.following_count !== undefined) {
    userProfile.value.following_count++
  }
}

const handleUnfollowFromModal = (user) => {
  console.log('👋 모달에서 언팔로우:', user)
  // 언팔로우 성공 시 프로필 정보 업데이트
  if (userProfile.value.following_count !== undefined && userProfile.value.following_count > 0) {
    userProfile.value.following_count--
  }
}

const closeReviewModal = () => {
  showReviewModal.value = false
  selectedReview.value = null
}

// 메서드들
const handleReviewLikeToggled = async (likeData) => {
  try {
    const { reviewId, currentLiked, review } = likeData

    console.log('🔄 리뷰 좋아요 토글 시작:', { reviewId, currentLiked })

    const result = await movieStore.toggleReviewLike(reviewId, currentLiked)

    if (selectedReview.value && selectedReview.value.id === reviewId) {
      selectedReview.value.isLiked = result.is_liked
      selectedReview.value.likesCount = result.like_count
    }

    const reviewIndex = userReviews.value.findIndex(r => r.id === reviewId)
    if (reviewIndex !== -1) {
      userReviews.value[reviewIndex].isLiked = result.is_liked
      userReviews.value[reviewIndex].likesCount = result.like_count
    }

    console.log('✅ 리뷰 좋아요 토글 성공:', {
      reviewId,
      isLiked: result.is_liked,
      likeCount: result.like_count
    })

  } catch (error) {
    console.error('❌ 리뷰 좋아요 토글 실패:', error)

    let errorMessage = '좋아요 처리에 실패했습니다.'
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.message) {
      errorMessage = error.message
    }

    alert(errorMessage)
  }
}

const toggleFollow = async () => {
  followLoading.value = true

  try {
    const result = await userStore.toggleFollow(route.params.userId)

    userProfile.value.isFollowing = result.is_following
    userProfile.value.followers_count = result.followers_count

    const message = result.is_following ? '팔로우했습니다!' : '언팔로우했습니다!'
    console.log(message)

  } catch (error) {
    console.error('팔로우 오류:', error)

    let errorMessage = '팔로우 처리에 실패했습니다.'
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    }

    alert(errorMessage)

  } finally {
    followLoading.value = false
  }
}

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const reportUser = () => {
  console.log('사용자 신고')
}

const blockUser = () => {
  console.log('사용자 차단')
}

const startChat = async () => {
  try {
    // 로딩 상태 표시
    isLoading.value = true

    // 채팅방 생성 또는 조회 API 호출
    const response = await axios({
      method: 'get',
      url: API_URLS.CHAT_WITH_USER(userProfile.value.id),
      headers: {
        'Authorization': `Token ${userStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    // 채팅방 ID 가져오기
    const roomId = response.data.room_id

    // 채팅방으로 이동
    router.push(`/chat/${roomId}`)

  } catch (error) {
    console.error('채팅방 생성 실패:', error)

    let errorMessage = '채팅방을 생성할 수 없습니다.'
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.response?.status === 401) {
      errorMessage = '로그인이 필요합니다.'
    }

    alert(errorMessage)
  } finally {
    isLoading.value = false
  }
}

const editProfile = () => {
  showEditModal.value = true
}

const handleAvatarClick = () => {
  if (isOwnProfile.value) {
    console.log('프로필 이미지 변경')
  }
}

const handleAvatarError = (event) => {
  event.target.src = '/api/placeholder/200/200'
}

const viewReview = async (review) => {
  try {
    console.log('🔍 리뷰 상세 정보 로딩:', review.id)

    const detailedReview = await movieStore.getReviewDetail(review.id)

    selectedReview.value = {
      id: detailedReview.id,
      movieID: detailedReview.movie.id,
      movieTitle: detailedReview.movie.title,
      moviePoster: detailedReview.movie.poster_path
        ? `https://image.tmdb.org/t/p/w500${detailedReview.movie.poster_path}`
        : '/api/placeholder/100/150',
      rating: detailedReview.rating,
      content: detailedReview.comment,
      createdAt: detailedReview.created_at,
      likesCount: detailedReview.like_count || 0,
      isLiked: detailedReview.is_liked || false,
      reviewer: {
        id: detailedReview.user.id,
        nickname: detailedReview.user.nickname,
        avatar: detailedReview.user.profile_image || '/api/placeholder/50/50'
      }
    }

    showReviewModal.value = true
    console.log('✅ 리뷰 모달 열기 성공:', selectedReview.value)

  } catch (error) {
    console.error('❌ 리뷰 상세 정보 로딩 실패:', error)

    selectedReview.value = {
      ...review,
      likesCount: 0,
      isLiked: false,
      reviewer: {
        id: userProfile.value?.id || 1,
        nickname: userProfile.value?.nickname || '영화리뷰어',
        avatar: userProfile.value?.profile_image || '/api/placeholder/50/50'
      }
    }
    showReviewModal.value = true

    console.warn('⚠️ 리뷰 정보를 불러오는데 실패했지만 기본 정보로 표시합니다.')
  }
}

const handlePlayMovie = (movie) => {
  console.log('영화 재생:', movie.title)
}

const handleToggleLike = (movie) => {
  movieStore.toggleLike(movie.id)

  const likedIndex = likedMovies.value.findIndex(m => m.id === movie.id)
  if (likedIndex !== -1) {
    likedMovies.value.splice(likedIndex, 1)
  }
}

const handleProfileSave = async (updatedData) => {
  const { success, data, error } = await userStore.updateProfile(updatedData)

  if (!success) {
    const msg = error?.message || (typeof error === 'string' ? error : '프로필 업데이트에 실패했습니다.')
    alert(msg)
    return
  }

  userProfile.value = {
    ...userProfile.value,
    ...data
  }

  console.log('프로필이 업데이트되었습니다:', data)
}

const handleMovieClick = (movie) => {
  router.push(`/movies/${movie.id}`)
}

// 유틸리티 함수들
const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatRelativeTime = (dateString) => {
  const now = new Date()
  const date = new Date(dateString)
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    if (diffHours === 0) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return `${diffMinutes}분 전`
    }
    return `${diffHours}시간 전`
  } else if (diffDays === 1) {
    return '어제'
  } else if (diffDays < 7) {
    return `${diffDays}일 전`
  } else {
    return formatDate(dateString)
  }
}

const truncateText = (text, length) => {
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const getActivityIcon = (type) => {
  const icons = {
    created: 'bi bi-chat-quote-fill',
    liked: 'bi bi-heart-fill',
    followed: 'bi bi-person-plus-fill',
  }
  return icons[type] || 'bi bi-circle-fill'
}

// 클릭 외부 감지
const handleClickOutside = (event) => {
  if (!event.target.closest('.dropdown')) {
    showDropdown.value = false
  }
}

// 생명주기
// 🎯 라우트 변경 감지 추가 (새로 추가)
watch(() => route.params.userId, (newUserId, oldUserId) => {
  console.log('🔄 사용자 ID 변경 감지:', { oldUserId, newUserId })

  if (newUserId && newUserId !== oldUserId) {
    console.log('📊 새로운 사용자 데이터 로딩 시작')

    // 이전 데이터 초기화
    userProfile.value = null
    isLoading.value = true

    // 🎯 다른 사용자 프로필로 이동 시 장르/추천 탭에 있다면 리뷰 탭으로 변경
    if (['genres', 'recommendations'].includes(activeTab.value)) {
      activeTab.value = 'reviews'
    }

    // 새로운 사용자 데이터 로드
    fetchUserData()
  }
}, { immediate: false })

// 기존 생명주기 (수정됨)
onMounted(() => {
  console.log('🚀 Profile 컴포넌트 마운트:', route.params.userId)

  if (route.query.tab) {
    activeTab.value = route.query.tab
  }

  // 초기 데이터 로드
  fetchUserData()

  document.addEventListener('click', handleClickOutside)
})

// 탭 변경 시 URL 업데이트 (기존과 동일)
watch(activeTab, (newTab) => {
  router.push({
    path: route.path,
    query: { ...route.query, tab: newTab }
  })
})

// 탭 변경 시 URL 업데이트
watch(activeTab, (newTab) => {
  router.push({
    path: route.path,
    query: { ...route.query, tab: newTab }
  })
})
</script>

<style scoped>
/* 페이지 기본 스타일 */
.profile-page {
  min-height: 100vh;
  padding-top: 76px;
  background: linear-gradient(135deg, #073763 0%, #780909 100%);
  color: #ffffff;
}

/* 프로필 헤더 */
.profile-header {
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 3rem 0;
}

.profile-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

/* 프로필 메인 정보 */
.profile-main-info {
  display: flex;
  gap: 2rem;
  flex: 1;
}

.profile-avatar-section {
  position: relative;
}

.avatar-container {
  position: relative;
  width: 150px;
  height: 150px;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.avatar-container:hover {
  transform: scale(1.05);
  border-color: rgba(255, 255, 255, 0.4);
}

.profile-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-size: 2rem;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.online-status {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 20px;
  height: 20px;
  background: #6c757d;
  border-radius: 50%;
  border: 3px solid #ffffff;
  transition: background-color 0.3s ease;
}

/* 프로필 정보 */
.profile-info {
  flex: 1;
}

.profile-header-top {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.profile-nickname {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #ffffff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.profile-badges {
  display: flex;
  gap: 0.5rem;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.verified-badge {
  background: linear-gradient(135deg, #1e88e5, #1565c0);
  color: white;
}

.premium-badge {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.profile-email {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.profile-bio {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  max-width: 500px;
}

/* 🎯 팔로우 통계 스타일 개선 */
.follow-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(219, 0, 0, 0.3);
  box-shadow: 0 8px 25px rgba(219, 0, 0, 0.2);
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #db0000;
  margin-bottom: 0.2rem;
}

.stat-label {
  display: block;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

/* 프로필 액션 */
.profile-actions {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  overflow: hidden;
}

.follow-btn {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  min-width: 120px;
  justify-content: center;
}

.follow-btn:hover {
  background: linear-gradient(135deg, #c0392b, #a93226);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(231, 76, 60, 0.4);
}

.follow-btn.following {
  background: linear-gradient(135deg, #27ae60, #229954);
}

.follow-btn.following:hover {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.follow-btn .btn-hover-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) translateY(100%);
  opacity: 0;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.follow-btn.following:hover .btn-content {
  transform: translateY(-100%);
  opacity: 0;
}

.follow-btn.following:hover .btn-hover-content {
  transform: translate(-50%, -50%);
  opacity: 1;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 0.75rem;
  width: 48px;
  height: 48px;
  justify-content: center;
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

/* 드롭다운 */
.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(30, 30, 30, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 0.5rem;
  min-width: 150px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  z-index: 1000;
}

.dropdown-menu.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  width: 100%;
  padding: 0.75rem 1rem;
  background: transparent;
  color: white;
  border: none;
  text-align: left;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 프로필 네비게이션 */
.profile-nav {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.75rem 0;
  position: sticky;
  top: 76px;
  z-index: 100;
}

.nav-tabs {
  display: flex;
  gap: 2rem;
  overflow-x: auto;
  justify-content: center;
}

.nav-tab {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  padding: 1rem 2rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  position: relative;
  min-height: 48px;
}

.nav-tab:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.nav-tab.active {
  color: white;
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  transform: translateY(-1px);
  box-shadow: 0 8px 25px rgba(231, 76, 60, 0.3);
}

.tab-count {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 600;
}

.nav-tab.active .tab-count {
  background: rgba(255, 255, 255, 0.3);
}

/* 프로필 콘텐츠 */
.profile-content {
  padding: 3rem 0;
}

.tab-content {
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.content-header h3 {
  font-size: 2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.sort-options,
.view-options {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.sort-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  outline: none;
}

.view-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.7);
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn:hover,
.view-btn.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
}

/* 리뷰 그리드 */
.reviews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 2rem;
}

.review-card {
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.review-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.review-movie-info {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.review-movie-poster {
  width: 60px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
}

.review-movie-details {
  flex: 1;
}

.review-movie-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: white;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars {
  display: flex;
  gap: 0.2rem;
  color: #ffd700;
}

.rating-text {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.review-content {
  margin-top: 1rem;
}

.review-text {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.review-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.review-date {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.review-actions {
  display: flex;
  gap: 1rem;
}

.review-likes,
.review-comments {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 영화 그리드 */
.movies-grid {
  margin-bottom: 2rem;
}

.movies-grid.list-view .row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 5rem;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 1.5rem;
}

.empty-state h4 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: white;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
}

/* 활동 타임라인 */
.activity-timeline {
  max-width: 600px;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.activity-icon.created {
  background: linear-gradient(135deg, #3498db, #2980b9);
}

.activity-icon.liked {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.activity-icon.followed {
  background: linear-gradient(135deg, #27ae60, #229954);
}

.activity-content {
  flex: 1;
  padding-top: 0.5rem;
}

.activity-text {
  color: white;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.activity-time {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .reviews-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 992px) {
  .profile-hero {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .profile-main-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .profile-info {
    text-align: center;
    width: 100%;
  }

  .profile-header-top {
    justify-content: center;
    flex-wrap: wrap;
  }

  .profile-actions {
    width: 100%;
    justify-content: center;
  }

  .follow-stats {
    justify-content: center;
  }

  .reviews-grid {
    grid-template-columns: 1fr;
  }

  .dropdown-menu {
    top: auto;
    bottom: 100%;
    transform: translateY(10px);
  }
}

@media (max-width: 768px) {
  .profile-header {
    padding: 2rem 0;
  }

  .avatar-container {
    width: 120px;
    height: 120px;
  }

  .profile-nickname {
    font-size: 2rem;
  }

  .nav-tabs {
    gap: 1rem;
    padding: 0 1rem;
  }

  .nav-tab {
    padding: 0.75rem 1.5rem;
    font-size: 0.9rem;
    border-radius: 40px;
    min-height: 42px;
  }

  .content-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .content-header h3 {
    font-size: 1.5rem;
  }

  .dropdown {
    z-index: 2000;
  }

  .dropdown-menu {
    top: auto;
    bottom: 100%;
    transform: translateY(10px);
  }

  .dropdown-menu.show {
    transform: translateY(0);
  }

  /* 🎯 모바일에서 팔로우 통계 조정 */
  .follow-stats {
    gap: 1.5rem;
    flex-wrap: wrap;
    justify-content: center;
  }

  .stat-item {
    min-width: 80px;
  }
}

@media (max-width: 576px) {
  .profile-actions {
    flex-direction: column;
    gap: 0.5rem;
  }

  .follow-stats {
    gap: 1rem;
  }

  .stat-number {
    font-size: 1.2rem;
  }

  .review-card {
    padding: 1rem;
  }

  .activity-item {
    padding: 1rem 0;
  }

  .activity-icon {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
}

.genre-preferences {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.genre-chart {
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
}

.genre-bars {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.genre-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.genre-info {
  min-width: 120px;
  text-align: left;
}

.genre-name {
  display: block;
  font-weight: 600;
  color: white;
  font-size: 1rem;
}

.genre-count {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.bar-container {
  flex: 1;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.8s ease;
  position: relative;
}

.bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }

  100% {
    transform: translateX(100%);
  }
}

.genre-percentage {
  min-width: 50px;
  text-align: right;
  font-weight: 600;
  color: white;
}

.genre-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.summary-card {
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
}

.summary-card i {
  font-size: 2.5rem;
  color: #e74c3c;
  margin-bottom: 1rem;
}

.summary-card h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.summary-card p {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e74c3c;
  margin: 0;
}

/* 추천 유저 스타일 */
.recommended-users .header-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  margin-top: 0.5rem;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.user-recommendation-card {
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.user-recommendation-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-avatar {
  cursor: pointer;
}

.avatar-image {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.user-avatar:hover .avatar-image {
  transform: scale(1.1);
  border-color: #e74c3c;
}

.user-info {
  flex: 1;
}

.user-nickname {
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.5rem 0;
  cursor: pointer;
  transition: color 0.3s ease;
}

.user-nickname:hover {
  color: #e74c3c;
}

.similarity-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #e74c3c;
  font-weight: 600;
  font-size: 0.9rem;
}

.follow-btn-small {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.follow-btn-small:hover {
  background: linear-gradient(135deg, #c0392b, #a93226);
  transform: scale(1.05);
}

.follow-btn-small.following {
  background: linear-gradient(135deg, #27ae60, #229954);
}

.follow-btn-small.following:hover {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.user-stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  padding: 1rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.stat i {
  color: #e74c3c;
}

.common-genres h5 {
  color: white;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.8rem;
}

.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.genre-tag {
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}
</style>
