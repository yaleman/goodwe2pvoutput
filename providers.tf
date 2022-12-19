terraform {
    required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
    archive = {
      source = "hashicorp/archive"
    }
    http = {
      source = "hashicorp/http"
    }
  }
  required_version = ">= 0.13"

}

provider aws {
  profile = var.aws_profile
  region = var.aws_region
}