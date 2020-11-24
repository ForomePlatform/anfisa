# Anfisa

## Overview

Anfisa is a Variant Analysis and Curation Tool. Its purpose is to 
bring together Genetic Research and Clinical settings and provide a 
medical genticist with access to research Genome.

See more about the goal of the project at https://forome.org/  

A detailed [Setup and Administration Guide](https://github.com/ForomePlatform/anfisa/blob/master/Anfisa%20v.0.5%20Setup%20%26%20Administration%20Reference.pdf) is included with the distribution. 

## Online Development Documentation

https://foromeplatform.github.io/anfisa/

##  Installation

#### Caution:
This is a master branch that from time to time can be unstable or untested.
If you would like to try Anfisa, we strongly recommend installing it from one 
of the released tags 


### Installation instructions

To install Anfisa on a local Linux or MacOS system:

1. Clone the repository on your system. We suggest cloning one of 
the tagged (released) version as the master branch is undergoing 
continues development.

2. Change into anfisa directory, e.g.:

`cd anfisa`

3. Decide what directory will be a working directory for Anfisa

4. Decide which of the following installation paths you prefer:
- Use a Docker container. This method will also install Druid and 
other dependencies. However, Druid requires at least 8G of memory, 
if your box does not have this amount of RAM, you should avoid running 
Druid or adjust its settings. Druid can also be run on a separate box. 
- Install all components in your local system. This is only recommended 
if you will contributing to Anfisa development or customizing its code. 

#### Installing via Docker

**Attention: Docker installation also installs Druid. Druid is required for
handling whole exome/genome datasets, but it takes a lot of memory. 
Minimum required memory is 8G and swap should be enabled.** 

**If you have 4G of memory, first adjust Druid parameters in environment.template file.**

**If you have less than 4G, you can install demo version without Druid. 
Update docker-compose.yml.template**

1. Run 

`deploy.sh --workdir=<Absolute path to the chosen working directory> --hostip=<your local IP address>`

2. Point your browser to http://localhost:9010/anfisa/app/dir 

3. Download whole genome dataset from 
https://forome-project-bucket.s3.eu-central-1.amazonaws.com/v6/pgp3140_wgs_nist-v4.2/pgp3140_anfisa.json.gz 
and ingest it. Will require around 4 hours

#### Installing without Docker

1. [Optionally] Create virtual environment (See https://docs.python.org/3/library/venv.html) 
and activate it. We will be installing a lot of dependent packages, 
make sure you have permission to do it. A sample command is:

`python3 -m venv .anfisa && source .anfisa/bin/activate`

2. Make sure you have MongoDB installed. If its endpoint 
is not localhost:27017, after the installation you will need to edit anfisa.json

2. Make sure that sphinx is installed. On Ubuntu the instllation command is:

`sudo apt-get install python3-sphinx`

3. Run deploy script (will use pip to install requirements):

`. deploy_local.sh`

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

## Public Demo 

Also available is a demo of Anfisa based on a high 
confidence small variants callset v 4.2 created by NIST 
by integrating results of sequencing, alignment and 
variant calling from different sources; including 
both short and long read techniques.  


The demo is available at: http://demo.forome.org

 
