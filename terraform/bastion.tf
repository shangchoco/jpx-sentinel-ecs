# 1. 最新の Amazon Linux 2023 AMI を自動取得 (リージョン別に自動マッピング)
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }
}

# 2. Bastion Host 用セキュリティグループ: 外部からSSH(22)接続のみ許可
resource "aws_security_group" "bastion_sg" {
  name   = "jpx-bastion-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    # セキュリティのため、実際のパブリックIPのみ許可することを推奨
    cidr_blocks = ["153.240.19.142/32"] 
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Bastion EC2 インスタンス作成: パブリックサブネットに配置し、ジャンプサーバーとして運用
resource "aws_instance" "bastion" {
  ami           = data.aws_ami.amazon_linux_2023.id 
  instance_type = "t3.micro"
  subnet_id     = module.vpc.public_subnets[0] # パブリックサブネットへ配置

  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.bastion_sg.id]
  key_name      = "my-key-pair" # 事前に作成済みのキーペア名

  tags = { Name = "jpx-bastion" }
}