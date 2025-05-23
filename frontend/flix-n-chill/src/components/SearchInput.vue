<template>
  <div class="search-input-container">
    <div class="search-box" :class="{ 'focused': isFocused }">
      <!-- 검색 아이콘 -->
      <div class="search-icon">
        <i class="bi bi-search"></i>
      </div>
      
      <!-- 검색 입력창 -->
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        :placeholder="placeholder"
        @focus="handleFocus"
        @blur="handleBlur"
        @keyup.enter="handleSearch"
        ref="searchInputRef"
      >
      
      <!-- 검색어 지우기 버튼 -->
      <button
        v-if="searchQuery"
        class="clear-btn"
        @click="clearSearch"
        title="검색어 지우기"
      >
        <i class="bi bi-x-lg"></i>
      </button>
      
      <!-- 검색 버튼 -->
      <button
        class="search-btn"
        @click="handleSearch"
        :disabled="!searchQuery.trim()"
        title="검색"
      >
        <i class="bi bi-arrow-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits, defineExpose } from 'vue'

// Props 정의
const props = defineProps({
  placeholder: {
    type: String,
    default: '영화 제목을 입력하세요...'
  },
  initialValue: {
    type: String,
    default: ''
  }
})

// Emits 정의
const emit = defineEmits(['search'])

// 반응형 데이터
const searchQuery = ref(props.initialValue)
const isFocused = ref(false)
const searchInputRef = ref(null)

// 메서드들
const handleFocus = () => {
  isFocused.value = true
}

const handleBlur = () => {
  isFocused.value = false
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    emit('search', searchQuery.value.trim())
    console.log('🔍 검색 실행:', searchQuery.value)
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searchInputRef.value?.focus()
}

// 외부에서 검색어 설정하는 메서드
const setSearchQuery = (query) => {
  searchQuery.value = query
}

// initialValue 변경 감지
watch(() => props.initialValue, (newValue) => {
  searchQuery.value = newValue
})

// 외부에서 접근 가능한 메서드 노출
defineExpose({
  setSearchQuery,
  focus: () => searchInputRef.value?.focus(),
  blur: () => searchInputRef.value?.blur()
})
</script>

<style scoped>
/* 검색 컨테이너 */
.search-input-container {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

/* 검색 박스 */
.search-box {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  padding: 0.75rem 1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.search-box.focused {
  border-color: #db0000;
  box-shadow: 0 0 0 0.2rem rgba(219, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.15);
}

/* 검색 아이콘 */
.search-icon {
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.1rem;
  margin-right: 0.75rem;
  transition: color 0.3s ease;
}

.search-box.focused .search-icon {
  color: #db0000;
}

/* 검색 입력창 */
.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 400;
  padding: 0.25rem 0;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.3s ease;
}

.search-box.focused .search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

/* 지우기 버튼 */
.clear-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.6);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  transform: scale(1.1);
}

/* 검색 버튼 */
.search-btn {
  background: linear-gradient(135deg, #db0000, #ff4757);
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
  font-size: 0.9rem;
}

.search-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff4757, #ff6b7a);
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(219, 0, 0, 0.4);
}

.search-btn:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
}

/* 반응형 */
@media (max-width: 768px) {
  .search-input-container {
    max-width: 100%;
  }
  
  .search-box {
    padding: 0.6rem 0.8rem;
  }
  
  .search-input {
    font-size: 0.95rem;
  }
  
  .search-btn {
    width: 36px;
    height: 36px;
  }
  
  .clear-btn {
    width: 28px;
    height: 28px;
  }
}

@media (max-width: 480px) {
  .search-box {
    padding: 0.5rem 0.7rem;
  }
  
  .search-input {
    font-size: 0.9rem;
  }
  
  .search-btn {
    width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }
}
</style>