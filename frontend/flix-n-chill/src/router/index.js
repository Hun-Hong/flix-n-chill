// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// 뷰 컴포넌트들 import
import HomePage from '@/views/HomePage.vue'
import SearchPage from '@/views/SearchPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import SignupPage from '@/views/SignupPage.vue'
import MyPage from '@/views/MyPage.vue'
import SettingsPage from '@/views/SettingsPage.vue'
import MovieSurveyPage from '@/views/MovieSurveyPage.vue'

// 장르 페이지 - 하나로 통합
import GenrePage from '@/views/GenrePage.vue'


const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: {
      title: 'FLIXnCHILL - Home'
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: SearchPage,
    meta: {
      title: 'FLIXnCHILL - Search'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: {
      title: 'FLIXnCHILL - Sign in',
      requiresGuest: true
    }
  },
  {
    path: '/signup',
    name: 'Signup',
    component: SignupPage,
    meta: {
      title: 'FLIXnCHILL - Sign up',
      requiresGuest: true
    }
  },
  {
    path: '/my-page',
    name: 'MyPage',
    component: MyPage,
    meta: {
      title: 'FLIXnCHILL - My page',
      requiresAuth: true
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage,
    meta: {
      title: 'FLIXnCHILL - Settings',
      requiresAuth: true
    }
  },
  
  // 장르 페이지 - 하나의 컴포넌트로
  {
    path: '/genre',
    name: 'Genre',
    component: GenrePage,
    meta: {
      title: 'FLIXnCHILL - 장르별 영화'
    }
    // query 예시: /genre?type=action, /genre?type=comedy
  },
  
  // 영화 상세 페이지 (동적 라우트)
  {
    path: '/movie/:id',
    name: 'MovieDetail',
    component: () => import('@/views/MovieDetailPage.vue'),
    meta: {
      title: 'FLIXnCHILL - 영화 상세'
    }
  },
  {
    path: '/survey',
    name: 'movie-survey', 
    component: MovieSurveyPage
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomePage,
      meta: {
        title: 'FLIXnCHILL - Home'
      }
    },
    {
      path: '/search',
      name: 'Search',
      component: SearchPage,
      meta: {
        title: 'FLIXnCHILL - Search'
      }
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginPage,
      meta: {
        title: 'FLIXnCHILL - Sign in',
        requiresGuest: true
      }
    },
    {
      path: '/signup',
      name: 'Signup',
      component: SignupPage,
      meta: {
        title: 'FLIXnCHILL - Sign up',
        requiresGuest: true
      }
    },
    {
      path: '/my-page',
      name: 'MyPage',
      component: MyPage,
      meta: {
        title: 'FLIXnCHILL - My page',
        requiresAuth: true
      }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: SettingsPage,
      meta: {
        title: 'FLIXnCHILL - Settings',
        requiresAuth: true
      }
    },
    
    // 장르 페이지 - 하나의 컴포넌트로
    {
      path: '/genre',
      name: 'Genre',
      component: GenrePage,
      meta: {
        title: 'FLIXnCHILL - 장르별 영화'
      }
      // query 예시: /genre?type=action, /genre?type=comedy
    },
    
    // 영화 상세 페이지 (동적 라우트)
    {
      path: '/movie/:id',
      name: 'MovieDetail',
      component: () => import('@/views/MovieDetailPage.vue'),
      meta: {
        title: 'FLIXnCHILL - 영화 상세'
      }
    },
    {
      path: '/survey',
      name: 'movie-survey', 
      component: MovieSurveyPage
    }
  ]
})
// 라우트 가드
router.beforeEach((to, from, next) => {
  // 장르 페이지의 경우 타이틀을 동적으로 설정
  if (to.name === 'Genre' && to.query.type) {
    const genreNames = {
      action: '액션',
      comedy: '코미디', 
      drama: '드라마',
      horror: '호러',
      adventure: '모험',
      family: '가족',
      romance: '로맨스'
    }
    const genreName = genreNames[to.query.type] || '영화'
    document.title = `FLIXnCHILL - ${genreName}`
  } else if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // 로그인 상태 체크
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
  // 예: 로그인을 이미 한 사용자가 다시 로그인 페이지로 가려고 하면 -> 홈 페이지를 보여줌  
  } else if (to.meta.requiresGuest && isLoggedIn) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router