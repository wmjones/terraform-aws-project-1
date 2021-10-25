resource "aws_sagemaker_code_repository" "repo" {
  code_repository_name = "terraform-aws-project-1"

  git_config {
    repository_url = "https://github.com/wmjones/terraform-aws-project-1"
  }
}

locals {
  lifecycle_config = <<-EOT
  #!/bin/bash
  sudo -u ec2-user -i <<'EOF'

  # This will affect only the Jupyter kernel called "conda_python3".
  source activate python3

  # Replace myPackage with the name of the package you want to install.
  pip install xgboost
  # change to -r requirements.txt
  # You can also perform "conda install" here as well.

  source deactivate

  EOF
  EOT
}

resource "aws_sagemaker_notebook_instance_lifecycle_configuration" "lc" {
  name      = "AWS-PROJECT-1-NOTEBOOK-LIFECYCLE"
  on_create = base64encode(local.lifecycle_config)
}

resource "aws_sagemaker_notebook_instance" "ni" {
  name                    = "terraform-aws-project-1"
  role_arn                = "arn:aws:iam::761551243560:role/SageMakerFullAccess"
  instance_type           = "ml.t2.medium"
  default_code_repository = aws_sagemaker_code_repository.repo.code_repository_name
  lifecycle_config_name   = aws_sagemaker_notebook_instance_lifecycle_configuration.lc.name
}
