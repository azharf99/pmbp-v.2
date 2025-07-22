# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# import numpy as np

# from utils.datetime_wtih_tz import get_current_local_date, get_current_local_datetime
# from .models import Student, AttendanceRecord
# from .face_utils import decode_base64_image, encode_face, compare_faces
# import pickle
# import face_recognition

# def dashboard(request):
#     return render(request, 'attendance/dashboard.html')

# def register_student(request):
#     students = Student.objects.filter(student_status="Aktif")
#     if request.method == "POST":
#         try:
#             nis = request.POST['students']
#             image_data = request.POST['image_data']

#             if not nis or not image_data:
#                 return JsonResponse({'error': 'Missing NIS or image data'}, status=400)

#             # Write the binary data to a file
#             np_img = decode_base64_image(image_data)

#             face_locations = face_recognition.face_locations(np_img)
#             if not face_locations:
#                     return JsonResponse({'error': 'No face detected. Try again.'}, status=422)
            
#             face_encoding = face_recognition.face_encodings(np_img, face_locations)[0]
            

#             Student.objects.update_or_create(
#                 nis=nis,
#                 defaults=dict(
#                     face_encoding=pickle.dumps(face_encoding),
#                 )
#             )
#             return redirect('attendance-dashboard')
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return render(request, 'attendance/register.html', {"students": students})

# def take_attendance(request): 
#     if request.method == "POST":
#         _, image_data = request.POST['image_data'].split(",", 1)
#         np_img = decode_base64_image(image_data)
#         face_encodings = encode_face(np_img)
#         if not face_encodings:
#             return JsonResponse({'status': 'No face detected.'})
#         students = list(Student.objects.filter(student_status="Aktif", face_encoding__isnull=False))
#         known_encodings = [pickle.loads(s.face_encoding) for s in students]
#         present_students = []
#         for face_encoding in face_encodings:
#             match_index = compare_faces(known_encodings, face_encoding)
#             if match_index is not None:
#                 student = students[int(match_index)]
#                 AttendanceRecord.objects.update_or_create(
#                     student=student,
#                     date=get_current_local_date(),
#                     defaults=dict(
#                         timestamp=get_current_local_datetime(),
#                     )
#                 )
#                 present_students.append(student.student_name)
#         if present_students:
#             return JsonResponse({'status': f"Marked present: {', '.join(present_students)}"}, status=200)
#         else:
#             return JsonResponse({'status': 'Face not recognized.'}, status=404)
#     return render(request, 'attendance/take_attendance.html')

# def attendance_records(request):
#     records = AttendanceRecord.objects.all().order_by('-timestamp')
#     return render(request, 'attendance/records.html', {'records': records})