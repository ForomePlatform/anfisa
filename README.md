# Anfisa

<!-- toc -->

- [Overview](#overview)
- [Online Development Documentation](#online-development-documentation)
- [Installation](#installation)
  * [Select branch or release:](#select-branch-or-release)
  * [Installation instructions](#installation-instructions)
    + [Installing via Docker](#installing-via-docker)
    + [Installing without Docker](#installing-without-docker)
  * [Ingesting demo whole genome](#ingesting-demo-whole-genome)
- [Public Demo](#public-demo)

<!-- tocstop -->

## Overview

Anfisa is a Variant Analysis and Curation Tool. Its purpose is to 
bring together Genetic Research and Clinical settings and provide a 
medical geneticist with access to research Genome.

See more about the goal of the project at https://forome.org/  

A detailed [Setup and Administration Guide](https://github.com/ForomePlatform/anfisa/blob/master/Anfisa%20v.0.5%20Setup%20%26%20Administration%20Reference.pdf) is included with the distribution. 

## Online Development Documentation

- Installation & Administration Documentation

https://foromeplatform.github.io/documentation/anfisa-dev.v0.7/

- User Documentation

https://foromeplatform.github.io/documentation/anfisa-user.v0.7/

##  Installation

### Select branch or release:
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

`deploy.sh --workdir=<Absolute path to the chosen working directory>`

2. Point your browser to http://localhost:9010/anfisa/app/dir 

3. [Optionally] Adjust setting for your webserver to serve Anfisa. 
For nginx add the following location block:

``` 
location /anfisa {
	proxy_pass http://127.0.0.1:9010/anfisa;
}
```

4. Download [sample whole genome dataset](https://forome-dataset-public.s3.us-south.cloud-object-storage.appdomain.cloud/pgp3140_wgs_nist-v4.2.tar.gz) 
and [ingest it](#ingesting-demo-whole-genome). Will require around 4 hours

#### Installing without Docker

1. Ensure that the following packages are installed on your system:
    * zip 
    * unzip 
    * python3-dev 
    * python3-pip 
    * python3-venv
    * [MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
   
   For example, on Ubuntu, the following command can be used:
   
       sudo apt update && sudo apt install zip unzip python3-dev python3-pip python3-venv
    
   > You might need to restart your shell or source .bashrc (or similar) file after the 
   > installation

3. [Optionally] Create [virtual environment](https://docs.python.org/3/library/venv.html) 
and activate it. We will be installing a lot of dependent packages, 
make sure you have permission to do it. A sample command is:

       python3 -m venv .anfisa && source .anfisa/bin/activate

4. Make sure you have MongoDB installed. If its endpoint 
is not localhost:27017, after the installation you will need to edit anfisa.json

5. Make sure that sphinx is installed. On Ubuntu the installation command is:

       sudo apt-get install python3-sphinx

6. Run deploy script (will use pip to install requirements):

       . deploy_local.sh

First, the script will ask for an installation directory. 
By default it would install in the same directory 
where you have cloned the code, but you can 
change it to any other directory. 
Once installation directory is confirmed, the script 
will configure Anfisa for your local system.

When the script has finished, it will display 
the command to start Anfisa server. 

When the system is running you can access 
the web interface by the url: http://localhost:8190 

The port is configurable in your configuration file.
                                                            

###  Ingesting demo whole genome
> You will need approximately 25G of space available to 
> experiment with a whole genome 

* First, download 
  [prepared dataset](https://forome-dataset-public.s3.us-south.cloud-object-storage.appdomain.cloud/pgp3140_wgs_nist-v4.2.tar.gz)
* Unpack the content into some directory (e.g. directory `data` 
  under your work directory)
* Run Anfisa ingestion process
                                     
Here are sample commands that can be executed:

    curl -L -O https://forome-dataset-public.s3.us-south.cloud-object-storage.appdomain.cloud/pgp3140_wgs_nist-v4.2.tar.gz
    docker cp pgp3140_wgs_nist-v4.2.tar.gz anfisa7:/anfisa/a-setup/data/examples/
    docker exec -it anfisa7 sh -c 'cd /anfisa/a-setup/data/examples && tar -zxvf pgp3140_wgs_nist-v4.2.tar.gz'
    docker exec -it anfisa7 sh -c 'PYTHONPATH=/anfisa/anfisa/ python3 -u -m app.storage -c /anfisa/anfisa.json -m create --reportlines 1000 -f -k xl -i /anfisa/a-setup/data/examples/pgp3140_wgs_nist-v4.2/pgp3140_wgs_nist-v4.2.cfg XL_PGP3140_NIST_V42'
            

## Public Demo 

For a quick introduction, look at a demo of Anfisa based on a high 
confidence small variants callset v 4.2 created by NIST 
by integrating results of sequencing, alignment and 
variant calling from different sources; including 
both short and long read techniques.  


The demo server with REST API and a stable built-in UI 
is available at: https://api.demo.forome.org/

A novel [React](https://reactjs.org/) Front End is under development
and a beta version can be previewed at: https://app.demo.forome.org/ 
