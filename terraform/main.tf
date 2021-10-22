terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">=3.61.0"
    }
  }
  required_version = ">= 0.14"

  backend "remote" {
    organization = "wyatt-prod"

    workspaces {
      name = "terraform-aws-project-1"
    }
  }
}

data "terraform_remote_state" "main" {
  backend = "remote"
  config = {
    organization = "wyatt-prod"
    workspaces = {
      name = "wyatt-prod"
    }
  }
}

provider "aws" {
  region = data.terraform_remote_state.main.outputs.aws_region
}

output "test" {
  description = "The CIDR block of the VPC"
  value       = data.terraform_remote_state.main.outputs.vpc_cidr_block
}