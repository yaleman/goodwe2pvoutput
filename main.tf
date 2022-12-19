module dependabot_lambda {
  source = "git::https://github.com/yaleman/terraform_lambda?ref=1.0.4"
  function_name = var.project_name
  lambda_handler = "${var.project_name}/lambda.lambda_handler"
  lambda_runtime = "python3.8"

  lambda_script_filename = "${var.project_name}/lambda.py"
  lambda_schedule_expression = var.schedule_expression
  lambda_timeout = var.lambda_timeout
  lambda_memory = 128

  layer_arns = [
      local.lambda_layer_requests_arn,
      aws_lambda_layer_version.layer_requirements.arn,
  ]

  aws_region = var.aws_region
  aws_profile = var.aws_profile

  environment_variables = {
    PVOUTPUT_DONATION_MODE = var.PVOUTPUT_DONATION_MODE
    PVOUTPUT_APIKEY = var.PVOUTPUT_APIKEY
    PVOUTPUT_SYSTEMID = var.PVOUTPUT_SYSTEMID

    GOODWE_USERNAME = var.GOODWE_USERNAME
    GOODWE_PASSWORD = var.GOODWE_PASSWORD
    GOODWE_SYSTEMID = var.GOODWE_SYSTEMID

    SOC_ENABLE = var.SOC_ENABLE
    SOC_FIELD = var.SOC_FIELD
  }
}

# grab the latest layers for things
data http requests_layers {
  url = "https://api.klayers.cloud/api/v1/layers/${var.aws_region}/requests"
  request_headers = {
    Accept = "application/json"
  }
}


locals {
  lambda_layer_requests_arn = [for entry in jsondecode(data.http.requests_layers.response_body) :  entry.arn if entry["deployStatus"] != "deprecated" ][0]
}
########## requirements LAYER START
data archive_file layer_requirements {
  type        = "zip"
  source_dir = "./layer_requirements/"
  output_path = "layer_requirements.zip"

}

resource aws_lambda_layer_version layer_requirements {
  filename   = data.archive_file.layer_requirements.output_path
  layer_name = "goodwe2pvoutput-requirements"
  compatible_runtimes = ["python3.8"]
  source_code_hash = data.archive_file.layer_requirements.output_base64sha256
  provisioner "local-exec" {
    command = "./update_layer_files.sh"
  }
  depends_on = [
    data.archive_file.layer_requirements
  ]
}
########## GHAPI LAYER END 
