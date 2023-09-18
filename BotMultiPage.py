import requests
import time
from bs4 import BeautifulSoup

# Base URL of the Newegg page with pagination
base_url = 'https://www.newegg.com/p/pl?N=100006740%204814%20600004344&page='

# Set the range of pages you want to scrape
start_page = 1
end_page = 5

# Retry settings
max_retries = 5
retry_delay = 5  # seconds

# Set a custom User-Agent header to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

for page in range(start_page, end_page + 1):
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
    
    # Find all the product items
    product_items = soup.find_all('div', class_='item-info')
    price_items = soup.find_all('li', class_='price-current')
    
    # Print the scraped data for the current page
    print(f"Scraping page {page}")
    for item, price_item in zip(product_items, price_items):
        title = item.find('a', class_='item-title').get_text().strip()
        
        # Extract the price, handling cases where the price might not be available
        price_element = price_item.find('strong')
        if price_element:
            price = price_element.get_text()
            sup_element = price_item.find('sup')
            if sup_element:
                price += sup_element.get_text()
        else:
            price = "Price not available"
        
        print("Title:", title)
        print("Price:", price)
        print("-" * 50)
