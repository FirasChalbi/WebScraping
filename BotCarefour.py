import requests
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
    
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


# Base URL of the Carrefour page with pagination
base_url = 'https://www.carrefour.tn/default/les-prix-les-plus-bas.html?p='

# Set the range of pages you want to scrape
start_page = 1
end_page = 17

# Retry settings
max_retries = 5
retry_delay = 5  # seconds

# Set a custom User-Agent header to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Set up MongoDB connection
mongo_uri = "mongodb+srv://Firasch:Firasch@cluster0.8fbmhhc.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client['scraped_data_db']
collection = db['stores']

for page in range(start_page, end_page + 1):
    url = base_url + str(page)
    
    for retry in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            break
        
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
    else:
        print("Max retries reached. Unable to get a successful response.")
        exit()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    product_items = soup.find_all('div', class_='cr-product-listing-wrapper')
    
    for item in product_items:
        title = item.find('strong', class_='product name').get_text().strip()
        brand = item.find('a', class_='cr-brand-name').get_text().strip()
        desc = item.find('p', class_='cr-product-list-short-description-grid').get_text().strip()
        price_container = item.find('span', class_='price-final_price')
        price_amount = price_container.find('span', {'data-price-type': 'finalPrice'}).get('data-price-amount')
        price_decimal = price_container.find('span', class_='cr-products-price-decimal-point').get_text().strip()
        product_price = f"{price_amount},{price_decimal}"  # Remove ' dt' from the format
        
        existing_product = collection.find_one({'title': title})
        print(correct_price_format(product_price))
        if existing_product:
            print(f"Product '{title}' already exists. Updating data...")
            updated_data = {
                'brand': brand,
                'description': desc,
                'price': f"{correct_price_format(product_price)}"  # Add formatted price
            }
            collection.update_one({'title': title}, {'$set': updated_data})
        else:
            print("Inserting new product:", title)
            data = {
                'title': title,
                'brand': brand,
                'description': desc,
                'price': f"{correct_price_format(product_price)}"  # Add formatted price
            }
            collection.insert_one(data)
        
        print("-" * 50)

print("Scraped data uploaded to MongoDB collection")
