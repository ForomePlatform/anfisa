# Anfisa

## Overview

Anfisa is a Variant Analysis and Curation Tool. Its purpose is to 
bring together Genetic Research and Clinical settings and provide a 
medical genticist with access to research Genome.

See more about the goal of the project at https://forome.org/  

Please visit our [Wiki](https://github.com/ForomePlatform/anfisa/wiki) 
for User Guides and other documentation. 
A detailed [Setup and Administration Guide](https://github.com/ForomePlatform/anfisa/blob/master/Anfisa%20v.0.5%20Setup%20%26%20Administration%20Reference.pdf) is included with the distribution. 

## Local Installation

#### Caution:
This is a master branch that from time to time can be unstable or untested.
If you would like to try Anfisa, we strongly recommend installing it from one 
of the released tags 


#### Installation instructions

To install Anfisa on a local Linux or MacOS system:

1. Clone the repository on your system. We suggest cloning one of 
the tagged (released) version as the master branch is undergoing 
continues development.

2. Change into anfisa directory, e.g.:

`cd anfisa`

3. Install all the requirements by running 

`pip3 install -r requirements.txt`

4. Run deploy script:

`. deploy.sh`

The script will ask for an installation directory. 
By default it would install in the same directory 
where you have cloned the code, but you can 
change to any other directory. 
Then it will configure Anfisa for your local system

When the script has finished, it will display 
the command to run the system. 

Once the system is running you can access 
the web interface by the url: http://localhost:8190 

The port is configurable in your configuration file.

## Run in Docker container

### Before you begin
[Installation Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)

[Run Docker as non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)

### Build and start container

Warning!
You must have permissions to write to folders. No root privileges required!

`./runcompose.sh --asetup=/path/to/asetup --druidwork=/path/to/druid/workdir/ --airflowwork=/path/to/airflow/workdir/ --hostip=INTERNAL_IP_ADDRESS_OF_MACHINE`

If any of the folders does not exist, then they will be created automatically. All parameters are required!

Open your browser and go to: http://localhost:9000/anfisa/app/dir/

If you run container in VM, go to: `http://<VMIP>:9000/anfisa/app/dir/`

**Port 9000 must be opened in VM firewall.**

### Add datasets to Anfisa

!!!Before you begin: put datasets files to /path/to/asetup/data on your host!

`docker exec -it anfisa5_docker sh -c 'PYTHONPATH=/anfisa/anfisa/ python3 -m app.storage -c /anfisa/anfisa.json -m create -f -k ws -i /anfisa/a-setup/data/path/to/inventory/file.cfg DATASET_NAME'`

or

`docker exec -it anfisa5_docker sh -c 'PYTHONPATH=/anfisa/anfisa/ python3 -m app.storage -c /anfisa/anfisa.json -m create -f -k xl -i /anfisa/a-setup/data/path/to/inventory/file.cfg XL_DATASET_NAME'`

and then restart container with Anfisa5:

`docker stop anfisa5_docker && docker start anfisa5_docker`

## Public Demo 

Also avilable is an Anfisa demo based on potential 
hearing loss panel of genes on a genome taken 
from Personal Genome Project with the consent of
the family.

The demo is available at: http://demo.forome.org/anfisa

 
