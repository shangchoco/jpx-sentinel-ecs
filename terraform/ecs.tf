# ECS 클러스터 생성 (모든 컨테이너가 모이는 공간)
resource "aws_ecs_cluster" "main" {
  name = "jpx-delisting-cluster"
}

# ---------------------------------------------
# 1. Java 서비스: 백엔드 API 처리
# ---------------------------------------------
resource "aws_ecs_service" "java_service" {
  name            = "jpx-java-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.java_app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  depends_on      = [aws_lb_target_group.java_tg]

  network_configuration {
    subnets          = module.vpc.private_subnets # 프라이빗 서브넷에 배치
    security_groups  = [aws_security_group.ecs_sg.id] # ECS 보안 그룹
    assign_public_ip = false # 외부 직접 접근 차단
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.java_tg.arn # Java용 대상 그룹과 연결
    container_name   = "jpx-java-backend"
    container_port   = 8080
  }
}

resource "aws_ecs_task_definition" "java_app" {
  family                   = "jpx-java-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name  = "jpx-java-backend"
    image = "${aws_ecr_repository.java_repo.repository_url}:latest" # 나중에 ECR 주소로 수정
    portMappings = [{
      containerPort = 8080
      hostPort      = 8080
    }]
  }])
}

# ---------------------------------------------
# 2. Python 서비스: 스케줄러 및 데이터 분석
# ---------------------------------------------
resource "aws_ecs_service" "python_service" {
  name            = "jpx-python-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.python_app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  depends_on      = [aws_lb_target_group.python_tg]

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.python_tg.arn # Python용 대상 그룹과 연결
    container_name   = "jpx-python-backend"
    container_port   = 8080
  }
}

resource "aws_ecs_task_definition" "python_app" {
  family                   = "jpx-python-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024" # 크롬 멀티 프로세싱을 위한 1 vCPU 스펙 유지
  memory                   = "2048" # 크롬의 안정적인 실행을 위한 2 GB 메모리 유지
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  # 💡 [Fargate 전용 우회책] sharedMemorySize 대신 비어있는 임시 볼륨을 생성합니다.
  # (위치 교정 완료: task_definition의 독립 속성으로 정상 배치되었습니다.)
  volume {
    name = "dshm"
  }

  # container_definitions에 파이썬 백엔드와 크롬 사이드카를 함께 묶어 배포합니다.
  container_definitions = jsonencode([
    {
      name      = "jpx-python-backend"
      image     = "${aws_ecr_repository.python_repo.repository_url}:latest" # 나중에 ECR 주소로 수정
      essential = true
      portMappings = [{
        containerPort = 8080
        hostPort      = 8080
      }]
    },
    {
      name      = "chrome"
      image     = "selenium/standalone-chrome:4.18.1" # 무겁지 않고 검증된 셀레늄 공식 크롬 이미지
      essential = true
      portMappings = [{
        containerPort = 4444 # 파이썬 내부에서 localhost:4444로 통신할 포트 개방
        hostPort      = 4444
      }]
      # 💡 [Fargate 전용 우회책] 문제가 된 linuxParameters를 지우고, 
      # 크롬의 /dev/shm 경로에 방금 선언한 임시 볼륨을 마운트하여 크래시를 원천 차단합니다.
      mountPoints = [
        {
          sourceVolume  = "dshm"
          containerPath = "/dev/shm"
        }
      ]
    }
  ])
}