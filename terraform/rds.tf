resource "aws_db_instance" "default" {
  allocated_storage     = 20
  db_name               = "jpxdb"
  engine                = "mysql"
  engine_version        = "8.0"
  instance_class        = "db.t3.micro" # AWS無料利用枠の範囲内
  username              = var.db_username
  password              = var.db_password # 本番環境ではAWS Secrets Manager等の利用を推奨
  skip_final_snapshot   = true

  # セキュリティ強化のため、パブリックアクセスを無効化
  publicly_accessible = false

  # セキュリティグループおよびサブネットグループの紐付け
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = module.vpc.database_subnet_group_name

  tags = {
    Name = "jpx-db-instance"
  }
}