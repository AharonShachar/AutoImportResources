__author__ = 'Aharon.S'
import os
import csv
from qualipy.api.cloudshell_api import *
import qualipy.api.cloudshell_api as API
import qualipy.scripts.cloudshell_dev_helpers as dev
import qualipy.scripts.cloudshell_scripts_helpers as script_helper
import  xml.etree.ElementTree as ET
from xml.sax.saxutils import unescape

#Globals
AttrbuteIndexInCSVFile = 7
FamilyColumn = 3
ModelColumn = 4
ResourceNameColumn = 2

class CloudShellManager:
    def __init__(self, session):
        self.session = session
        self.Families = []
        self.models = []
        self.attributes = []
        filename = "C:\\Users\\aharon.s\\Desktop\\system.xml"
        file_object = open(filename, "r")
        self.Tree = ET.fromstring( file_object.read())
        #xmlres = session.ExportFamiliesAndModels()
        #unescape. xmlres
        #file_object.write(xmlres)
        #xmlres = xmlres.replace("&gt;", ">")
        #xmlres = xmlres.replace("&gt;&#xD;", ">")
        #xmlres = xmlres.replace("&lt;", "<")
        #xmlres = xmlres.replace("&#xD;", "")
        #xmlres = xmlres.replace('xmlns="[^"]+"', '', 1000)
        #res1 = xmlres.replace("xmlns:xsd=""http://www.w3.org/2001/XMLSchema""", "", 1000)
        #xmlres = xmlres.replace("xmlns=""http://schemas.qualisystems.com/ResourceManagement/ExportImportConfigurationSchema.xsd""", "")

    def IslegalResource(self, row):
        res = True

        familyName = row[FamilyColumn]
        modelName = row[ModelColumn]
        perdicate = 'ResourceFamilies/ResourceFamily[@Name="_family_name_"]/Models/ResourceModel[@Name="_model_name_"]'
        perdicate = perdicate.replace('_family_name_', familyName)
        perdicate = perdicate.replace('_model_name_', modelName)
        model = self.Tree.findall(perdicate)

        if len(model) == 0:
            print ("Can't locate Family/ Model: " + row[FamilyColumn] + '/' + row[ModelColumn] + " for the following resource: " + row[ResourceNameColumn])
            res = False

        return res

    def IsLegalResourceAttributes(self, row):
        res = True

        familyName = row[FamilyColumn]
        modelName = row[ModelColumn]

        perdicate = '../ResourceFamilies/ResourceFamily[@Name="_family_name_"]/AttachedAttributes/AttachedAttribute'
        perdicate = perdicate.replace('_family_name_', familyName)
        familyAttributes = self.Tree.findall(perdicate)

        perdicate = 'ResourceFamilies/ResourceFamily[@Name="_family_name_"]/Models/ResourceModel[@Name="_model_name_"]//AttachedAttribute'
        perdicate = perdicate.replace('_family_name_', familyName)
        perdicate = perdicate.replace('_model_name_', modelName)
        modelAttributes = self.Tree.findall(perdicate)

        legalAttributes = familyAttributes + modelAttributes
        resourceAttributrs = row[AttrbuteIndexInCSVFile:len(row)]

        filterdResourceAttributrs = filter(None,resourceAttributrs)
        if not filterdResourceAttributrs: #no attributes exists
            return False

        for index, attribute in enumerate(resourceAttributrs):
            if attribute:
                attributeKey = self.attributes[index]
                if not attributeKey in legalAttributes:
                    print ("Can't locate attribute: " + attributeKey + " for the following resource: " + row[ResourceNameColumn])
                    return False

        return res

    def AddRow(self, row):
        parent = row[0]
        description = row[1]
        name = row[2]
        family = row[3]
        model = row[4]
        folder = row[5]
        address = row[6]
        if name == 'Name':#Row 0 - save the attributes keys
            if len(row) > AttrbuteIndexInCSVFile:
                self.attributes = row[AttrbuteIndexInCSVFile:len(row)-1]
        else:
            if folder and (not parent):
                self.session.CreateFolder(folder)

            try:#add reource
                if self.IslegalResource(row):
                    res = self.session.CreateResource(family, model, name, address, folder, parent, description)
                    print('Resource: '+name+'added successfully.' )

            except CloudShellAPIError as error:
                print 'Error creating resource: '+name+'. '+error.message

            try:#add reesource attributes
                if self.IsLegalResourceAttributes(row):
                    self.SetAttributes(row)
                    print('Resource attributes : '+name+'added successfully.' )

            except CloudShellAPIError as error:
                print 'Error adding resource attributes: '+name+'. '+error.message


    def SetAttributes(self, row):
        if not len(row) <= AttrbuteIndexInCSVFile:
            attributes = row[AttrbuteIndexInCSVFile:len(row)-1]
            for index,  att in enumerate(attributes):

                name = row[2]
                parent = row[0]

                if parent:  # Not root resource
                    fullName = row[0] + '\\' + name
                else:
                    fullName = name

                AttributeName = self.attributes[index]
                AttributeValue = attributes[index]
                if not AttributeValue:
                    self.session.SetAttributeValue(fullName, AttributeName, AttributeValue)


ApiSession = CloudShellAPISession("localhost", "admin", "admin", "Global")
manager = CloudShellManager(ApiSession)
#ApiSession.SetAttributesValues()

with open('C:\\Users\\aharon.s\\Dropbox\\\QualiSystems\\Python\\Resources.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='\n')
    for row in spamreader:
        try:
            manager.AddRow(row)

        except CloudShellAPIError as error:
            print error.message + ". Input entry row in CSV: " + ', '.join(row)
