import re

def extract_product_size(description):
    # Regular expression pattern to match size indicators like ml, L, g, kg
    size_pattern = r'(\d+\s*(ml|L|g|kg|cl|portions|tranches|pièces))'
    
    # Search for size pattern in the description
    match = re.search(size_pattern, description, re.IGNORECASE)
    
    if match:
        # Extract the matched size
        size = match.group()
        return size
    else:
        return None  # If no size is found

# Example usage:
description = "This product 20kg of liquid."
product_size = extract_product_size(description)
if product_size:
    print("Product Size:", product_size)
else:
    print("Product size not found in description.")
