// stores/accounts.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  // 상태 관리
  const token = ref(localStorage.getItem('token') || null)
  const userData = ref(JSON.parse(localStorage.getItem('userData') || 'null'))
  const isLoading = ref(false)
  const lastActivity = ref(Date.now())

  const BE_API_PATH = "http://127.0.0.1:8000/"

  // Computed - 로그인 상태 확인
  const isAuthenticated = computed(() => {
    return !!token.value && !!userData.value
  })

  // Computed - 사용자 정보 가져오기
  const currentUser = computed(() => {
    return userData.value || null
  })

  // Computed - 사용자 이름 (이메일에서 추출)
  const userName = computed(() => {
    if (userData.value?.email) {
      return userData.value.email.split('@')[0]
    }
    return '사용자'
  })

  // Actions - 토큰 설정
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)

    // Axios 기본 헤더 설정
    axios.defaults.headers.common['Authorization'] = `Token ${newToken}`

    // 사용자 정보 가져오기
    fetchUserData()
  }

  // Actions - 사용자 데이터 설정
  const setUserData = (data) => {
    userData.value = data
    localStorage.setItem('userData', JSON.stringify(data))
    updateLastActivity()
  }

  // Actions - 사용자 정보 가져오기
  const fetchUserData = async () => {
    if (!token.value) return

    isLoading.value = true
    try {
      console.log('유저 요청 보냄')
      const response = await axios({
        method: 'get',
        url: 'http://127.0.0.1:8000/accounts/user/',
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        }
      })


      setUserData(response.data)
    } catch (error) {
      console.error('사용자 정보 가져오기 실패:', error)

      // 토큰이 유효하지 않은 경우 로그아웃
      if (error.response?.status === 401) {
        clearUserData()
      }
    } finally {
      isLoading.value = false
    }
  }

  const toggleFollow = async (userId) => {
    if (!token.value) {
      throw new Error('로그인이 필요합니다.')
    }

    try {
      // 먼저 현재 팔로우 상태 확인
      const statusResponse = await axios({
        method: 'get',
        url: `http://127.0.0.1:8000/auth/${userId}/follow-status/`,
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        }
      })

      const isCurrentlyFollowing = statusResponse.data.is_following
      const method = isCurrentlyFollowing ? 'delete' : 'post'

      // 팔로우/언팔로우 요청
      const response = await axios({
        method: method,
        url: `http://127.0.0.1:8000/auth/${userId}/follow/`,
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        }
      })

      console.log(`✅ ${response.data.is_following ? '팔로우' : '언팔로우'} 성공:`, response.data)

      return {
        success: true,
        is_following: response.data.is_following,
        followers_count: response.data.followers_count,
        following_count: response.data.following_count,
        message: response.data.detail
      }

    } catch (error) {
      console.error('❌ 팔로우 토글 실패:', error)

      let errorMessage = '팔로우 처리에 실패했습니다.'

      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.status === 401) {
        errorMessage = '로그인이 필요합니다.'
      } else if (error.response?.status === 404) {
        errorMessage = '사용자를 찾을 수 없습니다.'
      }

      throw new Error(errorMessage)
    }
  }

  // 팔로우 상태 확인만 하는 함수
  const checkFollowStatus = async (userId) => {
    if (!token.value) {
      return { is_following: false, followers_count: 0, following_count: 0 }
    }

    try {
      const response = await axios({
        method: 'get',
        url: `http://127.0.0.1:8000/auth/${userId}/follow-status/`,
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        }
      })

      return response.data

    } catch (error) {
      console.error('팔로우 상태 확인 실패:', error)
      return { is_following: false, followers_count: 0, following_count: 0 }
    }
  }


  // Actions - 로그인
  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await axios({
        method: 'post',
        url: 'http://127.0.0.1:8000/accounts/login/',
        headers: { 'Content-Type': 'application/json' },
        data: {
          username: credentials.email,
          password: credentials.password
        }
      })

      const newToken = response.data.key
      setToken(newToken)

      return { success: true, data: response.data }
    } catch (error) {
      console.error('로그인 실패:', error)
      return {
        success: false,
        error: error.response?.data || { message: '로그인에 실패했습니다.' }
      }
    } finally {
      isLoading.value = false
    }
  }

  // Actions - 로그아웃 (서버 요청 포함)
  const logout = async () => {
    if (!token.value) {
      clearUserData()
      return { success: true }
    }

    isLoading.value = true
    try {
      // 서버에 로그아웃 요청
      await axios({
        method: 'post',
        url: 'http://127.0.0.1:8000/accounts/logout/',
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        }
      })

      return { success: true }
    } catch (error) {
      console.error('서버 로그아웃 실패:', error)
      // 서버 요청이 실패해도 클라이언트는 로그아웃 진행
      return { success: true, warning: '서버 연결에 문제가 있었지만 로그아웃되었습니다.' }
    } finally {
      // 항상 클라이언트 데이터는 정리
      clearUserData()
      isLoading.value = false
    }
  }

  // Actions - 사용자 데이터 완전 정리
  const clearUserData = () => {
    token.value = null
    userData.value = null
    lastActivity.value = Date.now()

    // 로컬 스토리지 정리
    localStorage.removeItem('token')
    localStorage.removeItem('userData')
    localStorage.removeItem('lastActivity')

    // Axios 헤더 정리
    delete axios.defaults.headers.common['Authorization']

    console.log('사용자 데이터가 완전히 정리되었습니다.')
  }

  // Actions - 마지막 활동 시간 업데이트
  const updateLastActivity = () => {
    lastActivity.value = Date.now()
    localStorage.setItem('lastActivity', lastActivity.value.toString())
  }

  // Actions - 세션 만료 확인 (30분)
  const checkSessionExpiry = () => {
    const SESSION_TIMEOUT = 30 * 60 * 1000 // 30분
    const now = Date.now()
    const lastActivityTime = parseInt(localStorage.getItem('lastActivity') || '0')

    if (isAuthenticated.value && (now - lastActivityTime) > SESSION_TIMEOUT) {
      console.log('세션이 만료되어 자동 로그아웃됩니다.')
      clearUserData()
      return true
    }
    return false
  }

  // Actions - 토큰 갱신 (필요한 경우)
  const refreshToken = async () => {
    if (!token.value) return false

    try {
      const response = await axios({
        method: 'post',
        url: 'http://127.0.0.1:8000/accounts/token/refresh/',
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.data.token) {
        setToken(response.data.token)
        return true
      }
    } catch (error) {
      console.error('토큰 갱신 실패:', error)
      clearUserData()
      return false
    }
  }

  // Actions - 프로필 업데이트
  const updateProfile = async (profileData) => {
    if (!token.value)
      return { success: false, error: '로그인이 필요합니다.' }

    isLoading.value = true
    try {
      // 1) FormData 에 텍스트 필드와 파일 필드 모두 담는다
      const form = new FormData()
      form.append('nickname', profileData.nickname)
      // form.append('email',         profileData.email)
      // if (profileData.bio !== undefined) {
      //   form.append('bio', profileData.bio)
      // }
      form.append('profile_bio', profileData.profile_bio)
      // 만약 파일을 선택했다면
      if (profileData.profileImageFile) {
        // <input type="file"> 에서 가져온 File 객체
        form.append('profile_image', profileData.profileImageFile)
      }

      // 2) axios 요청: Content-Type 은 multipart/form-data 로
      const response = await axios.patch(
        'http://127.0.0.1:8000/accounts/user/',
        form,
        {
          headers: {
            'Authorization': `Token ${token.value}`,
            // multipart/form-data 로 보내면 boundary 도 같이 붙으니
            // Content-Type 헤더는 생략하거나 'multipart/form-data'만 지정하세요
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setUserData(response.data)
      return { success: true, data: response.data }

    } catch (error) {
      console.error('프로필 업데이트 실패:', error)
      return {
        success: false,
        error: error.response?.data || { message: '프로필 업데이트에 실패했습니다.' }
      }
    } finally {
      isLoading.value = false
    }
  }

  // Actions - 비밀번호 변경
  const changePassword = async (passwordData) => {
    if (!token.value) return { success: false, error: '로그인이 필요합니다.' }

    isLoading.value = true
    try {
      const response = await axios({
        method: 'post',
        url: 'http://127.0.0.1:8000/accounts/password/change/',
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        },
        data: {
          old_password: passwordData.oldPassword,
          new_password1: passwordData.newPassword,
          new_password2: passwordData.confirmPassword
        }
      })

      return { success: true, message: '비밀번호가 성공적으로 변경되었습니다.' }
    } catch (error) {
      console.error('비밀번호 변경 실패:', error)
      return {
        success: false,
        error: error.response?.data || { message: '비밀번호 변경에 실패했습니다.' }
      }
    } finally {
      isLoading.value = false
    }
  }

  // Actions - 회원탈퇴
  const deleteAccount = async (password) => {
    if (!token.value) return { success: false, error: '로그인이 필요합니다.' }

    isLoading.value = true
    try {
      await axios({
        method: 'delete',
        url: 'http://127.0.0.1:8000/accounts/user/',
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json'
        },
        data: { password }
      })

      clearUserData()
      return { success: true, message: '계정이 성공적으로 삭제되었습니다.' }
    } catch (error) {
      console.error('계정 삭제 실패:', error)
      return {
        success: false,
        error: error.response?.data || { message: '계정 삭제에 실패했습니다.' }
      }
    } finally {
      isLoading.value = false
    }
  }

  // 초기화 - 앱 시작시 토큰이 있으면 사용자 정보 가져오기
  const initialize = async () => {
    const savedToken = localStorage.getItem('token')
    const savedActivity = localStorage.getItem('lastActivity')

    if (savedToken && savedActivity) {
      // 세션 만료 확인
      if (checkSessionExpiry()) {
        return false
      }

      token.value = savedToken
      axios.defaults.headers.common['Authorization'] = `Token ${savedToken}`

      // 사용자 정보 가져오기
      await fetchUserData()
      updateLastActivity()

      return true
    }

    return false
  }

  // 자동 세션 관리를 위한 인터벌 설정
  let sessionCheckInterval = null

  const startSessionMonitoring = () => {
    if (sessionCheckInterval) clearInterval(sessionCheckInterval)

    sessionCheckInterval = setInterval(() => {
      if (isAuthenticated.value) {
        checkSessionExpiry()
      }
    }, 60000) // 1분마다 확인
  }

  const stopSessionMonitoring = () => {
    if (sessionCheckInterval) {
      clearInterval(sessionCheckInterval)
      sessionCheckInterval = null
    }
  }

  // Store 반환
  return {
    //
    BE_API_PATH,

    // State
    token,
    userData,
    isLoading,
    lastActivity,

    // Getters
    isAuthenticated,
    currentUser,
    userName,

    // Actions
    setToken,
    setUserData,
    fetchUserData,
    login,
    logout,
    clearUserData,
    updateLastActivity,
    checkSessionExpiry,
    refreshToken,
    updateProfile,
    changePassword,
    deleteAccount,
    initialize,
    startSessionMonitoring,
    stopSessionMonitoring,
    toggleFollow,
    checkFollowStatus,

  }
})