import argparse
import time
from os import getenv
from dotenv import load_dotenv
import boto3
from my_args import vpc_arguments

parser = argparse.ArgumentParser(
    description="CLI program that helps with Aws VPC.",
    prog='main.py')

subparsers = parser.add_subparsers(dest='command')
vpc = vpc_arguments(subparsers.add_parser("vpc", help="work with Aws vpcs/s"))

load_dotenv()


def main():
    aws_ec2_client = init_client()
    args = parser.parse_args()

    match args.command:
        case "vpc":
            if args.create_vpc:
                result = aws_ec2_client.create_vpc(CidrBlock="10.22.0.0/16")
                vpc = result.get("Vpc")
                vpc_id = vpc.get("VpcId")
                
                print(f"Successfully created vpc: {vpc}, vpc id: {vpc_id}")
                
                print(f"Assigning tag: {args.tag} to vpc_id: {vpc_id}")
                
                aws_ec2_client.create_tags(Resources=[vpc_id],
                         Tags=[{
                           "Key": "Name",
                           "Value": args.tag
                         }])
                print(f'{args.tag} tag was assigned to vpc: {vpc_id}')
                

            if args.create_internet_gateway:
                result = aws_ec2_client.create_internet_gateway()
                print(f"Successfully created igw: {igw_id}")
                igw_id = result.get("InternetGateway").get("InternetGatewayId")
                
                if args.attach_internet_gateway:
                    aws_ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=args.vpc_id)
                    print(f"Successfully attached internet gateway: {igw_id} to vpc: {vpc}")

            if args.create__with_subnets:
                if args.public_subnets + args.private_subnets > 200:
                    print("Public + Private subnets should be less than 200")

                result = aws_ec2_client.create_vpc(CidrBlock="10.22.0.0/16")
                vpc = result.get("Vpc")
                vpc_id = vpc.get("VpcId")
                print(f"Successfully created vpc with id: {vpc_id}")
                
                for i in range(args.npr):
                    subnet_id = create_subnet(vpc_id, f'10.22.{i}.0/24', f'private_sub_{i}')
                    time.sleep(2)
                    rtb_id = create_route_table(aws_ec2_client, aws_ec2_client, vpc_id, False)
                    time.sleep(2)
                    
                    associate_route_table_to_subnet(rtb_id, subnet_id)
                    time.sleep(2)
                    
                for i in range(args.npu):
                    subnet_id = create_subnet(vpc_id, f'10.22.{i+args.npr}.0/24', f'public_sub_{i+args.npr}')
                    time.sleep(2)
                    rtb_id = create_route_table(aws_ec2_client, vpc_id, True, 'my_route_name', create_or_get_igw(vpc_id))
                    time.sleep(2)
                    associate_route_table_to_subnet(aws_ec2_client, rtb_id, subnet_id)
                    time.sleep(2)
                    enable_auto_public_ips(aws_ec2_client, subnet_id, 'enable')
                    time.sleep(2)
                                                
            if args.assign_read_policy == "True":
                print(1)

def enable_auto_public_ips(client, subnet_id, action):
  new_state = True if action == "enable" else False
  response = client.modify_subnet_attribute(MapPublicIpOnLaunch={"Value": new_state}, SubnetId=subnet_id)
  
  print(f"IP association state changed to {new_state}")

def associate_route_table_to_subnet(client, route_table_id, subnet_id):
  response = client.associate_route_table(RouteTableId=route_table_id,
                                              SubnetId=subnet_id)
  print(f"Succesfully associated route table: {route_table_id} with subnet: {subnet_id}")

def create_or_get_igw(client, vpc_id):
  igw_id = None
  igw_response = client.describe_internet_gateways(
    Filters=[{
      'Name': 'attachment.vpc-id',
      'Values': [vpc_id]
    }])

  if 'InternetGateways' in igw_response and igw_response['InternetGateways']:
    igw = igw_response['InternetGateways'][0]
    igw_id = igw['InternetGatewayId']
  else:
    response = client.create_internet_gateway()
    
    igw = response.get("InternetGateway")
    igw_id = igw.get("InternetGatewayId")
    print(f"Successfully created igw with id: {igw_id}")
    response = client.attach_internet_gateway(InternetGatewayId=igw_id,
                                                  VpcId=vpc_id)
    print(f"Succesfully attached igw: {igw_id} to vpc: {vpc_id}")
  return igw_id


def create_route_table(client,vpc_id, route=False, route_table_name=None, igw_id=None):
  response = client.create_route_table(VpcId=vpc_id)
  route_table = response.get("RouteTable")
  route_table_id = route_table.get("RouteTableId")
  print("Route table id", route_table_id)
  time.sleep(2)
  
  if route == True:
    client.create_tags(
        Resources=[route_table_id],
        Tags=[
        {
            "Key": "Name",
            "Value": route_table_name
        },
        ],
    )

    response = client.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id,
        RouteTableId=route_table_id,
    )
  else:
    client.create_tags(
    Resources=[route_table_id],
    Tags=[
      {
        "Key": "Name",
        "Value": "private-route-table"
      },
    ],
  )
  return route_table_id 


def create_subnet(client, vpc_id, cidr_block, subnet_name):
    time.sleep(2)
    response = client.create_subnet(VpcId=vpc_id, CidrBlock=cidr_block)
    subnet = response.get("Subnet")

    subnet_id = subnet.get("SubnetId")
    print(f"Succesfully created vpc with id" {vpc_id})
    
    time.sleep(2)
    
    client.create_tags(
        Resources=[subnet_id],
        Tags=[
            {
            "Key": "Name",
            "Value": subnet_name
            },
        ],
    )
    return subnet_id


def init_client():
    client = boto3.client(
        "ec2",
        aws_access_key_id=getenv("aws_access_key_id"),
        aws_secret_access_key=getenv("aws_secret_access_key"),
        aws_session_token=getenv("aws_session_token"),
        region_name=getenv("aws_region_name"))
    
    # check if credentials are correct
    client.list_buckets()

    return client


if __name__ == "__main__":
    main()
