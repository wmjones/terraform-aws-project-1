resource "aws_sagemaker_code_repository" "repo" {
  code_repository_name = "terraform-aws-project-1"

  git_config {
    repository_url = "https://github.com/wmjones/terraform-aws-project-1"
  }
}

resource "aws_sagemaker_notebook_instance_lifecycle_configuration" "lc" {
  name     = "lc"
  on_start = <<-EOT
  #!/bin/bash
  sudo -u ec2-user -i <<'EOF'
  
  # Note that "base" is special environment name, include it there as well.
  for env in base /home/ec2-user/anaconda3/envs/*; do
      source /home/ec2-user/anaconda3/bin/activate $(basename "$env")
  
      # Installing packages in the Jupyter system environment can affect stability of your SageMaker
      # Notebook Instance.  You can remove this check if you'd like to install Jupyter extensions, etc.
      if [ $env = 'JupyterSystemEnv' ]; then
        continue
      fi
  
      # Replace myPackage with the name of the package you want to install.
      pip install --upgrade --quiet xgboost
      # You can also perform "conda install" here as well.
  
      source /home/ec2-user/anaconda3/bin/deactivate
  done
  
  EOF
  EOT
}

resource "aws_sagemaker_notebook_instance" "ni" {
  name                    = "terraform-aws-project-1"
  role_arn                = "arn:aws:iam::761551243560:role/SageMakerFullAccess"
  instance_type           = "ml.t2.medium"
  default_code_repository = aws_sagemaker_code_repository.repo.code_repository_name
  lifecycle_config_name   = aws_sagemaker_notebook_instance_lifecycle_configuration.lc.name
}