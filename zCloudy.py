import boto3
import argparse
import botocore.exceptions
from rich import box
from rich.table import Table
import logging
from rich.console import Console

Print = Console(style="green")
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
    instance_type = arg.type
    instance_id = arg.id
    instances_count = arg.max
    instance_initscript = arg.initscript
    Print.print("[+] Launching instances")
    Ec2 = session.resource('ec2')
    instances = Ec2.create_instances(InstanceType=instance_type,
                                     MinCount=1,
                                     MaxCount=instances_count,
                                     ImageId=instance_id)
    # UserData=instance_initscript)
    for instance in instances:
        Print.print(f"[+] launched {instance}")


def TerminateInstances(arg):
    instance_id = arg.id
    Ec2 = session.client('ec2')
    if instance_id.lower() != "all":
        Print.print(f"[+] Terminating {instance_id}")
        response = Ec2.terminate_instances(InstanceIds=[instance_id])
        Error.print(f"[!] Terminated: {instance_id}")
        Print.print(response)
    elif instance_id.lower() == 'all':
        Print.print("[+] Terminating all instances")
        getinstaces = Ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for n, instance in enumerate(getinstaces['Reservations']):
            inst = getinstaces['Reservations'][n]['Instances'][0]['InstanceId']
            Error.print(f"[!] Terminated: {inst}")
            response = Ec2.terminate_instances(InstanceIds=[inst])
            Print.print(response)


def DescribeInstaces(arg, msg="[+] Listing.."):
    instance_status = arg.status
    Print.print(msg)
    response = session.client('ec2')
    getinstaces = response.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': [instance_status]}])
    table = Table(box=box.ASCII)
    table.add_column("PublicDnsName", style="cyan", no_wrap=True)
    table.add_column("InstanceId", style="magenta", no_wrap=True)
    table.add_column("InstanceType", style="magenta", no_wrap=True)
    table.add_column("LaunchTime", style="magenta", no_wrap=True)
    try:
        for n, instance in enumerate(getinstaces['Reservations']):  # InstanceType
            table.add_row(instance['Instances'][0]['PublicDnsName'],
                          instance['Instances'][0]['InstanceId'],
                          instance['Instances'][0]['InstanceType'],
                          str(instance['Instances'][0]['LaunchTime']))
    except KeyError:
        Error.print_exception()
    Print.print(table)
    # print(getinstaces['Reservations'][1]['Instances'][0]['PublicDnsName'])


def DescribeImages(arg):
    instance_os = arg.os
    Print.print("[+] Listing Images")
    Ec2 = session.client('ec2')
    Instances = Ec2.describe_images(
        ExecutableUsers=['all'],
        Filters=[
            {
                'Name': 'name',
                'Values': ['ubuntu/images/hvm-ssd/ubuntu-*']
            }])
    table = Table(title="AMI Instances")
    table.add_column("ImageId", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta", no_wrap=True)
    try:
        for n, instance in enumerate(Instances['Images']):
            table.add_row(Instances['Images'][n]['ImageId'], Instances['Images'][n]['Description'])
    except KeyError:
        table.add_row(Instances['Images'][n]['ImageId'], "[bold red]No Description[/bold red]")
    Print.print(table)


def SecurityGroups():
    pass


def CreateSecurityKey():
    pass


def banner():
    Print.print("""[blue]
          ██████   ██                       ██
         ██░░░░██ ░██                      ░██  ██   ██
 ██████ ██    ░░  ░██  ██████  ██   ██     ░██ ░░██ ██
░░░░██ ░██        ░██ ██░░░░██░██  ░██  ██████  ░░███
   ██  ░██        ░██░██   ░██░██  ░██ ██░░░██   ░██
  ██   ░░██    ██ ░██░██   ░██░██  ░██░██  ░██   ██
 ██████ ░░██████  ███░░██████ ░░██████░░██████  ██
░░░░░░   ░░░░░░  ░░░  ░░░░░░   ░░░░░░  ░░░░░░  ░░[/blue]

 [white]☁[/white][green]  zCloudy[/green] [red]|[/red] [red]Creator:[/red] [green]zAbuQasem[/green]

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
        create_parser.set_defaults(func=CreateInstance)
        """List Options"""
        list_parser.add_argument("-s", "--state", help="list instances based on it's state",
                                 choices=["running", "pending", "terminated", "rebooting"], required=True)
        list_parser.set_defaults(func=DescribeInstaces)
        """Describe Options"""
        describe_parser.add_argument('-o', '--os', help='Operating system ex: ubuntu')
        describe_parser.set_defaults(func=DescribeImages)
        """Terminate Options"""
        terminate_parser.add_argument('-i', '--id',
                                      help='Instance AMI-Id you want to terminate (all: to terminate all instances)')
        terminate_parser.set_defaults(func=TerminateInstances)
        """End of argparse"""
        args = parser.parse_args()
        args.func(args)
    except Exception:
        Error.print_exception()

# Generator for displaying tables?
