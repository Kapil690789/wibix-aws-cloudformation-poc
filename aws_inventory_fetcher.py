#!/usr/bin/env python3
"""
AWS Inventory Fetcher

This script connects to AWS using the CloudFormation stack ARN or name
and fetches inventory details of resources like EC2 instances and S3 buckets.

Usage:
    python aws_inventory_fetcher.py --stack-name <stack_name>
    or
    python aws_inventory_fetcher.py --stack-arn <stack_arn>
"""

import argparse
import boto3
import json
from botocore.exceptions import ClientError


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Fetch AWS inventory details using CloudFormation stack')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--stack-name', help='Name of the CloudFormation stack')
    group.add_argument('--stack-arn', help='ARN of the CloudFormation stack')
    return parser.parse_args()


def get_stack_outputs(cf_client, stack_identifier):
    """Get the outputs from a CloudFormation stack."""
    try:
        response = cf_client.describe_stacks(StackName=stack_identifier)
        if 'Stacks' in response and len(response['Stacks']) > 0:
            return {
                output['OutputKey']: output['OutputValue']
                for output in response['Stacks'][0].get('Outputs', [])
            }
        return {}
    except ClientError as e:
        print(f"Error getting stack outputs: {e}")
        return {}


def get_ec2_inventory(ec2_client):
    """Fetch EC2 instance inventory."""
    print("\n=== EC2 Instances ===")
    try:
        response = ec2_client.describe_instances()
        instances = []
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_info = {
                    'InstanceId': instance.get('InstanceId'),
                    'InstanceType': instance.get('InstanceType'),
                    'State': instance.get('State', {}).get('Name'),
                    'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                    'PublicIpAddress': instance.get('PublicIpAddress', 'N/A'),
                    'LaunchTime': instance.get('LaunchTime', 'N/A').strftime('%Y-%m-%d %H:%M:%S') if instance.get('LaunchTime') else 'N/A'
                }
                instances.append(instance_info)
                print(f"Instance ID: {instance_info['InstanceId']}")
                print(f"  Type: {instance_info['InstanceType']}")
                print(f"  State: {instance_info['State']}")
                print(f"  Private IP: {instance_info['PrivateIpAddress']}")
                print(f"  Public IP: {instance_info['PublicIpAddress']}")
                print(f"  Launch Time: {instance_info['LaunchTime']}")
                print("---")
        
        if not instances:
            print("No EC2 instances found.")
        
        return instances
    except ClientError as e:
        print(f"Error fetching EC2 inventory: {e}")
        return []


def get_s3_inventory(s3_client):
    """Fetch S3 bucket inventory."""
    print("\n=== S3 Buckets ===")
    try:
        response = s3_client.list_buckets()
        buckets = []
        
        for bucket in response.get('Buckets', []):
            bucket_info = {
                'Name': bucket.get('Name'),
                'CreationDate': bucket.get('CreationDate', 'N/A').strftime('%Y-%m-%d %H:%M:%S') if bucket.get('CreationDate') else 'N/A'
            }
            
            # Get bucket location
            try:
                location = s3_client.get_bucket_location(Bucket=bucket_info['Name'])
                bucket_info['Region'] = location.get('LocationConstraint', 'us-east-1') or 'us-east-1'
            except ClientError:
                bucket_info['Region'] = 'Unknown'
            
            buckets.append(bucket_info)
            print(f"Bucket Name: {bucket_info['Name']}")
            print(f"  Region: {bucket_info['Region']}")
            print(f"  Creation Date: {bucket_info['CreationDate']}")
            print("---")
        
        if not buckets:
            print("No S3 buckets found.")
        
        return buckets
    except ClientError as e:
        print(f"Error fetching S3 inventory: {e}")
        return []


def main():
    """Main function to fetch AWS inventory."""
    args = parse_arguments()
    
    # Create boto3 session without explicit credentials
    # This will use the instance profile or environment credentials
    session = boto3.Session()
    
    # Create CloudFormation client
    cf_client = session.client('cloudformation')
    
    # Determine stack identifier
    stack_identifier = args.stack_name if args.stack_name else args.stack_arn
    print(f"Using stack identifier: {stack_identifier}")
    
    # Get stack outputs
    stack_outputs = get_stack_outputs(cf_client, stack_identifier)
    print(f"Stack outputs: {json.dumps(stack_outputs, indent=2)}")
    
    # Create clients for AWS services
    ec2_client = session.client('ec2')
    s3_client = session.client('s3')
    
    # Fetch inventory
    print("\nFetching AWS inventory...")
    
    # EC2 inventory
    ec2_inventory = get_ec2_inventory(ec2_client)
    
    # S3 inventory
    s3_inventory = get_s3_inventory(s3_client)
    
    # Compile complete inventory
    inventory = {
        'EC2Instances': ec2_inventory,
        'S3Buckets': s3_inventory
    }
    
    # Save inventory to file
    with open('aws_inventory.json', 'w') as f:
        json.dump(inventory, f, indent=2, default=str)
    
    print("\nInventory fetching complete. Results saved to aws_inventory.json")


if __name__ == "__main__":
    main()