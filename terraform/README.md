# Setup of aws iot thing
The Terraform script main.tf sets up an iot thing with certs endpoints etc

The output of the script is used in the awsiot examples to connect to the newly setup script

To setup a new iot-thing use create.sh and when done run destroy.sh to remove the AWS resources.

Some hard coding is used as this is an example, but try to parameterize as much as possible.
