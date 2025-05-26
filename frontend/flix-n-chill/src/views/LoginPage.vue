<template>
    <div class="login-page">
      <!-- 배경 -->
      <div class="background-gradient"></div>
  
      <!-- 메인 컨테이너 -->
      <div class="login-container">
        <div class="login-card">
          <!-- 헤더 -->
          <div class="login-header">
            <h1 class="login-title">로그인</h1>
            <p class="login-subtitle">계정에 로그인하여 서비스를 이용하세요</p>
          </div>
  
          <!-- 로그인 폼 -->
          <form @submit.prevent="handleSubmit" class="login-form">
            <!-- 이메일 입력 -->
            <div class="form-group">
              <label for="email" class="form-label">이메일 주소</label>
              <div class="input-wrapper">
                <input
                  id="email"
                  v-model="formData.email"
                  type="email"
                  class="form-input"
                  :class="{ error: errors.email, success: !errors.email && formData.email && isEmailValid }"
                  placeholder="example@email.com"
                  @blur="validateEmail"
                  @input="clearError('email')"
                  :disabled="userStore.isLoading"
                />
                <div class="input-icon">
                  <i class="bi bi-envelope"></i>
                </div>
              </div>
              <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
            </div>
  
            <!-- 비밀번호 입력 -->
            <div class="form-group">
              <label for="password" class="form-label">비밀번호</label>
              <div class="input-wrapper">
                <input
                  id="password"
                  v-model="formData.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input"
                  :class="{ error: errors.password, success: !errors.password && formData.password && formData.password.length >= 1 }"
                  placeholder="비밀번호를 입력해주세요"
                  @blur="validatePassword"
                  @input="clearError('password')"
                  :disabled="userStore.isLoading"
                />
                <button type="button" class="toggle-password-btn" @click="showPassword = !showPassword">
                  <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
              <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
            </div>
  
            <!-- 로그인 버튼 -->
            <button type="submit" class="login-btn" :disabled="!isFormValid || userStore.isLoading">
              <span v-if="userStore.isLoading" class="loading-spinner"></span>
              {{ userStore.isLoading ? '로그인 중...' : '로그인' }}
            </button>
          </form>
  
          <!-- 회원가입 링크 -->
          <div class="signup-link">
            <p>아직 계정이 없으신가요? <router-link to="/signup" class="link">회원가입</router-link></p>
          </div>
        </div>
      </div>
  
      <!-- 로그인 성공 팝업 -->
      <div v-if="showSuccessPopup" class="popup-overlay" @click="closeSuccessPopup">
        <div class="popup-content" @click.stop>
          <div class="popup-header">
            <div class="success-icon">
              <i class="bi bi-check-circle-fill"></i>
            </div>
            <h2 class="popup-title">로그인 성공!</h2>
            <p class="popup-message">환영합니다!<br />잠시 후 메인 페이지로 이동합니다.</p>
          </div>
          <div class="popup-actions">
            <button class="popup-btn primary" @click="goToMain">메인으로 이동</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useUserStore } from '@/stores/accounts'
  
  // 라우터와 스토어
  const router = useRouter()
  const userStore = useUserStore()
  
  // 폼 데이터
  const formData = ref({
    email: '',
    password: ''
  })
  
  // 상태 관리
  const errors = ref({})
  const showPassword = ref(false)
  const showSuccessPopup = ref(false)
  
  // 이메일 유효성 검사
  const isEmailValid = computed(() => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(formData.value.email)
  })
  
  // 폼 전체 유효성 검사
  const isFormValid = computed(() => {
    return isEmailValid.value && formData.value.password.length >= 1 && Object.keys(errors.value).length === 0
  })
  
  // 에러 클리어
  const clearError = (field) => {
    if (errors.value[field]) {
      delete errors.value[field]
    }
  }
  
  // 이메일 유효성 검사
  const validateEmail = () => {
    if (!formData.value.email) {
      errors.value.email = '이메일을 입력해주세요'
    } else if (!isEmailValid.value) {
      errors.value.email = '올바른 이메일 형식이 아닙니다'
    } else {
      clearError('email')
    }
  }
  
  // 비밀번호 유효성 검사
  const validatePassword = () => {
    if (!formData.value.password) {
      errors.value.password = '비밀번호를 입력해주세요'
    } else {
      clearError('password')
    }
  }
  
  // 로그인 폼 제출
  const handleSubmit = async () => {
    console.log('🚀 로그인 시도:', formData.value.email)
    
    // 유효성 검사
    validateEmail()
    validatePassword()
  
    if (!isFormValid.value) {
      console.log('❌ 폼 유효성 검사 실패')
      return
    }
  
    // 기존 에러 초기화
    errors.value = {}
  
    try {
      // Pinia Store의 login 함수 사용
      const result = await userStore.login({
        email: formData.value.email,
        password: formData.value.password
      })
  
      console.log('로그인 결과:', result)
  
      if (result.success) {
        console.log('✅ 로그인 성공!')
        showSuccessPopup.value = true
      } else {
        console.error('❌ 로그인 실패:', result.error)
        
        // 에러 메시지 처리
        if (result.error.non_field_errors) {
          errors.value.password = result.error.non_field_errors.join(' ')
        } else if (result.error.password) {
          errors.value.password = Array.isArray(result.error.password) ? result.error.password.join(' ') : result.error.password
        } else if (result.error.email) {
          errors.value.email = Array.isArray(result.error.email) ? result.error.email.join(' ') : result.error.email
        } else {
          errors.value.password = result.error.message || '이메일 또는 비밀번호가 올바르지 않습니다'
        }
      }
    } catch (error) {
      console.error('💥 로그인 처리 중 예외 발생:', error)
      errors.value.password = '로그인 처리 중 오류가 발생했습니다. 다시 시도해주세요.'
    }
  }
  
  // 성공 팝업 닫기
  const closeSuccessPopup = () => {
    showSuccessPopup.value = false
    goToMain()
  }
  
  // 메인 페이지로 이동
  const goToMain = () => {
    showSuccessPopup.value = false
    const redirectPath = router.currentRoute.value.query.redirect || '/'
    console.log(`📍 페이지 이동: ${redirectPath}`)
    router.push(redirectPath)
  }
  
  // 컴포넌트 마운트 시 실행
  onMounted(() => {
    console.log('🎬 로그인 페이지 마운트')
    
    // 이미 로그인된 경우 리다이렉트
    if (userStore.isAuthenticated) {
      console.log('👤 이미 로그인된 사용자, 홈으로 리다이렉트')
      router.push('/')
    }
  })
  </script>
  
  <style scoped>
  .login-page {
    min-height: 100vh;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    overflow: hidden;
  }
  
  .background-gradient {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #0a0a0a 0%, #1a0f1f 20%, #2d1b69 40%, #8e2de2 60%, #4a00e0 80%, #000000 100%);
    z-index: -2;
  }
  
  .login-container {
    width: 100%;
    max-width: 450px;
    z-index: 1;
    position: relative;
  }
  
  .login-card {
    background: rgba(0, 0, 0, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);
    position: relative;
    overflow: hidden;
  }
  
  .login-header {
    text-align: center;
    margin-bottom: 2.5rem;
  }
  
  .login-title {
    color: #ffffff;
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #ffffff 0%, #e8e8e8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .login-subtitle {
    color: rgba(255, 255, 255, 0.75);
    font-size: 1.05rem;
    margin: 0;
    font-weight: 400;
  }
  
  .login-form {
    display: flex;
    flex-direction: column;
    gap: 1.8rem;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    position: relative;
  }
  
  .form-label {
    color: #ffffff;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 0.7rem;
    letter-spacing: 0.5px;
  }
  
  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }
  
  .form-input {
    width: 100%;
    padding: 1rem 1.2rem 1rem 3rem;
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 400;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  .form-input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .form-input::placeholder {
    color: rgba(255, 255, 255, 0.45);
  }
  
  .form-input:focus {
    outline: none;
    border-color: rgba(138, 43, 226, 0.8);
    background: rgba(255, 255, 255, 0.12);
    box-shadow: 0 0 0 0.3rem rgba(138, 43, 226, 0.15);
  }
  
  .form-input.error {
    border-color: rgba(255, 99, 132, 0.8);
    background: rgba(255, 99, 132, 0.08);
    box-shadow: 0 0 0 0.2rem rgba(255, 99, 132, 0.15);
  }
  
  .form-input.success {
    border-color: rgba(75, 192, 192, 0.8);
    background: rgba(75, 192, 192, 0.08);
    box-shadow: 0 0 0 0.2rem rgba(75, 192, 192, 0.15);
  }
  
  .input-icon {
    position: absolute;
    left: 1rem;
    color: rgba(255, 255, 255, 0.5);
    font-size: 1.1rem;
    pointer-events: none;
  }
  
  .toggle-password-btn {
    position: absolute;
    right: 1rem;
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1.1rem;
  }
  
  .toggle-password-btn:hover {
    color: rgba(255, 255, 255, 0.9);
    background: rgba(255, 255, 255, 0.1);
  }
  
  .error-message {
    color: rgba(255, 99, 132, 0.9);
    font-size: 0.85rem;
    margin-top: 0.5rem;
    font-weight: 500;
  }
  
  .login-btn {
    width: 100%;
    padding: 1.2rem;
    background: linear-gradient(135deg, #8e2de2 0%, #4a00e0 100%);
    border: none;
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    margin-top: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .login-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #a653e8 0%, #5d15e6 100%);
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(138, 43, 226, 0.4);
  }
  
  .login-btn:disabled {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.4);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  
  .loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .signup-link {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .signup-link p {
    color: rgba(255, 255, 255, 0.75);
    margin: 0;
    font-size: 0.95rem;
  }
  
  .link {
    color: #8e2de2;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
  }
  
  .link:hover {
    color: #4a00e0;
  }
  
  /* 성공 팝업 */
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
    z-index: 1000;
    backdrop-filter: blur(15px);
    animation: fadeIn 0.3s ease-out;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
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
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6);
    animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
    min-width: 120px;
  }
  
  .popup-btn.primary {
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
    color: white;
  }
  
  .popup-btn.primary:hover {
    background: linear-gradient(135deg, #a653e8, #5d15e6);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(138, 43, 226, 0.4);
  }
  
  /* 반응형 디자인 */
  @media (max-width: 768px) {
    .login-page {
      padding: 1.5rem 1rem;
    }
  
    .login-card {
      padding: 2.5rem 2rem;
      border-radius: 16px;
    }
  
    .login-title {
      font-size: 1.9rem;
    }
  
    .form-input {
      padding: 0.9rem 1rem 0.9rem 2.8rem;
    }
  }
  
  @media (max-width: 480px) {
    .login-page {
      padding: 1rem 0.5rem;
    }
  
    .login-card {
      padding: 2rem 1.5rem;
      border-radius: 12px;
    }
  
    .login-title {
      font-size: 1.6rem;
    }
  
    .form-input {
      font-size: 16px;
      padding: 0.8rem 1rem 0.8rem 2.6rem;
    }
  
    .input-icon {
      left: 0.8rem;
      font-size: 1rem;
    }
  
    .popup-content {
      padding: 2rem 1.5rem;
    }
  
    .success-icon {
      font-size: 3.5rem;
    }
  }
  </style>