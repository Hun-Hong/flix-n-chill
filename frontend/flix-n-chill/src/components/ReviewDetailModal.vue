<template>
    <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-container" @click.stop>
            <div class="modal-header">
                <h2 class="modal-title">리뷰 상세</h2>
                <button class="close-btn" @click="$emit('close')">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>

            <div class="modal-body">
                <!-- 영화 정보 -->
                <div class="movie-info">
                    <img :src="review?.moviePoster || '/api/placeholder/100/150'" :alt="review?.movieTitle"
                        class="movie-poster">
                    <div class="movie-details">
                        <h3 class="movie-title">{{ review?.movieTitle }}</h3>
                        <div class="movie-rating">
                            <div class="stars">
                                <i v-for="star in 5" :key="star" class="bi"
                                    :class="star <= review?.rating ? 'bi-star-fill' : 'bi-star'"></i>
                            </div>
                            <span class="rating-text">{{ review?.rating }}/5</span>
                        </div>
                    </div>
                </div>

                <!-- 리뷰어 정보 -->
                <div class="reviewer-info">
                    <div class="reviewer-avatar">
                        <img :src="review?.reviewer?.avatar || '/api/placeholder/50/50'"
                            :alt="review?.reviewer?.nickname" class="avatar">
                    </div>
                    <div class="reviewer-details">
                        <h4 class="reviewer-name">{{ review?.reviewer?.nickname }}</h4>
                        <p class="review-date">{{ formatDate(review?.createdAt) }}</p>
                    </div>
                </div>

                <!-- 리뷰 내용 -->
                <div class="review-content">
                    <p class="review-text">{{ review?.content }}</p>
                </div>

                <!-- 리뷰 액션 -->
                <div class="review-actions">
                    <button class="action-btn like-btn" :class="{ 'liked': review?.isLiked }" @click="toggleLike">
                        <i :class="review?.isLiked ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
                        <span>{{ review?.likesCount || 0 }}</span>
                    </button>
                    <button class="action-btn comment-btn" @click="focusCommentInput">
                        <i class="bi bi-chat"></i>
                        <span>{{ comments.length }}</span>
                    </button>
                    <button class="action-btn share-btn" @click="shareReview">
                        <i class="bi bi-share"></i>
                        <span>공유</span>
                    </button>
                </div>

                <!-- 댓글 섹션 -->
                <div class="comments-section">
                    <h4 class="comments-title">
                        댓글 <span class="comments-count">({{ comments.length }})</span>
                    </h4>

                    <!-- 댓글 입력 -->
                    <div class="comment-input-section">
                        <div class="user-avatar">
                            <img :src="currentUser?.avatar || '/api/placeholder/40/40'" :alt="currentUser?.nickname"
                                class="avatar">
                        </div>
                        <div class="comment-input-container">
                            <textarea ref="commentInput" v-model="newComment" placeholder="댓글을 작성해주세요..."
                                class="comment-input" rows="2" @keydown.ctrl.enter="submitComment"></textarea>
                            <div class="comment-input-actions">
                                <button class="submit-comment-btn" @click="submitComment"
                                    :disabled="!newComment.trim()">
                                    댓글 작성
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- 댓글 목록 -->
                    <div class="comments-list">
                        <div v-for="comment in comments" :key="comment.id" class="comment-item">
                            <div class="comment-avatar">
                                <img :src="comment.user?.avatar || '/api/placeholder/40/40'"
                                    :alt="comment.user?.nickname" class="avatar">
                            </div>
                            <div class="comment-content">
                                <div class="comment-header">
                                    <h5 class="comment-author">{{ comment.user?.nickname }}</h5>
                                    <span class="comment-date">{{ formatRelativeTime(comment.createdAt) }}</span>
                                </div>
                                <p class="comment-text">{{ comment.content }}</p>

                                <!-- 댓글 액션 -->
                                <div class="comment-actions">
                                    <button class="comment-action-btn like-btn" :class="{ 'liked': comment.isLiked }"
                                        @click="toggleCommentLike(comment)">
                                        <i :class="comment.isLiked ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
                                        <span v-if="comment.likesCount > 0">{{ comment.likesCount }}</span>
                                    </button>
                                    <button class="comment-action-btn reply-btn" @click="toggleReplyInput(comment.id)">
                                        <i class="bi bi-reply"></i>
                                        답글
                                    </button>
                                    <button v-if="comment.user?.id === currentUser?.id"
                                        class="comment-action-btn delete-btn" @click="deleteComment(comment.id)">
                                        <i class="bi bi-trash3"></i>
                                        삭제
                                    </button>
                                </div>

                                <!-- 대댓글 입력 -->
                                <div v-if="replyingToComment === comment.id" class="reply-input-section">
                                    <div class="user-avatar">
                                        <img :src="currentUser?.avatar || '/api/placeholder/32/32'"
                                            :alt="currentUser?.nickname" class="avatar small">
                                    </div>
                                    <div class="reply-input-container">
                                        <textarea v-model="newReply"
                                            :placeholder="`@${comment.user?.nickname}님에게 답글...`" class="reply-input"
                                            rows="2" @keydown.ctrl.enter="submitReply(comment.id)"></textarea>
                                        <div class="reply-input-actions">
                                            <button class="cancel-reply-btn" @click="cancelReply">
                                                취소
                                            </button>
                                            <button class="submit-reply-btn" @click="submitReply(comment.id)"
                                                :disabled="!newReply.trim()">
                                                답글 작성
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <!-- 대댓글 목록 -->
                                <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
                                    <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                                        <div class="reply-avatar">
                                            <img :src="reply.user?.avatar || '/api/placeholder/32/32'"
                                                :alt="reply.user?.nickname" class="avatar small">
                                        </div>
                                        <div class="reply-content">
                                            <div class="reply-header">
                                                <h6 class="reply-author">{{ reply.user?.nickname }}</h6>
                                                <span class="reply-date">{{ formatRelativeTime(reply.createdAt)
                                                    }}</span>
                                            </div>
                                            <p class="reply-text">
                                                <span v-if="reply.parentUser" class="mention">@{{
                                                    reply.parentUser?.nickname }}</span>
                                                {{ reply.content }}
                                            </p>

                                            <!-- 대댓글 액션 -->
                                            <div class="reply-actions">
                                                <button class="reply-action-btn like-btn"
                                                    :class="{ 'liked': reply.isLiked }" @click="toggleReplyLike(reply)">
                                                    <i :class="reply.isLiked ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
                                                    <span v-if="reply.likesCount > 0">{{ reply.likesCount }}</span>
                                                </button>
                                                <button class="reply-action-btn reply-btn"
                                                    @click="replyToReply(comment.id, reply.user)">
                                                    <i class="bi bi-reply"></i>
                                                    답글
                                                </button>
                                                <button v-if="reply.user?.id === currentUser?.id"
                                                    class="reply-action-btn delete-btn"
                                                    @click="deleteReply(comment.id, reply.id)">
                                                    <i class="bi bi-trash3"></i>
                                                    삭제
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

