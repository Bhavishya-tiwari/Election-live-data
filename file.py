import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_party_name(text):
  parts = text.split("(")
  if len(parts) > 1:
    party_name = parts[1].strip()
    party_name = party_name.split(")")[0].strip()
    return party_name
  else:
    return None

url = "https://results.eci.gov.in/PcResultGenJune2024/index.htm"
response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    result_div = soup.find('div', class_='rslt-table table-responsive')
    if result_div:
        table = result_div.find('table')
        if table:
            rows = table.find_all('tr')
            leading_column_data = []
            for row in rows:
                columns = row.find_all('td')
                if len(columns) > 0:
                    header_row = table.find('tr')
                    headers = [th.text.strip() for th in header_row.find_all('th')]
                    
                    if "Leading" in headers:
                        leading_index = headers.index("Leading")
                        leading_column = columns[leading_index]
                        leading_column_data.append(str(leading_column))

            leading_column_html = ''.join(leading_column_data)
            soup = BeautifulSoup(leading_column_html, 'html.parser')
            href_links = [a['href'] for a in soup.find_all('a')]

dataframes = []
for link in href_links:
    url = "https://results.eci.gov.in/PcResultGenJune2024/" + link

    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        party = soup.find('div', class_="page-title").find('h2').find('span')
        result_div = soup.find('div', class_="table-responsive")
        if result_div:
            table = result_div.find('table')    
            headers = []
            for th in table.find_all('th'):
                headers.append(th.text.strip())
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip the header row
                cells = tr.find_all('td')
                row = [cell.text.strip() for cell in cells]
                rows.append(row)
            df = pd.DataFrame(rows, columns=headers)
            df["party"] = extract_party_name(party.text)
            dataframes.append(df)
big_df = pd.concat(dataframes, ignore_index=True)


big_df['Margin'] = pd.to_numeric(big_df['Margin'], errors='coerce')
sorted_df = big_df.sort_values(by='Margin', ascending=True)
sorted_df = sorted_df.reset_index(drop=True)
sorted_df.to_csv("Final_data.csv")