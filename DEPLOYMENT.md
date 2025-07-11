# GCP VM 배포 가이드 📚

Flix N Chill 프로젝트를 GCP VM에 올인원으로 배포하는 방법을 안내합니다.

## 🚀 빠른 시작

### 1단계: GCP VM 생성

```bash
# GCP Console에서 VM 인스턴스 생성
# - Machine type: e2-medium (2 vCPU, 4GB RAM) 이상 권장
# - Boot disk: Ubuntu 20.04 LTS
# - Firewall: HTTP, HTTPS 트래픽 허용
```

### 2단계: VM 접속 및 코드 다운로드

```bash
# VM에 SSH 접속
gcloud compute ssh your-vm-instance

# 코드 클론
git clone https://github.com/your-username/flix-n-chill.git
cd flix-n-chill
```

### 3단계: 환경 변수 설정

```bash
# TMDB API 키 설정 (필수)
export TMDB_API_KEY="your-tmdb-api-key"

# 또는 .env 파일 생성
cp .env.production .env
# .env 파일을 편집하여 실제 값 입력
nano .env
```

### 4단계: 자동 배포 실행

```bash
# 배포 스크립트 실행 (모든 설정 자동화)
chmod +x deploy.sh
./deploy.sh
```

## 📋 상세 배포 가이드

### 시스템 요구사항

- **OS**: Ubuntu 20.04 LTS 이상
- **CPU**: 2 vCPU 이상
- **RAM**: 4GB 이상
- **Storage**: 20GB 이상
- **포트**: 80 (HTTP), 443 (HTTPS), 22 (SSH)

### 필수 환경 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `TMDB_API_KEY` | TMDB API 키 (필수) | `abc123def456...` |
| `DJANGO_SECRET_KEY` | Django 보안 키 | 자동 생성 |
| `DJANGO_DEBUG` | 디버그 모드 | `False` |
| `DJANGO_ALLOWED_HOSTS` | 허용 도메인 | `your-domain.com,server-ip` |

### 수동 배포 (고급 사용자)

#### 1. 시스템 패키지 설치

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 재로그인 (Docker 그룹 적용)
exit
# SSH 재접속
```

#### 2. 프론트엔드 빌드

```bash
# Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 프론트엔드 빌드
cd frontend/flix-n-chill
npm ci
npm run build
cd ../..
```

#### 3. 환경 설정

```bash
# 환경 변수 파일 생성
cat > .env << EOF
DJANGO_SECRET_KEY=$(openssl rand -base64 32)
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,$(curl -s ifconfig.me),127.0.0.1,localhost
TMDB_API_KEY=your-tmdb-api-key-here
EOF
```

#### 4. 배포 실행

```bash
# Docker 이미지 빌드 및 실행
docker-compose build
docker-compose up -d

# 서비스 상태 확인
docker-compose ps
docker-compose logs
```

## 🔧 관리 명령어

### 기본 명령어

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs
docker-compose logs web  # 특정 서비스 로그

# 서비스 재시작
docker-compose restart

# 서비스 중지
docker-compose down

# 서비스 시작
docker-compose up -d
```

### 데이터베이스 관리

```bash
# 마이그레이션 실행
docker-compose exec web python /app/backend/manage.py migrate

# 슈퍼유저 생성
docker-compose exec web python /app/backend/manage.py createsuperuser

# 정적 파일 수집
docker-compose exec web python /app/backend/manage.py collectstatic --noinput
```

### 백업

```bash
# 데이터베이스 백업
docker-compose exec web python /app/backend/manage.py dumpdata > backup.json

# 미디어 파일 백업
tar -czf media_backup.tar.gz backend/media/
```

## 🌐 도메인 연결

### DNS 설정

1. 도메인 DNS에서 A 레코드 추가:
   ```
   Type: A
   Name: @ (또는 www)
   Value: [GCP VM의 외부 IP]
   TTL: 300
   ```

2. 환경 변수 업데이트:
   ```bash
   # .env 파일에서 DJANGO_ALLOWED_HOSTS 수정
   DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com,VM-IP
   ```

3. 컨테이너 재시작:
   ```bash
   docker-compose restart
   ```

### SSL 인증서 (선택사항)

```bash
# Certbot을 이용한 Let's Encrypt SSL 설정
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🛠️ 트러블슈팅

### 일반적인 문제

**1. 포트 80 접근 불가**
```bash
# 방화벽 확인
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443

# GCP 방화벽 규칙 확인 (Console에서)
```

**2. Docker 권한 오류**
```bash
# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
# 재로그인 필요
```

**3. 메모리 부족**
```bash
# 메모리 사용량 확인
free -h
docker stats

# 스왑 파일 생성
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**4. 데이터베이스 오류**
```bash
# 마이그레이션 재실행
docker-compose exec web python /app/backend/manage.py migrate --run-syncdb
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs

# 실시간 로그 모니터링
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs nginx
docker-compose logs web
```

## 📊 모니터링

### 시스템 리소스 모니터링

```bash
# CPU, 메모리 사용량
htop

# 디스크 사용량
df -h

# Docker 컨테이너 리소스
docker stats
```

### 애플리케이션 모니터링

```bash
# 애플리케이션 상태 확인
curl http://localhost/api/health/  # API 헬스체크 (구현 필요)

# Nginx 상태
sudo systemctl status nginx

# 포트 사용 현황
sudo netstat -tlnp
```

## 🔄 업데이트

### 코드 업데이트

```bash
# 코드 업데이트
git pull origin master

# 프론트엔드 재빌드
cd frontend/flix-n-chill
npm run build
cd ../..

# 컨테이너 재빌드 및 재시작
docker-compose down
docker-compose build
docker-compose up -d
```

### 의존성 업데이트

```bash
# Python 패키지 업데이트
docker-compose exec web pip install -r /app/requirements.txt --upgrade

# Node.js 패키지 업데이트
cd frontend/flix-n-chill
npm update
cd ../..
```

## 🔐 보안 강화

### 기본 보안 설정

```bash
# 방화벽 설정
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS

# SSH 보안 강화
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no (키 기반 인증 사용)
# PermitRootLogin no
sudo systemctl restart ssh
```

### Django 보안 설정

```bash
# .env 파일에 추가
cat >> .env << EOF
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=True
EOF
```

## 📞 지원

- **이메일**: adeliae.p1841@gmail.com
- **문제 리포트**: GitHub Issues
- **문서**: 이 파일과 프로젝트 README.md

---

🎉 **배포 완료!** 이제 Flix N Chill을 GCP VM에서 안정적으로 운영할 수 있습니다.