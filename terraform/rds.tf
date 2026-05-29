resource "aws_db_instance" "default" {
  allocated_storage    = 20
  db_name              = "jpxdb"
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro" # 프리티어 범위
  username             = "admin"
  password             = "Password123!" # 실제 사용 시에는 AWS Secrets Manager 등을 써야 합니다!
  skip_final_snapshot  = true

  publicly_accessible = true

  # 앞서 만든 보안 그룹과 서브넷 그룹 연결
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = module.vpc.database_subnet_group_name

  tags = {
    Name = "jpx-db-instance"
  }
}