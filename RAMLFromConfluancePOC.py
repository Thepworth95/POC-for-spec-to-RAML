import requests
from bs4 import BeautifulSoup
import creds


def retrieve_data(request_url):
    # This URL will be the URL that your login form points to with the "action" tag.
    POST_LOGIN_URL = 'https://confluence.tools.tax.service.gov.uk/login.action'

    payload = {
        'os_username': creds.username,
        'os_password': creds.password
    }

    # This fetches the data and separates the parts we need for use in the RAML
    with requests.Session() as session:
        session.post(POST_LOGIN_URL, data=payload)
        page = session.get(request_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        list_of_values = soup.find_all("td", class_="confluenceTd")
        result = []

        for item in list_of_values:
            if item.p is not None:
                result.append(item.p.text)
            elif item.div is not None:
                result.append(item.div.text)
            elif item.strong is not None:
                result.append(item.strong.text)
            else:
                result.append(item.text)
        return result


# This function separates out the relevant data for the path Parameters and presents them in the same style used in
# the RAML
def retrieve_path_parameters(request_url):
    data = retrieve_data(request_url)
    if 'Path Parameter' in data:
        another_path_parameter = True
        res = data.index('Path Parameter')
    else:
        another_path_parameter = False
    response_data = []
    while another_path_parameter:
        response_data.append([data[res + 1], data[res + 2], data[res + 3]])
        if data[res + 11] == 'Path Parameter':
            res = res + 11
        else:
            another_path_parameter = False
    response = []
    print(response_data)
    for item in response_data:
        path_parameter = """uriParameters:
                {}:
                    description: {}
                    type: {}
                    example: ---Insert Example---""".format(
            item[0],
            item[1],
            item[2]
        )
        response.append(path_parameter)
    print(response)
    return response


# This function separates out the relevant data for the query Parameters and presents them in the same style used in
# the RAML 
def retrieve_query_parameters(request_url):
    data = retrieve_data(request_url)
    if 'Query Parameter' in data:
        another_query_parameter = True
        res = data.index('Query Parameter')
    else:
        another_query_parameter = False
    response_data = []
    while another_query_parameter:
        response_data.append([data[res + 1], data[res + 2], data[res + 5]])
        if data[res + 11] == 'Query Parameter':
            res = res + 11
        else:
            another_query_parameter = False
    response = []
    for item in response_data:
        response.append("""
            {}:
                queryParameters:
                    {}:
                        description: {}
                        example: "---Insert Example Here---"
                        required: {}""".format(
            item[0],
            item[0],
            item[1],
            item[2] == 'M'
        ))
    print(response)
    return response


# This function separates out the relevant data for the Request body schema and presents it in the same style used in
# the RAML schema's 
def retrieve_request_body_schema(request_url, first_field):
    data = retrieve_data(request_url)
    response_data = []
    if first_field in data:
        another_parameter = True
        res = data.index(first_field)
        response = """{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "---Insert title---",
    "description": "---Insert description---",
    "type": "object",
    "properties": {"""
    else:
        another_parameter = False
    while another_parameter:
        response_data.append([data[res], data[res + 1], data[res + 2]])
        if data[res + 9] != 'O1' and data[res + 9] != 'L1':
            res = res + 10
        else:
            another_parameter = False

    for item in response_data:
        element = ""
        if item[2] == 'Array' or item[2] == 'array':
            response = response + """
        {}: {{
            "type": "Array",
            "description": {},
            "items": {{""".format(
                item[0],
                item[1]
            )
        elif item[2] == 'Object' or item[2] == 'object':
            response = response + """
                "type": "object",
                "properties": {"""
        elif item[2] == 'String (date)' or item[2] == 'string (date)':
            element = """
        "{}": {{
            "description": "{}",
            "type": "string",
            "example": "---Insert example---"
        }}""".format(
                item[0],
                item[1]
            )
        else:
            element = """
        {}: {{
            "description": {},
            "type": {},
            "example": "---Insert example---"
        }}""".format(
                item[0],
                item[1],
                item[2]
            )
        response = response + element
    if first_field in data:
        response = response + """  
    },
    "additionalProperties": false
}"""
    else:
        response = ""
    print(response)
    return response


# This function separates out the relevant data for the Response body schema and presents it in the same style used 
# in the RAML schema's 
def retrieve_response_body_schema(request_url):
    data = retrieve_data(request_url)
    response_data = []
    if 'O1' in data:
        another_parameter = True
        res = data.index('O1')
        response = """{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "---Insert title---",
    "description": "---Insert description---",
    "type": "object",
    "properties": {"""
    else:
        another_parameter = False
    while another_parameter:
        response_data.append([data[res + 1], data[res + 2], data[res + 3]])
        if data[res + 9] != 'L1':
            res = res + 9
        else:
            another_parameter = False
    for item in response_data:
        element = ""
        if item[2] == 'Array' or item[2] == 'array':
            response = response + """
        {}: {{
            "type": "Array",
            "description": {},
            "items": {{
                """.format(
                item[0],
                item[1]
            )
        elif item[2] == 'Object' or item[2] == 'object':
            response = response + """
                "type": "object",
                "properties": {{"""
        elif item[2] == 'String (date)' or item[2] == 'string (date)':
            element = """
        "{}": {{
            "description": "{}",
            "type": "string",
            "example": "---Insert example---"
        }}""".format(
                item[0],
                item[1]
            )
        else:
            element = """
        "{}": {{
            "description": "{}",
            "type": "{}",
            "example": "---Insert example---"
        }}""".format(
                item[0],
                item[1],
                item[2]
            )
        response = response + element
    if 'O1' in data:
        response = response + """  
    },
    "additionalProperties": false
}""" 
    else:
        response = ""
    print(response)
    return response


# This function separates out the relevant data for the Errors
def retrieve_errors_list(request_url, last_error):
    data = retrieve_data(request_url)
    another_parameter = True
    response = []
    res = data.index('E2')
    res = res - 7
    while another_parameter:
        response.append([data[res + 2], data[res + 3]])
        if data[res] != last_error:
            res = res + 7
        else:
            another_parameter = False
    print(response)
    return response


def all(url, first_field, last_error):
    print('---path Parameters---')
    retrieve_path_parameters(url)

    print('---query Parameters---')
    retrieve_query_parameters(url)
    print('---Request Body---')
    # request body schema will require close brackets Applying to the Appropriate places, formatting, and required and
    # additionalProperties fields
    retrieve_request_body_schema(url, first_field)

    print('---Response Body---')
    # response body schema will require close brackets Applying to the Appropriate places, formatting, and required and
    # additionalProperties fields
    retrieve_response_body_schema(url)

    print('---Errors---')
    retrieve_errors_list(url, last_error)


if __name__ == '__main__':
    all(
        'https://confluence.tools.tax.service.gov.uk/display/MTE/Create+SE+Periodic+Update+Period+-+Requirements+Spec',
        'Period From Date',
        'E14'
    )