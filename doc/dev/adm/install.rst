**************************
Installation documentation
**************************

.. index:: 
    Installation documentation

Overview
########

Anfisa is a Linux-based Python application (Python 3.5+) and provides access via HTTP/HTTPS protocols. It deals with datasets of mutation variants in the human genome. The datasets can be of two different kinds with Anfisa providing different functionality dependent on the kind:

* :term:`XL-dataset` (XL, eXtra Large) usually represents a whole exome (WES) or a whole genome and can encompass up to 10 million variants. Users can search subsets of variants, and form (secondary) workspaces from them to perform more detailed studies.
    
    
* :term:`Workspace` (WS) is a dataset of a small number of variants (up to 10000). Users can view and tag variants in it. Workspaces are either created as derivative datasets from an XL-dataset or can also be directly ingested into the system as primary datasets. The latter option is used for analyzing gene panels.
        
Only administrators of the system can create primary datasets in the vault of the system or remove them from there. A primary dataset is created directly from prepared data and can be of type XL or WS. “Normal” users can create secondary datasets only (automatically). These are filtered out from XL datasets and are always of type WS.

Anfisa uses the following external systems:

* MongoDB_, this database is used to store information about user activities; it does NOT contain information about datasets.

.. _MongoDB: https://www.mongodb.com/

* Druid_ OLAP system, this engine is used for effective support of :term:`XL-datasets<xl-dataset>` (Druid is not necessary while working without XL-datasets)

.. _Druid: https://druid.apache.org/


There are two variants for Anfisa service configuration:

.. _uWSGI:

* Server (uWSGI) mode:
    
    * Anfisa application being wrapped into a uWSGI container. uWSGI is the common way to handle a Python application under a web service:

        `<https://uwsgi-docs.readthedocs.io/en/latest/>`_
        
    * and this container is used by the main web server, usually Nginx or Apache

* Stand-alone mode: this mode is used for development purposes and may be installed on a personal computer without a server environment

.. index:: 
    Legacy UI; current User Interface 

For the current version of system 0.6 only Legacy UI is supported. Legacy UI​ is a collection of web pages which gives the user access to the full functionality of the system; unfortunately this kind of UI does not satisfy all criteria for a “good UI”. In particular, it works properly only under Chrome or Firefox browsers.

.. index:: 
    NextGen frontend; future advanced User Interface

NextGen Frontend for the version 0.6, which satisfies the criteria for a "good UI", is currently a subject of development.

Setup
#####

Anfisa installation and configuration
*************************************

To setup the Anfisa system in Server (uWSGI) mode it is recommended to install the stand-alone variant first, and then upgrade it to the server variant.

1. Stand-alone installation
===========================

Following instructions are tested on Ubuntu 18.04 LTS. Still, there shouldn’t be anything too specific.

1.1. Prerequisites
------------------
 
* Standard Python tools: Python 3.5+, pip3, virtualenv (optional)

* MongoDB_ (version 2.6.10 or higher): If not installed already install it with the default configuration using the official guides:

    `<https://docs.mongodb.com/manual/installation/>`_
    
look for the appropriate Linux distribution using the links in this document). It should be up and running.

* git version control system: 

    `<https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_
    
* If you want to use the XL-dataset functionality, Druid_ v0.17 or later needs to be installed:

    `<http://druid.io/>`_
        
1.2. Installation
-----------------

To install Anfisa in the stand-alone variant execute the steps below.

    .. index:: 
        ANFISA_ROOT; system directory path
            
* Create a new directory for the project and go there. From now on, this directory will be referred as ``ANFISA_ROOT``: 

::
        
            $ mkdir -p $ANFISA_ROOT
            $ cd $ANFISA_ROOT

.. _virtualenv:
            
* At this point we advise one to create virtual environment using any suitable tool. In this example we use virtualenv: 
    
::
        
            $ pip3 install virtualenv
            $ python -m virtualenv venv
            $ source venv/bin/activate
        
* Clone the repository of the system: 
    
::
    
            $ git clone https://github.com/ForomePlatform/anfisa.git

* Cloning the repository creates the directory anfisa, containing the application. Change into this directory: 
    
::
        
            $ cd anfisa

        .. index:: 
            ANFISA_HOME; system directory path
            
*Note*: below we will refer to this directory as ``ANFISA_HOME`` ::
        
            ANFISA_HOME ​=​/data/projects/Anfisa/anfisa

* Install dependencies by running​: 

::
        
            $ pip3 install -r requirements.txt

.. warning:: TODO: package forome-tools
        
* Now try to initialize the working environment for the system 
    
::
        
            $ bash deploy.sh
            
.. warning:: TODO: check if deploy.sh works properly
        
