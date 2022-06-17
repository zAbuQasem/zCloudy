#!/usr/bin/env python3
import time

import boto3
import logging
import argparse
from sys import argv
from rich import box
import botocore.exceptions
from rich.table import Table
from rich.pretty import pprint
from rich.console import Console

Info = Console(style="green")
Result = Console(style="blue")
Error = Console(style="bold red")

# Better exception? (put invalid creds to test and see the error)
try:
    session = boto3.Session()
except botocore.exceptions.ClientError:
    Error.print("[!] Cannot connect to AWS Services!")
    exit(2)


def GetCreds():
    """This should take the creds from the user env vars
        encrypt them and then save them to a '.zcloudy.conf' file"""
    pass


# Remove the hardcoded keyname
def CreateInstance(arg):
    # 1- List pending instances
    # 2- Live block to watch instances as they are running
    instance_type = arg.type
    instance_id = arg.id
    instances_count = arg.max
    instance_name = arg.name
    if arg.initscript:
        with open(arg.initscript, "r") as f:
            instance_userdata = f.read().strip()
            f.close()
    else:
        instance_userdata = '''nothing'''
    Info.print("[+] Launching instances")
    Ec2 = session.resource('ec2')
    instances = Ec2.create_instances(InstanceType=instance_type,
                                     MinCount=1,
                                     MaxCount=instances_count,
                                     ImageId=instance_id,
                                     UserData=instance_userdata,
                                     # KeyName=CreateSecurityKey(),
                                     TagSpecifications=[
                                         {
                                             'ResourceType': 'instance',
                                             'Tags': [
                                                 {
                                                     'Key': 'Name',
                                                     'Value': f'{instance_name}'
                                                 },
                                             ]
                                         },
                                     ],

                                     )
    """To ensure the public ips is initialized (remove after implementing wait group)"""
    time.sleep(2)
    getinstances = Ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ["pending"]}])
    table = Table(box=box.ASCII)
    table.add_column("InstanceId", style="white", no_wrap=True, justify="center")
    table.add_column("PublicDnsName", style="bold cyan", no_wrap=True, justify="center")
    table.add_column("InstanceType", style="magenta", no_wrap=True, justify="center")
    table.add_column("LaunchTime", style="magenta", no_wrap=True, justify="center")
    table.add_column("State", style="red", no_wrap=True, justify="center")
    for instance in getinstances:  # InstanceType
        table.add_row(instance.id,
                      instance.public_ip_address,
                      instance.instance_type,
                      str(instance.launch_time),
                      instance.state["Name"])
    Result.print(table)


def StartInstances(arg):
    # Here we can use a list of ids=["", ""] (accepts only lists)
    # This function is to use later
    ids = arg.id
    Ec2 = session.resource('ec2')
    Info.print(f"[+] Starting instance: {ids[0]}")
    Ec2.instances.filter(InstanceIds=ids).start()
    Result.print("[+] Done")


def StopInstaces(arg):
    # Here we can use a list of ids=["", ""] (accepts only lists)
    # This function is to use later
    ids = arg.id
    Ec2 = session.resource('ec2')
    Info.print(f"[+] Stopping instance: {ids[0]}")
    Ec2.instances.filter(InstanceIds=ids).stop()
    Result.print("[+] Done")


