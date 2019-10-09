# Script *cos-upload.py*

This python script uploads one or more local files to IBM Cloud Object Store (COS) using the Aspera Transfer Manager

## Setup

You need Python to run the script. The script was tested with Python 2.7 and 3.6.

Before you install the required Python libraries, you may want to create a virtual Python environment.

To create a virtual environment, decide upon a directory where you want to place it, and run the following code:

For Python 3:
```
python3 -m venv cos-env
```

For Python 2:
```
pip install virtualenv
virtualenv -p /usr/bin/python2.7 cos-env
````

This will create the cos-env directory if it doesn’t exist, and also create directories inside it containing a copy of the Python interpreter, the standard library, and various supporting files.

Once you’ve created a virtual environment, you may activate it.

```
source cos-env/bin/activate
````

Finally, call the install script to download the required libraries.

```
./install.sh
```

## Usage

```
./cos-upload.py <endpoint> <apikey> <bucket> <prefix> <file> ...
```

Parameters:
-    **endpoint**: The COS endpoint for the bucket, or a short (location) name<br>
Examples: `s3.us-south.cloud-object-storage.appdomain.cloud` or just `us-south`
-    **apikey**:   An API key for authentication against COS
-    **bucket**:   The name of the target bucket
-    **prefix**:   A prefix for the object name (can be empty, pass "" in that case)
-    **file**:     One or more file paths

The name of the target object is derived from the file name.

### Examples:

Upload one file from current and another file from a sub directory to bucket "mybucket" with the following object names: `myprefix/file1.json` and `myprefix/samples/file2.csv`

`./cos-upload.py eu-de <apikey> mybucket myprefix file1.json samples/file2.csv`

Upload all files (ignoring sub directories) from current directory to bucket "mybucket":

`./cos-upload.py eu-de <apikey> mybucket $(find . -maxdepth 1 -type f)`

Upload all files including all nested sub directories of a given sub directory to bucket "mybucket":

`./cos-upload.py eu-de <apikey> mybucket $($(find my_subdir))`


## Limitations

At the time of writing this readme file, Python 3.7 is not supported by the current cos-aspera library (cos-aspera-0.1.163682)

## Links

[COS Documentation](https://cloud.ibm.com/docs/services/cloud-object-storage)

[COS Endpoints](https://cloud.ibm.com/docs/services/cloud-object-storage/libraries?topic=cloud-object-storage-endpoints)

[IBM Aspera](https://asperasoft.com)
