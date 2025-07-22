from datetime import datetime, time
from zoneinfo import ZoneInfo
import cv2
from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse
import numpy as np
from deepface import DeepFace
from utils.datetime_wtih_tz import get_current_local_date, get_current_local_datetime
from .models import Student, AttendanceRecord
from .face_utils import decode_base64_image, extract_face_embeddings, compare_embeddings
import pickle
import face_recognition

def dashboard(request):
    
    return render(request, 'attendance/dashboard.html')

def dashboard_data(request):
    """
    API endpoint for real-time dashboard data
    """
    today = get_current_local_date()
    records = AttendanceRecord.objects.filter(date=today).select_related('student')
    present_students = [
        {"name": r.student.student_name, "student_id": r.student.nis, "time": time(r.timestamp.hour, r.timestamp.minute, r.timestamp.second, tzinfo=ZoneInfo("Asia/Jakarta"))}
        for r in records
    ]
    total_present = len(set(r.student.id for r in records))
    return JsonResponse({
        "total_present": total_present,
        "present_students": present_students
    })

def register_student(request):
    students = Student.objects.filter(student_status="Aktif")
    if request.method == "POST":
        try:
            nis = request.POST['students']
            _, image_data = request.POST['image_data'].split(",", 1)

            if not nis or not image_data:
                return JsonResponse({'error': 'Missing NIS or image data'}, status=400)

            # Write the binary data to a file
            np_img = decode_base64_image(image_data)
            embeddings = extract_face_embeddings(np_img)

            if not embeddings:
                    return JsonResponse({'error': 'No face detected. Try again.'}, status=422)
            

            Student.objects.update_or_create(
                nis=nis,
                defaults=dict(
                    face_encoding=pickle.dumps(embeddings[0]),
                )
            )
            return redirect('attendance-dashboard')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'attendance/register.html', {"students": students})

def take_attendance(request): 
    if request.method == "POST":
        _, image_data = request.POST['image_data'].split(",", 1)
        np_img = decode_base64_image(image_data)
        detected_embeddings = extract_face_embeddings(np_img)
        if not detected_embeddings:
            return JsonResponse({'status': 'error', 'message': 'No faces detected.'}, status=404)
        
        students = list(Student.objects.filter(student_status="Aktif", face_encoding__isnull=False))
        known_embeddings = [pickle.loads(s.face_encoding) for s in students]

        present_students = []

        for embedding in detected_embeddings:
            match_index = compare_embeddings(known_embeddings, embedding)
            if match_index is not None:
                student = students[int(match_index)]
                AttendanceRecord.objects.update_or_create(
                    student=student,
                    date=get_current_local_date(),
                    defaults=dict(
                        timestamp=get_current_local_datetime(),
                    )
                )
                present_students.append(student.student_name)
        if not present_students:
                return JsonResponse({'status': 'info', 'message': 'No known faces recognized.'}, status=404)
        return JsonResponse({'status': 'success', 'message': f"Marked present: {', '.join(present_students)}"}, status=200)
    return render(request, 'attendance/browser_attendance.html')

def attendance_records(request):
    records = AttendanceRecord.objects.all().order_by('-timestamp')
    return render(request, 'attendance/records.html', {'records': records})


# Load all known student embeddings once
def load_known_students():
    students = Student.objects.filter(student_status="Aktif", face_encoding__isnull=False)
    known_embeddings = []
    student_info = []
    for student in students:
        embedding = pickle.loads(student.face_encoding)
        known_embeddings.append(embedding)
        student_info.append((student.id, student.student_name))
    return known_embeddings, student_info

def mark_attendance(student_id):
    student = Student.objects.get(id=student_id)
    if not AttendanceRecord.objects.filter(student=student, date=get_current_local_date()).exists():
        AttendanceRecord.objects.create(student=student, date=get_current_local_date())

def video_stream():
    cap = cv2.VideoCapture(0)
    known_embeddings, student_info = load_known_students()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect and analyze faces
        try:
            results = DeepFace.find(frame, db_path=None, enforce_detection=False, model_name="Facenet", detector_backend="opencv", silent=True)

            for face in results:
                embedding = face["embedding"]
                distances = [np.linalg.norm(embedding - known) for known in known_embeddings]
                min_distance = min(distances)
                match_idx = np.argmin(distances)

                if min_distance < 0.6:  # Threshold for recognition
                    student_id, student_name = student_info[match_idx]
                    mark_attendance(student_id)
                    # Draw rectangle & name
                    x, y, w, h = face["facial_area"].values()
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, student_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                else:
                    x, y, w, h = face["facial_area"].values()
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

        except Exception as e:
            print(f"Detection error: {e}")

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\\r\\n'
               b'Content-Type: image/jpeg\\r\\n\\r\\n' + frame_bytes + b'\\r\\n')

    cap.release()

def realtime_attendance(request):
    return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')