// API 설정 중앙화
export const API_CONFIG = {
  // 개발환경: localhost:8000, 배포환경: 환경변수 필수 설정
  BASE_URL: import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000'),
  WS_BASE_URL: import.meta.env.VITE_WS_BASE_URL || (import.meta.env.PROD ? '' : 'ws://localhost:8000'),
  
  // API 엔드포인트 경로들
  ENDPOINTS: {
    // 인증 관련
    AUTH: '/auth',
    ACCOUNTS: '/accounts',
    
    // 영화 관련  
    MOVIES: '/api/v1/movies',
    
    // 채팅 관련
    CHAT: '/api/chat',
    
    // 미디어 파일
    MEDIA: '/media'
  }
}

// 완전한 URL 생성 헬퍼 함수들
export const getApiUrl = (endpoint) => `${API_CONFIG.BASE_URL}${endpoint}`
export const getMediaUrl = (path) => `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.MEDIA}/${path}`
export const getWsUrl = (path) => `${API_CONFIG.WS_BASE_URL}${path}`

// 자주 사용되는 API URL들
export const API_URLS = {
  // 인증
  LOGIN: getApiUrl(`${API_CONFIG.ENDPOINTS.AUTH}/login/`),
  LOGOUT: getApiUrl(`${API_CONFIG.ENDPOINTS.AUTH}/logout/`),
  REGISTRATION: getApiUrl(`${API_CONFIG.ENDPOINTS.ACCOUNTS}/registration/`),
  EMAIL_CHECK: getApiUrl(`${API_CONFIG.ENDPOINTS.AUTH}/email_check/`),
  USER_DETAIL: (userId) => getApiUrl(`${API_CONFIG.ENDPOINTS.AUTH}/${userId}/detail/`),
  
  // 영화
  MOVIES_BASE: getApiUrl(API_CONFIG.ENDPOINTS.MOVIES),
  MOVIE_DETAIL: (movieId) => getApiUrl(`${API_CONFIG.ENDPOINTS.MOVIES}/${movieId}/`),
  MOVIE_LIKE: (movieId) => getApiUrl(`${API_CONFIG.ENDPOINTS.MOVIES}/${movieId}/like/`),
  MOVIE_REVIEW_COMMENT: (reviewId) => getApiUrl(`${API_CONFIG.ENDPOINTS.MOVIES}/review/${reviewId}/comment/`),
  COMMENT_REPLY: (commentId) => getApiUrl(`${API_CONFIG.ENDPOINTS.MOVIES}/comment/${commentId}/reply/`),
  COMMENT_DELETE: (commentId) => getApiUrl(`${API_CONFIG.ENDPOINTS.MOVIES}/comment/${commentId}/delete/`),
  COMMENT_LIKE: (commentId) => getApiUrl(`${API_CONFIG.ENDPOINTS.MOVIES}/comment/${commentId}/like/`),
  SIMILAR_USERS: getApiUrl(`${API_CONFIG.ENDPOINTS.MOVIES}/user/similar-users/`),
  GENRE_ANALYSIS: getApiUrl(`${API_CONFIG.ENDPOINTS.MOVIES}/user/genre-analysis/`),
  
  // 채팅
  CHAT_WITH_USER: (userId) => getApiUrl(`${API_CONFIG.ENDPOINTS.CHAT}/with/${userId}/`),
  CHAT_ROOM: (roomId) => getApiUrl(`${API_CONFIG.ENDPOINTS.CHAT}/room/${roomId}/`)
}