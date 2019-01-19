#!/usr/bin/env python2.7

""" Extracts unique PDB id, chain, accession number combinations from the RCSB PDB database.
Requires BeautifulSoup and lxml.
(C) Aleksandra Jarmolinska 2019"""


import sys
from bs4 import BeautifulSoup
import urllib2
import re

def fetchReleasedPdbs(from_date,to_date=''):
    '''
        Download list of pdb ids released in range from_date - to_date (or in day from_date). Return False if empty list
	(C) Michal Jarmoz
    '''
    if to_date == '':
        to_date = from_date
    '''
    date in format 2009-07-01
    '''
    url = 'http://www.rcsb.org/pdb/rest/search'
    queryText = """
<orgPdbCompositeQuery version="1.0">
<queryRefinement>
<queryRefinementLevel>0</queryRefinementLevel>
<orgPdbQuery>

<queryType>org.pdb.query.simple.ReleaseDateQuery</queryType>
<pdbx_audit_revision_history.revision_date.comparator>between</pdbx_audit_revision_history.revision_date.comparator>
<pdbx_audit_revision_history.revision_date.min>%s</pdbx_audit_revision_history.revision_date.min>
<pdbx_audit_revision_history.revision_date.max>%s</pdbx_audit_revision_history.revision_date.max>
<pdbx_audit_revision_history.ordinal.comparator>=</pdbx_audit_revision_history.ordinal.comparator>
<pdbx_audit_revision_history.ordinal.value>1</pdbx_audit_revision_history.ordinal.value>
</orgPdbQuery>
</queryRefinement>
<queryRefinement>
<queryRefinementLevel>1</queryRefinementLevel>
<conjunctionType>and</conjunctionType>
<orgPdbQuery>
<queryType>org.pdb.query.simple.ChainTypeQuery</queryType>
<description>Chain Type: there is a Protein chain</description>
<containsProtein>Y</containsProtein>
<containsDna>?</containsDna>
<containsRna>?</containsRna>
<containsHybrid>?</containsHybrid>
</orgPdbQuery>
</queryRefinement>
</orgPdbCompositeQuery>
    """%(from_date,to_date)

    req = urllib2.Request(url, data=queryText)
    f = urllib2.urlopen(req)
    result = [i.strip() for i in f.readlines()]
    f.close()
    if result:
        return result
    else:
        return False

def urlopen(address):
    """ Retry the connection in case of an overload """
    x = None
    for i in xrange(3):
        try:
            response = urllib2.urlopen(address)
            return response
        except urllib2.HTTPError, e:
            x = e
            continue
        except urllib2.URLError, e:
            x = e
            continue
    else:
        raise urllib2.URLError("Error trying to connect to {}:\n{}\nRefresh page to retry".format(address,x))


def get_xml(pdbId):
    ''' Open the XML desctiption of the molecule '''
    address="http://www.rcsb.org/pdb/rest/describeMol?structureId={PDBID}".format(PDBID=pdbId)
    response = urlopen(address)
    html = response.read()
    return html

def extract_chain_from_xml(PDB_ID):
    ''' Extract (and return) the chain id and accession number for every protein chain (only unique polymers) '''
	thefile = get_xml(PDB_ID)
	y=BeautifulSoup(thefile,"lxml")
	return [(x.chain["id"],x.macromolecule.accession["id"] if x.macromolecule else None) for x in y.findAll("polymer") if x["type"]=="protein"]

def get_unique_accession_chains(from_date,to_date = ''):
    ''' Extract unique (in terms of accession) protein chains deposited between (or on the date[s])'''

	accessions = {}
	accessions["unknown"] = []

	pdbs = fetchReleasedPdbs(date_from,date_to)
	for pdb in pdbs:
		for chain in extract_chain_from_xml(pdb):
			if chain[1]:
				accessions[chain[1]] = (pdb,chain[0])
			else:
				accessions["unknown"].append((pdb,chain[0]))
    return accessions

if __name__ == "__main__":
	date_from = sys.argv[1]
	date_to = sys.argv[2] if len(sys.argv)>2 else ''
    accessions = get_unique_accession_chains(from_date,to_date)
	for p,c in accessions["unknown"]:
		print p,c,None
	del accessions["unknown"]
	for a,(p,c) in accessions.items():
		print p, c,a

#	thefile = get_xml("4yvi")
#	y=BeautifulSoup(thefile,"lxml")
#	print [x.chain["id"] for x in y.findAll("polymer") if x["type"]=="protein"]
#	e = xml.etree.ElementTree.fromstring(thefile)
#	print e
