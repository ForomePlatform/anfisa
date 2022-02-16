import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "app",
            "VERSION"
         ),
        "r", encoding = "utf-8"
    ) as inp:
    v = inp.read().strip().split(' ')
    VERSION = v[1]


setuptools.setup(
    name = "forome_anfisa",
    version = VERSION,
    author = "Sergey Trifonov, with colleagues",
    author_email = "trf@ya.ru",
    description = "Variant Analysis and Curation Tool (Back-end, REST API and Internal Client)",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/ForomePlatform/anfisa",
    packages = setuptools.find_packages(),
    install_requires = [
        'alabaster==0.7.10',
        'asn1crypto==0.24.0',
        'Babel==2.5.3',
        'backports-datetime-fromisoformat',
        'backports.statistics',
        'bcrypt==3.1.4',
        'bitarray',       
        'cachetools',
        'certifi==2018.4.16',
        'cffi',
        'chardet==3.0.4',
        'crcmod==1.7',
        'docutils==0.14',
        'enum34',
        'et-xmlfile==1.0.1',
        'export',
        'funcsigs==1.0.2',
        'forome_tools>=0.1.7',
        'gunicorn==19.7.1',
        'idna==2.6',
        'imagesize==1.0.0',
        'ipaddress==1.0.22',
        'JayDeBeApi==1.1.1',
        'jdcal==1.4',
        'Jinja2',
        'jsonpath_rw',
        'JPype1==0.6.3',
        'lxml',
        'MarkupSafe',
        'mock==2.0.0',
        'netifaces==0.10.7',
        'openpyxl',
        'pipreqs',
        'Pygments',
        'pymongo>=4.0.1',
        'packaging==17.1',
        'paramiko',
        'pbr==4.0.3',
        'pycparser==2.18',
        'pyliftover==0.3',
        'PyNaCl==1.2.1',
        'PyOpenGL==3.0.2',
        'pyparsing',
        'pytz==2018.4',
        'PyVCF==0.6.8',
        'PyYAML',
        'requests',
        'six==1.11.0',
        'snowballstemmer==1.2.1',
        'sortedcontainers==2.0.5',
        'Sphinx==1.7.4',
        'sphinxcontrib-websupport==1.0.1',
        'sshtunnel==0.1.4',
        'stevedore==1.28.0',
        'typing==3.6.4',
        'urllib3',
        'uWSGI==2.0.17.1',
        'virtualenv==15.1.0',
        'virtualenv-clone==0.2.6',
        'virtualenvwrapper==4.8.2',       
        'wheel'
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"]
)
