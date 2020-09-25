# Don't forget to open up the security group on port 22 for your IP
aws ec2-instance-connect send-ssh-public-key --region <region> --instance-id <instance_id_bastion> --availability-zone <regionaz> --instance-os-user ec2-user --ssh-public-key file://bastion_host_key.pub
ssh -L 5432:<rds_endpoint>:5432 -i bastion_host_key ec2-user@<bastion_host_public_dns_name>

