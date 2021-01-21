#!/bin/bash
terraform destroy -auto-approve
rm -f certs/*
rm -f endpoint.py
