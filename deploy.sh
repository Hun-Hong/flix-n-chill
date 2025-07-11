#!/bin/bash

# GCP VM 배포 스크립트
set -e

echo "🚀 Flix N Chill 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 확인
check_env() {
    log_info "환경 변수 확인 중..."
    
    if [ -z "$TMDB_API_KEY" ]; then
        log_error "TMDB_API_KEY 환경 변수가 설정되지 않았습니다."
        echo "export TMDB_API_KEY=your_api_key 를 실행하거나 .env 파일을 생성하세요."
        exit 1
    fi
    
    log_info "환경 변수 확인 완료"
}

# Docker 및 Docker Compose 설치 확인
check_docker() {
    log_info "Docker 설치 확인 중..."
    
    if ! command -v docker &> /dev/null; then
        log_warn "Docker가 설치되지 않았습니다. 설치를 시작합니다..."
        
        # Docker 설치
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        
        log_info "Docker 설치 완료"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_warn "Docker Compose가 설치되지 않았습니다. 설치를 시작합니다..."
        
        # Docker Compose 설치
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        log_info "Docker Compose 설치 완료"
    fi
}

# 방화벽 설정
setup_firewall() {
    log_info "방화벽 설정 중..."
    
    # UFW 설치 및 설정 (Ubuntu/Debian)
    if command -v ufw &> /dev/null; then
        sudo ufw allow 22    # SSH
        sudo ufw allow 80    # HTTP
        sudo ufw allow 443   # HTTPS
        sudo ufw --force enable
        log_info "방화벽 설정 완료"
    else
        log_warn "UFW를 찾을 수 없습니다. 수동으로 방화벽을 설정하세요."
    fi
}

# 프론트엔드 빌드
build_frontend() {
    log_info "프론트엔드 빌드 중..."
    
    cd frontend/flix-n-chill
    
    # Node.js 설치 확인
    if ! command -v node &> /dev/null; then
        log_error "Node.js가 설치되지 않았습니다."
        echo "Node.js 18 이상을 설치하세요: https://nodejs.org/"
        exit 1
    fi
    
    # 패키지 설치 및 빌드
    npm ci
    npm run build
    
    cd ../..
    log_info "프론트엔드 빌드 완료"
}

# 환경 변수 파일 생성
create_env_file() {
    log_info "환경 변수 파일 생성 중..."
    
    cat > .env << EOF
# Django 설정
DJANGO_SECRET_KEY=$(openssl rand -base64 32)
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,$(curl -s ifconfig.me)

# TMDB API
TMDB_API_KEY=${TMDB_API_KEY}

# 데이터베이스 (SQLite - 기본값)
DATABASE_URL=sqlite:///db.sqlite3
EOF
    
    log_info "환경 변수 파일 생성 완료"
}

# Docker 이미지 빌드 및 실행
deploy_docker() {
    log_info "Docker 컨테이너 배포 중..."
    
    # 기존 컨테이너 중지 및 제거
    docker-compose down 2>/dev/null || true
    
    # 이미지 빌드
    docker-compose build
    
    # 컨테이너 실행
    docker-compose up -d
    
    log_info "Docker 컨테이너 배포 완료"
}

# 헬스 체크
health_check() {
    log_info "서비스 헬스 체크 중..."
    
    sleep 10  # 서비스 시작 대기
    
    if curl -f http://localhost > /dev/null 2>&1; then
        log_info "✅ 서비스가 정상적으로 실행 중입니다!"
        echo "🌐 접속 URL: http://$(curl -s ifconfig.me)"
    else
        log_error "❌ 서비스 실행에 실패했습니다."
        echo "로그 확인: docker-compose logs"
        exit 1
    fi
}

# 메인 실행
main() {
    log_info "🎬 Flix N Chill GCP VM 배포 스크립트"
    echo "======================================"
    
    check_env
    check_docker
    setup_firewall
    build_frontend
    create_env_file
    deploy_docker
    health_check
    
    echo ""
    echo "🎉 배포 완료!"
    echo "📋 유용한 명령어:"
    echo "   - 로그 확인: docker-compose logs"
    echo "   - 컨테이너 재시작: docker-compose restart"
    echo "   - 컨테이너 중지: docker-compose down"
    echo "   - 데이터베이스 마이그레이션: docker-compose exec web python /app/backend/manage.py migrate"
}

# 스크립트 실행
main "$@"