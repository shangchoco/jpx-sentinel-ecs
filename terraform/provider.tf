# AWS 제공자 설정
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# 도쿄 리전으로 설정
provider "aws" {
  region = "ap-northeast-1"
}