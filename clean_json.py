import json
import re

def clean_key(key):
    # Convert to lowercase
    key = key.lower()
    # Replace spaces with underscores
    key = key.replace(' ', '_')
    # Remove all non-alphanumeric characters except underscores
    key = re.sub(r'[^a-z0-9_]', '', key)
    return key

# Read the original JSON data
with open('data.json', 'r') as f:
    data = json.load(f)

# Process each user to clean the keys
new_users = []
for user in data['users']:
    new_user = {}
    for old_key, value in user.items():
        new_key = clean_key(old_key)
        new_user[new_key] = value
    new_users.append(new_user)

data['users'] = new_users

# Save the modified data to a new JSON file
with open('data_clean.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Keys have been cleaned and saved to 'data_clean.json'.")