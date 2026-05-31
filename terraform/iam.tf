# 1. ECS タスク実行ロールの定義
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "jpx-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# 2. ロールへの基本権限付与 (ECRアクセスおよびログ出力用)
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  # ECRからのイメージプルおよびCloudWatchログ出力に必要な基本ポリシー
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}