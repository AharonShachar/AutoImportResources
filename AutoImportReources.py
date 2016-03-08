__author__ = 'Aharon.S'
import os
import csv
from qualipy.api.cloudshell_api import *
import HTMLParser
import  xml.etree.ElementTree as ET



#Globals
AttrbuteIndexInCSVFile = 7
FamilyColumn = 3
ModelColumn = 4
ResourceNameColumn = 2
ParentColumn = 0

class CloudShellManager:
    def __init__(self, session):
        self.ns = {'xsd': 'http://www.w3.org/2001/XMLSchema',
              'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
              'xmlns': 'http://schemas.qualisystems.com/ResourceManagement/ExportImportConfigurationSchema.xsd'}
        self.session = session
        self.Families = []
        self.models = []
        self.attributes = []

        #filename = "C:\\Users\\aharon.s\\Desktop\\system.xml"
        #file_object = open(filename, "r")
        #self.Tree = ET.fromstring( file_object.read())

        xmlres = session.ExportFamiliesAndModels()
        xmlres = HTMLParser.HTMLParser().unescape(xmlres)

        appendixNnodelocation = xmlres.index('<ResourceManagementExportImport')
        xmlres = xmlres.replace(xmlres[0:appendixNnodelocation],'',appendixNnodelocation)

        suffixNnodelocation = xmlres.index('</Configuration></ResponseInfo></Response>')
        xmlres = xmlres.replace(xmlres[suffixNnodelocation: len(xmlres)],'',len(xmlres))

        self.Tree = ET.fromstring(xmlres)

    def IslegalResource(self, row):
        res = True

        familyName = row[FamilyColumn]
        modelName = row[ModelColumn]
        name = row[ResourceNameColumn]

        if (not familyName or not modelName or familyName.isspace() or modelName.isspace() ):
            print ("Error create resource: "+ row[ResourceNameColumn]+ ". The Model / Familiy can't be empty")
            return False
        if (name.isspace()):
            print ("Error create resource: "+ row[ResourceNameColumn]+ ". resource name can't be empty")
            return False


        perdicate = 'xmlns:ResourceFamilies/xmlns:ResourceFamily[@Name="_family_name_"]/xmlns:Models/xmlns:ResourceModel[@Name="_model_name_"]'
        perdicate = perdicate.replace('_family_name_', familyName)
        perdicate = perdicate.replace('_model_name_', modelName)
        model = self.Tree.findall(perdicate,self.ns)

        return res

    def IsLegalResourceAttributes(self, row):
        res = True

        familyName = row[FamilyColumn]
        modelName = row[ModelColumn]


        if (not familyName or not modelName or familyName.isspace() or modelName.isspace() ):
            print ("Error set addtibute for resource: "+ row[ResourceNameColumn]+ ". The Model / Familiy can't be empty")
            return False

        perdicate = 'xmlns:ResourceFamilies/xmlns:ResourceFamily[@Name="_family_name_"]/xmlns:Models/xmlns:ResourceModel[@Name="_model_name_"]/xmlns:AttributeValues'
        perdicate = perdicate.replace('_family_name_', familyName)
        perdicate = perdicate.replace('_model_name_', modelName)
        modelAttributes = self.Tree.findall(perdicate, self.ns)
        attributesModelKeys = []

        if not modelAttributes:
            print ("No defined attributes for resource Family/ Model: '" + familyName + "'/ '" + modelName +"'" )
            return False

        for modelAttribute in modelAttributes[0]._children:
            attributesModelKeys.append(modelAttribute.attrib['Name'])

        #List of all the resource attributes
        resourceAttributrs = row[AttrbuteIndexInCSVFile:len(row)]

        for index, attribute in enumerate(resourceAttributrs):
            if attribute:
                attributeKey = self.attributes[index]
                if not attributeKey in attributesModelKeys:
                    print ("Can't locate attribute: '" + attributeKey + "' for the following resource: " + row[ResourceNameColumn])
                    return False
        return res

    def AddResource(self, row):
        parent = row[0]
        description = row[1]
        name = row[2]
        family = row[3]
        model = row[4]
        folder = row[5]
        address = row[6]

        try:#add reource
            if self.IslegalResource(row):
                if(parent):
                    folder = self.session.GetResourceDetails(parent).FolderFullPath

            res = self.session.CreateResource(family, model, name, address, folder, parent, description)
            print('Resource: '+name+'added successfully.' )

        except CloudShellAPIError as error:
            print 'Error creating resource: '+name+'. '+error.message

    def AddAttributes(self, row):

        name = row[ResourceNameColumn]

        if not len(row) <= AttrbuteIndexInCSVFile:
            attributes = row[AttrbuteIndexInCSVFile:len(row)]

        isEmptyList = True

        for attribute in attributes:
            if attribute and not attribute.isspace():#there is real attribute
                isEmptyList = False
                break

        if isEmptyList:
            print('No attributes for resource: '+ row[ResourceNameColumn])
            return

        try:#add reesource attributes
            if self.IsLegalResourceAttributes(row):
                self.SetAttributes(row)
                print('Attributes for resource: '+ name +' added successfully.' )

        except CloudShellAPIError as error:
            print 'Error adding resource attributes: '+name+'. '+error.message

    def SetAttributes(self, row):

        if not len(row) <= AttrbuteIndexInCSVFile:
            attributes = row[AttrbuteIndexInCSVFile:len(row)]

            resourceName = row[ResourceNameColumn]

            for index,  att in enumerate(attributes):
                name = row[ResourceNameColumn]
                parent = row[ParentColumn]

                if parent and not parent.isspace():  # Not root resource
                    fullName = row[ParentColumn] + '\\' + name
                else:
                    fullName = name

                AttributeName = self.attributes[index]
                AttributeValue = attributes[index]

                if AttributeValue and not AttributeValue.ispace():
                    self.session.SetAttributeValue(fullName, AttributeName, AttributeValue)
                    print ("Attribute set - Attribute name: " + AttributeValue + ", Attribute value: "+AttributeValue +", for resource: " + resourceName  )


ApiSession = CloudShellAPISession("localhost", "admin", "admin", "Global")
manager = CloudShellManager(ApiSession)


with open('C:\\Users\\aharon.s\\Dropbox\\\QualiSystems\\Python\\Resources.csv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='\n')
    for row in spamreader:

        parent = row[0]
        description = row[1]
        name = row[2]
        family = row[3]
        model = row[4]
        folder = row[5]
        address = row[6]

        try:
            if name == 'Name':#Row 0 -
                if len(row) > AttrbuteIndexInCSVFile:
                   manager.attributes = row[AttrbuteIndexInCSVFile:len(row)]#save the attributes keys
            else:
                if folder and (not parent):
                    manager.session.CreateFolder(folder)

                manager.AddResource(row)
                manager.AddAttributes(row)

        except CloudShellAPIError as error:
            print error.message + ". Input entry row in CSV: " + ', '.join(row)
