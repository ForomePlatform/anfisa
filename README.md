# Anfisa

## Overview

Anfisa is a Variant Analysis and Curation Tool. Its purpose is to 
bring together Genetic Research and Clinical settings and provide a 
medical genticist with access to research Genome.

See more about the goal of the project at https://forome.org/  

## Local Installation

To install Anfisa on a local Linux or MacOS system:

1. Clone the repository on your system. We suggest cloning one of 
the tagged (released) version as the master branch is undergoing 
continues development.

2. Install all the requirements by running 

`pip install -r requirements.txt`

3. Run deploy script:

`. deploy.sh`

The script will ask for an installation directory. 
By default it would install in the same directory 
where you have cloned the code, but you can 
change to any other directory. 
Then it will configure Anfisa for your local system

When the script has finished, it will display 
the command to run the system. 

Once the system is running you can access 
the web interface by teh url: http://localhost:8090 

The port is configurable in your configuration file.

## Public Demo 

Anfisa is also as a demo based on potential 
hearing loss panel of genes on a genome taken 
from Personal Genome Project with the consent of
the family.

The demo is available at: http://anfisa.forome.org/anfisa

Please contact us on the https://forome.org/ to obtain a 
username and password to access it.  
