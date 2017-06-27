import boto3

hosted_zone_id = "Z3VOT2C3XXXXXX"
domain = ".domain.local"
instance_matrix = {}
route53_matrix = {}

ec2_client = boto3.client("ec2")
route_client = boto3.client('route53')

def get_ec2_instances():
    """Get all the EC2 instances which have been set the tag 'DNSName'
    and composes a dictionary with its private ip address.
    """

    response = ec2_client.describe_instances()

    # Recorre las instancias
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:

            # Uncomment the following 3 comments to use instance IDs as DNS name for instances without DNSName tag
            #hasName = False
            for tag in instance['Tags']:
                if tag["Key"] == "DNSName":
                    instance_matrix[tag["Value"]+domain] = instance["NetworkInterfaces"][0]["PrivateIpAddress"]
                    #hasName = True
            #if not hasName:
                #instance_matrix.append([instance["InstanceId"], instance["NetworkInterfaces"][0]["PrivateIpAddress"]])


def get_route53_instances():
    """Get the Route53 records and composes a dictionary
    with the DNS name and the private address of the instance.
    """

    response = route_client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id
    )
    for record in response["ResourceRecordSets"]:

        if ".genesis.local" in record["Name"]:
            route53_matrix[record['Name'][:-1]] = record["ResourceRecords"][0]["Value"]


    #print route53_matrix

def delete_from_route(name, ip):
    """Delete a record in Route53 from a given DNS name and IP"""

    #print "DELETING "+name+" "+ip+"..."
    route_client.change_resource_record_sets(
        HostedZoneId = hosted_zone_id,
        ChangeBatch = {
            'Comment': 'Delete old entries',
            'Changes': [
                {
                    'Action': "DELETE",
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': 'A',
                        "TTL": 180,
                        'ResourceRecords': [{ 'Value': ip }]
                    }
                }
            ]
        }
    )

    #print "DELETED "+name+" "+ip

def clean_route53():
    """Look for records on Route53 which are no longer EC2 instances."""

    for inst in route53_matrix.keys():
        print "Clean Route: " + inst
        if inst not in instance_matrix:
            delete_from_route(inst, route53_matrix[inst])

def add_to_route(name, ip):
    """Delete a record in Route53 from a given DNS name and IP"""

    print "ADDING "+name+" "+ip+"..."
    route_client.change_resource_record_sets(
        HostedZoneId = hosted_zone_id,
        ChangeBatch = {
            'Comment': 'Add a new entry',
            'Changes': [
                {
                    'Action': "CREATE",
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': 'A',
                        "TTL": 180,
                        'ResourceRecords': [{ 'Value': ip }]
                    }
                }
            ]
        }
    )

    print "ADDED "+name+" "+ip


def add_instances_to_route53():
    """Look for new EC2 instances"""

    for inst in instance_matrix.keys():
        print "Add Instances " + inst
        if inst not in route53_matrix:
            add_to_route(inst, instance_matrix[inst])


def lambda_handler(event, context):

    get_ec2_instances()
    get_route53_instances()

    clean_route53()
    add_instances_to_route53()

    return 'OK!'
