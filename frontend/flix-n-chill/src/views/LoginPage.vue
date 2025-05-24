<template>
    <div class="login-page">
        <!-- 배경 그라데이션 -->
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
                            <input id="email" v-model="formData.email" type="email" class="form-input" :class="{
                                'error': errors.email,
                                'success': !errors.email && formData.email && isEmailValid
                            }" placeholder="example@email.com" @blur="validateEmail" @input="clearError('email')">
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
                            <input id="password" v-model="formData.password" :type="showPassword ? 'text' : 'password'"
                                class="form-input" :class="{
                                    'error': errors.password,
                                    'success': !errors.password && formData.password && formData.password.length >= 1
                                }" placeholder="비밀번호를 입력해주세요" @blur="validatePassword" @input="clearError('password')">
                            <button type="button" class="toggle-password-btn" @click="showPassword = !showPassword">
                                <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                            </button>
                        </div>
                        <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
                    </div>

                    <!-- 로그인 옵션 -->
                    <div class="login-options">
                        <div class="checkbox-group">
                            <input id="rememberMe" v-model="rememberMe" type="checkbox" class="checkbox-input">
                            <label for="rememberMe" class="checkbox-label">
                                <span class="checkbox-custom"></span>
                                <span class="checkbox-text">로그인 상태 유지</span>
                            </label>
                        </div>
                        <a href="#" class="forgot-password-link" @click.prevent="showForgotPasswordModal = true">
                            비밀번호 찾기
                        </a>
                    </div>

                    <!-- 로그인 버튼 -->
                    <button type="submit" class="login-btn" :disabled="!isFormValid || isSubmitting">
                        <span v-if="isSubmitting" class="loading-spinner"></span>
                        {{ isSubmitting ? '로그인 중...' : '로그인' }}
                    </button>

                    <!-- 소셜 로그인 -->
                    <div class="social-login">
                        <div class="divider">
                            <span>또는</span>
                        </div>

                        <div class="social-buttons">
                            <button type="button" class="social-btn google" @click="loginWithGoogle">
                                <i class="bi bi-google"></i>
                                <span>Google로 로그인</span>
                            </button>
                            <button type="button" class="social-btn kakao" @click="loginWithKakao">
                                <i class="bi bi-chat-fill"></i>
                                <span>카카오로 로그인</span>
                            </button>
                            <button type="button" class="social-btn naver" @click="loginWithNaver">
                                <span class="naver-icon">N</span>
                                <span>네이버로 로그인</span>
                            </button>
                        </div>
                    </div>
                </form>

                <!-- 회원가입 링크 -->
                <div class="signup-link">
                    <p>아직 계정이 없으신가요?
                        <router-link to="/signup" class="link">회원가입</router-link>
                    </p>
                </div>
            </div>
        </div>

        <!-- 비밀번호 찾기 모달 -->
        <div v-if="showForgotPasswordModal" class="modal-overlay" @click="showForgotPasswordModal = false">
            <div class="modal-content" @click.stop>
                <div class="modal-header">
                    <h2 class="modal-title">비밀번호 찾기</h2>
                    <button class="modal-close-btn" @click="showForgotPasswordModal = false">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p class="modal-description">
                        가입하신 이메일 주소를 입력하시면,<br>
                        비밀번호 재설정 링크를 보내드립니다.
                    </p>
                    <div class="form-group">
                        <label for="resetEmail" class="form-label">이메일 주소</label>
                        <input id="resetEmail" v-model="resetEmail" type="email" class="form-input" :class="{
                            'error': resetEmailError,
                            'success': !resetEmailError && resetEmail && isResetEmailValid
                        }" placeholder="example@email.com" @input="resetEmailError = ''">
                        <div v-if="resetEmailError" class="error-message">{{ resetEmailError }}</div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="modal-btn secondary" @click="showForgotPasswordModal = false">취소</button>
                    <button class="modal-btn primary" @click="sendResetEmail"
                        :disabled="!isResetEmailValid || isSendingReset">
                        <span v-if="isSendingReset" class="loading-spinner small"></span>
                        {{ isSendingReset ? '전송 중...' : '재설정 링크 전송' }}
                    </button>
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
                    <p class="popup-message">
                        환영합니다!<br>
                        잠시 후 메인 페이지로 이동합니다.
                    </p>
                </div>
                <div class="popup-actions">
                    <button class="popup-btn primary" @click="goToMain">메인으로 이동</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/accounts'
import axios from 'axios'

// 폼 데이터
const formData = ref({
    email: '',
    password: ''
})

// 상태 관리
const errors = ref({})
const rememberMe = ref(false)
const showPassword = ref(false)
const isSubmitting = ref(false)
const showSuccessPopup = ref(false)
const showForgotPasswordModal = ref(false)
const resetEmail = ref('')
const resetEmailError = ref('')
const isSendingReset = ref(false)

// 이메일 유효성 검사
const isEmailValid = computed(() => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(formData.value.email)
})

// 비밀번호 재설정 이메일 유효성 검사
const isResetEmailValid = computed(() => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(resetEmail.value)
})

