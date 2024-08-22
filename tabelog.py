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

    rating = soup.find('b', class_='c-rating__val c-rating__val--strong')
    if rating:
        rating = rating.getText()
        listtext.append('\n' + rating)

    # categories
    listtext.append('\n\nCategories:\n')
    category = soup.find('span', attrs={"property": "v:category"})
    if category:
        listtext.append(category.getText())

    # contact
    listtext.append('\n\nTEL/reservation\n')
    contact = soup.find('strong', attrs={"property": "v:tel"})
    if contact:
        contact = contact.getText()
        contact = rgx_newline.sub(' ', contact).strip()
        contact = rgx_whitespace.sub(' ', contact).strip()
        listtext.append(contact)

    reserve = soup.find('p', class_='rd-detail-info__rst-booking-status translate')
    if reserve:
        reserve = reserve.getText()
        reserve = translator.translate(reserve, src='ja').text
        listtext.append('\n' + reserve)

    # address
    listtext.append('\n\nAddress:\n')
    addr = soup.find('p', class_='rd-detail-info__rst-address')
    if addr:
        addr = addr.getText()
        addr = rgx_newline.sub('', addr)
        addr = rgx_whitespace.sub(' ', addr).strip()
        listtext.append(addr)

    # detailed address
    addr = ''
    region = soup.find('span', attrs={"property": "v:region"})
    if region:
        region = region.a.getText()
        region = rgx_newline.sub('', region)
        region = rgx_whitespace.sub(' ', region).strip()
        addr += region + ' '
    locality = soup.find('span', attrs={"property": "v:locality"})
    if locality:
        localities = locality.findAll('a')
        for locality in localities:
            locality = locality.getText()
            locality = rgx_newline.sub('', locality)
            locality = rgx_whitespace.sub(' ', locality).strip()
            addr += locality + ' '
    street = soup.find('span', attrs={"property": "v:street-address"})
    if street:
        street = street.getText()
        street = rgx_newline.sub('', street)
        street = rgx_whitespace.sub(' ', street).strip()
        if street != '':
            addr += street + ' '
    listtext.append('\n' + addr)

    # address
    listtext.append('\n\nTransportation:\n')
    txt_transport = soup.find(string="Transportation")
    if txt_transport:
        td_transport = txt_transport.parent.findNext('td')
        if td_transport:
            transports = td_transport.findAll('p')
            for transport in transports:
                transport =  transport.getText()
                if not rgx_en.match(transport):
                    try:
                        transport = translator.translate(transport, src='ja').text
                    except:
                        pass
                listtext.append(transport + '\n')

    # hours
    listtext.append('\nOperating Hours:\n')
    txt_operation = soup.find(string="Opening hours")
    if txt_operation:
        td_operation = txt_operation.parent.findNext('td')
        if td_operation:
            br_operation = td_operation.p.findAll('br')
            if br_operation:
                for operation in br_operation:
                    str_operation = operation.previous
                    try:
                        str_operation = translator.translate(str_operation, src='ja').text
                        listtext.append(str_operation + '\n')
                    except:
                        pass
                # check the last line
                str_operation = operation.next
                try:
                    str_operation = translator.translate(str_operation, src='ja').text
                    listtext.append(str_operation + '\n')
                except:
                    pass


    # fixed holidays
    listtext.append('\nFixed holidays:\n')
    txt_operation = soup.find(string="Fixed holidays")
    if txt_operation:
        td_operation = txt_operation.parent.findNext('td')
        if td_operation:
            operation = td_operation.p.getText()
            if operation != '':
                operation = translator.translate(operation, src='ja').text
                listtext.append(operation)

    # budget
    listtext.append('\n\nBudget:\n')
    budget = soup.find('span', class_='c-rating__time c-rating__time--dinner')
    if budget:
        budget_dinner = budget.findNextSibling()
        if budget_dinner:
            budget_dinner = budget_dinner.getText()
            listtext.append('Dinner: ' + budget_dinner)
    budget = soup.find('span', class_='c-rating__time c-rating__time--lunch')
    if budget:
        budget_lunch = budget.findNextSibling()
        if budget_lunch:
            budget_lunch = budget_lunch.getText()
            listtext.append('\nLunch: ' + budget_lunch)

    # payment
    listtext.append('\n\nPayment:\n')
    txt_payment = soup.find(string="Method of payment")
    if txt_payment:
        td_payment = txt_payment.parent.findNext('td')
        if td_payment:
            payments = td_payment.findAll('div')
            if payments:
                for payment in payments:
                    payment = payment.p.getText()
                    listtext.append(payment + '\n')

    fulltext = '' 
    fulltext = fulltext.join(listtext)
    print(fulltext)
    to_file('fulltext.txt', 'w', fulltext)
    
    return addr

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