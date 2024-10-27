import json
import requests
from django.conf import settings
token = settings.TOKEN

def send_WA_general(phone="085701570100", action="", messages=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil {action} {messages}.

_Ini adalah pesan otomatis, jangan dibalas._'''
    url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone != '0' else '85701570100'}&pesan={message}"
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
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
    url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone != '0' else '85701570100'}&pesan={message}"
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return None


def send_WA_create_update_delete(phone="085701570100", action="", messages="", type="", slug=""):
    if not settings.DEBUG and type == "report/" and "menambahkan" in action:
        url = "https://jogja.wablas.com/api/v2/send-message"
        payload = {
            "data": [
                {
                    'phone': '6281293034867-1565170276',
                    'message': f'''*[NOTIFIKASI PMBP]*
Data masuk: {action} {messages}.
Detail: https://pmbp.smasitalbinaa.com/{type}{slug}''',
                    'isGroup': 'true'
                },
                {
                    'phone': '6281293034867',
                    'message': f'''*[NOTIFIKASI PMBP]*
Data masuk: {action} {messages}.
Detail: https://pmbp.smasitalbinaa.com/{type}{slug}'''
                }
            ]
        }

        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        try:
            requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        except:
            return None
        
    elif not settings.DEBUG and type == "olympiads/" and "menambahkan" in action:
        url = "https://jogja.wablas.com/api/v2/send-message"
        payload = {
            "data": [
                {
                    'phone': '120363021651921651',
                    'message': f'''*[NOTIFIKASI OLIMPIADE]*
Data masuk: {action} {messages}.
Detail: https://pmbp.smasitalbinaa.com/{type}{slug}''',
                    'isGroup': 'true'
                },
                {
                    'phone': '120363328278016757',
                    'message': f'''*[NOTIFIKASI OLIMPIADE]*
Data bimbingan: {action} {messages}.
Detail: https://pmbp.smasitalbinaa.com/{type}{slug}''',
                    'isGroup': 'true'
                },
#                 {
#                     'phone': '120363310795868820', #Grup Tanpa Bimbingan Internal
#                     'message': f'''*[NOTIFIKASI OLIMPIADE]*
# Data bimbingan: {action} {messages}.
# Detail: https://pmbp.smasitalbinaa.com/{type}{slug}''',
#                     'isGroup': 'true'
#                 },
                {
                    'phone': '6285701570100',
                    'message': f'''*[NOTIFIKASI OLIMPIADE]*
Data masuk: {action} {messages}.
Detail: https://pmbp.smasitalbinaa.com/{type}{slug}'''
                }
            ]
        }
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        try:
            requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        except:
            return None
        
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil {action} {messages}.
Detail:
https://pmbp.smasitalbinaa.com/{type}{slug}

_Ini adalah pesan otomatis, jangan dibalas._'''
    url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone != '0' else '85701570100'}&pesan={message}"
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return None


def send_WA_print(phone="085701570100", doc_type="", messages=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil mencetak {doc_type} {messages}.

_Ini adalah pesan otomatis, jangan dibalas._'''
    url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone != '0' else '85701570100'}&pesan={message}"
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return None