// 폼 전체 유효성 검사
const isFormValid = computed(() => {
    return isEmailValid.value &&
        formData.value.password.length >= 1 &&
        Object.keys(errors.value).length === 0
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
const handleSubmit = () => {
  validateEmail()
  validatePassword()

  if (!isFormValid.value) return

  isSubmitting.value = true

  const payload = {
    username: formData.value.email,
    password: formData.value.password
  }

  axios({
    method: 'post',
    url: 'http://127.0.0.1:8000/accounts/login/',
    headers: { 'Content-Type': 'application/json' },
    data: payload
  })
    .then(response => {
      // rest-auth 기본 응답: { key: '...' }
      const token = response.data.key
      const userStore = useUserStore()
      userStore.token = token

      showSuccessPopup.value = true
    })
    .catch(error => {
      if (error.response?.data?.non_field_errors) {
        errors.value.password = error.response.data.non_field_errors.join(' ')
      } else if (error.response?.data?.password) {
        errors.value.password = error.response.data.password.join(' ')
      } else {
        errors.value.password = '이메일 또는 비밀번호가 올바르지 않습니다'
      }
    })
    .finally(() => {
      isSubmitting.value = false
    })
}

// 비밀번호 재설정 이메일 전송
const sendResetEmail = async () => {
    if (!isResetEmailValid.value) {
        resetEmailError.value = '올바른 이메일을 입력해주세요'
        return
    }

    isSendingReset.value = true

    try {
        // 실제 API 호출 시뮬레이션
        await new Promise(resolve => setTimeout(resolve, 1500))

        // 여기서 실제 비밀번호 재설정 API를 호출하세요
        console.log('비밀번호 재설정 이메일:', resetEmail.value)

        alert('비밀번호 재설정 링크를 이메일로 전송했습니다!')
        showForgotPasswordModal.value = false
        resetEmail.value = ''

    } catch (error) {
        console.error('이메일 전송 실패:', error)
        resetEmailError.value = '이메일 전송 중 오류가 발생했습니다'
    } finally {
        isSendingReset.value = false
    }
}

// 소셜 로그인 함수들
const loginWithGoogle = () => {
    console.log('Google 로그인')
    // Google OAuth 로직 구현
}

const loginWithKakao = () => {
    console.log('카카오 로그인')
    // 카카오 OAuth 로직 구현
}

const loginWithNaver = () => {
    console.log('네이버 로그인')
    // 네이버 OAuth 로직 구현
}

// 성공 팝업 닫기
const closeSuccessPopup = () => {
    showSuccessPopup.value = false
}

// 메인 페이지로 이동
const goToMain = () => {
    closeSuccessPopup()
    // 여기서 메인 페이지로 라우팅
    console.log('메인 페이지로 이동')
}
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
    background: linear-gradient(135deg,
            #0a0a0a 0%,
            #1a0f1f 20%,
            #2d1b69 40%,
            #8e2de2 60%,
            #4a00e0 80%,
            #000000 100%);
    z-index: -2;
}

.background-gradient::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 30% 20%, rgba(138, 43, 226, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 70% 80%, rgba(74, 0, 224, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 20% 80%, rgba(142, 45, 226, 0.2) 0%, transparent 50%);
    animation: gradientShift 8s ease-in-out infinite alternate;
}

@keyframes gradientShift {
    0% {
        opacity: 0.7;
    }

    100% {
        opacity: 1;
    }
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
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(255, 255, 255, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.login-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(138, 43, 226, 0.8) 50%,
            transparent 100%);
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
    text-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);
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
    position: relative;
}

.form-input::placeholder {
    color: rgba(255, 255, 255, 0.45);
    transition: all 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: rgba(138, 43, 226, 0.8);
    background: rgba(255, 255, 255, 0.12);
    box-shadow:
        0 0 0 0.3rem rgba(138, 43, 226, 0.15),
        0 8px 25px rgba(138, 43, 226, 0.1);
    transform: translateY(-1px);
}

.form-input:focus::placeholder {
    color: rgba(255, 255, 255, 0.6);
    transform: translateX(4px);
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
    transform: scale(1.1);
}

.error-message {
    color: rgba(255, 99, 132, 0.9);
    font-size: 0.85rem;
    margin-top: 0.5rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.error-message::before {
    content: '⚠';
    font-size: 0.9rem;
}

/* 로그인 옵션 */
.login-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0.5rem 0;
}

.checkbox-group {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.checkbox-input {
    display: none;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.checkbox-label:hover {
    transform: translateX(2px);
}

.checkbox-custom {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 4px;
    background: transparent;
    position: relative;
    flex-shrink: 0;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.checkbox-input:checked+.checkbox-label .checkbox-custom {
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
    border-color: transparent;
    transform: scale(1.1);
}

.checkbox-input:checked+.checkbox-label .checkbox-custom::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) scale(1.2);
    color: white;
    font-size: 10px;
    font-weight: bold;
    animation: checkmark 0.3s ease-in-out;
}

@keyframes checkmark {
    0% {
        transform: translate(-50%, -50%) scale(0) rotate(45deg);
    }

    100% {
        transform: translate(-50%, -50%) scale(1.2) rotate(0deg);
    }
}

.checkbox-text {
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.9rem;
    font-weight: 400;
}

.forgot-password-link {
    color: #8e2de2;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
}

.forgot-password-link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 1px;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
    transition: width 0.3s ease;
}

.forgot-password-link:hover {
    color: #4a00e0;
}

.forgot-password-link:hover::after {
    width: 100%;
}

/* 로그인 버튼 */
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
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.login-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

.login-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #a653e8 0%, #5d15e6 100%);
    transform: translateY(-3px);
    box-shadow:
        0 15px 40px rgba(138, 43, 226, 0.4),
        0 0 0 1px rgba(255, 255, 255, 0.1);
}