def TerminateInstances(arg):
    instance_id = arg.id
    Ec2 = session.resource('ec2')
    try:
        if instance_id[0].lower() != "all":
            Info.print(f"[+] Terminating {instance_id}")
            Ec2.instances.filter(InstanceIds=instance_id).terminate()
            # Result.print("[+] Terminated Successfully !")
            Info.print("[+] Listing currently running instances")
            getinstances = Ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ["running"]}])
            table = Table(box=box.ASCII)
            table.add_column("InstanceId", style="white", no_wrap=True, justify="center")
            table.add_column("PublicDnsName", style="bold cyan", no_wrap=True, justify="center")
            table.add_column("InstanceType", style="magenta", no_wrap=True, justify="center")
            table.add_column("LaunchTime", style="magenta", no_wrap=True, justify="center")
            for instance in getinstances:  # InstanceType
                table.add_row(instance.id,
                              instance.public_ip_address,
                              instance.instance_type,
                              str(instance.launch_time))
            Result.print(table)
        elif instance_id[0].lower() == 'all':
            Info.print("[+] Terminating all instances")
            instances = Ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ["running"]}])
            ids = [instance.id for instance in instances]
            Ec2.instances.filter(InstanceIds=ids).terminate()
            # Result.print("[+] Terminated Successfully !")
            Info.print("[+] Listing instances")
            getinstances = Ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ["shutting-down"]}])
            table = Table(box=box.ASCII)
            table.add_column("InstanceId", style="white", no_wrap=True, justify="center")
            table.add_column("PublicDnsName", style="bold cyan", no_wrap=True, justify="center")
            table.add_column("InstanceType", style="magenta", no_wrap=True, justify="center")
            table.add_column("LaunchTime", style="magenta", no_wrap=True, justify="center")
            table.add_column("State", style="red", no_wrap=True, justify="center")
            try:
                for instance in getinstances:  # InstanceType
                    table.add_row(instance.public_ip_address,
                                  instance.id,
                                  instance.instance_type,
                                  str(instance.launch_time),
                                  instance.state["Name"])
            except KeyError:
                Error.print_exception()
            Result.print(table)
    except botocore.exceptions.ClientError:
        Error.print(f"[!] Usage: {argv[0]} terminate -h/--help")
        exit(1)


def DescribeInstaces(arg):
    # ADD all and make this function suitable to overuse rather than reusing the same code again and again!
    instance_status = arg.state
    msg = f"[+] Listing {arg.state} instances"
    Info.print(msg)
    Ec2 = session.resource('ec2')
    getinstances = Ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': [instance_status]}])
    table = Table(box=box.ASCII)
    table.add_column("InstanceId", style="white", no_wrap=True, justify="center")
    table.add_column("PublicDnsName", style="bold cyan", no_wrap=True, justify="center")
    table.add_column("InstanceType", style="magenta", no_wrap=True, justify="center")
    table.add_column("LaunchTime", style="magenta", no_wrap=True, justify="center")
    try:
        for instance in getinstances:  # InstanceType
            table.add_row(instance.id,
                          instance.public_ip_address,
                          instance.instance_type,
                          str(instance.launch_time))
    except KeyError:
        Error.print_exception()
    Result.print(table)


def DescribeImages(arg):
    instance_os = arg.os
    Info.print("[+] Listing Images")
    Ec2 = session.client('ec2')
    Instances = Ec2.describe_images(
        ExecutableUsers=['all'],
        Filters=[
            {
                'Name': 'name',
                'Values': ['ubuntu/images/hvm-ssd/ubuntu-*']
            }])
    table = Table(box=box.ASCII)
    table.add_column("ImageId", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta", no_wrap=True)
    try:
        for n, instance in enumerate(Instances['Images']):
            table.add_row(Instances['Images'][n]['ImageId'], Instances['Images'][n]['Description'])
    except KeyError:
        table.add_row(Instances['Images'][n]['ImageId'], "[bold red]No Description[/bold red]")
    Info.print(table)


def SecurityGroups():
    pass


def CreateSecurityKey():
    keypair_name = "zCloudy"
    ec2 = session.client('ec2')
    keypair = ec2.create_key_pair(KeyName=keypair_name)
    private_key_file = open(keypair_name, "w")
    private_key_file.write(keypair["KeyMaterial"])
    private_key_file.close()
    return keypair["KeyMaterial"]


""" Manage ec2 instances
1- Already finished
2- Create a security group (fixed)
3- Create health check
4- User can :  !run echo hello (all instances)
                run echo hello (all instances)
                
/** paramiko
"""

"""
CreateInstances:
    - Exception is thrown if the keypair is already available
    
CreateSecurityKey:
    - Remove the hardcoded name (or leave it)
    - Check whether the key is there or not else download the keyf
"""
