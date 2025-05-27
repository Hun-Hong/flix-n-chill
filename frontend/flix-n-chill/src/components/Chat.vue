<template>
  <div class="chat-container">
    <div class="chat-header">
      <h3>{{ roomName }}</h3>
      <div class="online-status" :class="{ connected: isConnected }">
        {{ isConnected ? '🟢 연결됨' : '🔴 연결 안됨' }}
      </div>
    </div>

    <div class="messages-container" ref="messagesContainer">
      <div 
        v-for="message in messages" 
        :key="message.id"
        class="message"
        :class="{ 'my-message': message.username === currentUser }"
      >
        <div class="message-header">
          <span class="username">{{ message.username }}</span>
          <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
        </div>
        <div class="message-content">{{ message.message }}</div>
      </div>
    </div>

    <div class="message-input-container">
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        type="text"
        placeholder="메시지를 입력하세요..."
        class="message-input"
        :disabled="!isConnected"
      />
      <button 
        @click="sendMessage" 
        class="send-button"
        :disabled="!isConnected || !newMessage.trim()"
      >
        전송
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useUserStore } from '@/stores/accounts'

const props = defineProps({
  roomId: {
    type: [String, Number],
    required: true
  },
  roomName: {
    type: String,
    default: '채팅방'
  }
})

const userStore = useUserStore()

// 반응형 데이터
const messages = ref([])
const newMessage = ref('')
const isConnected = ref(false)
const socket = ref(null)
const messagesContainer = ref(null)

// Computed
const currentUser = computed(() => userStore.user?.username)

// WebSocket 연결
const connectWebSocket = () => {
  const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const wsPath = `${wsScheme}://127.0.0.1:8000/ws/chat/${props.roomId}/`
  
  console.log('🔌 WebSocket 연결 시도:', wsPath)
  
  socket.value = new WebSocket(wsPath)

  socket.value.onopen = (event) => {
    console.log('✅ WebSocket 연결 성공')
    isConnected.value = true
  }

  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log('📩 메시지 수신:', data)
    
    messages.value.push({
      id: Date.now() + Math.random(),
      message: data.message,
      username: data.username,
      timestamp: data.timestamp
    })
    
    scrollToBottom()
  }

  socket.value.onclose = (event) => {
    console.log('❌ WebSocket 연결 종료')
    isConnected.value = false
  }

  socket.value.onerror = (error) => {
    console.error('🚨 WebSocket 오류:', error)
    isConnected.value = false
  }
}

// 메시지 전송
const sendMessage = () => {
  if (!newMessage.value.trim() || !isConnected.value) return

  const messageData = {
    message: newMessage.value,
    username: currentUser.value
  }

  console.log('📤 메시지 전송:', messageData)
  socket.value.send(JSON.stringify(messageData))
  
  newMessage.value = ''
}

// 스크롤을 맨 아래로
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 시간 포맷팅
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('ko-KR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 라이프사이클
onMounted(() => {
  console.log('🚀 채팅 컴포넌트 마운트, 룸 ID:', props.roomId)
  connectWebSocket()
})

onUnmounted(() => {
  console.log('🔚 채팅 컴포넌트 언마운트')
  if (socket.value) {
    socket.value.close()
  }
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-header h3 {
  margin: 0;
  color: #ffffff;
}

.online-status {
  font-size: 0.9rem;
  color: #ff6b6b;
}

.online-status.connected {
  color: #4ecdc4;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.message {
  margin-bottom: 1rem;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.message.my-message {
  background: rgba(219, 0, 0, 0.2);
  margin-left: 2rem;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.username {
  font-weight: 600;
  color: #4ecdc4;
}

.timestamp {
  color: rgba(255, 255, 255, 0.6);
}

.message-content {
  color: #ffffff;
  line-height: 1.4;
}

.message-input-container {
  display: flex;
  padding: 1rem;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.message-input {
  flex: 1;
  padding: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.message-input:focus {
  outline: none;
  border-color: #db0000;
}

.send-button {
  padding: 0.8rem 1.5rem;
  background: #db0000;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.send-button:hover:not(:disabled) {
  background: #c20000;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>