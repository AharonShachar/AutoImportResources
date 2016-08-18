import cloudshell.api.cloudshell_api as api
import argparse
from CloudShellManager import CloudShellManager
import csv

def cli():
    # Build CLI parser to get info. Should be passed in via CLI from PHP
    parser = argparse.ArgumentParser(description='CLI Tool to import resources via CLI into CloudShell v0.3')
    # creds
    parser.add_argument('-c', action="store", dest="create", help="create a sample CSV")
    parser.add_argument('-q', action="store", dest="host", help="server hostname for API session")
    parser.add_argument('-u', action="store", dest="un", help="username for API session")
    parser.add_argument('-p', action="store", dest="pw", help="password for API session")
    parser.add_argument('-d', action="store", dest="dom", help="domain for API session")
    # args
    parser.add_argument('-f', action='store', dest="file", help="filename to import")

    arg = parser.parse_args()

    if(arg.create != None):
        print "Creating sample CSV file in " + arg.create
        csvContents = """Parent,Description,Name,ResourceFamilyName,ResourceModelName,FolderFullPath,Address,Location,Vendor,Gateway,Duplex,Speed
,description,MyAccess,Access,ALU ADSL,LabA/room-C,199.999.777,,Huawei,,,
MyAccess,,Port1,Generic Port,Generic Ethernet Port,not relevant,1,,,,,1 Gbps
MyAccess,,Port2,Generic Port,Generic Ethernet Port,,2,,,,Half,
,,,,,,,,,,,
,,,,,,,,,,,
,GW description,myGateWay,Gateway,Gateway Generic Model,Lab_B/room_A,12.23.3.2,RoshPina,,,,
myGateWay,nas gateway,myBlade,Generic Blade,Generic Blade Model,not relevant,1,,,,,
myGateWay/myBlade,,p1,Generic Port,Generic Ethernet Port,,1,,,,Half,1 Gbps
myGateWay/myBlade,,p2,Generic Port,Generic Ethernet Port,,1,,,,Half,1 Gbps

"""
        fh = open(arg.create,"w")
        fh.write(csvContents)
        fh.close()
        exit(0)

    # make sure all args are there
    elif ((arg.host != None) and (arg.un != None) and (arg.pw != None) and (arg.dom != None) and (arg.file != None)):

        ApiSession = api.CloudShellAPISession(arg.host, arg.un, arg.pw, arg.dom)
        manager = CloudShellManager(ApiSession)

        with open(arg.file) as csvfile:
            csvReader = csv.reader(csvfile, delimiter=',', quotechar='\n')

            for row in csvReader:
                parent = row[manager.ParentColumn]
                name = row[manager.ResourceNameColumn]
                folder = row[manager.FolderColumn].decode('unicode_escape')

                try:
                    if name == 'Name':#Row 0 -
                        manager.SetHeader(row)

                    else:#
                        if folder and (not parent): #root resource
                            print folder
                            manager.session.CreateFolder(folder)

                        if not manager.isEmptyRow(row):
                            manager.AddResource(row)
                            manager.AddAttributes(row)

                except Exception as error:
                    print "Error in CSV row entry: '"  + ', '.join(row) +". "+ error.message
                    exit(5)
    else:
        print "You must provide the username, password, domain, and file."
        exit(1)