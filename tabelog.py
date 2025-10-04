import os, sys
import re
import requests
import pyperclip
import webbrowser
import credentials
from bs4 import BeautifulSoup
from googletrans import Translator

# references:
# https://jupyter-gmaps.readthedocs.io/en/latest/


# global var
cwd = os.path.dirname(os.path.realpath(__file__))
rgx_newline = re.compile(r'\n')
rgx_whitespace = re.compile(r'\s+')
rgx_en = re.compile(r'/^[a-zA-Z0-9]+$/')
translator = Translator()
listtext = []


# functions
def to_file(filename, mode, text):
    with open(os.path.join(cwd, filename), mode, encoding='utf-8') as f:
        f.write(text)

def from_file(filename):
    with open(os.path.join(cwd, filename), 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def parse(url):
    addr = ''

    resp = requests.get(url)
    if resp.status_code == 200:
        to_file('out.txt', 'w', resp.text)
        soup = BeautifulSoup(resp.text, 'html.parser')

    # html = from_file('out.txt')
    # soup = BeautifulSoup(html, 'html.parser')

    # url
    listtext.append(url)

    # rating
    rating = soup.find('b', attrs={"rel": "v:rating"})
    if rating:
        rating = rating.find('span')
        rating = rating.getText()
        listtext.append('\n' + rating)

    # main table
    table = soup.find('table', class_='c-table c-table--form rstinfo-table__table')
    if table:
        tb = table.find('tbody')

        # categories
        # print(tb.select_one('th:-soup-contains("ジャンル") + td'))
        listtext.append('\n\nCategories:')
        td = tb.select_one('th:-soup-contains("ジャンル") + td')
        if td:
            category = td.find('span')
            if category:
                category = category.getText()
                category = rgx_newline.sub(' ', category).strip()
                category = rgx_whitespace.sub(' ', category).strip()
                category = translator.translate(category, src='ja').text
                listtext.append('\n' + category)

        # contact
        # print(tb.select_one('th:-soup-contains("予約・") + td'))
        listtext.append('\n\nTEL/reservation:')
        td = tb.select_one('th:-soup-contains("予約・") + td')
        if td:
            contact = td.find('strong', class_='rstinfo-table__tel-num')
            if contact:
                contact = contact.getText()
                listtext.append('\n' + contact)

        # reservation
        # print(tb.select_one('th:-soup-contains("予約可否") + td'))
        td = tb.select_one('th:-soup-contains("予約可否") + td')
        if td:
            reserve = td.find('p', class_='rstinfo-table__reserve-status')
            if reserve:
                reserve = reserve.getText()
                reserve = translator.translate(reserve, src='ja').text
                listtext.append('\n' + reserve)

        # address
        # print(tb.select_one('th:-soup-contains("住所") + td'))
        listtext.append('\n\nAddress:')
        td = tb.select_one('th:-soup-contains("住所") + td')
        if td:
            address = td.find('p', class_='rstinfo-table__address')
            if address:
                locations = address.find_all('span')
                for location in locations:
                    s_location = location.getText()
                    if s_location != '':
                        s_location = translator.translate(s_location, src='ja').text
                        listtext.append('\n' + s_location)


        # transport
        # print(tb.select_one('th:-soup-contains("交通手段") + td'))
        listtext.append('\n\nTransportation:')
        td = tb.select_one('th:-soup-contains("交通手段") + td')
        if td:
            transports = td.find_all('p')
            for transport in transports:
                s_transport = transport.getText()
                s_transport = translator.translate(s_transport, src='ja').text
                listtext.append('\n' + s_transport)

        # business hours
        # print(tb.select_one('th:-soup-contains("営業時間") + td'))
        listtext.append('\n\nOperating Hours:')
        td = tb.select_one('th:-soup-contains("営業時間") + td')
        if td:
            # opening hours
            weeks = td.find_all('li', class_='rstinfo-table__business-item')
            for week in weeks:
                day = week.find('p', class_='rstinfo-table__business-title')
                if day:
                    s_day = day.getText()
                    s_day = rgx_newline.sub(' ', s_day).strip()
                    s_day = rgx_whitespace.sub(' ', s_day).strip()
                    s_day = translator.translate(s_day, src='ja').text
                    listtext.append('\n' + s_day)
                hours = week.find_all('li', class_='rstinfo-table__business-dtl-text')
                for hour in hours:
                    s_hour = hour.getText()
                    s_hour = translator.translate(s_hour, src='ja').text
                    listtext.append('\n' + s_hour)
                    if hour.p:
                        s_hour = translator.translate(hour.p.getText(), src='ja').text
                        # sometimes .p text is a repeat
                        if not s_hour in listtext[-1]:
                            listtext.append('\n' + s_hour)
            # regular holiday
            weeks = td.find_all('div', class_='rstinfo-table__business-other')
            for week in weeks:
                holidays = week.find_all('li', class_='rstinfo-table__business-item')
                for holiday in holidays:
                    s_holiday = holiday.getText()
                    s_holiday = s_holiday.replace("■", "")
                    s_holiday = rgx_newline.sub(' ', s_holiday).strip()
                    s_holiday = rgx_whitespace.sub(' ', s_holiday).strip()
                    s_holiday = translator.translate(s_holiday, src='ja').text
                    listtext.append('\n' + s_holiday)

        # budget
        # print(tb.select_one('th:-soup-contains("予算") + td'))
        listtext.append('\n\nBudget:')
        td = tb.select_one('th:-soup-contains("予算") + td')
        if td:
            budgets = td.find_all('p', class_='rstinfo-table__budget-item')
            if not budgets:
                # no p, try to find span
                budgets = td.find_all('span', class_='rstinfo-table__budget-item')
            for budget in budgets:
                if budget.i:
                    s_budget = budget.i.get('aria-label')
                    listtext.append('\n' + s_budget + ' ')
                if budget.em:
                    s_budget = budget.em.getText()
                    listtext.append(s_budget)


        # payment method
        # print(tb.select_one('th:-soup-contains("支払い方法") + td'))
        listtext.append('\n\nPayment:')
        td = tb.select_one('th:-soup-contains("支払い方法") + td')
        if td:
            payments = td.find_all('div', class_='rstinfo-table__pay-item')
            for payment in payments:
                if payment.p:
                    s_payment = translator.translate(payment.p.getText(), src='ja').text
                    listtext.append('\n' + s_payment)

        fulltext = '' 
        fulltext = fulltext.join(listtext)
        print(fulltext)
        to_file('fulltext.txt', 'w', fulltext)


        return


def main():
    if len(sys.argv) > 1:
        url = ' '.join(sys.argv[1:])
    else:
        url = pyperclip.paste()

    # parse info from url
    addr = parse(url)

    # open google map in browser
    # webbrowser.open('https://www.google.com.sg/maps/search/' + addr)

# main
if __name__ == "__main__":
    main()