__author__ = 'Aharon.S'
import os
import csv
from qualipy.api.cloudshell_api import *
import HTMLParser
import  xml.etree.ElementTree as ET



#Globals
AttrbuteIndexInCSVFile = 7
AddressColumn = 6
FolderColumn = 5
ModelColumn = 4
FamilyColumn = 3
ResourceNameColumn = 2
DescriptionColumn = 1
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
        self.countAttributeKeys = 0
        self.countRows = 0

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

        #Cheack if the row attributes exceed the legal attributes
        countAttributesValues = len(row[AttrbuteIndexInCSVFile:len(row)])
        if countAttributesValues > self.countAttributeKeys:
            print ("Error set attributes for resource: '"+row[ResourceNameColumn] +"', Number of attributes values exceeds the CSV file legal attribues keys. Please cheack if the CSV contains empty columns.")
            return False


        if (not familyName or not modelName or familyName.isspace() or modelName.isspace() ):
            print ("Error set attribute for resource: '"+ row[ResourceNameColumn]+ "'. The Model / Familiy can't be empty")
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
                    print ("Can't locate attribute: '" + attributeKey + "' for the following resource: '" + row[ResourceNameColumn]) +"'"
                    return False
        return res

    def AddResource(self, row):
        parent = row[ParentColumn]
        description = row[DescriptionColumn]
        name = row[ResourceNameColumn]
        family = row[FamilyColumn]
        model = row[ModelColumn]
        folder = row[FolderColumn]
        address = row[AddressColumn]

        try:#add reource
            if self.IslegalResource(row):
                if(parent): #sub resource
                    folder = self.session.GetResourceDetails(parent).FolderFullPath

                self.session.CreateResource(family, model, name, address, folder, parent, description)
                print("Resource: '"+name+"' added successfully" )

        except CloudShellAPIError as error:
            print "Error creating resource: '"+name+"'. "+error.message

    def AddAttributes(self, row):

        name = row[ResourceNameColumn]

        if not len(row) <= AttrbuteIndexInCSVFile:
            attributes = row[AttrbuteIndexInCSVFile:len(row)]

        #check if the resource has attributes
        isEmptyList = True

        for attribute in attributes:
            if attribute and not attribute.isspace():#there is real attribute
                isEmptyList = False
                break

        if isEmptyList:
            print("No attributes for resource: '"+ row[ResourceNameColumn] +"'")
            return

        try:#add reesource attributes
            if self.IsLegalResourceAttributes(row):
                self.SetAttributes(row)
                #print('Attributes for resource: '+ name +' added successfully.' )

        except CloudShellAPIError as error:
            print "Error set resource attributes, resource name: '"+ name +"'. "+ error.message

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

                if AttributeValue and not AttributeValue.isspace():
                    self.session.SetAttributeValue(fullName, AttributeName, AttributeValue)
                    print ("Set attribute for resource: '"+resourceName + "' - attribute name: '" + AttributeName + "', attribute value: '"+AttributeValue +"'" )

    def SetHeader(self,row):
        if len(row) > AttrbuteIndexInCSVFile:
                   self.attributes = row[AttrbuteIndexInCSVFile:len(row)]#save the attributes keys

        for index,key in enumerate(row):
            if key and not key.isspace():
                lastKeyPosition = index

        self.countAttributeKeys = len(row[AttrbuteIndexInCSVFile:lastKeyPosition]) + 1

    def isEmptyRow(self,row):
        res = True

        for value in row:
            if value and not value.isspace():
                return False

        return res



ApiSession = CloudShellAPISession("localhost", "admin", "admin", "Global")
manager = CloudShellManager(ApiSession)


with open('C:\\Resources.csv') as csvfile:
    csvReader = csv.reader(csvfile, delimiter=',', quotechar='\n')

    for row in csvReader:
        parent = row[ParentColumn]
        name = row[ResourceNameColumn]
        folder = row[FolderColumn].decode('unicode_escape')

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

        except CloudShellAPIError as error:
            print "Error in CSV row entry: '"  + ', '.join(row) +". "+ error.message
