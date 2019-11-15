This repository contains functions which perform pre-processing of archived LogDNA logs.

The preprocessing works as follows:
* A listener is attached to the logDNA COS bucket.
* A trigger is fired everytime a new logDNA archive file ( e.g ```a591844d24.2019-07-17.72.json.gz``` ) is added to the logDNA bucket.
* The trigger calls a function that converts the gzip logDNA file into partitioned json files using the following query:
```
SELECT 
*, 
date_format(from_unixtime(_source._ts / 1000, 'yyyy-MM-dd HH:mm:ss'), 'yyyy') AS _year, 
dayofyear(from_unixtime(_source._ts / 1000, 'yyyy-MM-dd HH:mm:ss')) AS _dayofyear,         
date_format(from_unixtime(_source._ts / 1000, 'yyyy-MM-dd HH:mm:ss'), 'HH') AS _hour 
FROM 
cos://{bucket_region}/{logDNA_bucket_name}/a591844d24.2019-07-17.72.json.gz STORED AS JSON 
INTO 
{target_cos_uri} STORED AS JSON PARTITIONED BY (_year, _dayofyear, _hour)
```
Note: Currently the listener fires the trigger when a file with suffix '.json.gz' is added into the bucket. This can be changed to listen to a prefix instead.
Refer to the manifest.yaml file to make this change

# Deploying

## Step1
```sh
git clone git@github.ibm.com:SqlServiceWdp/logdna-preprocessing.git
cd logdna-preprocessing
```

## Step2
Log into IBM cloud account using ibmcloud cli.
```sh
ibmcloud login --sso
```

## Step3
Set the required environment variables.

(Note: No trailing slashes in cos uri values)
```sh
export LOGDNA_DUMP_BUCKET_ENDPOINT=<logDNA_bucket_endpoint>
export LOGDNA_DUMP_BUCKET_URI=<logDNA_bucket_cos_uri>
export PARTITIONED_LOGDNA_TARGET_URI=<target_cos_uri_for_partitioned_data>
export SQL_QUERY_INSTANCE_CRN=<instance_crn>
export API_KEY=<api-key>
```

example values:
```sh
export LOGDNA_DUMP_BUCKET_ENDPOINT="https://s3.us-south.cloud-object-storage.appdomain.cloud"
export LOGDNA_DUMP_BUCKET_URI="cos://us-south/my-bucket"
export PARTITIONED_LOGDNA_TARGET_URI="cos://us-south/bucket123/result"
export SQL_QUERY_INSTANCE_CRN="crn:v1:bluemix:public:sql-query:us-south:a/290ec9931c0737248f3dc2aa57187d14:bcb96392-84a0-777a-4b20-40671b917679::"
export API_KEY="xxxxxxxxxxxxxxxxxxxxxxx"
```

## Step4
Run the deploy.sh script.
```sh
./deploy.sh
```

The script will prompt us for the following parameters.

* Resource group
* Name of cos instance which contains logDNA bucket
* Region of the bucket
* Name for a iam enabled namespace

example input:

(Note: Do not use quotes for any input)
```
Enter resource-group name/id:Default
Enter the name of your COS instance:Cloud Object Storage-pg
Enter the region in which your logDNA bucket is located (i.e us-south):us-south
Enter a new namespace name:my_new_namespace

```

The deployment will take few seconds to complete. 
When any new logDNA file (suffix: `.json.gz`) is added into the bucket (e.g `my-bucket` ), it will be automatically converted to partitioned json files stored in target bucket (e.g `cos://us-south/bucket123/result` ).