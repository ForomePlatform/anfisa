Configuration service: anfisa.json
==================================

Configuration of the service is organized via the file **anfisa.json**
The file is formed in extended JSON format, extension mean:

    * full line comments starting with '//' are allowed
    * macro definition mechanism supported

The following options are supported.

* **file-path-def**, *dictionary*

.. index:: 
    file-path-def; service configuration option

The directory macro ${HOME} is predefined; here we define more macros, 
in particular the macro ${WORK}::

    "file-path-def": {"WORK": "${HOME}/../a-setup"},

* **host**, *string*
* **port**, *int*

.. index:: 
    host; service configuration option
    port; service configuration option

Host and port are used in the stand-alone configuration to setup the server on a
specific port, ignored in the server (UWIGI container) mode::

    "host": "0.0.0.0",
    "port": 8190,

* **html-base**, *string*

.. index:: 
    html-base; service configuration option

Used in the internal UI: its HTML pages need to know their location in terms of
URL addresses, just to make correct reference to REST API or other pages of
the internal UI, in case of server setup with NextGen UI should end in ‘/​app’::

    "html-base": "/anfisa/",

* **html-ws-url**, *string*
    
.. index:: 
    html-ws-url; service configuration option
    
Address of the NextGen UI base page if the NextGen UI is set up, else keep the default value ​"ws"::

    "html-ws-url": "ws",

* **html-title**, *string*
    
.. index:: 
    html-title; service configuration option

Title prefix used in the pages of the Legacy UI::

    "html-title": "Anfisa",`

* **mongo-db**, *string*
    
.. index:: 
    mongo-db; service configuration option

The database in MongoDB used by the system::

    "mongo-db": "Anfisa",
    
    
* **data-vault**, *string*
    
.. index:: 
    data-vault; service configuration option
    
The location of the vault directory::

    "data-vault": "${WORK}/vault",

* **run-options**, *list*

    Some additional option to configure Anfisa service. Currently out of use::

    "run-options": []

.. _job_vault_check_period:         

    
* **job-vault-check-period**, *int*

    Period between checks of vault data consistence, in seconds::
    
        "job-vault-check-period": 30,
        
* **http-bam-base**, *string*
    
.. index:: 
    http-bam-base; service configuration option

HTTP base directory for access to BAM-files, used in IGV-links. Uncomment this option
and set it up correctly if the server provides access to BAM-files, otherwise keep it
commented::
    
    "http-bam-base": “http://<server>/anfisa/links/"`

* **export**, *dictionary*

  Configuration of export functionality

  * **excel-template**, *string*
    
    The template used to configure the Excel export styles.
    During evaluation of the script deploy.sh the file is being downloaded from URL:
    "​https://www.dropbox.com/s/4dvunn3dusqc636/SEQaBOO_output_template_20190317.xlsx​"

  * **work-dir**, *string*
   
    The directory where the service stores exported files
    
.. index:: 
    export; service configuration option
    excel-template; service configuration option
    work-dir; service configuration option

::

    "export": {
        "excel-template": "${WORK}/export/SEQaBOO_output_template_20190317.xlsx",`
        "work-dir": "${WORK}/export/work"
    }

* **dir-files**, *list*

  Setup of the mechanism of forwarding files as request results::
    
    "dir-files": [
        ["/ui/images", "${HOME}/int_ui/images"],
        ["/ui", "${HOME}/int_ui/files"],
        ["--/ui", "${WORK}/ui"],
        ["/excel", "${WORK}/export/work"]],

  .. index:: 
    export; service configuration option
        
  Comments for instructions in example:
  
  * ``"/ui/images", "/ui"``:
    
    Requests for images and other sources, actual in stand-alone case.
    Should transfer the content of files located in the specific directory in
    $ANFISA_HOME; used in the internal UI in the stand-alone mode; in the
    server mode the same task is solved by configuration of the “main
    server”, Nginx or Apache

  * ``"--/ui"``:
  
    Requests for the source files when the anti-cache mechanism is on; in the
    server mode, to be used in the internal UI instead of the previous
    instruction; (in server setup drop two leading ‘-’ to make it working, and
    comment out the previous instruction)

  * ``"excel"``:
  
    This line sets the directory used to place the content of exported Excel
    files, supposing that they are going to be immediately downloaded by an
    external client

.. _mirror_ui: 
    
* **mirror-ui**, *list*

    .. index:: 
        mirror-ui; service configuration option

    This instruction turns the :term:`anti-cache mechanism` on; it consists of the
    paths to the source and target directories for mirroring (drop two leading
    ‘-’ to make it working)::

    "--mirror-ui": ["${HOME}/int_ui/files", "${WORK}/ui"],

* **druid**, *dictionary*

    See the section about Druid in installation documentation

* **logging**, *dictionary*

    .. index:: 
        logging; service configuration option

    Some standard Python way to configure the logging of a service. Please pay
    attention to one specific line of this stuff:    
    
    **filename** line contains the configuration of the path to the logging directory::
    
        "logging": {
            ...
            "filename": "${WORK}/logs/anfisa.log"
        }
    
    
* **doc-report-css**, *string*
* **doc-pygments-css**, *string*
    
    .. index:: 
        doc-report-css; service configuration option
        doc-pygments-css; service configuration option

    These two options are used to configure styling of documentation pages for datasets::
        
        "doc-report-css": "${HOME}/int_ui/files/report.css",
        "doc-pygments-css": "${HOME}/int_ui/files/py_pygments.css",

