<template>
  <div id="app">
    <BaseHeader />
    <router-view />
  </div>
</template>

<script>
import BaseHeader from './components/BaseHeader.vue'
export default {
  name: 'App',
  components: {
    BaseHeader
  }
}
</script>

<style>
/* 다크 테마 전역 스타일 */
body { 
  background: linear-gradient(135deg, #073763 0%, #780909 100%);
  min-height: 100vh;
  color: #ffffff;
}

#app {
  min-height: 100vh;
}

/* 부트스트랩 다크 테마 호환성 */
.bg-light {
  background-color: #2d3748 !important;
}

.text-dark {
  color: #e2e8f0 !important;
}
</style>