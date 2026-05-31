# AWS プロバイダー設定
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# 東京リージョンを指定
provider "aws" {
  region = "ap-northeast-1"
}