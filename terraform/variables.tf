# データベース接続用ユーザー名
variable "db_username" {
  description = "データベースの接続ユーザー名"
  type        = string
  sensitive   = true # テラフォームのログに値が出力されないよう設定（セキュリティ保護）
}

# データベース接続用パスワード
variable "db_password" {
  description = "データベースの接続パスワード"
  type        = string
  sensitive   = true # 機密情報のため、ログ出力不可に設定（セキュリティ保護）
}