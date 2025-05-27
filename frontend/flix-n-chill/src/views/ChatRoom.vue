<template>
  <div class="chat-container">
    <!-- 채팅방 헤더 -->
    <div class="chat-header">
      <div class="header-left">
        <button @click="goBack" class="back-btn">
          <i class="icon-arrow-left">←</i>
        </button>
        <div v-if="partner" class="partner-info">
          <img 
            :src="partner.profile_image || '/default-avatar.png'" 
            :alt="partner.nickname"
            class="partner-avatar"
          >
          <div>
            <h3>{{ partner.nickname }}</h3>
            <span class="online-status" :class="{ online: partner.is_online }">
              {{ partner.is_online ? '온라인' : '오프라인' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 연결 상태 표시 -->
    <div 
      v-if="connectionStatus !== 'connected'" 
      class="connection-status"
      :class="connectionStatus"
    >
      {{ connectionMessage }}
    </div>

    <!-- 메시지 영역 -->
    <div class="messages-container" ref="messagesContainer">
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        메시지를 불러오는 중...
      </div>

      <template v-for="(message, index) in messages" :key="message.id">
        <!-- 날짜 구분선 -->
        <div v-if="shouldShowDateSeparator(message, index)" class="date-separator">
          {{ formatDate(message.timestamp) }}
        </div>

        <!-- 메시지 -->
        <div 
          class="message" 
          :class="{ 
            'own': message.sender.id === currentUser?.id,
            'partner': message.sender.id !== currentUser?.id 
          }"
        >
          <div class="message-content">
            <div v-if="message.sender.id !== currentUser?.id" class="sender-info">
              <img 
                :src="message.sender.profile_image || '/default-avatar.png'" 
                :alt="message.sender.nickname"
                class="sender-avatar"
              >
              <span class="sender-name">{{ message.sender.nickname }}</span>
            </div>

            <div class="message-bubble">
              <p>{{ message.content }}</p>
              <div class="message-time">
                {{ formatTime(message.timestamp) }}
                <span v-if="message.sender.id === currentUser?.id && message.is_read" class="read-indicator">
                  읽음
                </span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 타이핑 표시 -->
      <div v-if="isPartnerTyping" class="typing-indicator">
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span>{{ partner?.nickname }}님이 입력 중...</span>
      </div>
    </div>

    <!-- 입력 영역 -->
    <div class="input-container">
      <div class="input-wrapper">
        <textarea
          v-model="newMessage"
          @keydown="handleKeyDown"
          @input="handleTyping"
          :disabled="connectionStatus !== 'connected'"
          placeholder="메시지를 입력하세요..."
          class="message-input"
          rows="1"
          ref="messageInput"
        ></textarea>

        <button 
          @click="sendMessage"
          :disabled="!canSendMessage"
          class="send-button"
        >
          <i class="icon-send">📤</i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/accounts'

// Props
const props = defineProps({
  roomId: {
    type: [String, Number],
    required: true
  }
})

// User store
const userStore = useUserStore()
const token = computed(() => userStore.token)

// Router
const router = useRouter()

// Reactive data
const messages = ref([])
const newMessage = ref('')
const loading = ref(true)
const connectionStatus = ref('connecting') // connecting, connected, disconnected, error
const chatSocket = ref(null)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 5
const partner = ref(null)
const currentUser = ref(null)
const isPartnerTyping = ref(false)
const typingTimer = ref(null)
const lastTypingTime = ref(0)
const room = ref(null) // 채팅방 ID 저장용

// Template refs
const messagesContainer = ref(null)
const messageInput = ref(null)

// Computed
const canSendMessage = computed(() => {
  return newMessage.value.trim() && 
         connectionStatus.value === 'connected' && 
         !loading.value
})

const connectionMessage = computed(() => {
  switch (connectionStatus.value) {
    case 'connecting':
      return '연결 중...'
    case 'disconnected':
      return '연결이 끊어졌습니다. 재연결 시도 중...'
    case 'error':
      return '연결 오류가 발생했습니다.'
    default:
      return ''
  }
})

// Methods
const goBack = () => {
  router.go(-1)
}

const initializeChat = async () => {
  try {
    // 현재 사용자 정보 가져오기
    currentUser.value = await getCurrentUser()

    // 채팅방 정보 가져오기
    const roomInfo = await getRoomInfo()
    room.value = roomInfo.room_id
    partner.value = roomInfo.partner

    loading.value = false
  } catch (error) {
    console.error('채팅 초기화 실패:', error)
    connectionStatus.value = 'error'
    loading.value = false
  }
}

const connectWebSocket = () => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const backendHost = import.meta.env.VITE_BACKEND_HOST || '34.47.106.179'
  // 토큰을 URL 쿼리 파라미터로 추가
  const wsUrl = `${wsProtocol}//${backendHost}/ws/chat/${props.roomId}/?token=${token.value}`

  chatSocket.value = new WebSocket(wsUrl)

  chatSocket.value.onopen = () => {
    console.log('WebSocket 연결 성공')
    connectionStatus.value = 'connected'
    reconnectAttempts.value = 0
  }

  chatSocket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    handleWebSocketMessage(data)
  }

  chatSocket.value.onclose = () => {
    console.log('WebSocket 연결 종료')
    connectionStatus.value = 'disconnected'
    attemptReconnect()
  }

  chatSocket.value.onerror = (error) => {
    console.error('WebSocket 오류:', error)
    connectionStatus.value = 'error'
  }
}

