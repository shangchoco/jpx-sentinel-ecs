# 1. ALB (ロードバランサー) の作成
resource "aws_lb" "main" {
  name               = "jpx-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets # ALBは外部通信のためパブリックサブネットに配置
}

# 2. ターゲットグループ: Java用 / Python用 をそれぞれ作成
resource "aws_lb_target_group" "java_tg" {
  name        = "jpx-java-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip" # ECS Fargateのため ip タイプを指定

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
  target_type = "ip" # ECS Fargateのため ip タイプを指定

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

# 3. リスナー: ポート80へのリクエストを処理
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  # デフォルトではJavaサービスへ転送
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.java_tg.arn
  }
}

# 4. リスナールール: パスベースルーティング (/python/* はPythonサービスへ転送)
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