// ReviewDetailModal.vue의 script 부분 수정

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useUserStore } from '@/stores/accounts'
import axios from 'axios'

// Props & Emits
const props = defineProps({
    show: {
        type: Boolean,
        default: false
    },
    reviewId: {
        type: [Number, String],
        default: null
    }
})

const emit = defineEmits(['close', 'like-toggled', 'comment-added'])

// Stores
const userStore = useUserStore()

// 상태 관리
const review = ref(null)
const comments = ref([])
const loading = ref(false)
const newComment = ref('')
const newReply = ref('')
const replyingToComment = ref(null)
const commentInput = ref(null)

// 현재 사용자 정보
const currentUser = computed(() => ({
    id: userStore.userData?.id,
    nickname: userStore.userData?.nickname || userStore.userData?.username,
    avatar: userStore.userData?.profile_image || '/api/placeholder/40/40'
}))

// API 호출 함수들
const fetchReviewDetail = async () => {
    if (!props.reviewId) return

    loading.value = true
    try {
        const response = await axios.get(`/api/v1/reviews/${props.reviewId}/`, {
            headers: {
                'Authorization': userStore.token ? `Token ${userStore.token}` : ''
            }
        })

        review.value = {
            id: response.data.id,
            movieTitle: response.data.movie.title,
            moviePoster: response.data.movie.poster_path
                ? `https://image.tmdb.org/t/p/w500${response.data.movie.poster_path}`
                : '/api/placeholder/100/150',
            rating: response.data.rating,
            content: response.data.comment,
            createdAt: response.data.created_at,
            likesCount: response.data.likes_count,
            isLiked: response.data.is_liked,
            reviewer: {
                id: response.data.user.id,
                nickname: response.data.user.username,
                avatar: response.data.user.profile_image || '/api/placeholder/50/50'
            }
        }

        // 댓글 데이터 변환
        comments.value = response.data.comments.map(transformComment)

    } catch (error) {
        console.error('리뷰 상세 조회 실패:', error)
    } finally {
        loading.value = false
    }
}

