#!/usr/bin/env python3

import argparse
from rich.console import Console
from core import manage

Info = Console(style="green")
Result = Console(style="blue")
Error = Console(style="bold red")


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

 [white]☁[/white]  [green]zCloudy[/green] [red]|[/red] [red]Creator:[/red] [green]zAbuQasem[/green]

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
        create_parser.add_argument('-n', '--name', help='Instance name (All instances will have this name!)',
                                   default="-")
        create_parser.set_defaults(func=manage.CreateInstance)
        """List Options"""
        list_parser.add_argument("-s", "--state",
                                 help="list instances based on it's state (all: to list all instances)", required=True)
        list_parser.set_defaults(func=manage.DescribeInstaces)
        """Describe Options"""
        describe_parser.add_argument('-o', '--os', help='Operating system ex: ubuntu')
        describe_parser.set_defaults(func=manage.DescribeImages)
        """Terminate Options"""
        terminate_parser.add_argument('-i', '--id',
                                      nargs='*',
                                      help='Instance AMI-Id you want to terminate (all: to terminate all instances)')
        terminate_parser.set_defaults(func=manage.TerminateInstances)
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
