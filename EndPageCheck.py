import requests
import time
from bs4 import BeautifulSoup

# Base URL of the Newegg page with pagination
base_url = 'https://www.carrefour.tn/default/les-prix-les-plus-bas.html?p='

# Retry settings
max_retries = 5
retry_delay = 5  # seconds

# Set a custom User-Agent header to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Initialize variables
page = 1
end_page = None

while True:
    # Construct the URL for the current page
    url = base_url + str(page)
    
    # Retry logic to handle failed requests
    for retry in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            break
        
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
    else:
        print("Max retries reached. Unable to get a successful response.")
        exit()  # Exit the script if max retries are reached
    
    # Parse the HTML content of the page using Beautiful Soup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the "Next" button, if it exists
    next_button = soup.find('button', class_='next')
    
    # If the "Next" button is found, continue to the next page
    if next_button:
        page += 1
    else:
        # If "Next" button is not found, it's the last page
        end_page = page
        break

# Now that you have the end_page determined, you can proceed to scrape the data
# using the previous code within a loop from start_page to end_page
print(f"Determined end page: {end_page}")

# ... rest of the scraping code using the determined end_page ...
