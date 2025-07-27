# schedules/management/commands/generatetimetable.py
import random
from django.core.management.base import BaseCommand
from classes.models import Class
from schedules.models import Course, Schedule
from utils.constants import SCHEDULE_WEEKDAYS

class Command(BaseCommand):
    help = 'Generates a conflict-free timetable'

    def handle(self, *args, **options):
        self.stdout.write("Starting timetable generation...")

        # 1. Fetch all necessary data from the database
        courses = list(Schedule.objects.filter(type="putra").values("schedule_class__short_class_name", "schedule_course__course_name", "schedule_course__periods_per_week", "schedule_course__teacher__teacher_name", "schedule_course__teacher__day_off").order_by().distinct())
        classes = list(Schedule.objects.filter(type="putra").values("schedule_class__short_class_name").order_by().distinct())
        periods = list(Schedule.objects.filter(type="putra").values("schedule_time", "time_start", "time_end").order_by('schedule_time').distinct())
        days = [day[0] for day in SCHEDULE_WEEKDAYS]

        # Create a list of all individual course instances to be scheduled
        # If a course has periods_per_week=3, it will appear 3 times in this list.
        course_instances = []
        for course in courses:
            for _ in range(course["schedule_course__periods_per_week"]):
                course_instances.append(course)
        
        # Shuffle the list to ensure fairness and prevent bias
        random.shuffle(course_instances)

        # This dictionary will hold the generated schedule.
        # Key: (day, period), Value: list of (course, room) tuples
        self.schedule = {}
        
        # 2. Start the backtracking algorithm
        if self.solve(course_instances, days, periods, classes):
            self.stdout.write(self.style.SUCCESS("Successfully found a valid timetable!"))
            
            # 3. Save the generated schedule to the database
            self.save_schedule()
        else:
            self.stdout.write(self.style.ERROR("Could not find a valid timetable with the given constraints."))

    def solve(self, courses_to_schedule, days, periods, classes):
        """
        The core recursive backtracking function.
        """
        # Base case: If there are no more courses to schedule, we've succeeded.
        if not courses_to_schedule:
            return True

        # Take the first course from the list to try and place.
        course = courses_to_schedule[0]

        # Iterate through all possible days, periods, and classes.
        for day in days:
            for period in periods:
                for room in classes:
                    # Check if placing the course here is valid.
                    if self.is_valid_placement(course, day, period, room):
                        
                        # If valid, place the course.
                        slot = (day, period)
                        if slot not in self.schedule:
                            self.schedule[slot] = []
                        
                        self.schedule[slot].append({'course': course, 'room': room})

                        # Recursively call solve() for the rest of the courses.
                        remaining_courses = courses_to_schedule[1:]
                        if self.solve(remaining_courses, days, periods, classes):
                            return True # Success!

                        # If the recursive call failed, it means we hit a dead end.
                        # We must backtrack: undo the placement and try the next option.
                        self.schedule[slot].pop()
                        if not self.schedule[slot]:
                            del self.schedule[slot]
        
        # If we've tried all possibilities for this course and none worked,
        # return False to trigger backtracking in the parent call.
        return False

    def is_valid_placement(self, course, day, period, room):
        """
        Checks if a course can be placed in a specific slot and room
        without violating any constraints.
        """
        # Constraint 1: Teacher's Day Off
        if day == course["schedule_course__teacher__day_off"]:
            return False

        slot = (day, period)
        
        # Check if the slot is already partially or fully booked
        if slot in self.schedule:
            scheduled_courses_in_slot = self.schedule[slot]
            
            # Constraint 2: Room availability
            # Check if the room is already taken at this time.
            if any(entry['room'] == room for entry in scheduled_courses_in_slot):
                return False

            # Constraint 3: Teacher availability
            # Check if the teacher is already teaching another class at this time.
            if any(entry['course']["schedule_course__teacher__teacher_name"] == course["schedule_course__teacher__teacher_name"] for entry in scheduled_courses_in_slot):
                return False

            # Constraint 4: Class availability
            # Check if the class is already scheduled for another course at this time.
            if any(entry['course']["schedule_class__short_class_name"] == course["schedule_class__short_class_name"] for entry in scheduled_courses_in_slot):
                return False
        
        # If all checks pass, the placement is valid.
        return True

    def save_schedule(self):
        """
        Deletes the old timetable and saves the new one to the database.
        """
        self.stdout.write("Saving schedule to the database...")
        # Clear the old timetable first
        TimetableEntry.objects.all().delete()
        
        entries_to_create = []
        for (day, period), entries in self.schedule.items():
            for entry in entries:
                entries_to_create.append(
                    TimetableEntry(
                        course=entry['course'],
                        day=day,
                        period=period,
                        room=entry['room']
                    )
                )
        
        # Use bulk_create for efficiency
        TimetableEntry.objects.bulk_create(entries_to_create)
        self.stdout.write(self.style.SUCCESS(f"Successfully saved {len(entries_to_create)} timetable entries."))

