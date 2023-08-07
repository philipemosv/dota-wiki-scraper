import requests
import json
from bs4 import BeautifulSoup
from heroes import heroes, url_heroes
from items import items
from tags import tags


def get_values_heroes(tag):
    """Get the values of a tag."""
    found_tag = soup.find(id=tag['id']).parent
    found_tag_siblings = found_tag.find_next_siblings()
    values = []
    for tag_sibling in found_tag_siblings:
        if tag_sibling.name == tag['end_tag']:
            break
        if tag_sibling.text is not None:
            values.append(tag_sibling.text)
    return values


def get_values_items(tag):
    """Get the values of a tag."""
    found_tag = soup.find(id=tag['id'])
    if (found_tag is not None):
        found_tag = found_tag.parent
    else:
        return
    found_tag_siblings = found_tag.find_next_siblings()
    values = []
    items_list = []
    for tag_sibling in found_tag_siblings:
        # a-tags logic (get item's name)
        a_tags = tag_sibling.find_all('a')
        for a_tag in a_tags:
            if a_tag.has_attr('title'):
                if a_tag.attrs['title'] in items:
                    items_list.append(a_tag.attrs['title'])
        items_list = list(dict.fromkeys(items_list))
        # end a-tags logic

        lines_list = tag_sibling.text.split('\n')

        for line in lines_list:
            t_line = " ".join(line.split())
            for item_l in items_list:
                if item_l in t_line:
                    values.append(item_l)
                    values.append(t_line)
                    for item_l2 in items:
                        a = "and " + item_l2
                        if a in t_line:
                            values.append(item_l2)
                            values.append(t_line)
                    break

        if tag_sibling.name == tag['end_tag']:
            break

    return values


def fill_hero(hero_info, key, values):
    """Fill the hero info dictionary."""
    last_hero_index = -1
    for item in values:
        if item in heroes:
            hero_info[key].append({"hero": item})
            last_hero_index += 1
        else:
            hero_info[key][last_hero_index]['description'] = item


def fill_item(hero_info, key, values):
    """Fill the hero info dictionary."""
    if (values is None):
        return []
    try:
        last_hero_index = -1
        for item in values:
            if item in items:
                hero_info[key].append({"item": item})
                last_hero_index += 1
            else:
                hero_info[key][last_hero_index]['description'] = item
    except Exception:
        print(item)


def strip_list(a_list):
    if (a_list is not None):
        return [item for item in a_list if item.strip()]


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
        heroes_bad_against = get_values_heroes(tags['heroes_bad'])
        heroes_good_against = get_values_heroes(tags['heroes_good'])
        heroes_works_well = get_values_heroes(tags['heroes_well'])
        items_bad_against = get_values_items(tags['items_bad'])
        items_good_against = get_values_items(tags['items_good'])
    except Exception as e:
        print(f"Failed to parse data for {hero}. Exception: {e}")
        continue

    hero_info = {
        'hero': hero,
        'heroes_bad_against': [],
        'heroes_good_against': [],
        'heroes_works_well_with': [],
        'items_bad_against': [],
        'items_good_against': []
    }

    heroes_bad_against = strip_list(heroes_bad_against)
    heroes_good_against = strip_list(heroes_good_against)
    heroes_works_well = strip_list(heroes_works_well)
    items_bad_against = strip_list(items_bad_against)
    items_good_against = strip_list(items_good_against)

    fill_hero(hero_info, 'heroes_bad_against', heroes_bad_against)
    fill_hero(hero_info, 'heroes_good_against', heroes_good_against)
    fill_hero(hero_info, 'heroes_works_well_with', heroes_works_well)
    fill_item(hero_info, 'items_bad_against', items_bad_against)
    fill_item(hero_info, 'items_good_against', items_good_against)

    hero_list.append(hero_info)

# convert the list to JSON format
json_data = json.dumps(hero_list)

# write the JSON data to a file
try:
    with open('scraper_output_v1.json', 'w') as file:
        file.write(json_data)
except Exception as e:
    print(f"Failed to write data to file. Exception: {e}")
