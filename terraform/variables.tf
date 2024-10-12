variable "twilio_account_sid" {
    type = string
}
variable "twilio_auth_token" {
    type = string
}

variable "cockroach_db_connection_string" {
    type = string
    sensitive = true
}