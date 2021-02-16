#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
import PyPDF2


class ScrapDecimas():
    def __init__(self):
        self.versos = []

    def scrap_cervantes(self):
        link = "http://www.cervantesvirtual.com/obra-visor/decimas--0/html/fff7d914-82b1-11df-acc7-002185ce6064_2.html#I_33_"
        page = requests.get(link)
        #print(page.status_code)

        soup = BeautifulSoup(page.content, 'html.parser')
        #print(soup.prettify())
        versos_html = soup.find_all('td')
        versos = [verso.get_text(strip=True) for verso in versos_html]  # getting text inside <td> tags
        versos = [re.sub(r'\n', r' ', v) for v in versos if v]  # replacing \n
        versos = [v for v in versos if not v.isnumeric()]  # getting rid of numbers
        versos = [v for v in versos if len(v.split()) > 3 and len(v.split()) < 8]
        #print(versos)
        print(f'extracted {len(versos)} from {link}\n')  # 681
        self.versos.extend(versos)

        return

    def scrap_diferentemente(self):
        link = "https://www.diferentementeiguales.org/versos_en_decimas/"
        page = requests.get(link)
        #print(page.status_code)

        soup = BeautifulSoup(page.content, 'html.parser')
        #print(soup.prettify())
        versos_html = soup.find_all('blockquote')
        versos = [list(verso.children) for verso in versos_html]
        versos = [v.string.strip() for verso in versos for v in verso if v.string]
        print(f'extracted {len(versos)} from {link}')  # 723
        #print(versos)
        self.versos.extend(versos)

        return

    def scrap_violeta(self):
        # this documents requires further preprocessing
        file = '../decimas-violeta-parra.pdf'
        pdf_file = open(file, 'rb')
        read_pdf = PyPDF2.PdfFileReader(pdf_file)
        number_of_pages = read_pdf.getNumPages()
        #print(number_of_pages)  # 71

        text_document = []
        for page in range(number_of_pages-1):  # last page shows credits
            page = read_pdf.getPage(page)
            page_content = page.extractText()
            #print(page_content)
            text_document.append(page_content)
        #print(len(text_document))  # 71

        #print(repr(text_document[0]))
        versos_document = []
        for text in range(len(text_document)):
            versos = text_document[text].split('\n')
            #versos = [re.sub(r'\s+', '', v) for v in versos if not v.isnumeric()]
            versos = [v.strip() for v in versos if v.strip() and not v.isnumeric()]
            versos_document.extend(versos)

        #print(versos_document)
        print(f'extracted {len(versos_document)} from {file}')  # 3273
        self.versos.extend(versos_document)

        return

    def output_file(self, file_name, versos):
        with open(file_name, 'w') as file:
            for verso in versos:
                file.write(f'{verso}\n')


SD = ScrapDecimas()
SD.scrap_cervantes()
SD.scrap_diferentemente()
SD.scrap_violeta()

# uncomment following line to output versos to file
#SD.output_file('decimas_data.txt', SD.versos)
