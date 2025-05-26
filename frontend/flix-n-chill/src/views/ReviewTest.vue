<template>
    <div class="review-test-page">
      <h1>리뷰 테스트 페이지</h1>
      <p>URL: {{ $route.path }}</p>
      <p>리뷰 ID: {{ $route.params.id }}</p>
      
      <button @click="showModal = true" class="test-btn">모달 열기</button>
      
      <!-- 모달 -->
      <div v-if="showModal" class="modal-overlay" @click="showModal = false">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2>리뷰 상세</h2>
            <button @click="showModal = false" class="close-btn">×</button>
          </div>
          <div class="modal-body">
            <div class="movie-info">
              <img src="https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg" alt="기생충" class="movie-poster">
              <div class="movie-details">
                <h3>기생충</h3>
                <div class="rating">⭐⭐⭐⭐⭐ 5/5</div>
              </div>
            </div>
            <div class="review-content">
              <p>정말 놀라운 작품이었습니다. 봉준호 감독님의 연출력과 배우들의 연기가 완벽하게 조화를 이뤘어요!</p>
            </div>
            <div class="review-actions">
              <button class="like-btn">❤️ 23</button>
              <button class="comment-btn">💬 12</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRoute } from 'vue-router'
  
  const route = useRoute()
  const showModal = ref(false)
  
  // 자동으로 모달 열기 (테스트용)
  setTimeout(() => {
    showModal.value = true
  }, 500)
  </script>
  
  <style scoped>
  .review-test-page {
    padding: 2rem;
    min-height: 100vh;
    background: #1a1a2e;
    color: white;
  }
  
  .test-btn {
    background: #3498db;
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    margin: 1rem 0;
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  }
  
  .modal-container {
    background: #16213e;
    border-radius: 16px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .modal-header h2 {
    margin: 0;
    color: white;
  }
  
  .close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .movie-info {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .movie-poster {
    width: 80px;
    height: 120px;
    object-fit: cover;
    border-radius: 8px;
  }
  
  .movie-details h3 {
    margin: 0 0 0.5rem 0;
    color: white;
  }
  
  .rating {
    color: #ffd700;
    font-size: 1.1rem;
  }
  
  .review-content {
    margin-bottom: 1.5rem;
  }
  
  .review-content p {
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.6;
  }
  
  .review-actions {
    display: flex;
    gap: 1rem;
  }
  
  .like-btn, .comment-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    cursor: pointer;
  }
  </style>