* This script asks for an installation directory, i.e. the working directory  where the system will store information (case data, intermediate files, indices, log files, etc.);
        
        ``​../a-setup​`` is recommended but a different name should work too

        .. index:: 
            ANFISA_WORK; system directory path
            
        *Note*: below we will refer to this directory as `ANFISA_WORK`
        
::
            
            ANFISA_WORK​ =​/data/projects/Anfisa/a-setup

Now you are good to go! To run the service in the stand-alone variant use commands printed by deploy script:  ::

    $ cd $ANFISA_HOME
    $ python -m app.run $ANFISA_WORK/anfisa_<hostname>.json
        
In a browser (Chrome or Firefox are supported) one can see the service at the following URL: http://localhost:8190/dir

Provided the script ​deploy.sh​ has worked properly, one should see the directory of Anfisa filled with one workspace, and be able to work with that workspace. 

(If it is a server installation and there are no open ports on the computer, use ssh tunneling to access this and other pages).

2. Upgrade to server setup
==========================

In a server variant Anfisa runs in uWSGI container served by a web application server.

2.1. Prerequisites
------------------

1. You will need to have root privileges to perform some of the following steps.

2. You need to have a web server installed, Apache or NGINX. Others are good too, but we will provide configuration examples only for those aforementioned.

Before setting up the server variant one needs to answer the following questions:

1. *Which user would run Anfisa?*

    *Note*: Below we refer to this username as ​ANFISA_ADMIN

    .. index:: 
        ANFISA_ADMIN; username of Anfisa application
    
2. *What is the URL pointing to the Anfisa application?*

    As a web application Anfisa is run using an address like:
    
    ``http://<server>/<directory>/...`` (http: or https:)

    .. index:: 
        ANFISA_HTML_BASE; top url of Anfisa web-application

    So, one needs to specify this directory. Let’s refer to it as ``​ANFISA_HTML_BASE​``. Its name should start and end with symbols ‘/’, and can be as short as ‘/’.

    When the NextGen Frontend appears, it would be accessed via this address.

    So the extended address ``ANFISA_HTML_APP_BASE`` is used as the base level of the internal REST API and the ​Legacy UI​: ::
    
        ANFISA_HTML_APP_BASE​ = $ANFISA_HTML_BASE + ‘app/’

3. *What is the port number for the http socket to be used for uWSGI connection?*

    Should be unique among the sockets running on the computer. Below we will use the number **3041**, one is free to choose any other unique number in case of conflict.

4. *What is the name of the MongoDB database which is going to support Anfisa?*

    The name ``Anfisa`` is recommended.

5. *Where is the Druid system set up?*

    There can be one of three answers:

        * nowhere - then there will be no XL-datasets support

        * on the same computer

        * on a different computer, with access via secure connections
    
    (see details in the :ref:`Druid setup<Druid_setup>` section below)

6. *What is the prefix for names of datasets represented in Druid?*

    The name ``Anfisa`` is recommended

7. *Does the server provide access to BAM-files for IGV direct support?*

    See below discussion in the :ref:`IGV direct support<IGV_direct_support>` section below.

And: create the directory ``$ANFISA_WORK/ui``: ::

    $ export ANFISA_WORK=/data/projects/Anfisa/a-setup
    $ mkdir $ANFISA_WORK/ui


2.2. Configure the application
------------------------------

Copy the configuration file ``$ANFISA_HOME/anfisa.json`` to the directory ``$ANFISA_ROOT`` and make the following changes to it (see :doc:`configuration` for details):

::

    "file-path-def": {"WORK": "${HOME}/../a-setup"},

Change the value of $WORK to the value of $ANFISA_WORK

::

    "html-base": "/anfisa/app",

