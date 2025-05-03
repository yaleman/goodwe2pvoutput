terraform {
    required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.97.0"
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
