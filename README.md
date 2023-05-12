# retrieveMetadataPubMed
Script to retrieve metadata for the FTP data from the baseline of PubMed

The metadata retrieved is the following: Title, abstract, year, pubmed id, doi, pmcid, ISSN, ISO abbreviation and the label and Id of the Mesh Tags.

As the script is created to parse large amounts of data (~ 40G is the full PubMed Metadata in 2022), it is stored in a SQLite database.
 
Python 3.5 or later is needed. The script depends on standard libraries, plus the ones declared in [requirements.txt](requirements.txt).
 
 * In order to install the dependencies you need `pip` and `venv` Python modules.
	- `pip` is available in many Linux distributions (Ubuntu package `python-pip`, CentOS EPEL package `python-pip`), and also as [pip](https://pip.pypa.io/en/stable/) Python package.
	- `venv` is also available in many Linux distributions (Ubuntu package `python3-venv`). In some of these distributions `venv` is integrated into the Python 3.5 (or later) installation.

* The creation of a virtual environment and installation of the dependencies in that environment is done running:

```bash
python3 -m venv .pyXMLenv
source .pyXMLenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Run the following command to use the script:

 
 ```
 
usage: parseXMLPubMed.py [-h] -d DATABASE -i INPUT

This program extracts sections and metadata of XML article from EuropePMC

options:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        Required. Database Name where the data will be stored. Not possible to update the database. It should have '.db' sufix
  -i INPUT, --input INPUT
                        Required. Path of the folder where the metadata files (pubmed**n****.xml.gz files) are located

 ```

 Example:

 ```
python3 parseXMLPubMed.py -i exampleData -d exampleDatabase.db
 ```

To look at the data I suggest to download the [DB Browser for SQLite](https://sqlitebrowser.org/).

The data is gathered from [ftp.ncbi.nlm.nih.gov/pubmed/baseline/](ftp.ncbi.nlm.nih.gov/pubmed/baseline/).
