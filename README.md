# LNS - Lambda Name Service
Next Generation DNS Service

## Introduction
The purpose of this Lambda function is to mantain an internal DNS zone for EC2 instances in a concrete VPC for internal resolution . It uses Route53 to store this internal DNS zone.

Each time this Lambda funcion is triggered, it looks for new and old records in EC2 service and in Route53 to perform updates.

## Usage
This is a lambda function written in Python 2.7. To start using, create a new lambda function and paste the code inline.

You must have the internal DNS zone created before starting (future automation in progress).

## Add new DNS records
This feature works tagging your instances with an concrete tag. To add a new record in Route53, choose an instance and add a new tag with the key "DNSName". The value must be the name you want to be accesible.

For example, if you have an instance tagged like this: **DNSName: proxy01**, and your domain is **mydomain.local**, you will get an entry on Route53 with the DNS name **proxy01.mydomain.local** pointing to its internal IP address.

## Delete DNS records
Just delete the DNSName tag on the instance that you want to delete from Route53.

## IAM Permissions
* EC2
  * Describe instances


* Route 53
  * List Resource Record Sets
  * Change Resource Record Sets