const transformComment = (comment) => ({
    id: comment.id,
    user: {
        id: comment.user.id,
        nickname: comment.user.username,
        avatar: comment.user.profile_image || '/api/placeholder/40/40'
    },
    content: comment.content,
    createdAt: comment.created_at,
    likesCount: comment.likes_count,
    isLiked: comment.is_liked,
    replies: comment.replies?.map(transformComment) || []
})

// 좋아요 토글
const toggleLike = async () => {
    if (!userStore.token) {
        alert('로그인이 필요합니다.')
        return
    }

    try {
        if (review.value.isLiked) {
            await axios.delete(`/api/v1/reviews/${props.reviewId}/like/`, {
                headers: { 'Authorization': `Token ${userStore.token}` }
            })
            review.value.likesCount--
        } else {
            await axios.post(`/api/v1/reviews/${props.reviewId}/like/`, {}, {
                headers: { 'Authorization': `Token ${userStore.token}` }
            })
            review.value.likesCount++
        }
        review.value.isLiked = !review.value.isLiked
        emit('like-toggled', review.value)
    } catch (error) {
        console.error('좋아요 토글 실패:', error)
        alert('좋아요 처리 중 오류가 발생했습니다.')
    }
}

// 댓글 작성
const submitComment = async () => {
    if (!newComment.value.trim()) return
    if (!userStore.token) {
        alert('로그인이 필요합니다.')
        return
    }

    try {
        const response = await axios.post(`/api/v1/reviews/${props.reviewId}/comments/`, {
            content: newComment.value.trim()
        }, {
            headers: { 'Authorization': `Token ${userStore.token}` }
        })

        const newCommentData = transformComment(response.data)
        comments.value.unshift(newCommentData)
        newComment.value = ''
        emit('comment-added', newCommentData)
    } catch (error) {
        console.error('댓글 작성 실패:', error)
        alert('댓글 작성 중 오류가 발생했습니다.')
    }
}

// 댓글 좋아요 토글
const toggleCommentLike = async (comment) => {
    if (!userStore.token) {
        alert('로그인이 필요합니다.')
        return
    }

    try {
        if (comment.isLiked) {
            await axios.delete(`/api/v1/comments/${comment.id}/like/`, {
                headers: { 'Authorization': `Token ${userStore.token}` }
            })
            comment.likesCount--
        } else {
            await axios.post(`/api/v1/comments/${comment.id}/like/`, {}, {
                headers: { 'Authorization': `Token ${userStore.token}` }
            })
            comment.likesCount++
        }
        comment.isLiked = !comment.isLiked
    } catch (error) {
        console.error('댓글 좋아요 토글 실패:', error)
    }
}

