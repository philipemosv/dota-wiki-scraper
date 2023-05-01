import requests
import json
from bs4 import BeautifulSoup
from heroes import heroes, url_heroes
from tags import tags


def get_values(tag):
    """Get the values of a tag."""
    found_tag = soup.find(
        lambda t: t.name == tag['tag'] and t.text.lower() == tag['text'])
    found_tag_siblings = found_tag.find_next_siblings()
    values = []
    for tag_sibling in found_tag_siblings:
        if tag_sibling.name == tag['end_tag']:
            break
        if tag['tag'] == 'h3':
            if tag_sibling.string is not None and len(tag_sibling.string) < 30:
                values.append(tag_sibling.string)
        else:
            if tag_sibling.text is not None:
                values.append(tag_sibling.text)
    return values


def fill(hero_info, key, values):
    """Fill the hero info dictionary."""
    last_hero_index = -1
    for item in values:
        if item in heroes:
            hero_info[key].append({"hero": item})
            last_hero_index += 1
        else:
            hero_info[key][last_hero_index]['description'] = item


# create a session object
session = requests.Session()

hero_list = []
for hero in url_heroes:
    print(hero)
    url = f"https://dota2.fandom.com/wiki/{hero}/Counters"
    try:
        response = session.get(url)
        # raise an exception if the status code is not 200 OK
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for {hero}. Exception: {e}")
        continue

    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        bad_against = get_values(tags['heroes_bad'])
        good_against = get_values(tags['heroes_good'])
        works_well = get_values(tags['heroes_well'])
    except Exception as e:
        print(f"Failed to parse data for {hero}. Exception: {e}")
        continue

    hero_info = {'hero': hero, 'bad_against': [],
                 'good_against': [], 'works_well_with': []}

    bad_against = [item for item in bad_against if item.strip()]
    good_against = [item for item in good_against if item.strip()]
    works_well = [item for item in works_well if item.strip()]

    fill(hero_info, 'bad_against', bad_against)
    fill(hero_info, 'good_against', good_against)
    fill(hero_info, 'works_well_with', works_well)

    hero_list.append(hero_info)

# convert the list to JSON format
json_data = json.dumps(hero_list)

# write the JSON data to a file
try:
    with open('scraper_output_v1.json', 'w') as file:
        file.write(json_data)
except Exception as e:
    print(f"Failed to write data to file. Exception: {e}")
