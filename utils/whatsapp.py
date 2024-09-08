import requests
from django.conf import settings
token = settings.TOKEN

def send_WA_general(phone="085701570100", action="", messages=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil {action} {messages}.

_Ini adalah pesan otomatis, jangan dibalas._'''
    url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return None


def send_WA_login_logout(phone="085701570100", action="", messages=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil {action}.
{messages}. Jika ada yang ditanyakan terkait aplikasi, silahkan hubungi:
https://wa.me/6285701570100

_Ini adalah pesan otomatis, jangan dibalas._'''
    url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return None


def send_WA_create_update_delete(phone="085701570100", action="", messages="", type="", slug=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil {action} {messages}.
Detail laporan:
https://pmbp.smasitalbinaa.com/{type}{slug}

_Ini adalah pesan otomatis, jangan dibalas._'''
    url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return None


def send_WA_print(phone="085701570100", doc_type="", messages=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil mencetak {doc_type} {messages}.

_Ini adalah pesan otomatis, jangan dibalas._'''
    url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return None
    

def send_WA_daily_plan(phone="085701570100", daily_plan="", messages="", problems="", id=""):
    message = f'''*[NOTIFIKASI PMBP]*
Daily Plan Masuk: {daily_plan} 
Target: {messages}.
Kendala: {problems}.

Detail: https://pmbp.smasitalbinaa.com/projects/plan/detail/{id}/

_Ini adalah pesan otomatis, jangan dibalas._'''
    url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return None

