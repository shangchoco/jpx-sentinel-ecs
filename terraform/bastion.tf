# 1. 최신 Amazon Linux 2023 AMI 자동 조회 (리전별 자동 매핑)
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }
}

# 2. Bastion Host용 보안 그룹: 외부(0.0.0.0/0)에서 SSH(22) 접속만 허용
resource "aws_security_group" "bastion_sg" {
  name   = "jpx-bastion-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 보안을 위해 실제 본인 공인 IP로 좁히는 것을 권장합니다.
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Bastion EC2 인스턴스 생성: 퍼블릭 서브넷에 배치하여 점프 서버 역할 수행
resource "aws_instance" "bastion" {
  ami           = data.aws_ami.amazon_linux_2023.id 
  instance_type = "t3.micro"
  subnet_id     = module.vpc.public_subnets[0] # 퍼블릭 서브넷에 배치

  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.bastion_sg.id]
  key_name      = "my-key-pair" # 미리 생성한 키 페어 이름

  tags = { Name = "jpx-bastion" }
}