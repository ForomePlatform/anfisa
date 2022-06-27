# Anfisa

<!-- toc -->

- [Overview](#overview)
- [Online Development Documentation](#online-development-documentation)
- [Public Demo](#public-demo)
- [Installation](#installation)
  * [Select branch or release:](#select-branch-or-release)
  * [Installation instructions](#installation-instructions)
    + [Installing via Docker](#installing-via-docker)
    + [Installing without Docker](#installing-without-docker)
  * [Ingesting demo whole genome](#ingesting-demo-whole-genome)

<!-- tocstop -->

## Overview

Anfisa is a Variant Analysis and Curation Tool. Its purpose is to 
bring together Genetic Research and Clinical settings and provide a 
medical geneticist with access to research Genome.

See more about the goal of the project at https://forome.org/  

## Online Development Documentation

- Installation & Administration Documentation

https://foromeplatform.github.io/documentation/anfisa-dev.v0.7/

- User Documentation

https://foromeplatform.github.io/documentation/anfisa-user.v0.7/

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

***
#### Installing via Docker

**Attention: Docker installation also installs Druid. Druid is required for
handling whole exome/genome datasets, but it takes a lot of memory. 
Minimum required memory is 8G and swap should be enabled.** 

**If you have 4G of memory, first adjust Druid parameters in environment.template file.**

**If you have less than 4G, you can install demo version without Druid. 
Update docker-compose.yml.template**

Ensure that the following packages are installed on your system:

  * curl
  * zip
  * unzip
  * Docker v19.03.0 or higher
  * Docker Compose v2.0.0 or higher

Click on the below appropriate tab to install the required packages on Ubuntu or Mac OS.

**<details><summary>Install prerequisites on Ubuntu</summary>**
<p>

Run the following command to install zip, unzip and curl packages:

       sudo apt update 
       sudo apt install zip unzip curl

Follow the link to install the latest version of Docker and Docker Compose 
on [Ubuntu](https://docs.docker.com/engine/install/ubuntu/). 
If you run script as non-root user, ensure that Docker has required rights 
according to the [Post-installation steps for Linux](https://docs.docker.com/engine/install/linux-postinstall/).

Ensure that Docker version is 19.03.0 or higher and Docker Compose version is 2.0.0 or higher.

       docker -v
       docker compose version

</p>
</details>

**<details><summary>Install prerequisites on Mac OS</summary>**
<p>

Install [Homebrew Package Manager](https://brew.sh/), command can be used:
	
       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Run the following command to install required packages:
	
       xcode-select --install
       brew update
       brew install curl
       brew install zip
       brew install unzip

Follow the link to install the latest version of Docker and Docker Compose on [Mac OS](https://docs.docker.com/desktop/mac/install/).

Ensure that Docker version is 19.03.0 or higher and Docker Compose version is 2.0.0 or higher.

       docker -v
       docker compose version

</p>
</details>

**Install Anfisa in Docker**

1. Run script:

`./deploy.sh --workdir=<Absolute path to the chosen working directory>`

2. Point your browser to http://localhost:9010/anfisa/app/dir 

3. [Optionally] For better data visualization, you can deploy Anfisa's graphical interface:

`./deploy_front.sh`

4. Point your browser to http://localhost:3000

5. [Optionally] Adjust setting for your webserver to serve Anfisa back-end. 
For nginx add the following location block:

``` 
location /anfisa {
	proxy_pass http://127.0.0.1:9010/anfisa;
}
```

6. Download [sample whole genome dataset](https://forome-dataset-public.s3.us-south.cloud-object-storage.appdomain.cloud/pgp3140_wgs_nist-v4.2.tar.gz) 
and [ingest it](#ingesting-demo-whole-genome). Will require around 4 hours

***
#### Installing without Docker

Ensure that the following packages are installed on your system:
   * curl
   * zip 
   * unzip 
   * python3-dev 
   * python3-pip 
   * python3-venv
   * MongoDB

***Note:*** *pip3 version should be 3.9 or higher*

Click on the below appropriate tab to install the required packages on Ubuntu or Mac OS.

**<details><summary>Install prerequisites on Ubuntu</summary>**
<p>
	
1. The following command can be used to install required packages:
   
       sudo apt update && sudo apt install zip unzip python3-dev python3-pip python3-venv curl
    
   > You might need to restart your shell or source .bashrc (or similar) file after the 
   > installation

   To install MongoDB follow the link [Install MongoDB Community Edition on Ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).

2. [Optionally] Create [virtual environment](https://docs.python.org/3/library/venv.html) 
and activate it. We will be installing a lot of dependent packages, 
make sure you have permission to do it. A sample command is:

       python3 -m venv .anfisa && source .anfisa/bin/activate

3. Make sure MongoDB is running. The command can be used:

       sudo systemctl status mongod
       
If its endpoint is not localhost:27017, you will need to edit *anfisa.json*.

4. Make sure that sphinx is installed. The installation command is:

       sudo apt-get install python3-sphinx

</p>
</details>

**<details><summary>Install prerequisites on Mac OS</summary>**
<p>
	
1. Install [Homebrew Package Manager](https://brew.sh/), command can be used:
	
       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   Run the following command to install required packages:
	
       xcode-select --install
       brew update
       brew install curl
       brew install zip
       brew install unzip

   To install MongoDB follow the link [Install MongoDB Community Edition on macOS](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/).

2. [Optionally] Create [virtual environment](https://docs.python.org/3/library/venv.html) 
and activate it. We will be installing a lot of dependent packages, 
make sure you have permission to do it. A sample command is:

       python3 -m venv .anfisa && source .anfisa/bin/activate

3. Make sure MongoDB is running, use link [Install MongoDB Community Edition on macOS](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/)
to verify that MongoDB is running accroding to the choosen running option.
If its endpoint is not localhost:27017, you will need to edit *anfisa.json*.

4. Make sure that sphinx is installed. The installation command is:

       brew install sphinx-doc

</p>
</details>

**Install Anfisa**

First, the script will ask for an installation directory. 
By default it would install in the same directory 
where you have cloned the code, but you can 
change it to any other directory. 
Once installation directory is confirmed, the script 
will configure Anfisa for your local system.

1. Run deploy script (will use pip to install requirements):

       chmod +x deploy_local.sh
       ./deploy_local.sh
       
2. When the script has finished, it will display 
the command to start Anfisa server, for example:

`env PYTHONPATH=. python3 app/run.py <Absolute path to the chosen working directory>/anfisa_hostname.json`

3. When the system is running you can access 
the web interface by the url: http://localhost:8190/dir

The port is configurable in your configuration file. Configuration file is located in the selected working directory with the name:

`anfisa_hostname.json`

***
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
