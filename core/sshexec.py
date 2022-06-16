import paramiko
import manage


def connect():
    k = paramiko.RSAKey.from_private_key_file("./tests.pem")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname="ec2-54-227-205-222.compute-1.amazonaws.com", username="ec2-user", pkey=k, allow_agent=False,
              look_for_keys=False)
    execute(c)


def execute(client):
    try:
        while True:
            cmd = input("[+] Enter a command to execute: ")
            print(f"running command: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode().strip())
            print(stderr.read().decode().strip())
    except KeyboardInterrupt:
        client.close()
        exit(0)


connect()
