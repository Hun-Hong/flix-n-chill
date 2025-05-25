<template>
  <!-- 프로필 수정 모달 -->
  <div class="modal-overlay" v-if="showModal" @click="closeModal">
    <div class="edit-profile-modal" @click.stop>
      <!-- 모달 헤더 -->
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="bi bi-person-gear"></i>
          프로필 수정
        </h2>
        <button class="modal-close-btn" @click="closeModal">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <!-- 모달 바디 -->
      <div class="modal-body">
        <!-- 프로필 사진 수정 -->
        <div class="form-section">
          <div class="profile-photo-section">
            <div class="current-photo">
              <img 
                :src="editForm.profileImage || '/api/placeholder/120/120'" 
                alt="프로필 사진"
                class="profile-preview"
                @error="handleImageError"
              >
              <div class="photo-overlay" @click="triggerPhotoUpload">
                <i class="bi bi-camera-fill"></i>
                <span>사진 변경</span>
              </div>
            </div>
            <input 
              type="file" 
              ref="photoInput" 
              @change="handlePhotoUpload"
              accept="image/*"
              style="display: none;"
            >
            <div class="photo-actions">
              <button 
                type="button" 
                class="btn btn-secondary btn-sm"
                @click="triggerPhotoUpload"
              >
                <i class="bi bi-upload"></i>
                사진 업로드
              </button>
              <button 
                type="button" 
                class="btn btn-outline btn-sm"
                @click="removePhoto"
                v-if="editForm.profileImage"
              >
                <i class="bi bi-trash"></i>
                사진 삭제
              </button>
            </div>
          </div>
        </div>

        <!-- 이메일 수정 -->
        <div class="form-section">
          <label class="form-label">
            <div>
              <i class="bi bi-envelope"></i>
              이메일
            </div>
          </label>
          <div class="form-group">
            <input 
              type="email" 
              v-model="editForm.email"
              class="form-input"
              placeholder="이메일을 입력해주세요"
              :class="{ 'error': errors.email }"
            >
            <div class="error-message" v-if="errors.email">
              {{ errors.email }}
            </div>
          </div>
        </div>

        <!-- Bio 수정 -->
        <div class="form-section">
          <label class="form-label">
            <div>
              <i class="bi bi-chat-text"></i>
              한마디
            </div>
            <span class="char-count">{{ editForm.bio.length }}/200</span>
          </label>
          <div class="form-group">
            <textarea 
              v-model="editForm.bio"
              class="form-textarea"
              placeholder="자신을 소개해주세요..."
              rows="4"
              maxlength="200"
              :class="{ 'error': errors.bio }"
            ></textarea>
            <div class="error-message" v-if="errors.bio">
              {{ errors.bio }}
            </div>
          </div>
        </div>
      </div>

      <!-- 모달 푸터 -->
      <div class="modal-footer">
        <button 
          type="button" 
          class="btn btn-outline"
          @click="closeModal"
        >
          취소
        </button>
        <button 
          type="button" 
          class="btn btn-primary"
          @click="saveProfile"
          :disabled="saving"
        >
          <i class="bi bi-check-lg" v-if="!saving"></i>
          <i class="bi bi-arrow-clockwise spin" v-else></i>
          {{ saving ? '저장 중...' : '저장하기' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  userProfile: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'save'])

// 반응형 데이터
const showModal = ref(props.show)
const saving = ref(false)
const photoInput = ref(null)

// 폼 데이터
const editForm = reactive({
  email: '',
  bio: '',
  profileImage: ''
})

// 에러 상태
const errors = reactive({
  email: '',
  bio: ''
})

// Props 변화 감지
watch(() => props.show, (newVal) => {
  showModal.value = newVal
  if (newVal) {
    resetForm()
  }
})

watch(() => props.userProfile, (newProfile) => {
  if (newProfile) {
    editForm.email = newProfile.email || ''
    editForm.bio = newProfile.bio || ''
    editForm.profileImage = newProfile.profileImage || ''
  }
}, { immediate: true })

// 메서드들
const resetForm = () => {
  editForm.email = props.userProfile.email || ''
  editForm.bio = props.userProfile.bio || ''
  editForm.profileImage = props.userProfile.profileImage || ''
  
  // 에러 초기화
  errors.email = ''
  errors.bio = ''
}

const closeModal = () => {
  showModal.value = false
  emit('close')
}

