# ECS クラスターの作成 (すべてのコンテナを集約する空間)
resource "aws_ecs_cluster" "main" {
  name = "jpx-delisting-cluster"
}

# ---------------------------------------------
# 1. Java サービス: バックエンド API 処理
# ---------------------------------------------
resource "aws_ecs_service" "java_service" {
  name            = "jpx-java-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.java_app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  depends_on      = [aws_lb_target_group.java_tg]

  network_configuration {
    subnets         = module.vpc.private_subnets # プライベートサブネットに配置
    security_groups = [aws_security_group.ecs_sg.id] # ECS用セキュリティグループ
    assign_public_ip = false # 外部からの直接アクセスを遮断
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.java_tg.arn # Java用ターゲットグループと連携
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
    image = "${aws_ecr_repository.java_repo.repository_url}:latest"
    portMappings = [{
      containerPort = 8080
      hostPort      = 8080
    }]
  }])
}

# ---------------------------------------------
# 2. Python サービス: スケジューラーおよびデータ分析
# ---------------------------------------------
resource "aws_ecs_service" "python_service" {
  name            = "jpx-python-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.python_app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  depends_on      = [aws_lb_target_group.python_tg]

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.python_tg.arn # Python用ターゲットグループと連携
    container_name   = "jpx-python-backend"
    container_port   = 8080
  }
}

resource "aws_ecs_task_definition" "python_app" {
  family                   = "jpx-python-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024" # Chromeマルチプロセッシングのためのスペック
  memory                   = "2048" # Chrome安定稼働のためのメモリ確保
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  # [Fargate対策] 共有メモリ不足問題を回避するための一時ボリューム作成
  volume {
    name = "dshm"
  }

  # PythonバックエンドとChromeサイドカーをセットでデプロイ
  container_definitions = jsonencode([
    {
      name      = "jpx-python-backend"
      image     = "${aws_ecr_repository.python_repo.repository_url}:latest"
      essential = true
      portMappings = [{
        containerPort = 8080
        hostPort      = 8080
      }]
    },
    {
      name      = "chrome"
      image     = "selenium/standalone-chrome:4.18.1"
      essential = true
      portMappings = [{
        containerPort = 4444
        hostPort      = 4444
      }]
      # [Fargate対策] Chromeの /dev/shm に一時ボリュームをマウントしクラッシュを防止
      mountPoints = [
        {
          sourceVolume  = "dshm"
          containerPath = "/dev/shm"
        }
      ]
    }
  ])
}