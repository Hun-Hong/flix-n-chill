<template>
  <div class="chat-page">
    <h1>영화 토론방 💬</h1>
    <ChatComponent 
      :room-id="roomId" 
      :room-name="`영화 토론방 #${roomId}`"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ChatComponent from '@/components/ChatComponent.vue'

const route = useRoute()
const roomId = computed(() => route.params.roomId)
</script>
<style>
</style>