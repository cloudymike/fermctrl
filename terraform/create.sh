#!/bin/bash

# Initialize terraform, not required at all builds
terraform init

terraform plan -out planfile
terraform apply planfile

# Save the endpoint as created
terraform output > endpoint.py

# Get root certificate
curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > certs/AmazonRootCA1.pem
