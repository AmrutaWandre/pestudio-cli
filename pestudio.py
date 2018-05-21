#!/usr/bin/python3

import argparse
from SignatureMatcher import SignatureMatcher
from PeAnalyzer import PeAnalyzer
from VirusTotalClient import VirusTotalClient
import prettytable
import re
import constants
import xml.etree.ElementTree as ET
import sys

def parseCommandLineArguments():
	parser = argparse.ArgumentParser(description='PE file analyzer. The default output is human-readable and structured in tables. If no file is specifies, the interactive mode is entered.')
	parser.add_argument("-f", "--file", help="The file to analyze", required=False, dest="file")
	parser.add_argument("-v", "--virusTotal", help="Submit the file to virus total and get their score.", action="store_true", dest="virusTotal")
	parser.add_argument("--header", help="Show information from header.", action="store_true", dest="header")
	parser.add_argument("-i", "--imports", help="Check the imports against known malicious functions.", action="store_true", dest="imports")
	parser.add_argument("-r", "--resources", help="Check the resources for blacklisted values.", action="store_true", dest="resources")
	parser.add_argument("-s", "--signatures", help="Check for known signatures (e.g. packers).", action="store_true", dest="signatures")
	parser.add_argument("-x", "--xml", help="Format output as xml.", action="store_true", dest="xml")
	return parser.parse_args()

def interactiveMode():
	print("No file has been specified. Entering interactive mode...")

def checkFile(args):
	if args.xml:
		root = ET.Element("Report")

	if args.virusTotal:
		vt = VirusTotalClient(args.file)
		resource = vt.sendRequest()
		if resource is not None:
			report = vt.getReport(resource)
			if args.xml:
				root = vt.getXmlReport(report, root)
			else:
				print(vt.printReport(report))
	
	peAnalyzer = PeAnalyzer(args.file)
	
	if args.header:
		if args.xml:
			peAnalyzer.addHeaderInformationXml(root)
		else:
			peAnalyzer.printHeaderInformation()
	
	if args.imports:
		blacklistedImports, imports = peAnalyzer.blacklistedImports()
		
		if args.xml:
			suspicious, imp = peAnalyzer.checkImportNumber()
			root = peAnalyzer.getImportXml(blacklistedImports, imports, root)
		else:
			peAnalyzer.printImportInformation(blacklistedImports, imports, suspicious)
	
	if args.resources:
		blacklistedResources = peAnalyzer.blacklistedResources()
		
		if args.xml:
			root = peAnalyzer.addResourcesXml(blacklistedResources, root)
		else:
			print("Blacklisted resources found: " + str(blacklistedResources) if len(blacklistedResources) > 0 else "No blacklisted resources found")
			# TODO: Check resource types and corresponding thresholds in thresholds.xml
			
			peAnalyzer.showAllResources()
	
	if args.signatures:
		matcher = SignatureMatcher(args.file)
		signatures, maxSize = matcher.getSignatures()
		packers = matcher.findPackers(signatures, maxSize)
		
		if args.xml:
			matcher.addPackersXml(packers, root)
		else:
			if len(packers):
				print(constants.RED + "The signature of the following packer was found: " + str(packers) + constants.RESET)
			else:
				print("No packer signature was found in the PE file")
	
	if args.xml:
		print(ET.tostring(root))
	

if __name__ == "__main__":
	args = parseCommandLineArguments()
	if args.file is None:
		interactiveMode()
	else:
		checkFile(args)