data "archive_file" "aws-lambda-archive" {
  type                        = "zip"
  source_dir                  = "lambda/"
  output_path                 = "${path.module}/lambda.zip"
}

data "aws_iam_policy" "aws-lambda-basic-exec-role" {
  arn                     = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "aws-lambda-role" {
  name                        = "${var.app_name}-lambda-role"
  assume_role_policy          = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws-lambda-iam-attach-1" {
  role                    = aws_iam_role.aws-lambda-role.name
  policy_arn              = data.aws_iam_policy.aws-lambda-basic-exec-role.arn
}

resource "aws_lambda_function" "aws-lambda-function" {
  filename                    = "${path.module}/lambda.zip"
  function_name               = "${var.app_name}-lambda-function"
  role                        = aws_iam_role.aws-lambda-role.arn
  handler                     = "lambda_function.lambda_handler"
  runtime                     = "python3.9"
  timeout                     = 120
  memory_size                 = 128
  source_code_hash            = data.archive_file.aws-lambda-archive.output_base64sha256
  environment {
    variables = {
      OPENAI_API_KEY = var.openai_api_key
    }
  }
}

resource "aws_lambda_permission" "aws-lambda-allow-alexa" {
  statement_id                = "AllowAlexaToCallLambda"
  action                      = "lambda:InvokeFunction"
  function_name               = aws_lambda_function.aws-lambda-function.function_name
  principal                   = "alexa-appkit.amazon.com"
}

