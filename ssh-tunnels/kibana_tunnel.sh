# Don't forget to open up the security group on port 22 for your IP
aws ec2-instance-connect send-ssh-public-key --region <region> --instance-id <instance-id> --availability-zone <region-az> --instance-os-user ec2-user --ssh-public-key file://bastion_host_key.pub
ssh -L 5000:<kibana-endpoint>:443 -i bastion_host_key ec2-user@<public-dns-name-of-bastion>
