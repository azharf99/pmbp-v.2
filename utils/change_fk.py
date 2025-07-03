import json

id_map_teachers = {
    1:39,
    2:40,
    3:41,
    4:42,
    5:43,
    6:44,
    7:45,
    8:46,
    9:47,
    10:48,
    11:49,
    12:50,
    13:51,
    14:52,
    15:53,
    16:54,
    17:55,
    18:56,
    19:57,
    20:58,
    21:59,
}

id_map_students = {
    1:135,
    2:136,
    3:137,
    4:138,
    5:139,
    6:140,
    7:141,
    8:142,
    9:143,
    10:144,
    11:145,
    12:146,
    13:147,
    14:148,
    15:149,
    16:150,
    17:151,
    18:152,
    19:153,
    20:154,
    21:155,
    22:156,
    23:157,
    24:158,
    25:159,
    26:160,
    27:161,
    28:162,
    29:163,
    30:164,
    31:165,
    32:166,
    33:167,
    34:168,
    35:169,
    36:170,
    37:171,
    38:172,


    41:175,
    42:176,
    43:177,
    44:178,
    45:179,
    46:180,
    47:181,
    48:182,
    49:183,
    50:184,
    51:185,
    52:186,
    53:187,
    54:188,
    55:189,
    56:190,
    57:191,
    58:192,
    59:193,
    60:194,
    61:195,

    63:197,
    64:198,
    65:199,
    66:200,
    67:201,
    68:202,

    70:204,
    71:205,
    72:206,
    73:207,
    74:208,
    75:209,
    76:210,
    77:211,
    78:212,
    79:213,
    80:214,
    81:215,
    82:216,
    83:217,
    84:218,
    85:219,
    86:220,
    87:221,
    88:222,
    89:223,
    90:224,
    91:225,
    92:226,
    93:227,
    94:228,
    95:229,
    96:230,
    97:231,
    98:232,
    99:233,
    100:234,
    101:235,
    102:236,
    103:237,
    104:238,
    105:239,
    106:240,
    107:241,
    108:242,
    109:243,
    110:244,
    111:245,
    112:246,
    113:247,
    114:248,
    115:249,
    116:250,
    117:251,
    118:252,
    119:253,
    120:254,
    121:255,
    122:256,
    123:257,
}

id_map_piket_users = {
    1:65,
    2:66,
    3:67,
    4:68,
    5:69,
    6:70,
    7:71,
    8:72,
    9:73,
    10:74,
    11:75,
    12:76,
    13:77,
    14:78,
    15:79,
    16:80,
    17:81,
    18:82,
    19:83,
    20:84,
    21:85,
    22:86,
    23:87,
    24:88,
    25:89,
    26:90,
    27:91,
    28:92,
    29:93,
    30:94,
    31:95,
    32:96,
    33:97,
    34:98,
    35:99,
    36:100,
    37:101,
    38:102,
    39:103,
    40:104,
    41:105,
    42:106,
    43:107,
    44:108,
    45:109,
    46:110,
    47:111,
    48:112,
    49:113,
    50:114,
    51:115,
    52:116,
    53:117,
}


# # Read the JSON file
# temp_teacher_ids = []
# with open('data_humas_july_2025_cleaned.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         if user["model"] == "private.subject":
#             for pembimbing_id in user["fields"]["pembimbing"]:
#                 if pembimbing_id in id_map_teachers.keys():
#                     temp_teacher_ids.append(id_map_teachers[pembimbing_id])
#             user["fields"]["pembimbing"] = temp_teacher_ids
#             temp_teacher_ids = []

# # Write the modified data back to the JSON file
# with open('data_humas_july_2025_cleaned_2.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability


# student_temp_ids = []
# with open('data_humas_july_2025_cleaned_2.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         if user["model"] == "private.group":
#             for student_id in user["fields"]["santri"]:
#                 if student_id in id_map_students.keys():
#                     student_temp_ids.append(id_map_students[student_id])
#             user["fields"]["santri"] = student_temp_ids
#             student_temp_ids = []

# # Write the modified data back to the JSON file
# with open('data_humas_july_2025_cleaned_2_2.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability



# student_temp_ids = []
# with open('data_humas_july_2025_cleaned_2_2.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         if user["model"] == "private.private":
#             pembimbing_id = user["fields"]["pembimbing"]
#             if pembimbing_id in id_map_teachers.keys():
#                 user["fields"]["pembimbing"] = id_map_teachers[pembimbing_id]

#             for student_id in user["fields"]["kehadiran_santri"]:
#                 if student_id in id_map_students.keys():
#                     student_temp_ids.append(id_map_students[student_id])
#             user["fields"]["kehadiran_santri"] = student_temp_ids
#             student_temp_ids = []

# # Write the modified data back to the JSON file
# with open('data_humas_july_2025_cleaned_2_2_2.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability


# with open('course.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         if user["model"] == "courses.course":
#             teacher_id = user["fields"]["teacher"]
#             if teacher_id in id_map_piket_users.keys():
#                 user["fields"]["teacher"] = id_map_piket_users[teacher_id]

# # Write the modified data back to the JSON file
# with open('course_2.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability


# with open('schedule.json', 'r') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for user in data:
#         if user["model"] == "schedules.reporterschedule":
#             reporter_id = user["fields"]["reporter"]
#             if reporter_id and reporter_id in id_map_piket_users.keys():
#                 user["fields"]["reporter"] = id_map_piket_users[reporter_id]

# # Write the modified data back to the JSON file
# with open('schedule_2.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability


# start_report_id = 1
# with open('report.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)  # Load JSON content into a Python dictionary or list
#     for report in data:
#         report["pk"] = start_report_id
#         reporter_id = report["fields"]["reporter"]
#         subtitute_teacher_id = report["fields"]["subtitute_teacher"]
#         if reporter_id and reporter_id in id_map_piket_users.keys():
#             report["fields"]["reporter"] = id_map_piket_users[reporter_id]

#         if subtitute_teacher_id and subtitute_teacher_id in id_map_piket_users.keys():
#             report["fields"]["subtitute_teacher"] = id_map_piket_users[subtitute_teacher_id]
#         start_report_id += 1

# # Write the modified data back to the JSON file
# with open('report_2.json', 'w') as file:
#     json.dump(data, file, indent=4)  # Save with indentation for readability