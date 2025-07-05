import json

start_humas_user_id = 44
start_humas_teacher_id = 39
start_piket_user_id = 65
start_piket_teacher_id = 61
add_humas_teacher_user_id = 43
start_humas_teacher_id = 39
start_humas_userlog_id = 1987
start_piket_userlog_id = 3038
# Read the JSON file
# with open('humas_username.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         user["pk"] = start_humas_user_id
#         user["fields"]["groups"] = []
#         user["fields"]["user_permissions"] = []
#         start_humas_user_id += 1

# # Write the modified data back to the JSON file
# with open('humas_username_fixed.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability

# Read the JSON file
# with open('humas_teachers.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         user["pk"] = start_humas_teacher_id
#         user["fields"]["user"] += add_humas_teacher_user_id
#         start_humas_teacher_id += 1

# # Write the modified data back to the JSON file
# with open('humas_teachers_fixed.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability


# # Read the JSON file
# with open('piket_username.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         user["pk"] = start_piket_user_id
#         start_piket_user_id += 1

# # Write the modified data back to the JSON file
# with open('piket_username_fixed.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability


# # Read the JSON file
# with open('data_humas_july_2025_cleaned.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         if user["model"] == "userlog.userlog":
#             user["pk"] = start_humas_userlog_id
#             start_humas_userlog_id += 1

# # Write the modified data back to the JSON file
# with open('data_humas_july_2025_cleaned_fixed_2.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability

    
# Read the JSON file
with open('piket_data_july_2025_cleaned.json', 'r') as file:
    data = json.load(file)  # Load JSON content into a Python dictionary or list
    for user in data:
        if user["model"] == "userlog.userlog":
            user["pk"] = start_piket_userlog_id
            start_piket_userlog_id += 1

# Write the modified data back to the JSON file
with open('piket_data_july_2025_cleaned_fixed_2.json', 'w') as file:
    json.dump(data, file, indent=4)  # Save with indentation for readability