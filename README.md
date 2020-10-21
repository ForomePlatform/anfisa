# Anfisa

## Overview

Anfisa is a Variant Analysis and Curation Tool. Its purpose is to 
bring together Genetic Research and Clinical settings and provide a 
medical genticist with access to research Genome.

See more about the goal of the project at https://forome.org/  

A detailed [Setup and Administration Guide](https://github.com/ForomePlatform/anfisa/blob/master/Anfisa%20v.0.5%20Setup%20%26%20Administration%20Reference.pdf) is included with the distribution. 

## Online Development Documentation

https://foromeplatform.github.io/anfisa/

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

## Public Demo 

Also available is a demo of Anfisa based on a high 
confidence small variants callset v 4.2 created by NIST 
by integrating results of sequencing, alignment and 
variant calling from different sources; including 
both short and long read techniques.  


The demo is available at: http://demo.forome.org

 