// 댓글 삭제
const deleteComment = async (commentId) => {
    if (!confirm('댓글을 삭제하시겠습니까?')) return

    try {
        await axios.delete(`/api/v1/comments/${commentId}/`, {
            headers: { 'Authorization': `Token ${userStore.token}` }
        })

        const index = comments.value.findIndex(c => c.id === commentId)
        if (index !== -1) {
            comments.value.splice(index, 1)
        }
    } catch (error) {
        console.error('댓글 삭제 실패:', error)
        alert('댓글 삭제 중 오류가 발생했습니다.')
    }
}

// 대댓글 작성
const submitReply = async (commentId) => {
    if (!newReply.value.trim()) return
    if (!userStore.token) {
        alert('로그인이 필요합니다.')
        return
    }

    try {
        const response = await axios.post(`/api/v1/comments/${commentId}/reply/`, {
            content: newReply.value.trim()
        }, {
            headers: { 'Authorization': `Token ${userStore.token}` }
        })

        const comment = comments.value.find(c => c.id === commentId)
        if (comment) {
            const newReplyData = transformComment(response.data)
            if (!comment.replies) comment.replies = []
            comment.replies.push(newReplyData)
        }

        cancelReply()
    } catch (error) {
        console.error('대댓글 작성 실패:', error)
        alert('대댓글 작성 중 오류가 발생했습니다.')
    }
}

// 대댓글 좋아요 토글
const toggleReplyLike = async (reply) => {
    if (!userStore.token) {
        alert('로그인이 필요합니다.')
        return
    }

    try {
        if (reply.isLiked) {
            await axios.delete(`/api/v1/comments/${reply.id}/like/`, {
                headers: { 'Authorization': `Token ${userStore.token}` }
            })
            reply.likesCount--
        } else {
            await axios.post(`/api/v1/comments/${reply.id}/like/`, {}, {
                headers: { 'Authorization': `Token ${userStore.token}` }
            })
            reply.likesCount++
        }
        reply.isLiked = !reply.isLiked
    } catch (error) {
        console.error('대댓글 좋아요 토글 실패:', error)
    }
}

// 대댓글 삭제
const deleteReply = async (commentId, replyId) => {
    if (!confirm('답글을 삭제하시겠습니까?')) return

    try {
        await axios.delete(`/api/v1/comments/${replyId}/`, {
            headers: { 'Authorization': `Token ${userStore.token}` }
        })

        const comment = comments.value.find(c => c.id === commentId)
        if (comment && comment.replies) {
            const index = comment.replies.findIndex(r => r.id === replyId)
            if (index !== -1) {
                comment.replies.splice(index, 1)
            }
        }
    } catch (error) {
        console.error('대댓글 삭제 실패:', error)
        alert('답글 삭제 중 오류가 발생했습니다.')
    }
}

// 기타 함수들
const toggleReplyInput = (commentId) => {
    replyingToComment.value = replyingToComment.value === commentId ? null : commentId
    newReply.value = ''
}

const cancelReply = () => {
    replyingToComment.value = null
    newReply.value = ''
}

const replyToReply = (commentId, targetUser) => {
    replyingToComment.value = commentId
    newReply.value = `@${targetUser.nickname} `
}

const shareReview = () => {
    // 리뷰 공유 로직
    console.log('리뷰 공유')
}

const focusCommentInput = () => {
    nextTick(() => {
        commentInput.value?.focus()
    })
}

const handleOverlayClick = () => {
    emit('close')
}

