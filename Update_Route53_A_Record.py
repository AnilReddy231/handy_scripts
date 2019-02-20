import boto3
import os

def Update_Route53_A_Record(Name,Value):
	os.environ['AWS_PROFILE'] = "default"
	client = boto3.client('route53')
	Updated=True
	try:
		response = client.change_resource_record_sets(
		HostedZoneId='ZUNJCWVKUZTFO',
		ChangeBatch= {
						'Changes': [
							{
							 'Action': 'UPSERT',
							 'ResourceRecordSet': {
								 'Name': Name,
								 'Type': 'A',
								 'TTL': 300,
								 'ResourceRecords': [{'Value': Value}]
							}
						}]
		})
	except Exception as e:
		print(e)
		Updated=False
	finally:
		return Updated

if __name__ == '__main__':
	IP=os.popen('curl http://169.254.169.254/latest/meta-data/public-ipv4').read()
	Recordset="anilens.co.za"
	Result=Update_Route53_A_Record(Recordset,IP)
	if Result:
		print("Route53 DNS RecordSet had been updated successfully")
	else:
		print("Failed to Updated the RecordSet")