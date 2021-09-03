import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

URL = "link here"

all_tables = pd.read_html(URL)

print(f'Total tables: {len(all_tables)}')


'''j = 1
for i in all_tables:
    print('table number: {}'.format(j))
    print(i.head())
    j += 1'''
