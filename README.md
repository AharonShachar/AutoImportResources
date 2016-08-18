# About this utility
This CLI utility will import resources from CSV  file to CloudShell server

# Pre-requisites
 * CloudShell 6.4 and up
 * The script does not create resource families/models & the attribute associations – that should be done before running the script in Resource Manager.


# How To
## Installing
 * Download the repository somewhere
 * `cd` to that directory
 * Run `pip install --editable .`
 
## From PyPi
 * `pip install CSImportResources`
 
## Using the utility
### Preparing the CSV file 
* Either download the CSV from this repo or use the create flag to create one: `CSImportResources -c C:\temp\sample.csv
* Edit the CSV file according to the following instructions:
 * The file headers must have the following 6 headers: Parent, Description, Name, ResourceFamilyName, ResourceModelName, FolderFullPath, Address
 * Attributes will be added in the 7th  and above.
 * Root resources – should not have parent value, but should have folder value – if folder is empty the resource will be created in the main root tree.
 * Sub resources – should have parent value – this value should be the full parent path – please see line No.9 in the Sample.csv file.
 * Attributes – in order to associate attributes with a resource - make sure the attribute is added to the resource model In the Resource Manager application.
 * In the resource line set the attribute value under the relevant attribute header,  if the attribute header is missing – add it.
* Run the script – look at the console to see the results
 * `CSImportResource -q localhost -u admin -p admin -d Global -f c:\temp\sample.csv`
 