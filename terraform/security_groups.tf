# 1. ALB(로드밸런서) 보안 그룹: 외부에서 80 포트로 접속 허용
resource "aws_security_group" "alb_sg" {
  name   = "jpx-alb-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 외부 전체 허용
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2. ECS(Spring Boot) 보안 그룹: 오직 ALB에서 오는 트래픽만 허용
resource "aws_security_group" "ecs_sg" {
  name   = "jpx-ecs-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 8080 # Spring Boot 실행 포트
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  # 로컬 PC에서 DB 접속 테스트를 위한 임시 허용 (추가)
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["153.240.19.142/32"] # 본인 공인 IP
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. RDS(데이터베이스) 보안 그룹: 오직 ECS에서 오는 트래픽만 허용
resource "aws_security_group" "rds_sg" {
  name   = "jpx-rds-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 3306 # MySQL 기준 (포스트그레면 5432)
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  # 2) [수정] 내 PC에서 접근 허용 (로컬 DBeaver용)
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [aws_security_group.bastion_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}