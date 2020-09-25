from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    core
)
import json

class VpcDb:

    # Exported resources created
    vpc = None
    db_security_group = None
    db_instance = None
    bastion_host_security_group = None
    bastion_host_linux = None
    db_security_group = None
    
    # factory pattern, return object instance
    @classmethod
    def build(cls, *, stack):

        vpc_db_instance = cls()

        vpc_db_instance.vpc = ec2.Vpc(stack, "vpc",
            cidr="10.0.0.0/24"
        )

        master_user_name = "exampleadmin"

        vpc_db_instance.db_security_group = ec2.SecurityGroup(stack, "dbsecuritygroup", 
            security_group_name="DBSG",
            vpc=vpc_db_instance.vpc,
            allow_all_outbound=True
        )

        vpc_db_instance.db_instance = rds.DatabaseInstance(stack,
            'exampleinstance', 
            master_username=master_user_name,
            engine=rds.DatabaseInstanceEngine.POSTGRES, 
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL), 
            vpc=vpc_db_instance.vpc,
            auto_minor_version_upgrade=True,
            database_name='exampledb',
            storage_encrypted=True,
            multi_az=False,
            security_groups=[vpc_db_instance.db_security_group]
        )

        # create bastion host in public subnet with no KeyPairName (use ec2-instance-connect)

        vpc_db_instance.bastion_host_security_group = ec2.SecurityGroup(stack, "bastionhostsecuritygroup", 
            security_group_name="bastionhostsecuritygroup",
            vpc=vpc_db_instance.vpc,
            allow_all_outbound=True
        )

        vpc_db_instance.bastion_host_linux = ec2.BastionHostLinux(stack, "bastionhostSG",
            vpc=vpc_db_instance.vpc,
            instance_name="bastionhost",
            instance_type=ec2.InstanceType("t2.micro"),
            subnet_selection={
                "subnet_type": ec2.SubnetType.PUBLIC
            },
            security_group=vpc_db_instance.bastion_host_security_group
        )

        vpc_db_instance.db_security_group.add_ingress_rule(vpc_db_instance.bastion_host_security_group, ec2.Port.tcp(5432), 'bastion host')

        return vpc_db_instance
