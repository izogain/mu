import logging
import subprocess
import boto3
import xmltodict
import simplejson as json
from optparse import OptionParser

class MetadataExtraction(object):
    def __init__(self):
      self.SIGNED_URL_EXPIRATION = 300     # The number of seconds that the Signed URL is valid
      self.logger = logging.getself.logger('boto3')
      self.logger.setLevel(logging.INFO)
      self.s3_client = boto3.client('s3')

    def lambda_handler(self, event, context):
      # Loop through records provided by S3 Event trigger
      self.logger.info("Working on bucket-key in S3...")
      # Extract the Key and Bucket names for the asset uploaded to S3
      key = event['key']
      bucket = event['bucket']
      self.logger.info("Bucket: {} \t Key: {}".format(bucket, key))
      # Generate a signed URL for the uploaded asset
      signed_url = get_signed_url(self.SIGNED_URL_EXPIRATION, bucket, key)
      self.logger.info("Signed URL: {}".format(signed_url))
      # Launch MediaInfo
      # Pass the signed URL of the uploaded asset to MediaInfo as an input
      # MediaInfo will extract the technical metadata from the asset
      # The extracted metadata will be outputted in XML format and
      # stored in the variable xml_output
      xml_output = subprocess.check_output(["mediainfo", "--full", "--output=XML", signed_url])
      self.logger.info("Output: {}".format(xml_output))
      xml_json = xmltodict.parse(xml_output)
      return write_job_spec_to_file(xml_json, bucket, key)
 
    def write_job_spec_to_file(self, xml_json, bucket, key):
      try:
        ofd = open("metadata.txt", "w")
        json_map = json.dumps(xml_json,
                              indent='    ')
        ofd.write(json_map)
        ofd.close()
        self.s3_client.upload_file("./metadata.txt", bucket, key + "metadata.txt")
        return json_map
      except Exception as inst:
        print (type(inst))
        print (inst.args)
        print (inst)
        return json_map

    def get_signed_url(self, expires_in, bucket, obj):
      """
      Generate a signed URL
      :param expires_in:  URL Expiration time in seconds
      :param bucket:
      :param obj:         S3 Key name
      :return:            Signed URL
      """
      s3_cli = boto3.client("s3")
      presigned_url = s3_cli.generate_presigned_url('get_object',
                                                  Params = {'Bucket': bucket,
                                                            'Key': obj},
                                                  ExpiresIn = expires_in)
      return presigned_url

    def invoke_metadata_extraction(self):
      print (self.bucket, self.key)
      event = {
        'bucket' : self.bucket,
        'key' :self. key
      }
      self.json_metadata = lambda_handler(event, {})

    def get_duration(self):
      print (len(self.json_metadata))
      duration = self.json_metadata["Mediainfo"]["File"]["track"]["Duration"][4]
      return duration
