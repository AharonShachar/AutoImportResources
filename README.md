# AutoImportResources
Import resources from CSV  file to CloudShell server

Pre-requisite:

CloudShell 6.4 and up

Before using:

The script does not create resource families/models & the attribute associations – that should be done before running the script in Resource Manager.

#How to use (alpha):

1.	Prepare your CSV file according to the following instructions (as well please see the attached Sample.csv):

	a.	The file headers must have the following 6 headers: Parent, Description, Name, ResourceFamilyName, ResourceModelName, FolderFullPath, Address
	
	b.	Attributes will be added in the 7th  and above.

	c.	Root resources – should not have parent value, but should have folder value – if folder is empty the resource will be created in the main root tree.
	
	d.	Sub resources – should have parent value – this value should be the full parent path – please see line No.9 in the Sample.csv file.

	e.	Attributes – in order to associate attributes with a resource - make sure the attribute is added to the resource model In the Resource Manager application.
	
	f.	In the resource line set the attribute value under the relevant attribute header,  if the attribute header is missing – add it.

2.	Download the script and open it using Python editor.

3.	Set the CloudShell server credentials – line 202: ApiSession = CloudShellAPISession("localhost", "admin", "admin", "Global")

4.	Set the CSV path: line 206: with open('C:\\Resources.csv') as csvfile:

5.	Run the script – look at the console to see the results.