// 유틸리티 함수들 (기존과 동일)
const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const formatRelativeTime = (dateString) => {
    const now = new Date()
    const date = new Date(dateString)
    const diffMs = now - date
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        if (diffHours === 0) {
            const diffMinutes = Math.floor(diffMs / (1000 * 60))
            return `${diffMinutes}분 전`
        }
        return `${diffHours}시간 전`
    } else if (diffDays === 1) {
        return '어제'
    } else if (diffDays < 7) {
        return `${diffDays}일 전`
    } else {
        return formatDate(dateString).split(' ').slice(0, 3).join(' ')
    }
}

// 생명주기
onMounted(() => {
    if (props.show && props.reviewId) {
        fetchReviewDetail()
    }
})

// 모달이 열릴 때마다 데이터 가져오기
watch(() => props.show, (newShow) => {
    if (newShow && props.reviewId) {
        fetchReviewDetail()
    }

    // ESC 키 이벤트 처리
    if (newShow) {
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                emit('close')
            }
        }
        document.addEventListener('keydown', handleEscape)

        return () => {
            document.removeEventListener('keydown', handleEscape)
        }
    }
})

watch(() => props.reviewId, (newReviewId) => {
    if (props.show && newReviewId) {
        fetchReviewDetail()
    }
})
</script>

<style scoped>
/* 모달 기본 스타일 */
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
    padding: 2rem;
}

.modal-container {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    width: 100%;
    max-width: 800px;
    max-height: 90vh;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 2rem 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
}

.close-btn {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 50%;
    transition: all 0.3s ease;
}

.close-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
}

.modal-body {
    padding: 2rem;
    overflow-y: auto;
    max-height: calc(90vh - 100px);
}

/* 영화 정보 */
.movie-info {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.movie-poster {
    width: 100px;
    height: 150px;
    object-fit: cover;
    border-radius: 12px;
}

.movie-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.movie-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1rem;
}

.movie-rating {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.stars {
    display: flex;
    gap: 0.3rem;
    color: #ffd700;
    font-size: 1.2rem;
}

.rating-text {
    font-size: 1.1rem;
    color: #ffffff;
    font-weight: 600;
}

/* 리뷰어 정보 */
.reviewer-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.reviewer-avatar .avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.reviewer-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0 0 0.2rem 0;
}

.review-date {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.9rem;
    margin: 0;
}

/* 리뷰 내용 */
.review-content {
    margin-bottom: 2rem;
}

.review-text {
    color: #ffffff;
    font-size: 1.1rem;
    line-height: 1.7;
    margin: 0;
}

/* 리뷰 액션 */
.review-actions {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    padding: 1rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.action-btn {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #ffffff;
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
}

.action-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.4);
}

.like-btn.liked {
    border-color: #e74c3c;
    color: #e74c3c;
}

/* 댓글 섹션 */
.comments-section {
    margin-top: 2rem;
}

.comments-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.comments-count {
    color: rgba(255, 255, 255, 0.6);
    font-weight: 400;
}

/* 댓글 입력 */
.comment-input-section {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}

.user-avatar .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.user-avatar .avatar.small {
    width: 32px;
    height: 32px;
}

.comment-input-container {
    flex: 1;
}

.comment-input {
    width: 100%;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 1rem;
    color: #ffffff;
    font-size: 1rem;
    line-height: 1.5;
    resize: vertical;
    min-height: 80px;
    transition: all 0.3s ease;
}

.comment-input:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.4);
    background: rgba(255, 255, 255, 0.08);
}

.comment-input::placeholder {
    color: rgba(255, 255, 255, 0.5);
}

.comment-input-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.5rem;
}

