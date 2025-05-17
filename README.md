# Booking scrapper

This Python script scrapes hotel listings from Booking.com and sends a top hotel suggestion via Amazon SNS to notify subscribers (e.g., by email or SMS).

Prerequisites
1. AWS Account
   You’ll need an active AWS account to use Amazon SNS.
2. Register and confirm your phone number in Amazon SNS
3. IAM User with AmazonSNS* role
4. Set the environment vars in the .env file
```shell
AWS_KEY=<key>
AWS_SECRET=<secret>
AWS_REGION=<region e.g. 'eu-west-2;>

PHONE_NUMBER=<phone number with country code>
```
