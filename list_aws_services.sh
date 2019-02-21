#!/bin/bash

_usage() {
  echo "Usage: $0 CHECKNAME PROFILE"
  echo "Lists instances, operating system, keypairs, volumes, and all"
}


_instances () {
	for region in $(aws ec2 describe-regions --output text | cut -f3); do
	   aws ec2 describe-instances --output text --region $region --profile $2 --query 'Reservations[*].Instances[*].[InstanceId, InstanceType, State.Name, Placement.AvailabilityZone, PrivateIpAddress, PrivateDnsName, PublicIpAddress, PublicDnsName, [Tags[?Key==`Name`].Value] [0][0], [Tags[?Key==`Environment`].Value] [0][0]]'
	done
}

_volumes () {
	for region in $(aws ec2 describe-regions --output text | cut -f3); do
	   aws ec2 describe-volumes --region $region --output text --profile $2 --query 'Volumes[*].{ID:VolumeId,InstanceId:Attachments[0].InstanceId,AZ:AvailabilityZone,Size:Size}'
	done
}

_os () {
	for region in $(aws ec2 describe-regions --output text | cut -f3); do
           aws ec2 describe-instances --output text --query "Reservations[*].Instances[*].[InstanceId,ImageId]" --region $region | awk -F' ' '{print $1,$2}' | while IFS=" " read -r instance image;
           do
             echo $instance $(aws ec2 describe-images --image-ids $image --output text --query 'Images[0].Name')
           done
	done
}


_keypairs () {
	for region in $(aws ec2 describe-regions --output text | cut -f3); do
		echo "Region:$region";aws ec2 describe-key-pairs --output text --region $region --profile $2 --query "KeyPairs[*].{Key:KeyName}"
	done
}



case "$1" in
        infra)
            _instances "$@"
            ;;

        vol)
            _volumes "$@"
            ;;

        os)
            _os "$@"
            ;;
        keys)
            _keypairs "$@"
            ;;
        all)
            _instances "$@"
            _volumes "$@"
            _os "$@"
            _keypairs "$@"
            ;;
        *)
            _usage
            exit 1

esac
