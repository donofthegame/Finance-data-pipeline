##############################
# 1. Glue Crawler Role
##############################
resource "aws_iam_role" "glue_crawler" {
  name = var.glue_crawler_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "glue.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "crawler_glue_policy" {
  role       = aws_iam_role.glue_crawler.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_policy" "crawler_s3_policy" {
  name   = "${var.glue_crawler_role_name}-s3-access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = ["s3:GetObject", "s3:ListBucket"],
      Resource = [
        "arn:aws:s3:::fdp-bronze-data-v5",
        "arn:aws:s3:::fdp-bronze-data-v5/*",
        "arn:aws:s3:::fdp-silver-data-v5",
        "arn:aws:s3:::fdp-silver-data-v5/*"
      ]
    }]
  })
}

resource "aws_iam_policy_attachment" "crawler_s3_policy_attach" {
  name       = "${var.glue_crawler_role_name}-attach"
  roles      = [aws_iam_role.glue_crawler.name]
  policy_arn = aws_iam_policy.crawler_s3_policy.arn
}

##############################
# 2. Glue Job Role (ETL)
##############################
resource "aws_iam_role" "glue_job" {
  name = var.glue_job_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "glue.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "job_glue_policy" {
  role       = aws_iam_role.glue_job.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_policy" "job_s3_logs_policy" {
  name   = "${var.glue_job_role_name}-s3-logs-access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:*"],
        Resource = [
          "arn:aws:s3:::fdp-bronze-data-v5", "arn:aws:s3:::fdp-bronze-data-v5/*",
          "arn:aws:s3:::fdp-silver-data-v5", "arn:aws:s3:::fdp-silver-data-v5/*",
          "arn:aws:s3:::fdp-gold-data-v5", "arn:aws:s3:::fdp-gold-data-v5/*",
          "arn:aws:s3:::fdp-glue-scripts-v5/*"
        ]
      },
      {
        Effect = "Allow",
        Action = ["logs:*"],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "job_s3_logs_policy_attach" {
  name       = "${var.glue_job_role_name}-attach"
  roles      = [aws_iam_role.glue_job.name]
  policy_arn = aws_iam_policy.job_s3_logs_policy.arn
}

##############################
# 3. Athena Role
##############################
resource "aws_iam_role" "athena" {
  name = var.athena_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "athena.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_policy" "athena_s3_policy" {
  name   = "${var.athena_role_name}-s3-access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "athena:*",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:PutObject"
      ],
      Resource = [
        "arn:aws:s3:::fdp-gold-data-v5", "arn:aws:s3:::fdp-gold-data-v5/*",
        "arn:aws:s3:::fdp-athena-query-results-v5", "arn:aws:s3:::fdp-athena-query-results-v5/*"
      ]
    }]
  })
}

resource "aws_iam_policy_attachment" "athena_s3_policy_attach" {
  name       = "${var.athena_role_name}-attach"
  roles      = [aws_iam_role.athena.name]
  policy_arn = aws_iam_policy.athena_s3_policy.arn
}

