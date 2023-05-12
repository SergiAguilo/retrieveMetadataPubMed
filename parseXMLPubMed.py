# Import libraries
import xml.etree.ElementTree as ET
import sqlite3
import gzip
import argparse

from os import walk

# Argument parser
parser = argparse.ArgumentParser(description='This program extracts metadata of XML articles from PubMed')


parser.add_argument("-d", "--database", help="Required. Database Name where the data will be stored. Not possible to update the database. It should have '.db' sufix",
required=True)

parser.add_argument("-i", "--input", help="Required. Path of the folder where the metadata files (pubmed**n****.xml.gz files) are located",
required=True)

args = parser.parse_args()

# Input PMID file, if not we will parse all available PMID publications of EuropePMC
# 

# # Name of the database
DB_FILE = args.database

# # Connect to the SQLite database
# # If name not found, it will create a new database
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

dummyCounter = 0


def createDatabase():

    c.execute('''DROP TABLE IF EXISTS MainMetadata''')
    c.execute('''CREATE TABLE IF NOT EXISTS "MainMetadata" (
	            "title"	TEXT,
                "abstract"	TEXT,
                "year"	INTEGER,
                "pmid"	INTEGER NOT NULL,
                "doi"	TEXT,
                "pmcid"	TEXT,
	            "ISSN" TEXT,
                "ISOAbbreviation" TEXT,
	            PRIMARY KEY("pmid")
            )''')

    c.execute('''DROP TABLE IF EXISTS MeshTags''')
    c.execute('''CREATE TABLE IF NOT EXISTS "MeshTags" (
	            "pmid"	INTEGER NOT NULL,
	            "descriptionName" TEXT,
                "descriptionUI" TEXT,
                "qualifierName" TEXT,
                "qualifierUI" TEXT,
	            FOREIGN KEY("pmid") REFERENCES "MainMetadata"("pmid")
            )''')
    conn.commit()

def commitToDatabase(dictMetadata, listMesh):

    c.execute(f'''INSERT OR IGNORE INTO MainMetadata
        values ("{dictMetadata["title"]}",
            "{dictMetadata["abstract"]}",
            "{dictMetadata["year"]}",
            "{dictMetadata["pubmed_id"]}",
            "{dictMetadata["doi_id"]}",
            "{dictMetadata["pmc_id"]}",
            "{dictMetadata["ISSN"]}",
            "{dictMetadata["ISOAbbrevation"]}"
        )''')
    
    for dictTag in listMesh:
        c.execute(f'''INSERT OR IGNORE INTO MeshTags
            values ("{dictMetadata["pubmed_id"]}",
                "{dictTag["descriptor_label"]}",
                "{dictTag["descriptor_UI"]}",
                "{dictTag["qualifier_label"]}",
                "{dictTag["qualifier_UI"]}"
            )''')


def retrieveMeshTags(article):
    list_Mesh = []
    
    for mesh_tags in article.iter("MeshHeading"):
        dictMesh = {"descriptor_label" : None,
                    "descriptor_UI" : None,
                    "qualifier_label" : None,
                    "qualifier_UI" : None}
        for descriptor_attr in mesh_tags.iter("DescriptorName"):
            dictMesh["descriptor_label"] = descriptor_attr.text
            dictMesh["descriptor_UI"] = descriptor_attr.attrib['UI']
        for qualifier_attr in mesh_tags.iter("QualifierName"):
            dictMesh["qualifier_label"] = qualifier_attr.text
            dictMesh["qualifier_UI"] = qualifier_attr.attrib['UI']
        list_Mesh.append(dictMesh)
    return list_Mesh
    

def parseFile(pathFile):
    global dummyCounter
    with gzip.open(pathFile,"r") as f:
        # Read XML file
        root = ET.parse(f)
        # For all the publications in the file
        for article in root.iter("PubmedArticle"):
            dummyCounter += 1
            # Initialize variables
            dictMetadata = {"title" : None,
                            "abstract" : None,
                            "year" : None,
                            "pubmed_id" : None,
                            "doi_id" : None,
                            "pmc_id" : None,
                            "ISSN" : None,
                            "ISOAbbrevation" : None}
            
            for title_atr in article.iter("ArticleTitle"):
                title = ''.join(title_atr.itertext())   # Take all text and the tags inside them
                dictMetadata["title"] = title.replace('"', "'")         # Standarize the quotation marks
            

            for abs_atr in article.iter("AbstractText"):
                abstract = ''.join(abs_atr.itertext())   # Take all text and the tags inside them
                dictMetadata["abstract"] = abstract.replace('"', "'")         # Standarize the quotation marks
            
            # Search and store the year of publication
            for date_atr in article.iter("PubDate"):
                for year_atr in date_atr.iter("Year"):  
                    dictMetadata["year"] = year_atr.text

            # Search and store the ID of the article
            # We only want the first <ArticleIdList>, because is the one having the Id of the article
            # The other <ArticleIdList> are for the references
            for articleId_atr in article.iter("ArticleIdList"):
                for Id_atr in articleId_atr.iter("ArticleId"):
                    if "pubmed" in Id_atr.attrib["IdType"]:
                        dictMetadata["pubmed_id"] = Id_atr.text
                    if "doi" in Id_atr.attrib["IdType"]:
                        dictMetadata["doi_id"] = Id_atr.text
                    if "pmc" in Id_atr.attrib["IdType"]:
                        dictMetadata["pmc_id"] = Id_atr.text
                break

            
            # Journal Info
            for journal_info in article.iter("Journal"):
                for ISSN_attr in journal_info.iter("ISSN"):
                    dictMetadata["ISSN"] = ISSN_attr.text
                for ISO_attr in journal_info.iter("ISOAbbreviation"):
                    dictMetadata["ISOAbbrevation"] = ISO_attr.text
            
            # Tags
            listMesh = retrieveMeshTags(article)
            
            # Insert data to database
            commitToDatabase(dictMetadata, listMesh)
    print(dummyCounter)


def main():
    
    createDatabase()

    # Take path
    _, _, filenames = next(walk(f"{args.input}/"))

    for files in filenames:
        filepath = f"{args.input}/{files}"
        # Not compressed files are not parsed (Ex: Index files)
        if not filepath.endswith("xml.gz"):
            continue
        print("Parsing", filepath)
        parseFile(filepath)
        conn.commit()

if __name__ == '__main__':
    main()
    c.close()