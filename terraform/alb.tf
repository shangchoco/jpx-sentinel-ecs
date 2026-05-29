# 1. ALB(로드밸런서) 생성
resource "aws_lb" "main" {
  name               = "jpx-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets # ALB는 외부 통신을 위해 퍼블릭 서브넷에 배치
}

# 2. 대상 그룹 (Target Group): Java용 / Python용 2개 생성
resource "aws_lb_target_group" "java_tg" {
  name        = "jpx-java-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip" # ECS Fargate는 반드시 ip 타입이어야 함

  health_check {
    enabled             = true
    path                = "/" 
    port                = "8080"
    protocol            = "HTTP"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 30
  }
}

resource "aws_lb_target_group" "python_tg" {
  name        = "jpx-python-tg-v2"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip" # ECS Fargate는 반드시 ip 타입이어야 함

  health_check {
    enabled             = true
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 30
  }

  lifecycle {
    create_before_destroy = true
  }
}

# 3. 리스너: 80번 포트로 들어온 요청을 처리
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  # 기본적으로 Java 서비스로 전달
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.java_tg.arn
  }
}

# 4. 리스너 규칙: 경로 기반 라우팅 (/python/* 요청은 파이썬으로 전달)
resource "aws_lb_listener_rule" "python_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.python_tg.arn
  }

  condition {
    path_pattern {
      values = ["/python/*"]
    }
  }
}

