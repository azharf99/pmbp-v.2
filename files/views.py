from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
# Create your views here.

@login_required
def RenderJsonToView(request):
    # Example JSON file
    file_path = 'data_clean.json'

    # Using json.load() to parse JSON data from file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Process JSON data
    # print(data['users'].keys())
    return render(request, 'json.html', context={'object_list': data['users']})