const validateForm = () => {
  let isValid = true
  
  // 에러 초기화
  errors.email = ''
  errors.bio = ''
  
  // 이메일 검증
  if (!editForm.email.trim()) {
    errors.email = '이메일을 입력해주세요.'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editForm.email)) {
    errors.email = '올바른 이메일 형식을 입력해주세요.'
    isValid = false
  }
  
  // Bio 검증 (선택사항이지만 길이 체크)
  if (editForm.bio.length > 200) {
    errors.bio = '소개는 200자 이하로 입력해주세요.'
    isValid = false
  }
  
  return isValid
}

const saveProfile = async () => {
  if (!validateForm()) {
    return
  }
  
  saving.value = true
  
  try {
    // 실제로는 API 호출
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 부모 컴포넌트로 수정된 데이터 전달
    emit('save', {
      email: editForm.email,
      bio: editForm.bio,
      profileImage: editForm.profileImage
    })
    
    closeModal()
  } catch (error) {
    console.error('프로필 저장 중 오류:', error)
    // 에러 처리 로직
  } finally {
    saving.value = false
  }
}

const triggerPhotoUpload = () => {
  photoInput.value?.click()
}

const handlePhotoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 파일 크기 체크 (5MB 제한)
    if (file.size > 5 * 1024 * 1024) {
      alert('파일 크기는 5MB 이하로 선택해주세요.')
      return
    }
    
    // 이미지 파일 체크
    if (!file.type.startsWith('image/')) {
      alert('이미지 파일만 선택할 수 있습니다.')
      return
    }
    
    // FileReader로 미리보기 생성
    const reader = new FileReader()
    reader.onload = (e) => {
      editForm.profileImage = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removePhoto = () => {
  editForm.profileImage = ''
  if (photoInput.value) {
    photoInput.value.value = ''
  }
}

const handleImageError = (event) => {
  event.target.src = '/api/placeholder/120/120'
}
</script>

<style scoped>
/* 모달 오버레이 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 1rem;
}

/* 모달 컨테이너 */
.edit-profile-modal {
  background: linear-gradient(135deg,
      rgba(30, 30, 30, 0.95) 0%,
      rgba(20, 20, 20, 0.98) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: modalSlideUp 0.3s ease;
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 모달 헤더 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

/* 모달 바디 */
.modal-body {
  padding: 2rem;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

/* 폼 섹션 */
.form-section {
  margin-bottom: 2rem;
}

.form-section:last-child {
  margin-bottom: 0;
}

/* 프로필 사진 섹션 */
.profile-photo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.current-photo {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
}

.current-photo:hover {
  transform: scale(1.05);
  border-color: rgba(255, 255, 255, 0.4);
}

.profile-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
  font-size: 0.9rem;
  gap: 0.25rem;
}

.current-photo:hover .photo-overlay {
  opacity: 1;
}

.photo-overlay i {
  font-size: 1.5rem;
}

.photo-actions {
  display: flex;
  gap: 0.5rem;
}

/* 폼 라벨 */
.form-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.form-label > div:first-child {
  display: flex;
  align-items: center;
  gap: 0.5rem; /* 🌟 아이콘과 텍스트 사이 간격 */
}

.char-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
}

/* 폼 그룹 */
.form-group {
  position: relative;
}

/* 폼 입력 */
.form-input,
.form-textarea {
  width: 100%;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  outline: none;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-input:focus,
.form-textarea:focus {
  border-color: #e74c3c;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.2);
}

.form-input.error,
.form-textarea.error {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  line-height: 1.5;
}

/* 에러 메시지 */
.error-message {
  color: #ff6b6b;
  font-size: 0.85rem;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.error-message::before {
  content: "⚠";
}

/* 모달 푸터 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 버튼 스타일 */
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
  text-decoration: none;
  font-size: 0.95rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #c0392b, #a93226);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(231, 76, 60, 0.4);
}

.btn-outline {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
}

/* 로딩 애니메이션 */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 0.5rem;
  }
  
  .edit-profile-modal {
    max-width: 100%;
    margin: 0.5rem;
  }
  
  .modal-header {
    padding: 1rem 1.5rem;
  }
  
  .modal-title {
    font-size: 1.25rem;
  }
  
  .modal-body {
    padding: 1.5rem;
    max-height: 70vh;
  }
  
  .modal-footer {
    padding: 1rem 1.5rem;
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .current-photo {
    width: 100px;
    height: 100px;
  }
  
  .photo-actions {
    flex-direction: column;
    width: 100%;
  }
}

@media (max-width: 480px) {
  .modal-header {
    padding: 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .modal-footer {
    padding: 1rem;
  }
  
  .form-section {
    margin-bottom: 1.5rem;
  }
}
</style>