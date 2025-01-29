import requests
from django.conf import settings
# token = settings.TOKEN
token = "QEXvQ90p0OzvwZLWOFMpHYwo22JdXG"

def send_WA_general(phone="085701570100", action="", messages=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil {action} {messages}.

_Ini adalah pesan otomatis, jangan dibalas._'''
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    # url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone.startswith('0') and phone != '0' else '85701570100'}&pesan={message}"
    url = f"https://sent.fafashop.my.id/send-message?api_key={token}&sender=6285776707304&number={phone}&message={message}"

    try:
        data = requests.get(url, timeout=5)
        return data
    except:
        return None


def send_WA_login_logout(phone="085701570100", action="", messages=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil {action}.
{messages}. Jika ada yang ditanyakan terkait aplikasi, silahkan hubungi:
https://wa.me/6285701570100

_Ini adalah pesan otomatis, jangan dibalas._'''
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    # url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone.startswith('0') and phone != '0' else '85701570100'}&pesan={message}"
    url = f"https://sent.fafashop.my.id/send-message?api_key={token}&sender=6285776707304&number={phone}&message={message}"

    try:
        data = requests.get(url, timeout=5)
        return data
    except:
        return None


def send_WA_create_update_delete(phone="085701570100", action="", messages="", type="", slug=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil {action} {messages}.
Detail laporan:
https://pmbp.albinaa.sch.id/{type}{slug}

_Ini adalah pesan otomatis, jangan dibalas._'''
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    # url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone.startswith('0') and phone != '0' else '85701570100'}&pesan={message}"
    url = f"https://sent.fafashop.my.id/send-message?api_key={token}&sender=6285776707304&number={phone}&message={message}"

    try:
        data = requests.get(url, timeout=5)
        return data
    except:
        return None


def send_WA_general(phone="085701570100", doc_type="", messages=""):
    message = f'''*[NOTIFIKASI PMBP]*
Anda berhasil mencetak {doc_type} {messages}.

_Ini adalah pesan otomatis, jangan dibalas._'''
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    # url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone.startswith('0') and phone != '0' else '85701570100'}&pesan={message}"
    url = f"https://sent.fafashop.my.id/send-message?api_key={token}&sender=6285776707304&number={phone}&message={message}"

    try:
        data = requests.get(url, timeout=5)
        return data
    except:
        return None
    

def send_WA_daily_plan(phone="085701570100", daily_plan="", messages="", problems="", id=""):
    message = f'''*[NOTIFIKASI PMBP]*
Daily Plan Masuk: {daily_plan} 
Target: {messages}.
Kendala: {problems}.

Detail: https://pmbp.albinaa.sch.id/projects/plan/detail/{id}/

_Ini adalah pesan otomatis, jangan dibalas._'''
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    # url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone.startswith('0') and phone != '0' else '85701570100'}&pesan={message}"
    url = f"https://sent.fafashop.my.id/send-message?api_key={token}&sender=6285776707304&number={phone}&message={message}"
    try:
        data = requests.get(url, timeout=5)
        return data
    except:
        return None

