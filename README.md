# AWS CloudFormation POC

This repository contains my solution for the AWS CloudFormation Proof of Concept (POC) task for the Wibix Consulting internship program.

## Solution Overview

This solution demonstrates how to use AWS CloudFormation and Python to create a system that can inventory AWS resources without hardcoded credentials. The solution consists of:

1. **CloudFormation Template** (`readonly-resources-template.yaml`): Creates an IAM role with read-only access to AWS resources like EC2, S3, etc.

2. **Python Script** (`aws_inventory_fetcher.py`): Connects to AWS using the CloudFormation stack name/ARN and fetches inventory details without using explicit credentials.

## Architecture Diagram
┌─────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                 │     │                   │     │                   │
│  CloudFormation │────▶│   ReadOnly IAM    │────▶│  AWS Resources    │
│     Template    │     │   Role & Policy   │     │  (EC2, S3, etc.)  │
│                 │     │                   │     │                   │
└─────────────────┘     └───────────────────┘     └───────────────────┘
│                                                  ▲
│                                                  │
│                                                  │
▼                                                  │
┌─────────────────┐                                         │
│                 │                                         │
│  Python Script  │─────────────────────────────────────────┘
│                 │            Fetches Inventory
└─────────────────┘

## CloudFormation Template

The template creates:
- An IAM role with read-only access to AWS resources using the AWS managed policy `ReadOnlyAccess`
- An instance profile that can be attached to EC2 instances

### How to Deploy (T Steps)

1. Log in to the AWS Management Console
2. Navigate to CloudFormation service
3. Click "Create stack" > "With new resources (standard)"
4. Upload the `readonly-resources-template.yaml` file
5. Follow the wizard to create the stack
6. Note the stack name and outputs for use with the Python script

### CloudFormation Launch URL

If deployed, the stack could be launched using a URL with this format:

https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/template



## Python Script

The script:
- Takes a CloudFormation stack name or ARN as input
- Uses boto3 without explicit credentials (relies on instance profile or environment)
- Fetches inventory details for EC2 instances and S3 buckets
- Outputs the results to console and a JSON file

### Prerequisites

- Python 3.6+
- boto3 library (`pip install boto3`)
- AWS credentials configured in the environment or instance profile

### Usage

```bash
# Using stack name
python aws_inventory_fetcher.py --stack-name ReadOnlyResourcesStack

# Using stack ARN
python aws_inventory_fetcher.py --stack-arn arn:aws:cloudformation:region:account-id:stack/ReadOnlyResourcesStack/id




**CloudFormation**: Infrastructure as Code (IaC) service to provision AWS resources
**IAM Roles and Policies**: Secure access management for AWS resources
**Boto3**: AWS SDK for Python to interact with AWS services
**EC2 and S3**: Core AWS services for compute and storage
