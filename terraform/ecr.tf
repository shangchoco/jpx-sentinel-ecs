# 자바용 리포지토리
resource "aws_ecr_repository" "java_repo" {
  name                 = "jpx-java"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# 파이썬용 리포지토리
resource "aws_ecr_repository" "python_repo" {
  name                 = "jpx-python"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}