# [실행 전용 환경]
# 로컬에서 빌드된 JAR 파일을 바로 실행하기 위해 가벼운 JRE 환경을 사용합니다.
FROM eclipse-temurin:17-jre-alpine

# 컨테이너 내부의 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# [중요] 아까 만드신 .jar 파일을 컨테이너 내부로 복사합니다.
# 로컬 경로: build/libs/backend-0.0.1-SNAPSHOT.jar
# 컨테이너 경로: /app/app.jar
COPY build/libs/backend-0.0.1-SNAPSHOT.jar app.jar

# 컨테이너가 외부로 노출할 포트
EXPOSE 8080

# 애플리케이션 실행 명령
ENTRYPOINT ["java", "-jar", "app.jar"]