const disconnectWebSocket = () => {
  if (chatSocket.value) {
    chatSocket.value.close()
    chatSocket.value = null
  }
}

const attemptReconnect = () => {
  if (reconnectAttempts.value < maxReconnectAttempts) {
    reconnectAttempts.value++
    setTimeout(() => {
      console.log(`재연결 시도 ${reconnectAttempts.value}/${maxReconnectAttempts}`)
      connectWebSocket()
    }, 2000 * reconnectAttempts.value)
  }
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'message_history':
      messages.value = data.messages
      nextTick(() => {
        scrollToBottom()
      })
      break

    case 'chat_message':
      messages.value.push(data.message)
      nextTick(() => {
        scrollToBottom()
      })
      break

    case 'typing_indicator':
      isPartnerTyping.value = data.is_typing
      if (data.is_typing) {
        nextTick(() => {
          scrollToBottom()
        })
      }
      break

    case 'user_status':
      if (partner.value) {
        partner.value.is_online = data.is_online
      }
      break
  }
}

const sendMessage = () => {
  if (!canSendMessage.value) return

  const message = newMessage.value.trim()

  if (chatSocket.value && chatSocket.value.readyState === WebSocket.OPEN) {
    chatSocket.value.send(JSON.stringify({
      type: 'chat_message',
      message: message
    }))

    newMessage.value = ''
    adjustTextareaHeight()
    messageInput.value?.focus()
  }
}

const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const handleTyping = () => {
  adjustTextareaHeight()

  const now = Date.now()
  lastTypingTime.value = now

  // 타이핑 표시 전송
  if (chatSocket.value && chatSocket.value.readyState === WebSocket.OPEN) {
    chatSocket.value.send(JSON.stringify({
      type: 'typing_indicator',
      is_typing: true
    }))
  }

  // 일정 시간 후 타이핑 중지 신호 전송
  if (typingTimer.value) {
    clearTimeout(typingTimer.value)
  }

  typingTimer.value = setTimeout(() => {
    if (Date.now() - lastTypingTime.value >= 1000) {
      if (chatSocket.value && chatSocket.value.readyState === WebSocket.OPEN) {
        chatSocket.value.send(JSON.stringify({
          type: 'typing_indicator',
          is_typing: false
        }))
      }
    }
  }, 1000)
}

const adjustTextareaHeight = () => {
  nextTick(() => {
    const textarea = messageInput.value
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
    }
  })
}

