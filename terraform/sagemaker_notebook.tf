resource "aws_sagemaker_code_repository" "repo" {
  code_repository_name = "terraform-aws-project-1"

  git_config {
    repository_url = "https://github.com/wmjones/terraform-aws-project-1"
  }
}

resource "aws_sagemaker_notebook_instance" "ni" {
  name                    = "my-notebook-instance"
  role_arn                = "arn:aws:iam::761551243560:role/SageMakerFullAccess"
  instance_type           = "ml.t2.medium"
  default_code_repository = aws_sagemaker_code_repository.repo.code_repository_name
}
