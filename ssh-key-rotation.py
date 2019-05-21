from Crypto.PublicKey import RSA
import boto3
import os


def sshKeysRotation(event, context):
    # Get AWS region
    get_region = boto3.client('ssm')
    region_name = get_region.meta.region_name
    ssm_client = boto3.client('ssm', region_name=region_name)
    # OS Users
    sshUsers = os.environ.get("ENV_USERS").split(",")
    instanceNameTag = os.environ.get("INSTANCE_NAME_TAG")

    for sshUser in sshUsers:
        PrivateKey = RSA.generate(4096)
        PublicKey = PrivateKey.publickey()
        PrivateKeyPEM = PrivateKey.exportKey('PEM')
        PublicKeyOpenSSH = PublicKey.exportKey('OpenSSH')
        PrivateKeyStr = PrivateKeyPEM.decode('utf-8')
        PublicKeyStr = PublicKeyOpenSSH.decode('utf-8')
        # Add Private Key to SSM Parameter Store
        ssm_client.put_parameter(
            Name=(instanceNameTag + '-' + sshUser + '-private-key'),
            Description=(instanceNameTag + '-' + sshUser + ': New private Key generated'),
            Value=PrivateKeyStr,
            Type='String',
            Overwrite=True,
        )
        # Add Public Key to SSM Parameter Store
        ssm_client.put_parameter(
            Name=(instanceNameTag + '-' + sshUser + '-public-key'),
            Description=(instanceNameTag + '-' + sshUser + ': New public Key generated'),
            Value=PublicKeyStr,
            Type='String',
            Overwrite=True,
        )
        ssm_client.send_command(
            Targets=[
                {
                    'Key': 'tag:Name',
                    'Values': [
                        instanceNameTag,
                    ]
                },
            ],
            DocumentName="AWS-RunShellScript",
            Parameters={
                'commands': [
                    ('echo "' + PublicKeyStr + '"' + ' | tee /home/' + sshUser + '/.ssh/authorized_keys')
                ]
            },
            Comment=(instanceNameTag + ': Adding new public key for ' + sshUser)
        )