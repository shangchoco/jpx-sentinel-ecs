# 1. 베이스 이미지로 경량화된 파이썬 사용
FROM python:3.13-slim

# 2. 도커 내에서 코드가 실행될 디렉토리 설정
WORKDIR /app

# 3. 패키지 설치용 텍스트 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 현재 폴더의 모든 소스코드(app.py 등)를 도커 안으로 복사
COPY . .

# 5. 플라스크가 사용할 5000번 포트 개방
EXPOSE 80

# 6. 도커 컨테이너가 켜질 때 플라스크 앱 자동 실행
CMD ["python", "main.py"]