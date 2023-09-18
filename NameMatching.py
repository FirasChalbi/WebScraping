from fuzzywuzzy import fuzz

product1_name = "Céréales blé"
product2_name = "Céréale"

# Calculate a similarity score between the two product names
similarity_score = fuzz.partial_ratio(product1_name, product2_name)

# Set a threshold for considering names as similar
threshold = 80  # Adjust this value based on your needs
print(similarity_score)
if similarity_score >= threshold:
    print("These product names are similar.")

else:
    print("These product names are not similar.")