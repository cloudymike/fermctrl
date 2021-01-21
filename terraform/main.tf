provider "aws" {
  region = "us-west-2"
}

resource "aws_iot_thing" "tempctrl_iot_thing" {
   name = "tempctrl"
}

# Create an aws iot certificate
resource "aws_iot_certificate" "tempctrl_cert" {
  active = true
}
# Attach AWS iot cert generated above to the aws iot thing(s)
resource "aws_iot_thing_principal_attachment" "tempctrl_principal_att" {
  principal = aws_iot_certificate.tempctrl_cert.arn
  thing     = aws_iot_thing.tempctrl_iot_thing.name
}

# A policy for the iot thing for Micro Python Examples
resource "aws_iot_policy" "tempctrl_policy" {
  name = "tempctrl"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect"
      ],
      "Resource": [
        "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Subscribe"
      ],
      "Resource": [
        "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topicfilter/tempctrlpub",
        "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topicfilter/tempctrlsub"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish",
        "iot:Receive"
      ],
      "Resource": [
        "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/tempctrlpub",
        "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/tempctrlsub"
      ]
    }
  ]
}
EOF
}
# Attach policy generated above to the aws iot thing(s)
resource "aws_iot_policy_attachment" "tempctrl_policy_att" {
  policy = aws_iot_policy.tempctrl_policy.name
  target = aws_iot_certificate.tempctrl_cert.arn
}


# Variables
###############################################################

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}


# Output created information for use by awsiot MicroPython Code
###############################################################
# Output certificate to /cert/ folder
resource "local_file" "tempctrl_cert_pem" {
  content     = aws_iot_certificate.tempctrl_cert.certificate_pem
  filename = "${path.module}/certs/tempctrl_cert.pem.crt"
}
# Output private key to /cert/ folder
resource "local_file" "tempctrl_private_key" {
  content     = aws_iot_certificate.tempctrl_cert.private_key
  filename = "${path.module}/certs/tempctrl_cert.private.key"
}
# Output public key to /cert/ folder
resource "local_file" "tempctrl_public_key" {
  content     = aws_iot_certificate.tempctrl_cert.public_key
  filename = "${path.module}/certs/tempctrl_cert.public.key"
}



# Get the aws iot endpoint to print out for reference
data "aws_iot_endpoint" "endpoint" {
    endpoint_type = "iot:Data-ATS"
}

# Output arn of iot thing(s)
output "iot_endpoint" {
  value = data.aws_iot_endpoint.endpoint.endpoint_address
}
