import truststore
truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.timesjobs.com/job-search?txtKeywords=%22Java+Developer%22%2C%22PHP+Developer%22%2C%22Android+Developer%22%2C%22Content+Writer%22%2C%22Business+Development+Manager%22%2C&refreshed=true')
soup = BeautifulSoup(response.content, 'lxml')
print(soup.prettify())
