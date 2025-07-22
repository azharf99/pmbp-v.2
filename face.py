# Face Recognition Presence Application
# This application uses the deepface library for face recognition
# and OpenCV for real-time video capture.
# This version uses multiprocessing to prevent video lag.

# --- Dependencies ---
# You need to install the following libraries:
# pip install deepface opencv-python pandas

import cv2
import os
import pandas as pd
from deepface import DeepFace
import time
from multiprocessing import Process, Queue

# --- Configuration ---
DB_PATH = "student_database"  # Path to the database of student images
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
FONT_THICKNESS = 2
BOX_COLOR = (0, 255, 0)  # Green for recognized faces
TEXT_COLOR = (255, 255, 255)  # White for text
UNKNOWN_COLOR = (0, 0, 255) # Red for unknown faces

def initialize_database():
    """Creates the database directory if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
        print(f"Database directory created at: {DB_PATH}")

def enroll_student():
    """Enrolls a new student by capturing their face."""
    student_name = input("Enter the student's name: ").strip().lower().replace(" ", "_")
    if not student_name:
        print("Student name cannot be empty.")
        return

    student_dir = os.path.join(DB_PATH, student_name)
    if not os.path.exists(student_dir):
        os.makedirs(student_dir)

    print("\nPreparing to capture image...")
    print("Please look at the camera and hold still.")
    print("The image will be taken in 5 seconds.")
    time.sleep(5)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam.")
        cap.release()
        return

    # Save the captured image
    image_count = len(os.listdir(student_dir)) + 1
    image_path = os.path.join(student_dir, f"{student_name}_{image_count}.jpg")
    cv2.imwrite(image_path, frame)
    print(f"Image saved for {student_name} at {image_path}")

    cap.release()
    cv2.destroyAllWindows()

def face_recognition_worker(input_q, output_q):
    """
    Worker process for face recognition.
    Gets frames from input_q, processes them, and puts results in output_q.
    """
    while True:
        frame = input_q.get()
        if frame is None:  # Sentinel value to stop the process
            break
        
        results = []
        try:
            # DeepFace.find is the time-consuming operation
            dfs = DeepFace.find(img_path=frame, db_path=DB_PATH, enforce_detection=False, silent=True)
            
            for df in dfs:
                if not df.empty:
                    for _, row in df.iterrows():
                        identity = row['identity']
                        student_name = os.path.basename(os.path.dirname(identity))
                        face_region = row['source_x'], row['source_y'], row['source_w'], row['source_h']
                        results.append((student_name, face_region))
        except Exception as e:
            # If no face is found, DeepFace throws an exception.
            # We put an empty list to signify no results.
            pass
        
        output_q.put(results)


def recognize_and_attend():
    """
    Recognizes students from the webcam feed using a separate process
    to avoid lagging the main video feed.
    """
    # Queues for communication between processes
    input_q = Queue(maxsize=1)
    output_q = Queue(maxsize=1)

    # Create and start the worker process
    recognition_process = Process(target=face_recognition_worker, args=(input_q, output_q))
    recognition_process.start()

    print("\nStarting real-time recognition...")
    print("Press 'q' to quit.")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        recognition_process.terminate()
        return

    present_students = set()
    latest_results = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam.")
            break

        # If the input queue is empty, it means the worker is ready for a new frame.
        if input_q.empty():
            input_q.put(frame)

        # Check for new results from the worker process without blocking.
        if not output_q.empty():
            latest_results = output_q.get()
            for name, _ in latest_results:
                present_students.add(name)

        # Draw the latest results on the current frame.
        if latest_results:
            for name, (x, y, w, h) in latest_results:
                cv2.rectangle(frame, (x, y), (x + w, y + h), BOX_COLOR, FONT_THICKNESS)
                cv2.putText(frame, name, (x, y - 10), FONT, FONT_SCALE, TEXT_COLOR, FONT_THICKNESS)

        cv2.imshow("Presence System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    input_q.put(None)  # Send sentinel to stop the worker process
    recognition_process.join() # Wait for the process to finish
    cap.release()
    cv2.destroyAllWindows()

    # Print the attendance list
    print("\n--- Attendance ---")
    if present_students:
        for student in sorted(list(present_students)):
            print(f"- {student.replace('_', ' ').title()}")
    else:
        print("No students were recognized.")
    print("------------------")


def main():
    """Main function to run the application."""
    initialize_database()

    while True:
        print("\n--- Presence Application Menu ---")
        print("1. Enroll a new student")
        print("2. Start attendance")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            enroll_student()
        elif choice == '2':
            recognize_and_attend()
        elif choice == '3':
            print("Exiting application.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # This check is essential for multiprocessing to work correctly on all platforms.
    main()
