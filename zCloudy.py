import boto3
import argparse
from rich import box
from rich.table import Table
from rich.console import Console

Print = Console(style="green")
Error = Console(style="bold red")


class ZCloudy:
    def __init__(self, arg):
        """Positional args"""
        #self.create = arg.create
        #self.list = arg.list
        #self.describe = arg.describe
        #self.terminate = arg.terminate
        """Sub args"""
        self.type = arg.type
        self.os = arg.os
        self.id = arg.id
        self.max = arg.max
        self.status = arg.status
        if arg.initscript:
            with open(arg.initscript, 'r') as f:
                self.initscript = f.read().strip()
                f.close()
                # print(self.initscript)
        else:
            self.initscript = '''nothing'''  # fix this nonsense
        """Remove below session and feed to init only if everything is ok (maybe use it as an indicator?)"""
        self.session = boto3.Session()


    def CreateInstance(self):
        """Error handling when the user doesn't specify required args
            - Maybe specify a wait to make sure it is running"""
        Print.print("[+] Launching instances")
        Ec2 = self.session.resource('ec2')
        instances = Ec2.create_instances(InstanceType=self.type,
                                         MinCount=1,
                                         MaxCount=self.max,
                                         ImageId=self.id,
                                         UserData=self.initscript)  # ADD keys - region later
        """Printing pending current instaces"""
        self.DescribeInstaces(status="pending", msg="[+] Listing Pending Instaces")

    def SecurityGroups(self):
        pass

    def CreateSecurityKey(self):
        pass


    def TerminateInstances(self, instance_id=None):
        try:
            Ec2 = self.session.client('ec2')
            if instance_id.lower() != "all":
                Print.print(f"[+] Terminating {instance_id}")
                response = Ec2.terminate_instances(InstanceIds=[instance_id])
                Error.print(f"[!] Terminated: {instance_id}")
                Print.print(response)
            elif instance_id.lower() == 'all':
                try:
                    Print.print("[+] Terminating all instances")
                    getinstaces = Ec2.describe_instances(
                        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
                    for n, instance in enumerate(getinstaces['Reservations']):
                        inst = getinstaces['Reservations'][n]['Instances'][0]['InstanceId']
                        Error.print(f"[!] Terminated: {inst}")
                        response = Ec2.terminate_instances(
                            InstanceIds=[inst])
                        Print.print(response)
                except Exception:
                    Error.print_exception()
        except Exception:
            Error.print_exception()


    def DescribeInstaces(self, status="running", msg="[+] Listing.."):
        """Listing instances"""
        Print.print(msg)
        response = self.session.client('ec2')
        getinstaces = response.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': [status]}])
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


    def DescribeImages(self):
        """Iterate over all instances instead of just 1"""
        Print.print("[+] Listing Images")
        Ec2 = boto3.client('ec2')
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

    def RUN(self):
        """Case statement on refactor
            - Fix everything is running at the same time"""
        #if self.create:
        #    self.CreateInstance()
        #elif self.list:
        #    self.list(status=self.status, msg=f"[+] Listing {self.status} Instaces")
        #elif self.describe:
        #    self.DescribeImages()
        #elif self.terminate:
        #    self.TerminateInstances(self.id)


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

[green]zCloudy[/green] [red]|[/red] [red]Creator:[/red] [green]zAbuQasem[/green]

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
        #create_parser.set_defaults(func=)
        """List Options"""
        list_parser.add_argument("-s", "--state", help="list instances based on it's state",
                                 choices=["running", "pending", "terminated", "rebooting"], required=True)
        """Describe Options"""
        describe_parser.add_argument('-o', '--os', help='Operating system ex: ubuntu')
        """Terminate Options"""
        terminate_parser.add_argument('-i', '--id', help='Instance AMI-Id you want to KILL :(')
        args = parser.parse_args()
        api = ZCloudy(args)
        api.RUN()
    except Exception:
        Error.print_exception()

"""TODO
The main aim of this tool is to automate creating, managing, configuring EC2 instances
- List of instance types and AMI images with proper error handling and session start timestamps + logs
- Create , start , hibernate, stop instances (region + min/max instances + sg + private key + elastic ip?)
- Option to provide a shell/Ps1 script to run at initialization
- Take aws creds and encrypt them for later usage
- Example configuration from a yaml file
    - Setup a bug bounty ubuntu os (with x11?).
    - Setup an AD environment with 3 computers. (Much work needed)
"""

"""Needed Attributes
image-type machine
Architecture ImageId Description 
"""
"""describe instaces
PublicDnsName
PublicIpAddress
InstanceId
InstanceType
"""

"""
Results of describing aren't accurate at all

--> (less code for sure but not adding anything for me...)https://stackoverflow.com/questions/62056422/not-getting-all-aws-instances-using-python-boto3-problem-with-reservation
import boto3

ec2_resource = boto3.resource('ec2')

for instance in ec2_resource.instances.all():
    print(instance.id)
    for tag in instance.tags:
        print(tag['Key'], tag['Value'])
    
"""

"""Args
https://stackoverflow.com/questions/38315599/not-getting-namespace-returned-from-subparser-in-parse-args

subpaser no namespace resolve seems to be a headache!s
"""
s