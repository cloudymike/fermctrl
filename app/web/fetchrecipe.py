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
            
            # Extract names using regex for viewrecipe links
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

def get_recipe(recipe_number):
    base_url="https://beersmithrecipes.com/download.php?id="
    url = f"{base_url}{str(recipe_number)}"
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
        "recipe_name": root.find("./Data/Recipe/F_R_NAME").text
        #"fermentation_profile_name": root.find("./Data/Recipe/F_R_AGE/F_A_NAME").text,
    }
    
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


# Run the functions
recipelist=fetch_recipe_numbers()

name_list=list_recipe_names(recipelist)
print(name_list)



#print(recipelist[1])
#bsmx1=get_recipe(recipelist[1])
#print(bsmx1)
#bsmxStr = bsmx1.replace('&', 'AMP')
#recipe_dict=parse_xml(bsmxStr)
#print(recipe_dict)
#print(recipe_dict['recipe_name'])
#print(recipe_dict['fermentation_profile_name'])