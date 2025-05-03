variable project_name {
    default = "goodwe2pvoutput"
    type = string
}

variable aws_region {
    type = string
    default = "us-east-1"
}

variable aws_profile {
    type=string
}

variable lambda_timeout {
    type = number
    default = 900
}

variable schedule_expression {
    type = string
    description = "How often to run the bot"
}

variable PVOUTPUT_DONATION_MODE {
	type=string
}
variable PVOUTPUT_APIKEY {
	type=string
}
variable PVOUTPUT_SYSTEMID {
	type=string
}

variable GOODWE_USERNAME {
	type=string
}
variable GOODWE_PASSWORD {
	type=string
}
variable GOODWE_SYSTEMID {
	type=string
}

variable SOC_ENABLE {
	type=string
}
variable SOC_FIELD {
	type=string
}