Write the value of ``$ANFISA_HTML_APP_BASE`` here (it should end with ​``/app"`` if it is a server installation)

::

    "mongo-db": "Anfisa"

Change this if a different database name is chosen for the MongoDB

::

    "data-vault": "${WORK}/vault",

You can change this value to put the vault to any other place on the computer. This directory can be large: it will contain the entire data of the datasets.

::

    "http-bam-base": “http://<server>/anfisa/links/”,

HTTP base directory for access to BAM-files, for :ref:`IGV direct support<IGV_direct_support>`. Uncomment this option and set it up correctly if the server provides access to BAM-files, otherwise keep it commented.

::

    "dir-files": [
  
..

        See explanation about this block :ref:`here<file_transfer>`.
  
    ::
    
        ["/ui", "${HOME}/int_ui/files"],

..

        Drop this line and uncomment the next one: 
        
    ::

            ["/ui", "${WORK}/ui"]
        ]

..
        
        This instruction and the next one will be used for :ref:`anti-cache subsystem<anti_cache>`;  ​make sure that you have the directory ``$ANFISA_WORK/ui`` is created​.

::

    "mirror-ui": ["${HOME}/int_ui/files", "${WORK}/ui"]
        
Please uncomment this instruction in server setup context, see details :ref:`here<anti_cache>`.

::

    "druid": {...}

If you are going to use :term:`XL-datasets<xl-dataset>`, set up the parameters of Druid properly (see the section :ref:`Druid Setup<Druid_setup>` below).


2.3. Create the uWSGI container descriptor
------------------------------------------

In the directory ``$ANFISA_ROOT`` create the file ​``uwsgi.anfisa.ini``​ with the following content (replace :ref:`conventional names<adm_notations>` with their proper values): ::

    [uwsgi]
    socket = 127.0.0.1:​3041
    chdir = ​$ANFISA_ROOT
    wsgi-file = ​$ANFISA_HOME​/app/run.py
    pythonpath = ​$ANFISA_HOME
    processes = 1
    threads = 30
    logger = file:logfile=​$ANFISA_WORK​/logs/uwsgi.log,maxsize=500000
    lazy

Note that the number **3041** is an HTTP socket. It should be unique among the HTTP sockets running on the computer, and can be changed to any other unique number within.

2.4. Register the uWSGI container
---------------------------------

As root (e. g. using sudo), create the file ``/etc/systemd/system/anfisa.service`` with the following contents (replace :ref:`conventional names<adm_notations>` with their proper values): ::

    [Unit]
    Description=uWSGI Anfisa
    User=​$ANFISA_ADMIN
    
    [Service]
    User=​$ANFISA_ADMIN
    Group=​$ANFISA_ADMIN_GROUP
    ExecStart=​$UWSGI_EXE​ \
        --ini ​$ANFISA_ROOT​/uwsgi.anfisa.ini \
        --virtualenv ​$ANFISA_ROOT​/venv
    # Requires systemd version 211 or newer
    RuntimeDirectory=uwsgi
    Restart=always
    KillSignal=SIGQUIT
    Type=notify
    StandardError=syslog
    
    [Install]
    WantedBy=multi-user.target

*Note*: you can obtain uWSGI executable ``​$UWSGI_EXE`` location with following: ::

    $ cd $ANFISA_ROOT
    $ source venv/bin/activate
    $ which uwsgi

Also take care of permissions for this file:

::

    $ sudo chmod 0644 /etc/systemd/system/anfisa.service

Now we need to notify systemd of the new service:

::

$ sudo systemctl daemon-reload

And start the service:

::

    $ sudo systemctl start anfisa

2.5. Setup web server configuration
-----------------------------------

We provide you with configurations templates for two popular web servers.

2.5.1 Nginx
^^^^^^^^^^^

Insert the following configuration directives into configuration file, for example: ``/etc/nginx/sites-enabled/default``

It governs the behaviour of the web server with respect to the application (replace :ref:`conventional names<adm_notations>` with their proper values): ::

    #####
    Anfisa
    #####
    location ​<ANFISA_HTML_APP_BASE>​ {
        include uwsgi_params;
        uwsgi_read_timeout 300;
        uwsgi_pass 127.0.0.1:​3041​;
    }
    location ~ ​<ANFISA_HTML_APP_BASE>​/ui {
        rewrite ^​<ANFISA_HTML_APP_BASE>​/ui/(.*)$ /$1 break;
        root ​<ANFISA_WORK>​/ui;
    }
    location ~ ​<ANFISA_HTML_APP_BASE>​/ui/images {
        rewrite ^​<ANFISA_HTML_APP_BASE>​/ui/images/(.*)$ /$1 break;
        root ​<ANFISA_HOME>​/int_ui/images;
    }

.. warning:: TODO: documentation redirect
    
The meaning of the above instructions is as follows:

1. The first instruction establishes connection to the uWSGI container with the main Anfisa application when requests (URL) starts with 
``<ANFISA_HTML_APP_BASE>`` ​.

    For example, in the notation of this document, a request to the directory page will have this URL: ``​http://<site>/​<ANFISA_HTML_APP_BASE>​/dir``
    
    It is necessary to get access to the kernel REST API of the application and to the Legacy UI. The directory path for these requests should end in ``/app/``.

    Note that we use here the socket number 3014, it can be changed to anything else, as long as it is the same as in ​uwsgi.anfisa.ini​ (see above)

2. The last two instructions forward content of the files used in the internal UI:

    * one forwards files (with extensions ``.js`` and ``.css``) from the mirror :ref:`anti-cache<anti_cache>` directory ​``<ANFISA_WORK>​/ui/``
            
    * the other forwards the images from the directory ``<ANFISA_HOME>​/int_ui/images``
    
    * see more details :ref:`here<file_transfer>`

3. There can be one more instruction here if the server provides access to BAM-files for :ref:`IGV direct support<IGV_direct_support>`.
        
Finally, you need to test new configuration: ::

    $ sudo nginx -t

If everything is ok, reload: ::

    $ sudo systemctl reload nginx

To ensure that system is up, visit ``​http://localhost/<ANFISA_HTML_BASE>`` and you should see the main application page. Look for workspaces in the menu to ensure that connection to the main Anfisa application is configured correctly.

2.5.2 Apache
^^^^^^^^^^^^

.. warning:: TODO: WRITE IT!


.. _IGV_direct_support:

2.6. IGV direct support
-----------------------

Anfisa provides functionality to run IGV local application:

    `<https://software.broadinstitute.org/software/igv/download>`_
    
over any variant in scope. To perform this call the server should provide HTTP/HTTPS access for BAM-files included in case. The setting “http-bam-base" in :doc:`configuration` file serves for this purpose. However, one needs to set up this access. It is not necessary to use the same WEB-server for these files, BAM-files can be located somewhere else.

In a simple example configuration, NGINX simply serves BAM-files from the location on the drive. Files are organized on disk as follows: ::

    <BAM_FILES_LOCATION>/{case}/{sample}.hg19.bam
    <BAM_FILES_LOCATION>/{case}/{sample}.hg19.bam.bai

NGINX configuration in turn contains the following: ::

    location /bams {
        root <BAM_FILES_LOCATION>;
    }

Finally, Anfisa configuration (anfisa.json) contains the following line: ::

    "http-bam-base": "https://<site>/bams"

.. _Druid_setup:

2.7. Druid setup
----------------

At the moment of this document being written, Apache Druid v.0.17.0 is the most recent one, and this exact version is assumed. Best source of information on Druid installation and configuration is it’s documentation:

`<https://druid.apache.org/docs/0.17.0/design/index.html>`_

In the following section we assume that Druid is installed and properly configured according to its documentation.

2.7.1. Connection configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When Druid is installed on the same machine as Anfisa, one needs to uncomment ​“druid” section of the ​anfisa.json​ configuration:

::

    "druid": {
        "vault-prefix": "Anfisa",
    
..

    Prefix is added to Druid names of datasets. It allows to use single Druid instance for multiple instances of Anfisa. 
        
    ::
        
        "index": "http://<DRUID_IP>:8081/druid/indexer/v1/task",
        "query": "http://<DRUID_IP>:8888/druid/v2",
        "sql":   "http://<DRUID_IP>:8888/druid/v2/sql",
        "coord": "http://<DRUID_IP>:8081/druid/coordinator/v1"

..

        Settings define addresses of four different kinds of requests to Druid. Settings are configured for Druid version v.0.17.0.

::

        "-scp": {...}
    }
    
    
2.7.2. Separate machine configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In case of a separate machine configuration, there are two recommended ways to provide connection between Anfisa and Druid machines.

The first way is to make mount point for vault directory to Druid machine, make sure path to vault is the same on both machines

The second variant is more complex. The problem is: Anfisa needs to copy data to the machine with Druid in order to perform data ingestion. This can be done via ​scp​.

In this section we will use:

    * Instance with Anfisa installation — ``<ANFISA_PC>``

    * Instance with Druid installation — ``<DRUID_PC>``

    Configuration steps:

    1. One needs to create data directory, which would receive data.

    2. SSH keypair needs to be created on a <ANFISA_PC>: ::

        $ ssh-keygen
    
      **Important**: passphrase should be empty.

    3. Public key of the new keypair needs to be added to the end of the ``/home/<user>/.ssh/authorized_keys`` file on the ``<DRUID_PC>``

    4. **Important**: ​you have to manually perform first login from ``<ANFISA_PC>`` to the ``<DRUID_PC>​``: ::
        
        $ ssh -i <PATH_TO_PRIVATE_KEY> <user>@<DRUID_PC>

    5. Uncomment ​“scp”​ subsection of the ​“druid”​ section in the ​anfisa.json: ::

        "scp": {
            "dir": "​<DATA_DIR>​",
            "key": "​<PATH_TO_PRIVATE_KEY>​",
            "host": "​<USER>​@​<DRUID_PC>​",
            "exe": "/usr/bin/scp"
        }
    
      Where:

        * ``<DATA_DIR>`` is a path of an existing directory on ``<DRUID_PC>``. This is the target directory, which would receive data.
            
        * ``<PATH_TO_PRIVATE_KEY>​`` is a path to the private key on ``<ANFISA_PC>``.
