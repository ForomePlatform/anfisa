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
        'backports.statistics',
        'bitarray',
        'cachetools',
        'enum34',
        'export',
        'forome_tools>=0.1.7',
        'jsonpath_rw',
        'openpyxl',
        'pipreqs',
        'Pygments',
        'pymongo>=4.0.1',
        'wheel'
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"]
)
