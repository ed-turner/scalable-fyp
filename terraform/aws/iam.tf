
resource "aws_iam_role" "execution_role" {
    name = "ecsTaskExecutionRole"
    assume_role_policy = jsonencode(
        {
            "Version" : "2012-10-17",
            "Statement" : [
              {
                "Effect" : "Allow",
                "Principal" : {
                  "Service" : "ecs-tasks.amazonaws.com"
                },
              }
              ]
        }
    )
}

resource "aws_iam_role_policy_attachment" "execution_role_policy" {
    role       = aws_iam_role.execution_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task_role" {
    name = "ecsTaskRole"
    assume_role_policy = jsonencode(
        {
            "Version" : "2012-10-17",
            "Statement" : [
              {
                "Effect" : "Allow",
                "Principal" : {
                  "Service" : "ecs-tasks.amazonaws.com"
                },
              }
              ]
        }
    )
}