from django.shortcuts import render, redirect
from django.core.management import call_command
from django.contrib import messages
from .models import TimetableEntry, Period, Class

def timetable_view(request):
    """
    This view fetches and displays the generated timetable in a grid format.
    """
    # Get all unique classes, periods, and the days of the week
    classes = Class.objects.filter(category="Putra")
    periods = Period.objects.order_by('number')
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday", "Sunday"]

    # You can select a class to view its specific timetable
    selected_class_id = request.GET.get('class_id')
    
    if selected_class_id:
        # Filter entries for the selected class
        schedule_entries = TimetableEntry.objects.filter(lesson__class_assigned_id=selected_class_id, lesson__subject_teacher__type="putra").select_related('lesson__subject_teacher', 'period', 'room')
        selected_class = Class.objects.get(id=selected_class_id)
    else:
        # By default, show the first class or an empty schedule
        if classes.exists():
            selected_class = classes.first()
            schedule_entries = TimetableEntry.objects.filter(lesson__class_assigned=selected_class, lesson__subject_teacher__type="putra").select_related('lesson__subject_teacher__teacher', 'lesson__subject_teacher__subject', 'period', 'room')
        else:
            selected_class = None
            schedule_entries = TimetableEntry.objects.none()

    # Structure the data for easy rendering in the template
    # The grid will be a dictionary: {(day, period_number): "Subject by Teacher in Room", ...}
    schedule_grid = {}
    for entry in schedule_entries:
        key = (entry.day, entry.period.number)
        schedule_grid[key] = f"{entry.lesson.subject_teacher.course_name}<br><small>{entry.lesson.subject_teacher.teacher.teacher_name}<br>({entry.room.name})</small>"

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'periods': periods,
        'days': days,
        'schedule_grid': schedule_grid,
    }
    return render(request, 'scheduler/timetable.html', context)

def generate_timetable_view(request):
    """
    This view triggers the timetable generation command.
    """
    if request.method == 'POST':
        try:
            # Call the management command programmatically
            call_command('generatetimetable')
            messages.success(request, 'Successfully generated a new timetable!')
        except Exception as e:
            # Catch potential errors during generation
            messages.error(request, f'An error occurred during timetable generation: {e}')
        
        # Redirect back to the timetable display page
        return redirect('timetable_view')
    
    # If not a POST request, just redirect
    return redirect('timetable_view')