#Lists all the instances that are being created under your account across all regions

for region in `aws ec2 describe-regions --output text | cut -f3`;
do
   echo -e "\nListing Instances in region:'$region'..."
   aws ec2 describe-instances --output table \
   --query "Reservations[*].Instances[*].[InstanceId,PrivateIpAddress,State.Name,LaunchTime,InstanceType,Placement.AvailabilityZone,Tags[?Key==\`Name\`]|[0].Value]" \
   --region $region
done
