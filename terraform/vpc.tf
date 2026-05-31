module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.0" # 最新の安定バージョン

  name = "jpx-project-vpc"
  cidr = "10.0.0.0/16"

  # 東京リージョンの2つのアベイラビリティーゾーンを使用
  azs             = ["ap-northeast-1a", "ap-northeast-1c"]
  
  # パブリックサブネット (ALB用)
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  
  # プライベートサブネット (ECS用)
  private_subnets = ["10.0.3.0/24", "10.0.4.0/24"]

  # データベースサブネット (RDS用)
  database_subnets = ["10.0.5.0/24", "10.0.6.0/24"]
  create_database_subnet_group = true # RDSがこのサブネットグループを参照するように設定

  # NATゲートウェイの有効化 (プライベートサブネットからのインターネット通信用)
  enable_nat_gateway = true
  single_nat_gateway = true # コスト削減のため1つのみ作成 (本番環境では冗長化を推奨)

  # タグ付け (AWSリソース管理の効率化)
  tags = {
    Environment = "dev"
    Project     = "jpx-delisting"
  }
}