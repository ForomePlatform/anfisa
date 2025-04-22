# AnFiSA

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

AnFiSA is a Variant Analysis and Curation Tool. Its purpose is to 
bring together Genetic Research and Clinical settings and provide a 
medical geneticist with access to research Genome.

See more about the goal of the project at https://forome.org/  

## Online Development Documentation

- Installation & Administration Documentation

https://foromeplatform.github.io/documentation/anfisa-dev.v0.7/

- User Documentation

https://foromeplatform.github.io/documentation/anfisa-user.v0.7/

## Public Demo 

For a quick introduction, look at a demo of AnFiSA based on a high 
confidence small variants callset v 4.2 created by NIST 
by integrating results of sequencing, alignment and 
variant calling from different sources; including 
both short and long read techniques.  


The demo server can be previewed at: https://anfisa.demo.forome.dev/.
Its [Front End](https://github.com/ForomePlatform/AnFiSA-React-Client), 
powered by [React](https://reactjs.org/) is currently under development.


REST API can be accessed using URL pattern

```
https://api.demo.forome.dev/app/{call}
```
                                     
Please consult 
[documentation](https://foromeplatform.github.io/documentation/anfisa-dev.v0.7/rest/index.html)
for the list of available calls. For example:

```
https://api.demo.forome.dev/app/dirinfo
```

Provides a list of datasets available on the demo server. 

Also, a stable built-in UI is available at: https://api.demo.forome.dev/app/dir

##  Installation

### Select branch or release:
This is a master branch that from time to time can be unstable or untested.
If you would like to try AnFiSA, we strongly recommend installing it from one 
of the released tags 


### Installation instructions

To install AnFiSA on a local Linux or MacOS system:

1. Clone the repository on your system. We suggest cloning one of 
the tagged (released) versions as the master branch is undergoing 
continues development.
```sh
       git clone https://github.com/ForomePlatform/anfisa.git
```
2. Change into anfisa directory, e.g.:
```sh
       cd anfisa
```


3. [Optionally] Checkout a stable release, e.g.,
```sh
       git checkout v.0.8.2
```

3. Decide what directory will be a working directory for AnFiSA

4. Decide which of the following installation paths you prefer:
  - Use a Docker container. This method will also install Druid and 
other dependencies. However, Druid requires at least 8G of memory, 
if your box does not have this amount of RAM, you should avoid running 
Druid or adjust its settings. Druid can also be run on a separate box. 
  - Install all components in your local system. This is only recommended 
if you will be contributing to AnFiSA development or customizing its code. 
                                              
> Druid is an analytics database used to support multidimensional 
> filtering and fast summarization in AnFiSA.
> See: https://druid.apache.org/

***

#### Installing via Docker

**Install AnFiSA in Docker*
                  
Deployment of AnFiSA has been moved to a separate repository.
You can find installation instructions using `docker-compose` 
[here](https://github.com/ForomePlatform/deploy/blob/main/docker-compose/README.md)

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

> ***Note:*** *Python version should be 3.9 or higher*

Click on the appropriate tab below to install the required packages on 
Ubuntu or MacOS.

<details>
<summary>Install prerequisites on Ubuntu</summary>
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
       
If its endpoint is not localhost:27017, you will need to edit the configuration 
file which is named *anfisa.json* or *anfisa_hostname.json*.

4. Make sure that sphinx is installed. The installation command is:

       sudo apt-get install python3-sphinx

</p>
</details>

<details>
<summary>Install prerequisites on Mac OS</summary>
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
   If its endpoint is not localhost:27017, you will need to edit the configuration
   file which is named *anfisa.json* or *anfisa_hostname.json

4. Make sure that sphinx is installed. The installation command is:

       brew install sphinx-doc

</p>
</details>

**Install AnFiSA**

First, the script will ask for an installation directory. 
By default, it would install in the same directory 
where you have cloned the code, but you can 
change it to any other directory. 
Once installation directory is confirmed, the script 
will configure AnFiSA for your local system.

1. Run [deploy script](deploy_local.sh) (will use pip to install requirements):

       ./deploy_local.sh
 
The script creates configuration file `anfisa_${hostname}.json`. The file
is created from [template](setup/anfisa.json.template). Its structure
is described in the 
[documentation](https://foromeplatform.github.io/documentation/anfisa-dev.v0.7/adm/configuration.html)
      
2. When the script has finished, it will display 
the command to start AnFiSA server, for example:

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
  [prepared dataset](https://zenodo.org/records/13906214/files/pgp3140_wgs_nist-v4.2-annotated.tgz)
* Unpack the content into some directory (e.g. directory `data` 
  under your work directory)
* Run AnFiSA ingestion process
                                     
Here are sample commands that can be executed:
     
```shell
export anfisa=$(pwd)
pushd a-setup/data/examples/ 
curl -L -O https://zenodo.org/records/13906214/files/pgp3140_wgs_nist-v4.2-annotated.tgz
tar -zxvf pgp3140_wgs_nist-v4.2-annotated.tgz
popd

PYTHONPATH=${anfisa}/anfisa/ python3 -u -m app.storage -c ${anfisa}/anfisa.json -m create --reportlines 1000 -f -k xl -i ${anfisa}/a-setup/data/examples/pgp3140_wgs_nist-v4.2/pgp3140_wgs_nist-v4.2.cfg XL_PGP3140_NIST_V42

```
