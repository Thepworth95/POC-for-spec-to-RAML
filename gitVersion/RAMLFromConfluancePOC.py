import requests
import json 
from lxml import html
from bs4 import BeautifulSoup

def retrieveData(RequstUrl):

    # This URL will be the URL that your login form points to with the "action" tag.
    PostLoginUrl = 'https://confluence.tools.tax.service.gov.uk/login.action'

    payload = {
        'os_username': '',
        'os_password': ''
    }

    # This fetches the data and seperates the parts we need for use in the RAML
    with requests.Session() as session:
        post = session.post(PostLoginUrl, data=payload)
        page = session.get(RequstUrl)
        soup = BeautifulSoup(page.text, 'html.parser')
        listOfvalues = soup.find_all("td", class_ = "confluenceTd")
        result = []

        for item in listOfvalues:
            if item.p != None:
                result.append(item.p.text)
            elif item.div != None:
                result.append(item.div.text)
            elif item.strong != None:
                result.append(item.strong.text)
            else:
                result.append(item.text)
        return(result)





# This function seperates out the relevent data for the path Parameters and presents them in the same style used in the RAML
def retrievePathParameters(RequstUrl):
    data = retrieveData(RequstUrl)
    res = data.index(u'Path Parameter')
    anotherPathParameter = True
    responseData = []
    while anotherPathParameter:
        responseData.append([data[res+1], data[res+2], data[res+3]])
        if data[res+11] == u'Path Parameter': 
            res = res + 11
        else:
            anotherPathParameter = False
    response = []
    for item in responseData:
        pathParameter = """uriParameters:
                {}:
                    description: {}
                    type: {}
                    example: Insert Example Here
            """.format(
        item[0],
        item[1],
        item[2]
        )
        response.append(pathParameter)
    print(response)
    return(response)





# This function seperates out the relevent data for the query Parameters and presents them in the same style used in the RAML
def retrieveQueryParameters(RequstUrl):
    data = retrieveData(RequstUrl)
    res = data.index(u'Query Parameter')
    anotherPathParameter = True
    responseData = []
    while anotherPathParameter:
        responseData.append([data[res+1], data[res+2], data[res+5]])
        if data[res+11] == u'Query Parameter': 
            res = res + 11
        else:
            anotherPathParameter = False
    response = []
    for item in responseData:
        response.append("""
            {}:
                queryParameters:
                    {}:
                        description: {}
                        example: "---Insert Example Here---"
                        required: {}
            """.format(
        item[0],
        item[0],
        item[1],
        item[2]==u'M'
        ))
    print(response)
    return(response)




# This function seperates out the relevent data for the Request body schema and presents it in the same style used in the RAML schema's
def retrieveRequestBodySchema(RequstUrl, firstField):
    data = retrieveData(RequstUrl)
    anotherPathParameter = True
    responseData = []
    res = data.index(firstField)
    while anotherPathParameter:
        responseData.append([data[res], data[res+1], data[res+2]])
        if data[res+9] != u'O1': 
            res = res + 10
        else:
            anotherPathParameter = False
    response = """{
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "---Insert title---",
        "description": "---Insert description---",
        "type": "object",
        "properties": {
    """
    for item in responseData:
        print(response)
        print(item)
        if item[2]==u'Array':
            response = response + """
            {}: {
                "type": "Array",
                "description": {},
                "items": {
                    "type": "object",
                    "properties": {
            """.format(
                item[0],
                item[1]
            )
        elif item[2]==u'Object':
            pass
        elif item[2]==u'string (date)':
            element = """
            {}: {
                "description": {},
                "type": {},
                "example": "---Insert example from description---"
            }""".format(
                item[0],
                item[1],
                u'string'
            )
        elif item[2]==u'string':
            element = """
            {}: {
                "description": {},
                "type": {},
                "example": "---Insert example from description---"
            }""".format(
                item[0],
                item[1],
                item[2]
            )
        response = response + element
    response = response + """  },
        "additionalProperties": false
    }
    """
    print(response)
    return(response)





# This function seperates out the relevent data for the Response body schema and presents it in the same style used in the RAML schema's
def retrieveResponseBodySchema(RequstUrl):
    data = retrieveData(RequstUrl)
    anotherPathParameter = True
    response = []
    res = data.index(u'O1')
    while anotherPathParameter:
        response.append([data[res], data[res+1], data[res+2], data[res+3], data[res+4], data[res+5], data[res+6], data[res+7], data[res+8]])
        if data[res+9] != u'L1': 
            res = res + 9
        else:
            anotherPathParameter = False
    print(response)
    return(response)





# This function seperates out the relevent data for the Errors
def retrieveErrorsList(RequstUrl, lastError):
    data = retrieveData(RequstUrl)
    anotherPathParameter = True
    response = []
    res = data.index(u'E2')
    res = res - 7
    while anotherPathParameter:
        response.append([data[res+2], data[res+3]])
        if data[res] != lastError: 
            res = res + 7
        else:
            anotherPathParameter = False
    print(response)
    return(response)









print('---path Parameters---')
retrievePathParameters('https://confluence.tools.tax.service.gov.uk/display/MTE/Retrieve+Income+Tax+%28Self+Assessment%29+Crystallisation+Obligations+-+Requirements+Spec')
print('---query Parameters---')
retrieveQueryParameters('https://confluence.tools.tax.service.gov.uk/display/MTE/Retrieve+Income+Tax+%28Self+Assessment%29+Crystallisation+Obligations+-+Requirements+Spec')
print('---Request Body---')
# request body schema will require close brackets Applying to the Appropriate places, formating, and required and additionalProperties fields
retrieveRequestBodySchema('https://confluence.tools.tax.service.gov.uk/pages/viewpage.action?spaceKey=MTE&title=Amend+Student+Loans+Example+Requirements+Spec', u'From Date')
print('---Response Body---')
# request body schema will require close brackets Applying to the Appropriate places, formating, and required and additionalProperties fields
retrieveResponseBodySchema('https://confluence.tools.tax.service.gov.uk/display/MTE/Retrieve+Income+Tax+%28Self+Assessment%29+Crystallisation+Obligations+-+Requirements+Spec')
print('---Errors---')
retrieveErrorsList('https://confluence.tools.tax.service.gov.uk/display/MTE/Retrieve+Income+Tax+%28Self+Assessment%29+Crystallisation+Obligations+-+Requirements+Spec', u'E6')