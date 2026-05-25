module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.0" # 최신 안정 버전

  name = "jpx-project-vpc"
  cidr = "10.0.0.0/16"

  # 일본(도쿄) 리전의 2개 가용 영역 사용
  azs             = ["ap-northeast-1a", "ap-northeast-1c"]
  
  # 퍼블릭 서브넷 (ALB용)
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  
  # 프라이빗 서브넷 (ECS/RDS용)
  private_subnets = ["10.0.3.0/24", "10.0.4.0/24"]

  # NAT 게이트웨이 활성화 (프라이빗 서브넷의 인터넷 통신용)
  enable_nat_gateway = true
  single_nat_gateway = true # 비용 절감을 위해 하나만 생성 (운영 환경에선 멀티 사용)

  # 태그 지정 (AWS 리소스 관리 효율화)
  tags = {
    Environment = "dev"
    Project     = "jpx-delisting"
  }
}