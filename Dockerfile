# 멀티스테이지 빌드로 Frontend와 Backend를 하나의 컨테이너에서 실행

# Stage 1: Frontend 빌드
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/flix-n-chill/package*.json ./
RUN npm ci

COPY frontend/flix-n-chill/ ./
RUN npm run build

# Stage 2: Backend 설정 및 최종 이미지
FROM python:3.11-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    redis-server \
    procps \
    net-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 백엔드 코드 복사
COPY backend/ ./backend/

# 프론트엔드 빌드 결과 복사
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# Nginx 설정
COPY deploy/nginx.conf /etc/nginx/sites-available/default
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 정적 파일 및 미디어 디렉토리 생성
RUN mkdir -p /app/backend/static /app/backend/media

# 데이터베이스 디렉토리 권한 설정 및 기존 db 파일 정리
RUN rm -rf /app/backend/db.sqlite3

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=flix_n_chill.settings

# 포트 노출
EXPOSE 80

# 실행 권한 설정
RUN chmod +x /usr/bin/supervisord

# 컨테이너 시작 시 실행할 명령
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]