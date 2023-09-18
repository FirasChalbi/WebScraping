import requests
import time
import random
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient


def extract_category_from_url(url):
    # Split the URL by slashes
    parts = url.split('/')
    
    # Find the part of the URL that corresponds to the category
    # Assuming it's the second-to-last part, but adjust as needed
    if len(parts) >= 2:
        category = parts[-2]
        return category
    else:
        return None  # If the URL structure is unexpected


def correct_price_format(price_str):
    parts = price_str.split('.')
    
    # Check if there are enough parts after the split
    if len(parts) < 2:
        return price_str  # Return the original price if split didn't work as expected
    
    integer_part = parts[0]
    
    # Check if the decimal part has a comma-separated value
    decimal_part_split = parts[1].split(',')
    if len(decimal_part_split) < 2:
        return price_str  # Return the original price if decimal part format is unexpected
    
    decimal_part = decimal_part_split[1]
    converted = f"{integer_part},{decimal_part} dt"
    return converted

def extract_product_size(description):
    # Regular expression pattern to match size indicators like ml, L, g, kg
    size_pattern = r'(\d+\s*(ml|L|g|kg|cl|portions|tranches|pièces|pièce))'
    
    # Search for size pattern in the description
    match = re.search(size_pattern, description, re.IGNORECASE)
    
    if match:
        # Extract the matched size
        size = match.group()
        return size
    else:
        return None  # If no size is found

# Define endpoints and their respective end_page values
endpoints = {
    #'https://www.carrefour.tn/default/les-prix-les-plus-bas.html?p=': 2,
    'https://www.carrefour.tn/default/mes-courses-alimentaires.html?p=': 170,
    # Add more endpoints and end_page values as needed
}

# Delay settings
min_delay = 1  # Minimum delay in seconds
max_delay = 3  # Maximum delay in seconds

# Retry settings
max_retries = 5
retry_delay = 5  # Delay between retries in seconds

# Set a custom User-Agent header
headers = {
    "User-Agent": "Your User-Agent String Here"
}

# MongoDB setup
mongo_uri = "mongodb+srv://Firasch:Firasch@cluster0.8fbmhhc.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client['Stores']
collection = db['Carrefour']

# Function to fetch page data with retries
def fetch_page_data(url):
    for retry in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for non-200 responses
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(2 ** retry_delay)  # Exponential backoff
    print(f"Max retries reached. Unable to fetch data from {url}.")
    return None

# Main scraping loop
for endpoint, end_page in endpoints.items():
    for page in range(1, end_page + 1):
        url = endpoint + str(page)
        
        # Fetch the page data with retries
        page_data = fetch_page_data(url)
        if page_data is None:
            continue
        
        # Introduce a random delay
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
        # Parse the page data with BeautifulSoup
        soup = BeautifulSoup(page_data, 'html.parser')
        
        product_items = soup.find_all('div', class_='cr-product-listing-wrapper')
    
        for item in product_items:
            title = item.find('strong', class_='product name').get_text().strip()
            desc = item.find('p', class_='cr-product-list-short-description-grid').get_text().strip()
            price_container = item.find('span', class_='price-final_price')
            price_amount = price_container.find('span', {'data-price-type': 'finalPrice'}).get('data-price-amount')
            price_decimal = price_container.find('span', class_='cr-products-price-decimal-point').get_text().strip()
            product_price = f"{price_amount},{price_decimal}"  # Remove ' dt' from the format
            imageSrc = item.find('img', class_='product-image-photo').get('src')
            shop_name = "Carrefour"
            product_url = item.find('a', class_='product photo product-item-photo').get('href')
            
            brand_element = item.find('a', class_='cr-brand-name')
            if brand_element:
                brand = brand_element.get_text().strip()
            else:
                brand = ""
            
            if item.find('div', class_='product-label').svg:
                promo = "Promotion"
            else:
                promo = ""


            existing_product = collection.find_one({'title': title})
            # print(category)
            print(correct_price_format(product_price))
            if existing_product:
                print(f"Product '{title}' already exists. Updating data...")
                updated_data = {
                    'brand': brand,
                    'description': extract_product_size(desc),
                    'price': f"{correct_price_format(product_price)}"  # Add formatted price
                }
                collection.update_one({'title': title}, {'$set': updated_data})
            else:
                print("Inserting new product:", title)
                data = {
                    'name': title,
                    'brand': brand,
                    'imageSrc' : imageSrc,
                    'description': desc,
                    'size': extract_product_size(desc),
                    'category': "",  
                    'regular_price' : "",
                    'product_price': f"{correct_price_format(product_price)}",
                    'product_url': product_url,
                    'promo' : promo,  
                    'shop_name': shop_name,
                }   
                collection.insert_one(data)

            print("-" * 50)
        
        # Introduce a small random delay before processing the next page
        time.sleep(random.uniform(0.5, 1))

print("Scraped data uploaded to MongoDB collection")
