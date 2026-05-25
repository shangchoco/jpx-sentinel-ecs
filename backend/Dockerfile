# [1단계] 빌드 전용 가스레인지: 도커 안에서 자바 소스코드를 압축하는 기계입니다.
FROM gradle:8.7.0-jdk17 AS build
WORKDIR /app

# 내 컴퓨터의 소스코드를 도커의 빌드 기계 안으로 싹 복사합니다.
COPY . .

# 도커 내부에서 gradlew 파일 없이 직접 그레이들 빌드 명령을 내려 .jar 파일을 뽑아냅니다.
RUN gradle build -x test --no-daemon

# [2단계] 실행 전용 가스레인지: 압축된 파일만 가지고 가볍게 실행하는 본체입니다.
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# 1단계 기계가 열심히 압축해 놓은 결과물(.jar)만 쏙 빼와서 실행용 그릇에 담습니다.
COPY --from=build /app/build/libs/*-SNAPSHOT.jar app.jar

EXPOSE 8080
CMD ["java", "-jar", "app.jar"]