.login-btn:hover:not(:disabled)::before {
    left: 100%;
}

.login-btn:active:not(:disabled) {
    transform: translateY(-1px);
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

.loading-spinner.small {
    width: 16px;
    height: 16px;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

/* 소셜 로그인 */
.social-login {
    margin-top: 2rem;
}

.divider {
    position: relative;
    text-align: center;
    margin-bottom: 1.5rem;
}

.divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
}

.divider span {
    background: rgba(0, 0, 0, 0.85);
    color: rgba(255, 255, 255, 0.6);
    padding: 0 1rem;
    font-size: 0.9rem;
    position: relative;
    z-index: 1;
}

.social-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.social-btn {
    width: 100%;
    padding: 0.9rem 1rem;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    color: white;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    position: relative;
    overflow: hidden;
}

.social-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
}

.social-btn:hover {
    border-color: rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
}

.social-btn:hover::before {
    left: 100%;
}

.social-btn.google:hover {
    border-color: rgba(66, 133, 244, 0.5);
    background: rgba(66, 133, 244, 0.1);
}

.social-btn.kakao:hover {
    border-color: rgba(254, 229, 0, 0.5);
    background: rgba(254, 229, 0, 0.1);
}

.social-btn.naver:hover {
    border-color: rgba(30, 200, 50, 0.5);
    background: rgba(30, 200, 50, 0.1);
}

.naver-icon {
    width: 18px;
    height: 18px;
    background: #1ec832;
    color: white;
    border-radius: 3px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 12px;
}

/* 회원가입 링크 */
.signup-link {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
}

.signup-link::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 50px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(138, 43, 226, 0.8), transparent);
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
    position: relative;
}

.link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
    transition: width 0.3s ease;
}

.link:hover {
    color: #4a00e0;
}

.link:hover::after {
    width: 100%;
}

/* 모달 스타일 */
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
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
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
            rgba(138, 43, 226, 0.8) 50%,
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
    background: rgba(255, 99, 132, 0.2);
    color: rgba(255, 99, 132, 0.9);
    transform: scale(1.1);
}

.modal-body {
    padding: 1.5rem 2.5rem;
}

.modal-description {
    color: rgba(255, 255, 255, 0.8);
    text-align: center;
    line-height: 1.6;
    margin-bottom: 2rem;
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
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
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
    background: linear-gradient(135deg, #a653e8, #5d15e6);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(138, 43, 226, 0.4);
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
            rgba(138, 43, 226, 0.8) 50%,
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
    0% {
        transform: scale(0);
    }

    50% {
        transform: scale(1.2);
    }

    100% {
        transform: scale(1);
    }
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
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
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
    background: linear-gradient(135deg, #a653e8, #5d15e6);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(138, 43, 226, 0.4);
}

.popup-btn.primary:hover::before {
    left: 100%;
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

    .social-buttons {
        gap: 0.6rem;
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
        /* iOS 줌 방지 */
        padding: 0.8rem 1rem 0.8rem 2.6rem;
    }

    .input-icon {
        left: 0.8rem;
        font-size: 1rem;
    }

    .login-options {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .popup-content {
        padding: 2rem 1.5rem;
    }

    .success-icon {
        font-size: 3.5rem;
    }

    .popup-title {
        font-size: 1.4rem;
    }
}

/* 다크모드 최적화 */
@media (prefers-color-scheme: dark) {
    .login-card {
        background: rgba(0, 0, 0, 0.9);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .form-input {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .social-btn {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
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

/* 포커스 스타일 */
.form-input:focus-visible,
.login-btn:focus-visible,
.social-btn:focus-visible,
.modal-btn:focus-visible,
.popup-btn:focus-visible {
    outline: 2px solid rgba(138, 43, 226, 0.8);
    outline-offset: 2px;
}

.checkbox-input:focus-visible+.checkbox-label .checkbox-custom {
    outline: 2px solid rgba(138, 43, 226, 0.8);
    outline-offset: 2px;
    border-radius: 4px;
}

.forgot-password-link:focus-visible {
    outline: 2px solid rgba(138, 43, 226, 0.8);
    outline-offset: 2px;
    border-radius: 4px;
}
</style>