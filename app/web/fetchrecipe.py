import requests
import re
import sys

import re
import xml.etree.ElementTree as ET

def extract_recipe_number(text: str) -> list:
    """
    Extracts all numbers following the viewrecipe pattern in the text.

    Args:
        text (str): Input text containing viewrecipe links.

    Returns:
        list: List of recipe numbers as strings.
    """
    pattern = r"href='https://beersmithrecipes\.com/viewrecipe/(\d+)/"
    return re.findall(pattern, text)

def extract_recipe_name(text: str) -> list:
    """
    Extracts all numbers following the viewrecipe pattern in the text.

    Args:
        text (str): Input text containing viewrecipe links.

    Returns:
        list: List of recipe numbers as strings.
    """
#<a title='View Recipe' href='https://beersmithrecipes.com/viewrecipe/5189856/355-neipa'>355 NEIPA</a>


    pattern = r"href='https://beersmithrecipes\.com/viewrecipe/\d+/.*'>(.*)<"
    return re.findall(pattern, text)

def fetch_recipe_numbers():
    base_url = "https://beersmithrecipes.com/listrecipes/5399/"
    page_number = 0

    recipelist=[]

    while True:
        url = f"{base_url}{page_number}"
        try:
            response = requests.get(url)
            
            # Check if the request was successful and content is not empty
            if response.status_code != 200 or not response.content.strip():
                print(f"No data found at page {page_number}. Exiting.")
                break
            
            # Extract number using regex for viewrecipe links
            matches = extract_recipe_number(response.text)
            if matches:
                recipelist.extend(matches)
            else:
                print(f"No recipes found on page {page_number}.")
                return(recipelist)

        except requests.RequestException as e:
            print(f"Error fetching page {page_number}: {e}")
            break
        
        page_number += 1
    return(recipelist)

def fetch_recipe_names():
    base_url = "https://beersmithrecipes.com/listrecipes/5399/"
    page_number = 0

    recipelist=[]

    while True:
        url = f"{base_url}{page_number}"
        try:
            response = requests.get(url)
            
            # Check if the request was successful and content is not empty
            if response.status_code != 200 or not response.content.strip():
                print(f"No data found at page {page_number}. Exiting.")
                break
            
            # Extract number using regex for viewrecipe links
            matches = extract_recipe_name(response.text)
            if matches:
                recipelist.extend(matches)
            else:
                print(f"No recipes found on page {page_number}.")
                return(recipelist)

        except requests.RequestException as e:
            print(f"Error fetching page {page_number}: {e}")
            break
        
        page_number += 1
    return(recipelist)

def get_recipe(recipe_number):
    base_url="https://beersmithrecipes.com/download.php?id="
    url = f"{base_url}{str(recipe_number)}"
    print(url)
    try:
        response = requests.get(url)
        
        # Check if the request was successful and content is not empty
        if response.status_code != 200 or not response.content.strip():
            print(f"No data found for recipe {recipe_number}. Exiting.")
            bsmx=None
        else:
            bsmx=response.text

    except requests.RequestException as e:
        print(f"Error fetching page {page_number}: {e}")
        bsmx=None
        
    return(bsmx)

def parse_xml(xml_content: str) -> dict:
    """
    Parses the given XML and extracts recipe information.

    Args:
        xml_content (str): XML content as a string.

    Returns:
        dict: Extracted data for recipe information.
    """
    root = ET.fromstring(xml_content)
    
    result = {
        "recipe_name" : root.find("./Data/Recipe/F_R_NAME").text,
        "targetTemp0" : round(float(root.find("./Data/Recipe/F_R_AGE/F_A_PRIM_TEMP").text)),
        "targetDuration0" : root.find("./Data/Recipe/F_R_AGE/F_A_PRIM_DAYS").text,
        "targetTemp1" : round(float(root.find("./Data/Recipe/F_R_AGE/F_A_SEC_TEMP").text)),
        "targetDuration1" : root.find("./Data/Recipe/F_R_AGE/F_A_SEC_DAYS").text,
        "targetTemp2" : round(float(root.find("./Data/Recipe/F_R_AGE/F_A_TERT_TEMP").text)),
        "targetDuration2" : root.find("./Data/Recipe/F_R_AGE/F_A_TERT_DAYS").text,
        "targetTemp3" : round(float(root.find("./Data/Recipe/F_R_AGE/F_A_BULK_TEMP").text)),
        "targetDuration3" : root.find("./Data/Recipe/F_R_AGE/F_A_BULK_DAYS").text,
        "targetTemp4" : round(float(root.find("./Data/Recipe/F_R_AGE/F_A_AGE_TEMP").text)),
        "targetDuration4" : root.find("./Data/Recipe/F_R_AGE/F_A_AGE").text
    }
    result["targetDay0"] = 0
    result["targetDay1"] = round(float(result["targetDuration0"]))
    result["targetDay2"] = round(float(result["targetDuration1"]))+result["targetDay1"]
    result["targetDay3"] = round(float(result["targetDuration2"]))+result["targetDay2"]
    result["targetDay4"] = round(float(result["targetDuration3"]))+result["targetDay3"]

    
    return result

def list_recipe_names(recipe_list):
    name_list=[]
    for recipeID in recipe_list:
        bsmx=get_recipe(recipeID)
        bsmxStr = bsmx.replace('&', 'AMP')
        recipe_dict=parse_xml(bsmxStr)
        recipe_name = recipe_dict['recipe_name']
        name_list.append(recipe_name)
    return(name_list)

def list_recipe_dicts(recipe_list):
    dict_list=[]
    for recipeID in recipe_list:
        bsmx=get_recipe(recipeID)
        bsmxStr = bsmx.replace('&', 'AMP')
        recipe_dict=parse_xml(bsmxStr)
        dict_list.append(recipe_dict)
    return(dict_list)

def recipeNameListBeersmith():
    #return([])
    XMLrecipelist=fetch_recipe_numbers()
    recipeList=list_recipe_names(XMLrecipelist)
    return(recipeList)

def recipeDictListBeersmith():
    #return([])
    XMLrecipelist=fetch_recipe_numbers()
    recipeList=list_recipe_dicts(XMLrecipelist)
    return(recipeList)


if __name__ == "__main__":
    # Run the functions
    recipelist=fetch_recipe_names()
    print(recipelist)
    sys.exit(0)

    name_list=list_recipe_names(recipelist)
    dict_list=list_recipe_dicts(recipelist)

    print(dict_list)