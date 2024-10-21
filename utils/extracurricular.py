import MySQLdb
import sshtunnel
import requests
import datetime

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

token = 'IeFSDe7RzYEDn4QJxKLX9Wc3luhUnMgvdQPB5Gr8tshU97RywNjkgpdG5XRZr8BT'

def send_whatsapp(phone='085701570100', pembina_ekskul='', nama_ekskul=''):
    message = f'''*[NOTIFIKASI PMBP]*
Assalamu'alaikum ustadz {pembina_ekskul}. 
Bulan ini belum ada laporan pertemuan ekskul {nama_ekskul}.
Link input laporan di: https://pmbp.smasitalbinaa.com/

_Ini adalah pesan otomatis dari system, jangan dibalas._'''
    url = f"https://albinaa.sch.id/wp-content/wa/api.php?sender=6285157030478&no=62{phone[1:] if phone is not '0' else '85701570100'}&pesan={message}"
    # url = f"https://jogja.wablas.com/api/send-message?phone={phone}&message={message}&token={token}"
    try:
        data = requests.get(url)
        return data
    except:
        return print("Error mengirim pesan WA!")




if (datetime.datetime.now().day >= 1):
    with sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com'),
        ssh_username='smaitalbinaa', ssh_password='Azhar1995',
        remote_bind_address=('smaitalbinaa.mysql.pythonanywhere-services.com', 3306)
    ) as tunnel:
        connection = MySQLdb.connect(
            user='smaitalbinaa',
            passwd='Azhar1995',
            host='127.0.0.1', port=tunnel.local_bind_port,
            db='smaitalbinaa$backup',
        )
        # Do stuff
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Example query: Select all rows from a table
        
        query = f'''select name, teacher_name from reports_teacher as pembimbing
                    join reports as laporan
                    on laporan.id = pembimbing.report_id
                    join extracurriculars as ekskul
                    on ekskul.id = laporan.extracurricular_id
                    join teachers as guru
                    on guru.id = pembimbing.teacher_id
                    where laporan.report_date >= "{datetime.date.today().year}-{datetime.date.today().month}-01"
                    order by laporan.report_date;'''

        cursor.execute(query)

        data = dict()

        # Fetch all the rows
        rows = cursor.fetchall()

        
        # Process the rows as needed
        for (nama_ekskul, pembina) in rows:
            if not data.get(nama_ekskul):
                data[nama_ekskul] = [pembina]
            else:
                if not pembina in data[nama_ekskul]: 
                    data[nama_ekskul].append(pembina)


        query2 = f'''select name, teacher_name, phone from extracurriculars_teacher
                    join extracurriculars
                    on extracurriculars.id = extracurriculars_teacher.extracurricular_id
                    join teachers
                    on teachers.id = extracurriculars_teacher.teacher_id
                    where phone != {"0"};'''

        cursor.execute(query2)
        ekskul_rows = cursor.fetchall()

        for (nama_ekskul, nama_pembina, nomor_hp) in ekskul_rows:
            if not nama_ekskul in data.keys():
                # send_whatsapp(nomor_hp, nama_pembina, nama_ekskul)
                print(nama_ekskul, nama_pembina, nomor_hp)
            elif not nama_pembina in data[nama_ekskul]:
                # send_whatsapp(nomor_hp, nama_pembina, nama_ekskul)
                print(nama_ekskul, nama_pembina, nomor_hp)

        # Close the cursor and connection
        cursor.close()
        connection.close()
    