const scrollToBottom = () => {
  const container = messagesContainer.value
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

const shouldShowDateSeparator = (message, index) => {
  if (index === 0) return true

  const prevMessage = messages.value[index - 1]
  const messageDate = new Date(message.timestamp).toDateString()
  const prevDate = new Date(prevMessage.timestamp).toDateString()

  return messageDate !== prevDate
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (date.toDateString() === today.toDateString()) {
    return '오늘'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '어제'
  } else {
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// API 호출 메서드들
const getCurrentUser = async () => {
  // 토큰이 없으면 현재 사용자 정보를 가져올 수 없음
  if (!token.value) {
    throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.')
  }

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://34.47.106.179/accounts'
  const response = await fetch(`${apiBaseUrl}/user/`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Token ${token.value}`
    }
  })

  if (!response.ok) {
    throw new Error('사용자 정보를 가져올 수 없습니다.')
  }

  return await response.json()
}

const getRoomInfo = async () => {
  // 토큰이 없으면 채팅방 정보를 가져올 수 없음
  if (!token.value) {
    throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.')
  }

  try {
    const response = await fetch(`34.47.106.179/api/chat/room/${props.roomId}/`, {
      method: 'GET',
      headers: {
        'Authorization': `Token ${token.value}`,
        'X-Requested-With': 'XMLHttpRequest',
      }
    })

    if (!response.ok) {
      throw new Error('채팅방 정보를 가져올 수 없습니다.')
    }

    const data = await response.json()

    // 응답 데이터 구조에 맞게 처리
    return {
      room_id: data.room_id,
      partner: data.partner
    }
  } catch (error) {
    console.error('채팅방 데이터 불러오기 실패', error)
    throw error
  }
}

// 특정 사용자와의 채팅방 ID 조회 또는 생성
const getChatRoomWithUser = async (userId) => {
  if (!token.value) {
    throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.')
  }

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://34.47.106.179/api'
  const response = await fetch(`${apiBaseUrl}/chat/with/${userId}/`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Token ${token.value}`
    }
  })

  if (!response.ok) {
    throw new Error('채팅방을 생성하거나 조회할 수 없습니다.')
  }

  return await response.json()
}

// 가장 최근 채팅방 정보 조회
const getLatestChatRoom = async () => {
  if (!token.value) {
    throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.')
  }

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://34.47.106.179/api'
  const response = await fetch(`${apiBaseUrl}/chat/latest/`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Token ${token.value}`
    }
  })

  if (!response.ok) {
    throw new Error('최근 채팅방 정보를 가져올 수 없습니다.')
  }

  return await response.json()
}

// Watchers
watch(newMessage, () => {
  adjustTextareaHeight()
})

// Lifecycle
onMounted(async () => {
  await initializeChat()
  connectWebSocket()
  adjustTextareaHeight()
})

onUnmounted(() => {
  disconnectWebSocket()
  if (typingTimer.value) {
    clearTimeout(typingTimer.value)
  }
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh;
  background: #f8f9fa;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.back-btn:hover {
  background: rgba(255,255,255,0.1);
}

.partner-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.partner-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.3);
  object-fit: cover;
}

.partner-info h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.online-status {
  font-size: 12px;
  opacity: 0.8;
}

.online-status.online {
  color: #4ade80;
}

.connection-status {
  padding: 8px 16px;
  text-align: center;
  font-size: 14px;
  background: #fef3c7;
  color: #92400e;
  border-bottom: 1px solid #fbbf24;
}

.connection-status.error {
  background: #fecaca;
  color: #dc2626;
}

.connection-status.disconnected {
  background: #fecaca;
  color: #dc2626;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #6b7280;
  gap: 16px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.date-separator {
  text-align: center;
  margin: 20px 0;
  position: relative;
  color: #6b7280;
  font-size: 12px;
}

.date-separator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e5e7eb;
  z-index: 1;
}

.date-separator::after {
  content: '';
  background: #f8f9fa;
  padding: 0 16px;
  position: relative;
  z-index: 2;
}

.message {
  display: flex;
  margin-bottom: 12px;
}

.message.own {
  justify-content: flex-end;
}

.message.partner {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.sender-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.sender-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.sender-name {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  word-wrap: break-word;
  word-break: break-word;
}

.message.own .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.partner .message-bubble {
  background: white;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  color: #333333;
}

.message-bubble p {
  margin: 0;
  line-height: 1.4;
  white-space: pre-wrap;
}

.message-time {
  font-size: 11px;
  margin-top: 4px;
  opacity: 0.7;
  display: flex;
  align-items: center;
  gap: 4px;
}

.read-indicator {
  font-size: 10px;
  color: #4ade80;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #6b7280;
  font-size: 14px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.typing-dots {
  display: flex;
  gap: 2px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #6b7280;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.input-container {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  max-width: 100%;
}

.message-input {
  flex: 1;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  padding: 12px 16px;
  resize: none;
  outline: none;
  font-family: inherit;
  font-size: 16px;
  line-height: 1.4;
  min-height: 44px;
  max-height: 120px;
  transition: border-color 0.2s;
  color: #333333;
}

.message-input:focus {
  border-color: #667eea;
}

.message-input:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.send-button {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: transform 0.2s, box-shadow 0.2s;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-button:active:not(:disabled) {
  transform: scale(0.95);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 스크롤바 스타일링 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .messages-container {
    padding: 16px;
  }

  .message-content {
    max-width: 85%;
  }

  .input-container {
    padding: 12px 16px;
  }

  .chat-header {
    padding: 12px 16px;
  }

  .partner-info h3 {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .message-content {
    max-width: 90%;
  }

  .partner-avatar {
    width: 32px;
    height: 32px;
  }

  .partner-info h3 {
    font-size: 14px;
  }

  .online-status {
    font-size: 11px;
  }
}
</style>
