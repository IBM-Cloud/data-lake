#!/bin/bash
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

set -e

function _check_version_ibmcloud {
  local existing_version="$1"
  local required_version="$2"

  if [ "$existing_version" == "" ]; then
    echo "ibmcloud cli has not been installed. Please install it and re-run this script"
    exit 1
  else
    split_string=($existing_version)
    local IFS='+'; version_number=(${split_string[2]}); unset IFS
    local IFS='.'; split_version_number=($version_number); unset IFS
    parsed_version_number="${split_version_number[0]}.${split_version_number[1]}"
    if (( $(echo "$parsed_version_number > $required_version" | bc -l) )) || (( $(echo "$parsed_version_number == $required_version" | bc -l) ))
    then
        echo "The installed version of ibmcloud cli satisfies the requirement"
    else
        echo "The installed version of ibmcloud cli ($version_number) is lower than the required version (0.19.0)"
        echo "Please update ibmcloud cli using the command 'ibmcloud update' and re-run this script"
        exit 1
    fi
  fi
}

# Check for required version of ibmcloud cli
_check_version_ibmcloud "$(ibmcloud --version 2>/dev/null || true)" "0.19"

# Setting the trigger bucket name
if [[ -z "$LOGDNA_DUMP_BUCKET_URI" ]]
then
    echo "Please set LOGDNA_DUMP_BUCKET_URI before running this script"
    exit 1
else
    export LOGDNA_DUMP_BUCKET_NAME=${LOGDNA_DUMP_BUCKET_URI##*/}
fi

# Set the name or ID of resource group
read -p "Enter resource-group name/id:" resource
ibmcloud target -g "$resource"

# Setting the name of Cos instance where logDNA dumps are stored
read -p "Enter the name of your COS instance:" cosInstanceName

if [[ -z "$cosInstanceName" ]]
then
    echo "No COS instance name specified!"
    exit 1
fi

# Setting the region
read -p "Enter the region in which your logDNA bucket is located (i.e us-south):" bucketRegion

if [[ -z "$bucketRegion" ]]
then
    # Setting default region: us-south
    echo "Setting region to 'us-south'"
    bucketRegion="us-south"
fi

ibmcloud target -r "$bucketRegion"

# Setting up iam-enabled namespace
echo 'Setting IBM Cloud Functions namespace'
# Target your IAM-enabled namespace. Note: Your namespace must be in the same region as your bucket.
echo "Creating new namespace"
read -p "Enter a new namespace name:" iamNamespace
ibmcloud fn namespace create "$iamNamespace"
ibmcloud fn property set --namespace "$iamNamespace"

echo "Assigning the Notifications Manager role to your Cloud Functions namespace"
ibmcloud iam authorization-policy-create functions cloud-object-storage "Notifications Manager" \
    --source-service-instance-name "$iamNamespace" --target-service-instance-name "$cosInstanceName"
echo 'Deploying...'
ibmcloud fn deploy --manifest manifest.yaml
