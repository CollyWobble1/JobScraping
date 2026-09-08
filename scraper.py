from bs4 import BeautifulSoup
import requests
import pandas as pd

with open('Fake Python.html', 'r') as file:
    content = file.read()

soup = BeautifulSoup(content, 'lxml')

divs= soup.find_all('div', class_='card-content')
for div in divs:
    job = div.find('h2', class_='title is-5')
    location = div.find('h3', class_='subtitle is-6 company')

    print(job.text.strip())
    print(location.text.strip())


