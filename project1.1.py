import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import json

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

result_dict = {}
result_list = []

sorted_data =sorted (
    [(date, value) for date, value in shiller_pe_data.items()],
    key=lambda x: x[0],
    reverse = True )

calculated_data = []
for i in range(len(sorted_data) - 6):
    current_date, current_value = sorted_data[i]
    past_date, past_value = sorted_data[i+6]
    variance = current_value - past_value
    remarks = "Contraction -Sell" if variance < 0 else ("Expension -  Buy" if variance > 0 else "Hold")
    calculated_data.append({
        "Date": current_date,
        "Value": current_value,
        "2  Variance": round(variance, 2),
        "Remarks": remarks
    })

    result_dict[current_date] = {

        "Value": current_value,

        "2 Quarter Variance": round(variance, 2),

        "Remarks": remarks

    }

with open('shiller_pe_dict.py', 'w') as f:
    f.write("shiller_pe_data = ")
    f.write(json.dumps(result_dict, indent=4))


print("Complete Shiller PE Data:")
for date, value in shiller_pe_data.items():
    print(f"{date}: {value}")

print("\nCalculations Table:")
df = pd.DataFrame.from_dict(result_dict, orient='index')
df.index.name = 'Date'
print(df)

# Print total count
print(f"\nTotal entries scraped: {len(shiller_pe_data)}")

pd.DataFrame(calculated_data).to_csv("shiller_pe_with_calculations.csv", index=False)
print("Calculation complete. Data saved to CSV.")