.submit-comment-btn {
    background: linear-gradient(135deg, #3498db, #2980b9);
    border: none;
    color: #ffffff;
    padding: 0.75rem 1.5rem;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.submit-comment-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #2980b9, #21618c);
    transform: translateY(-1px);
}

.submit-comment-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* 댓글 목록 */
.comments-list {
    space-y: 1.5rem;
}

.comment-item {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.comment-avatar .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.comment-content {
    flex: 1;
}

.comment-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.5rem;
}

.comment-author {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
}

.comment-date {
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.85rem;
}

.comment-text {
    color: #ffffff;
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 0.8rem;
}

.comment-actions {
    display: flex;
    gap: 1rem;
}

.comment-action-btn {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    cursor: pointer;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    transition: color 0.3s ease;
}

.comment-action-btn:hover {
    color: rgba(255, 255, 255, 0.9);
}

.comment-action-btn.liked {
    color: #e74c3c;
}

/* 대댓글 입력 */
.reply-input-section {
    display: flex;
    gap: 0.8rem;
    margin-top: 1rem;
    padding-left: 1rem;
    border-left: 2px solid rgba(255, 255, 255, 0.1);
}

.reply-input-container {
    flex: 1;
}

.reply-input {
    width: 100%;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 0.8rem;
    color: #ffffff;
    font-size: 0.9rem;
    line-height: 1.4;
    resize: vertical;
    min-height: 60px;
    transition: all 0.3s ease;
}

.reply-input:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.05);
}

.reply-input::placeholder {
    color: rgba(255, 255, 255, 0.4);
}

.reply-input-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.cancel-reply-btn {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.7);
    padding: 0.5rem 1rem;
    border-radius: 15px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.3s ease;
}

.cancel-reply-btn:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.3);
}

.submit-reply-btn {
    background: linear-gradient(135deg, #27ae60, #229954);
    border: none;
    color: #ffffff;
    padding: 0.5rem 1rem;
    border-radius: 15px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.submit-reply-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #229954, #1e8449);
    transform: translateY(-1px);
}

.submit-reply-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* 대댓글 목록 */
.replies-list {
    margin-top: 1rem;
    padding-left: 1rem;
    border-left: 2px solid rgba(255, 255, 255, 0.1);
}

.reply-item {
    display: flex;
    gap: 0.8rem;
    margin-bottom: 1rem;
}

.reply-avatar .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.reply-content {
    flex: 1;
}

.reply-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.3rem;
}

.reply-author {
    font-size: 0.9rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
}

.reply-date {
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.8rem;
}

.reply-text {
    color: #ffffff;
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 0.6rem;
}

.mention {
    color: #3498db;
    font-weight: 600;
}

.reply-actions {
    display: flex;
    gap: 0.8rem;
}

.reply-action-btn {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    transition: color 0.3s ease;
}

.reply-action-btn:hover {
    color: rgba(255, 255, 255, 0.8);
}

.reply-action-btn.liked {
    color: #e74c3c;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
    .modal-overlay {
        padding: 1rem;
    }

    .modal-container {
        max-height: 95vh;
    }

    .modal-header {
        padding: 1.5rem 1.5rem 1rem;
    }

    .modal-body {
        padding: 1.5rem;
    }

    .movie-info {
        flex-direction: column;
        text-align: center;
    }

    .movie-poster {
        width: 80px;
        height: 120px;
        align-self: center;
    }

    .movie-title {
        font-size: 1.5rem;
    }

    .review-actions {
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .action-btn {
        flex: 1;
        min-width: 100px;
        justify-content: center;
    }

    .comment-input-section,
    .reply-input-section {
        flex-direction: column;
        gap: 0.8rem;
    }

    .user-avatar {
        align-self: flex-start;
    }
}

@media (max-width: 480px) {
    .modal-header {
        padding: 1rem;
    }

    .modal-body {
        padding: 1rem;
    }

    .modal-title {
        font-size: 1.3rem;
    }

    .movie-info {
        padding: 1rem;
    }

    .movie-title {
        font-size: 1.3rem;
    }

    .comment-item,
    .reply-item {
        gap: 0.8rem;
    }
}

/* 스크롤바 */
.modal-body::-webkit-scrollbar {
    width: 6px;
}

.modal-body::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}

/* 애니메이션 */
.modal-overlay {
    animation: fadeIn 0.3s ease;
}

.modal-container {
    animation: slideIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(-20px);
    }

    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
</style>