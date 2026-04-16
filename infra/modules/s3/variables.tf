variable "abort_incomplete_multipart_upload_days" {
  description = "Number of days before incomplete multipart uploads are cleaned up."
  type        = number
  default     = 7
}

variable "bucket_name" {
  description = "Name of the S3 bucket."
  type        = string
}

variable "tags" {
  description = "Tags to apply to the bucket."
  type        = map(string)
  default     = {}
}
