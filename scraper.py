import requests
from bs4 import BeautifulSoup
from tags import tags
from heroes import heroes
from items import items


class DotaWikiScraper:
    def __init__(self):
        self.session = requests.Session()

    def _do_request(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch data. Exception: {e}")

    def _get_values_heroes(self, soup, tag):
        found_tag = soup.find(id=tag['id']).parent
        found_tag_siblings = found_tag.find_next_siblings()
        values = []
        for tag_sibling in found_tag_siblings:
            if tag_sibling.name == tag['end_tag']:
                break
            if tag_sibling.text is not None:
                values.append(tag_sibling.text)
        values = [item for item in values if item.strip()]
        values = [s.strip() for s in values]
        return values

    def _get_values_items(self, soup, tag):
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
                        break
            if tag_sibling.name == tag['end_tag']:
                break
        return values

    def _fill_hero(self, values):
        if (values is None):
            return []
        last_hero_index = -1
        formatted_list = []
        for item in values:
            if item in heroes:
                formatted_list.append({"hero": item})
                last_hero_index += 1
            else:
                formatted_list[last_hero_index]['description'] = item
        return formatted_list

    def _fill_item(hero_info, values):
        if (values is None):
            return []
        try:
            last_item_index = -1
            formatted_list = []
            for item in values:
                if item in items:
                    formatted_list.append({"item": item})
                    last_item_index += 1
                else:
                    formatted_list[last_item_index]['description'] = item
            return formatted_list
        except Exception:
            print(item)

    def _extract_counters_heroes(self, hero, tag):
        try:
            url = f"https://dota2.fandom.com/wiki/{hero}/Counters"
            response = self._do_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            lst = self._fill_hero(self._get_values_heroes(soup, tags[tag]))
            return lst
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch data. Exception: {e}")

    def _extract_counters_items(self, hero, tag):
        """Get the values of a tag."""
        url = f"https://dota2.fandom.com/wiki/{hero}/Counters"
        response = self._do_request(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        lst = self._fill_item(self._get_values_items(soup, tags[tag]))
        return lst

    def extract_counters_heroes_bad_against(self, hero):
        return self._extract_counters_heroes(hero, 'heroes_bad')

    def extract_counters_heroes_good_against(self, hero):
        return self._extract_counters_heroes(hero, 'heroes_good')

    def extract_counters_heroes_works_well(self, hero):
        return self._extract_counters_heroes(hero, 'heroes_well')

    def extract_counters_items_bad_against(self, hero):
        return self._extract_counters_items(hero, 'items_bad')

    def extract_counters_items_good_against(self, hero):
        return self._extract_counters_items(hero, 'items_good')
