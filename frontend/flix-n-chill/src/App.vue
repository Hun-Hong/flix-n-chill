<template>
  <div id="app">
    <BaseHeader />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import BaseHeader from './components/BaseHeader.vue'
import { useUserStore } from './stores/accounts'

const userStore = useUserStore()

// onMounted(() => {
//   if (localStorage.getItem('token')) {
//     userStore.restoreUser()
//   }
// })
</script>

<style>
/* 전역 스타일 리셋 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 다크 테마 전역 스타일 */
body { 
  background: linear-gradient(135deg, #073763 0%, #780909 100%);
  min-height: 100vh;
  color: #ffffff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  position: relative;
}

/* 부트스트랩 다크 테마 호환성 */
.bg-light {
  background-color: #2d3748 !important;
}

.text-dark {
  color: #e2e8f0 !important;
}

/* 스크롤바 커스터마이징 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 컨테이너 기본 스타일 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 576px) {
  .container { max-width: 540px; }
}

@media (min-width: 768px) {
  .container { max-width: 720px; }
}

@media (min-width: 992px) {
  .container { max-width: 960px; }
}

@media (min-width: 1200px) {
  .container { max-width: 1140px; }
}

@media (min-width: 1400px) {
  .container { max-width: 1320px; }
}

/* 링크 기본 스타일 */
a {
  color: #ffffff;
  text-decoration: none;
}

a:hover {
  color: #db0000;
}

/* 버튼 기본 스타일 리셋 */
button {
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
}

/* 포커스 스타일 */
button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  outline: 2px solid #db0000;
  outline-offset: 2px;
}

/* 전환 효과 */
* {
  transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

/* 이미지 기본 스타일 */
img {
  max-width: 100%;
  height: auto;
}

/* 입력 요소 기본 스타일 */
input, textarea, select {
  font-family: inherit;
  font-size: inherit;
}

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 다크 모드 강제 적용 */
input, textarea, select {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  border-radius: 8px;
  padding: 0.5rem;
}

input::placeholder,
textarea::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

/* 모달 z-index 관리 */
.modal-overlay {
  z-index: 1050;
}

.navbar {
  z-index: 1030;
}

.sticky-header {
  z-index: 1020;
}
</style>