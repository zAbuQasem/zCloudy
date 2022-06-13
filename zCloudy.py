#!/usr/bin/env python3
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
except Exception:
    Error.print_exception()


def GetCreds():
    """This should take the creds from the user env vars
        encrypt them and then save them to a '.zcloudy.conf' file"""
    pass


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
    for instance in instances:
        Info.print(f"[+] launched {instance}")


def StopInstaces():
    # Here we can use a list of ids=["", ""]
    # This function is to use later
    ids = []
    Ec2 = session.resource('ec2')
    Ec2.instances.filter(InstanceIds=ids).stop()


def RunInstances():
    # Here we can use a list of ids=["", ""]
    # This function is to use later
    ids = []
    Ec2 = session.resource('ec2')
    Ec2.instances.filter(InstanceIds=ids).run()


def TerminateInstances(arg):
    instance_id = arg.id
    Ec2 = session.resource('ec2')
    try:
        if instance_id[0].lower() != "all":
            Info.print(f"[+] Terminating {instance_id}")
            Ec2.instances.filter(InstanceIds=instance_id).terminate()
            Result.print("[+] Terminated Successfully !")
            Info.print("[+] Listing currently running instances")
            getinstances = Ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ["running"]}])
            table = Table(box=box.ASCII)
            table.add_column("InstanceId", style="green", no_wrap=True, justify="center")
            table.add_column("PublicDnsName", style="bold cyan", no_wrap=True, justify="center")
            table.add_column("InstanceType", style="magenta", no_wrap=True, justify="center")
            table.add_column("LaunchTime", style="magenta", no_wrap=True, justify="center")
            for instance in getinstances:  # InstanceType
                table.add_row(instance.public_ip_address,
                              instance.id,
                              instance.instance_type,
                              str(instance.launch_time))
            Result.print(table)
        elif instance_id[0].lower() == 'all':
            Info.print("[+] Terminating all instances")
            instances = Ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ["running"]}])
            ids = [instance.id for instance in instances]
            Ec2.instances.filter(InstanceIds=ids).terminate()
            Result.print("[+] Terminated Successfully !")
            Info.print("[+] Listing instances")
            getinstances = Ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ["shutting-down"]}])
            table = Table(box=box.ASCII)
            table.add_column("InstanceId", style="green", no_wrap=True, justify="center")
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
    table.add_column("InstanceId", style="green", no_wrap=True, justify="center")
    table.add_column("PublicDnsName", style="bold cyan", no_wrap=True, justify="center")
    table.add_column("InstanceType", style="magenta", no_wrap=True, justify="center")
    table.add_column("LaunchTime", style="magenta", no_wrap=True, justify="center")
    try:
        for instance in getinstances:  # InstanceType
            table.add_row(instance.public_ip_address,
                          instance.id,
                          instance.instance_type,
                          str(instance.launch_time))
    except KeyError:
        Error.print_exception()
    Info.print(table)
    # print(getinstaces['Reservations'][1]['Instances'][0]['PublicDnsName'])


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
    pass


def banner():
    Info.print("""[blue]
          ██████   ██                       ██
         ██░░░░██ ░██                      ░██  ██   ██
 ██████ ██    ░░  ░██  ██████  ██   ██     ░██ ░░██ ██
░░░░██ ░██        ░██ ██░░░░██░██  ░██  ██████  ░░███
   ██  ░██        ░██░██   ░██░██  ░██ ██░░░██   ░██
  ██   ░░██    ██ ░██░██   ░██░██  ░██░██  ░██   ██
 ██████ ░░██████  ███░░██████ ░░██████░░██████  ██
░░░░░░   ░░░░░░  ░░░  ░░░░░░   ░░░░░░  ░░░░░░  ░░[/blue]

 [white]☁[/white] [green]zCloudy[/green] [red]|[/red] [red]Creator:[/red] [green]zAbuQasem[/green]

""")


if __name__ == '__main__':
    try:
        banner()
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)  # Other types of help formats?
        subparsers = parser.add_subparsers()
        create_parser = subparsers.add_parser("create", description="[@] Create Instaces on the fly")
        list_parser = subparsers.add_parser("list", description="[@] List My c00l Instaces")
        describe_parser = subparsers.add_parser("describe", description="[@] Get AMIs based on OS from Market")
        terminate_parser = subparsers.add_parser("terminate", description="[@] Terminate Bloody Instaces")
        """Create Options"""
        create_parser.add_argument('-t', '--type', help='Instance Type ex: t1.micro', required=True)
        create_parser.add_argument('-i', '--id', help='Specify AMI-Id (Instance ID)', required=True)
        create_parser.add_argument('-m', '--max', help='Max number of instances', type=int, default="1")
        create_parser.add_argument('-s', '--initscript', help='A script to run when the instance is initiated')
        create_parser.add_argument('-n', '--name', help='Instance name (All instances will have this name!)')
        create_parser.set_defaults(func=CreateInstance)
        """List Options"""
        list_parser.add_argument("-s", "--state",
                                 help="list instances based on it's state (all: to list all instances)", required=True)
        list_parser.set_defaults(func=DescribeInstaces)
        """Describe Options"""
        describe_parser.add_argument('-o', '--os', help='Operating system ex: ubuntu')
        describe_parser.set_defaults(func=DescribeImages)
        """Terminate Options"""
        terminate_parser.add_argument('-i', '--id',
                                      nargs='*',
                                      help='Instance AMI-Id you want to terminate (all: to terminate all instances)')
        terminate_parser.set_defaults(func=TerminateInstances)
        """End of argparse"""
        args = parser.parse_args()
        try:
            args.func(args)
        except AttributeError:
            # Error.print(f"[!] Help: [blue]{argv[0]} -h[/blue]")
            Error.print_exception()
            exit(1)
    except Exception:
        Error.print_exception()

"""
Info -> green
Results -> blue
Errors -> red
"""

"""
CORE:
    - Create, List, Terminate, Describe (manage.py)
    - AWS Creds encryption (secret.py)
    - Connect to a specific instance (connect.py)
    - configuration (config.yml) # OR similar
    - Send commands (send.py)
"""
