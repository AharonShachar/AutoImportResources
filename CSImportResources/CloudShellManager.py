import csv
import HTMLParser
import  xml.etree.ElementTree as ET
import cloudshell.api.cloudshell_api as api

class CloudShellManager:
    def __init__(self, session):
        self.AttrbuteIndexInCSVFile = 7
        self.AddressColumn = 6
        self.FolderColumn = 5
        self.ModelColumn = 4
        self.FamilyColumn = 3
        self.ResourceNameColumn = 2
        self.DescriptionColumn = 1
        self.ParentColumn = 0
        
        self.ns = {'xsd': 'http://www.w3.org/2001/XMLSchema',
              'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
              'xmlns': 'http://schemas.qualisystems.com/ResourceManagement/ExportImportConfigurationSchema.xsd'}
        self.session = session
        self.Families = []
        self.models = []
        self.attributes = []
        self.countAttributeKeys = 0
        self.countRows = 0

        xmlres = session.ExportFamiliesAndModels()
       # xmlres = HTMLParser.HTMLParser().unescape(xmlres)
       #  appendixNnodelocation = xmlres.index('<ResourceManagementExportImport')
       #  xmlres = xmlres.replace(xmlres[0:appendixNnodelocation],'',appendixNnodelocation)
       #  suffixNnodelocation = xmlres.index('</Configuration></ResponseInfo></Response>')
       #  xmlres = xmlres.replace(xmlres[suffixNnodelocation: len(xmlres)],'',len(xmlres))

        self.Tree = ET.fromstring(xmlres.Configuration)


    def IslegalResource(self, row):
        res = True

        familyName = row[self.FamilyColumn]
        modelName = row[self.ModelColumn]
        name = row[self.ResourceNameColumn]

        if (not familyName or not modelName or familyName.isspace() or modelName.isspace() ):
            print ("Error create resource: "+ row[self.ResourceNameColumn]+ ". The Model / Familiy can't be empty")
            return False
        if (name.isspace()):
            print ("Error create resource: "+ row[self.ResourceNameColumn]+ ". resource name can't be empty")
            return False


        perdicate = 'xmlns:ResourceFamilies/xmlns:ResourceFamily[@Name="_family_name_"]/xmlns:Models/xmlns:ResourceModel[@Name="_model_name_"]'
        perdicate = perdicate.replace('_family_name_', familyName)
        perdicate = perdicate.replace('_model_name_', modelName)
        model = self.Tree.findall(perdicate,self.ns)

        return res

    def IsLegalResourceAttributes(self, row):
        res = True

        familyName = row[self.FamilyColumn]
        modelName = row[self.ModelColumn]

        #Cheack if the row attributes exceed the legal attributes
        countAttributesValues = len(row[self.AttrbuteIndexInCSVFile:len(row)])
        if countAttributesValues > self.countAttributeKeys:
            print ("Error set attributes for resource: '"+row[self.ResourceNameColumn] +"', Number of attributes values exceeds the CSV file legal attribues keys. Please cheack if the CSV contains empty columns.")
            return False


        if (not familyName or not modelName or familyName.isspace() or modelName.isspace() ):
            print ("Error set attribute for resource: '"+ row[self.ResourceNameColumn]+ "'. The Model / Familiy can't be empty")
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
        resourceAttributrs = row[self.AttrbuteIndexInCSVFile:len(row)]

        for index, attribute in enumerate(resourceAttributrs):
            if attribute:
                attributeKey = self.attributes[index]
                if not attributeKey in attributesModelKeys:
                    print ("Can't locate attribute: '" + attributeKey + "' for the following resource: '" + row[self.ResourceNameColumn]) +"'"
                    return False
        return res

    def AddResource(self, row):
        parent = row[self.ParentColumn]
        description = row[self.DescriptionColumn]
        name = row[self.ResourceNameColumn]
        family = row[self.FamilyColumn]
        model = row[self.ModelColumn]
        folder = row[self.FolderColumn]
        address = row[self.AddressColumn]

        try:#add reource
            if self.IslegalResource(row):
                if(parent): #sub resource
                    folder = self.session.GetResourceDetails(parent).FolderFullPath

                self.session.CreateResource(family, model, name, address, folder, parent, description)
                print("Resource: '"+name+"' added successfully" )

        except Exception as error:
            print "Error creating resource: '"+name+"'. "+error.message

    def AddAttributes(self, row):

        name = row[self.ResourceNameColumn]

        if not len(row) <= self.AttrbuteIndexInCSVFile:
            attributes = row[self.AttrbuteIndexInCSVFile:len(row)]

        #check if the resource has attributes
        isEmptyList = True

        for attribute in attributes:
            if attribute and not attribute.isspace():#there is real attribute
                isEmptyList = False
                break

        if isEmptyList:
            print("No attributes for resource: '"+ row[self.ResourceNameColumn] +"'")
            return

        try:#add reesource attributes
            if self.IsLegalResourceAttributes(row):
                self.SetAttributes(row)
                #print('Attributes for resource: '+ name +' added successfully.' )

        except Exception as error:
            print "Error set resource attributes, resource name: '"+ name +"'. "+ error.message

    def SetAttributes(self, row):

        if not len(row) <= self.AttrbuteIndexInCSVFile:
            attributes = row[self.AttrbuteIndexInCSVFile:len(row)]

            resourceName = row[self.ResourceNameColumn]

            for index,  att in enumerate(attributes):
                name = row[self.ResourceNameColumn]
                parent = row[self.ParentColumn]

                if parent and not parent.isspace():  # Not root resource
                    fullName = row[self.ParentColumn] + '\\' + name
                else:
                    fullName = name

                AttributeName = self.attributes[index]
                AttributeValue = attributes[index]

                if AttributeValue and not AttributeValue.isspace():
                    self.session.SetAttributeValue(fullName, AttributeName, AttributeValue)
                    print ("Set attribute for resource: '"+resourceName + "' - attribute name: '" + AttributeName + "', attribute value: '"+AttributeValue +"'" )

    def SetHeader(self,row):
        if len(row) > self.AttrbuteIndexInCSVFile:
                   self.attributes = row[self.AttrbuteIndexInCSVFile:len(row)]#save the attributes keys

        for index,key in enumerate(row):
            if key and not key.isspace():
                lastKeyPosition = index

        self.countAttributeKeys = len(row[self.AttrbuteIndexInCSVFile:lastKeyPosition]) + 1

    def isEmptyRow(self,row):
        res = True

        for value in row:
            if value and not value.isspace():
                return False

        return res