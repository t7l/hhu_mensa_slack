# -*- coding: utf-8 -*-
import calendar
import datetime
import locale
import re
import sys
import os

from bs4 import BeautifulSoup
from german_holidays import get_german_holiday_calendar
import requests
from slackclient import SlackClient

# set locale to german (weekdays in German and needed for scraping)
try:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
except locale.Error as err:
    try:
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
    except locale.Error as err:
        print("Selected locale not available. Please install locale de_DE.utf8 first.")
        sys.exit(0)

# canteen (mensa) is open from monday to friday only and additionally
# closed on german holidays
GERMAN_HOLIDAY_CALENDAR = get_german_holiday_calendar('NW')()
TODAY = datetime.date.today()
TODAY_DAYNAME = datetime.datetime.now().strftime("%A")
WEEKDAYS = tuple(calendar.day_name)[:6]

# canteen url and info for webpage processing
CANTEEN_URL = 'http://www.stw-d.de/gastronomie/speiseplaene/mensa-universitaetsstrasse-duesseldorf/'
EXCLUDED_COMPONENTS = ['mehr informationen']
CUSTOMER_TYPES = ['studenten', 'bedienstete', 'gäste']

# slack data (token should be better in an environment variable)
SLACK_TOKEN = os.environ.get('SLACK_TOKEN', None)  # your slack token
# set to an existing channel, where canteen menu will be posted
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', None)
SLACK_USERNAME = 'mensabot'  # user does not need to be added before
SLACK_USERICON = ':fork_and_knife:'


def slack_format_string(string, formatstring):
    """Text formatting for Slack"""
    return "{}{}{}".format(formatstring, string, formatstring)


def process_counter_meal(counter_meal):
    """Process counter meal"""
    meal_components = []

    for component in counter_meal:
        component_name = component.text
        component_name = re.sub(r'\s?\((\d+\,?)+\)', '', component_name)
        if component_name:
            if component_name.lower() not in EXCLUDED_COMPONENTS:
                if ':' in component_name:
                    meal_components.append(
                        '_' + re.sub(r':', '', component_name).strip() + '_')
                else:
                    meal_components.append(component_name)

    return meal_components


def process_counter_prices(counter_description):
    """Process counter prices"""
    counter_pricing = counter_description.find(
        "ul", {"class": "price"}).find_all("li")
    counter_prices = {}

    for pricing in counter_pricing:
        pricing_details = pricing.find_all("span")
        if not len(pricing_details) == 2:
            print("Something is wrong with the pricing at counter {}.".format(
                counter_description))
        else:
            price = re.sub(r'[^\d\,?]+', '', pricing_details[1].text)
            price = price + ' €'
            counter_prices[str(pricing_details[0].text).rstrip(':')] = price

    return counter_prices


def process_counter(counter):
    """Process counter content: meal components and pricing"""
    counter_name = counter.find("h2").contents[0]
    counter_description = counter.find(
        "div", {"class": "counter-table"}).find("div", {"class": "description"})
    counter_meal = counter_description.find(
        "ul", {"class": "menu"}).find_all("li")

    meal_components = process_counter_meal(counter_meal)
    counter_prices = process_counter_prices(counter_description)

    # formatted meal for counter
    result = "{} {} (S: {}, M: {})".format(slack_format_string(counter_name + ':', '*'), ", ".join(
        meal_components), counter_prices.get('Studierende'), counter_prices.get('Bedienstete'))
    return result


def post_canteen_menu_to_slack(menu):
    """Post message to Slack channel"""
    sc = SlackClient(SLACK_TOKEN)
    call = sc.api_call(
        "chat.postMessage", channel=SLACK_CHANNEL, text=menu,
        username=SLACK_USERNAME, icon_emoji=SLACK_USERICON
    )
    if not call['ok']:
        print("Error while accessing Slack: {0}".format(call["error"]))
        sys.exit(0)


def scrape_and_format_canteen_menu(page_soup):
    """Scrape page content, process it and format it for Slack"""
    todays_menu = page_soup.find(
        "div", {"data-day": "{}".format(TODAY_DAYNAME)})
    todays_date = todays_menu.attrs.get('data-date')
    today_all_menus = todays_menu.find_all("div", {"class": "counter"})
    menus = []
    for menu in today_all_menus:
        menu_result = process_counter(menu)
        menus.append(menu_result)
    output = '\n'.join(menus)
    output = slack_format_string('Heute ({}) in der Mensa:'.format(
        todays_date), '*') + '\n\n' + output
    return output


def main():
    # if weekend or holiday today: exit program
    if (TODAY_DAYNAME not in WEEKDAYS) or (TODAY in GERMAN_HOLIDAY_CALENDAR.holidays()):
        print("Mensa not open today, so there is no data to get...")
        sys.exit(0)
    page = requests.get(CANTEEN_URL)
    page_soup = BeautifulSoup(page.text, "html5lib")
    menu = scrape_and_format_canteen_menu(page_soup)
    post_canteen_menu_to_slack(menu)


if __name__ == '__main__':
    main()
