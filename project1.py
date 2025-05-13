import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd


def scrape_shiller_pe():
    url = "https://www.multpl.com/shiller-pe/table/by-month"
    
    try:
        # Send request with headers to mimic browser behavior
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'datatable'})
        
        if not table:
            print("No table found on the page")
            return {}
        
        data = {}
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Extract and format date
                date_str = cells[0].text.strip()
                try:
                    date_obj = datetime.strptime(date_str, '%b %d, %Y')
                    formatted_date = date_obj.strftime('%Y%m%d')
                except ValueError:
                    continue
                
                # Extract and format value
                value_str = cells[1].text.strip().replace(',', '')
                try:
                    value_float = float(value_str)
                except ValueError:
                    continue
                
                # Add to dictionary
                data[formatted_date] = value_float
        
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# Run the scraper
shiller_pe_data = scrape_shiller_pe()

print("Complete Shiller PE Data:")
for date, value in shiller_pe_data.items():
    print(f"{date}: {value}")

# Print total count
print(f"\nTotal entries scraped: {len(shiller_pe_data)}")

df = pd.DataFrame(list(shiller_pe_data.items()), columns=['Date', 'Shiller_PE'])
df.to_csv('shiller_pe_data.csv', index=False)
print("Data saved to 'shiller_pe_data.csv'")