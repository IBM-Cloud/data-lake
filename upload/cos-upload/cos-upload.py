#!/usr/bin/env python
#
# ------------------------------------------------------------------------------
# Copyright IBM Corp. 2019
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
#
# Upload one or more files to IBM Cloud Object Store using Aspera High-Speed transfer
#
# Parameters:
# - Endpoint, or endpoint shortname (us-south, eu-de, ...)
# - Apikey
# - Bucket name
# - Object prefix
# - File path(s)
#
# Example: ./cos-upload.py eu-de <apikey> mybucket myprefix file1.json samples/file2.csv
# Uploaded into mybucket: "myprefix/file1.json" and "myprefix/file2.csv"
# For an empty prefix, use ""

# Tested with Python 2.7 and 3.6
#

import sys
import os.path
import ibm_boto3
from ibm_botocore.client import Config
from ibm_s3transfer.aspera.manager import AsperaConfig
from ibm_s3transfer.aspera.manager import AsperaTransferManager

def init_cos_client_aspera_manager(apikey, endpoint):
    """
    Initiate the COS client and and its associated Aspera transfer manager.
    """
    cos_client = ibm_boto3.client(
        service_name = 's3',
        ibm_api_key_id = apikey,
        ibm_auth_endpoint = 'https://iam.cloud.ibm.com/identity/token',
        config = Config(signature_version = 'oauth'),
        endpoint_url = endpoint
    )
    # Configure 2 sessions for transfer
    ms_transfer_config = AsperaConfig(multi_session=2,
                                      multi_session_threshold_mb=100)
    # Create the Aspera Transfer Manager
    transfer_manager = AsperaTransferManager(client=cos_client,
                                             transfer_config=ms_transfer_config)
    return [cos_client, transfer_manager]

def upload_object(transfer_manager, bucket_name, filename, object_name):
    """
    Upload the given file as an object to COS
    """
    print('Upload file to COS: {} => {}'.format(filename, object_name))
    status = False
    try:
        # Perform upload
        future = transfer_manager.upload(filename, bucket_name, object_name)
        # Wait for upload to complete
        future.result()
        print('Upload file to COS completed.')
        status = True
    except Exception as excpt:
        print('Upload file to COS failed, Error: {}'.format(str(excpt)))
    return status

def empty(string):
    return (" " + string).isspace()

##########

ep_prefix = 'https://'
ep_postfix = 'cloud-object-storage.appdomain.cloud'

usage='''
cos-upload.py endpoint apikey bucket prefix file ...
    endpoint: The COS endpoint for the bucket (or a short name like "us-south")
    apikey:   An API key for authentication
    bucket:   The name of the target bucket
    prefix:   A prefix for the object name (can be empty)
    file:     One or more file paths

The name of the target object is derived from the file name.
For example: ./cos-upload.py eu-de <apikey> mybucket myprefix file1.json samples/file2.csv
Objects created in "mybucket": "myprefix/file1.json" and "myprefix/file2.csv"
'''

if __name__ == '__main__':
    print()
    if len(sys.argv) < 6: sys.exit(usage)

    endpoint = sys.argv[1].strip()
    apikey = sys.argv[2].strip()
    bucket = sys.argv[3].strip()
    prefix = sys.argv[4].strip()
    file_list = [sys.argv[index].strip() for index in range(5, len(sys.argv))]

    # Parameter error handling
    if empty(endpoint) or empty(apikey) or empty(bucket) or len(file_list) == 0: sys.exit(usage)

    notfound = False
    for file in file_list:
        if not os.path.isfile(file):
            print('Error: The file {} cannot be found.'.format(file))
            notfound = True
    if notfound: sys.exit(1)

    # Process endpoint
    if not endpoint.startswith(ep_prefix): # If it starts with https://, we do not change it
        if endpoint.endswith(ep_postfix): # Just the http:// may be missing ...
            endpoint = ep_prefix + endpoint
        else: # We assume it's a short name
            endpoint = ep_prefix + 's3.' + endpoint + '.' + ep_postfix

    # Process prefix
    if not empty(prefix) and not prefix.endswith('/'):
        prefix = prefix + '/'

    print('Initialize COS and Aspera Transfer Manager using endpoint: {}\n'.format(endpoint))
    [cos_client, transfer_manager] = init_cos_client_aspera_manager(apikey, endpoint)

    try:
        # Upload all files
        for file in file_list:
            filename = os.path.basename(file)
            object = prefix + filename

            upload_object(transfer_manager, bucket, file, object)
    finally:
        transfer_manager.shutdown()
