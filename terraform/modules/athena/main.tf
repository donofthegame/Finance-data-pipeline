resource "aws_athena_workgroup" "this" {
  name = "fdp-analytics-wg-v2"

  configuration {
    enforce_workgroup_configuration = true

    result_configuration {
      output_location = var.athena_output_path
    }
  }

  state = "ENABLED"
  tags  = var.tags
}
