# 플릭스 앤 칠 (Flix N Chill)

Vue 3와 Vite를 사용한 영화 추천 커뮤니티 플랫폼입니다.

## 권장 개발 환경

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (Vetur는 비활성화)

## 설정 커스터마이징

[Vite 설정 가이드](https://vite.dev/config/)를 참고하세요.

## 환경 설정

1. 환경 변수 템플릿 복사:
```sh
cp .env.example .env
```

2. `.env` 파일을 수정하여 설정값 입력:
```sh
# 개발 환경 (기본값)
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# 배포 환경인 경우 서버 IP 입력
# VITE_API_BASE_URL=http://your-server-ip
# VITE_WS_BASE_URL=ws://your-server-ip
```

## 프로젝트 설치

```sh
npm install
```

### 개발 서버 실행 (Hot Reload)

```sh
npm run dev
```

### 배포용 빌드

```sh
npm run build
```

### 빌드 결과 미리보기

```sh
npm run preview
```

## API 설정

모든 API URL은 `src/config/api.js`에서 중앙 관리됩니다. 시스템이 자동으로 환경을 감지합니다:

- **개발 모드** (`npm run dev`): `localhost:8000` 자동 사용
- **배포 모드** (`npm run build`): 환경 변수 `VITE_API_BASE_URL` **필수 설정**

⚠️ **배포 시 주의사항**: 배포 환경에서는 반드시 `.env` 파일에 서버 주소를 설정해야 합니다.

```sh
# 배포용 .env 파일 예시
VITE_API_BASE_URL=http://your-server-domain
VITE_WS_BASE_URL=ws://your-server-domain
```

## 주요 기능

- 🎬 영화 검색 및 상세 정보
- 💬 실시간 채팅
- 👥 사용자 팔로우/팔로잉
- ⭐ 영화 평점 및 리뷰
- 🤖 개인 맞춤 영화 추천
- 📊 장르별 취향 분석