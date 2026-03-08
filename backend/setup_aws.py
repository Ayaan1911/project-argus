#!/usr/bin/env python3
"""
AWS Setup Script for Project Argus
Creates DynamoDB table for storing analysis submissions
"""

import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_dynamodb_table():
    """Create DynamoDB table for argus-submissions"""
    
    print("🚀 Setting up AWS resources for Project Argus...")
    print("-" * 50)
    
    # Initialize DynamoDB client
    try:
        dynamodb = boto3.client(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )
        print(f"✓ Connected to AWS region: {os.getenv('AWS_REGION', 'ap-south-1')}")
    except Exception as e:
        print(f"✗ Failed to connect to AWS: {str(e)}")
        print("\nPlease ensure:")
        print("1. AWS credentials are configured (aws configure)")
        print("2. Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env")
        return False
    
    # Create table
    table_name = os.getenv('DYNAMODB_TABLE', 'argus-submissions')
    
    try:
        print(f"\n📊 Creating DynamoDB table: {table_name}")
        
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'listing_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'listing_id',
                    'AttributeType': 'S'  # String
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand pricing (free tier friendly)
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'Argus'
                },
                {
                    'Key': 'Purpose',
                    'Value': 'Rental Scam Detection'
                }
            ]
        )
        
        print(f"✓ Table '{table_name}' created successfully!")
        print(f"  - Partition Key: listing_id (String)")
        print(f"  - Billing Mode: PAY_PER_REQUEST")
        print(f"  - Status: {response['TableDescription']['TableStatus']}")
        
        # Wait for table to be active
        print("\n⏳ Waiting for table to become active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        print(f"✓ Table '{table_name}' is now ACTIVE and ready to use!")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"✓ Table '{table_name}' already exists!")
        else:
            print(f"✗ Error creating table: {str(e)}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ AWS setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Push backend code to GitHub")
    print("2. Create AWS App Runner service from GitHub repo")
    print("3. Set environment variables in App Runner:")
    print("   - AWS_REGION=ap-south-1")
    print("   - AWS_ACCESS_KEY_ID=<your-key>")
    print("   - AWS_SECRET_ACCESS_KEY=<your-secret>")
    print("4. Deploy and test!")
    
    return True

if __name__ == "__main__":
    success = create_dynamodb_table()
    exit(0 if success else 1)
