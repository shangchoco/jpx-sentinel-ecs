# Java用リポジトリ
resource "aws_ecr_repository" "java_repo" {
  name                 = "jpx-java"
  image_tag_mutability = "MUTABLE" # タグの上書きを許可

  # プッシュ時の脆弱性スキャンを有効化
  image_scanning_configuration {
    scan_on_push = true
  }
}

# Python用リポジトリ
resource "aws_ecr_repository" "python_repo" {
  name                 = "jpx-python"
  image_tag_mutability = "MUTABLE" # タグの上書きを許可

  # プッシュ時の脆弱性スキャンを有効化
  image_scanning_configuration {
    scan_on_push = true
  }
}