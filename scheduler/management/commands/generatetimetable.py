# scheduler/management/commands/generatetimetable.py

import random
from django.core.management.base import BaseCommand
from scheduler.models import Lesson, Room, Period, TimetableEntry, DAY_CHOICES

class Command(BaseCommand):
    help = 'Generates a conflict-free timetable'

    def handle(self, *args, **options):
        self.stdout.write("Starting timetable generation...")

        # 1. Fetch all necessary data from the database
        lessons = list(Lesson.objects.all())
        rooms = list(Room.objects.all())
        periods = list(Period.objects.all())
        days = [day[0] for day in DAY_CHOICES]

        # Create a list of all individual lesson instances to be scheduled
        # If a lesson has periods_per_week=3, it will appear 3 times in this list.
        lesson_instances = []
        for lesson in lessons:
            for _ in range(lesson.periods_per_week):
                lesson_instances.append(lesson)
        
        # Shuffle the list to ensure fairness and prevent bias
        random.shuffle(lesson_instances)

        # This dictionary will hold the generated schedule.
        # Key: (day, period), Value: list of (lesson, room) tuples
        self.schedule = {}
        
        # 2. Start the backtracking algorithm
        if self.solve(lesson_instances, days, periods, rooms):
            self.stdout.write(self.style.SUCCESS("Successfully found a valid timetable!"))
            
            # 3. Save the generated schedule to the database
            self.save_schedule()
        else:
            self.stdout.write(self.style.ERROR("Could not find a valid timetable with the given constraints."))

    def solve(self, lessons_to_schedule, days, periods, rooms):
        """
        The core recursive backtracking function.
        """
        # Base case: If there are no more lessons to schedule, we've succeeded.
        if not lessons_to_schedule:
            return True

        # Take the first lesson from the list to try and place.
        lesson = lessons_to_schedule[0]

        # Iterate through all possible days, periods, and rooms.
        for day in days:
            for period in periods:
                for room in rooms:
                    # Check if placing the lesson here is valid.
                    if self.is_valid_placement(lesson, day, period, room):
                        
                        # If valid, place the lesson.
                        # (Senin, Jam 1)
                        slot = (day, period)
                        if slot not in self.schedule:
                            self.schedule[slot] = []
                        
                        self.schedule[slot].append({'lesson': lesson, 'room': room})
                        """
                        schedule = {
                        (Senin, 1):[
                        {"lesson": biologi, "room": "10A"},
                        {"lesson": fisika, "room": "10B"},
                        ],
                        
                        }
                        """

                        # Recursively call solve() for the rest of the lessons.
                        remaining_lessons = lessons_to_schedule[1:]
                        if self.solve(remaining_lessons, days, periods, rooms):
                            return True # Success!

                        # If the recursive call failed, it means we hit a dead end.
                        # We must backtrack: undo the placement and try the next option.
                        self.schedule[slot].pop()
                        if not self.schedule[slot]:
                            del self.schedule[slot]
        
        # If we've tried all possibilities for this lesson and none worked,
        # return False to trigger backtracking in the parent call.
        return False

    def is_valid_placement(self, lesson, day, period, room):
        """
        Checks if a lesson can be placed in a specific slot and room
        without violating any constraints.
        """
        # Constraint 1: Teacher's Day Off
        if day == lesson.subject_teacher.teacher.day_off:
            return False

        slot = (day, period)
        
        # Check if the slot is already partially or fully booked
        if slot in self.schedule:
            scheduled_lessons_in_slot = self.schedule[slot]
            
            # Constraint 2: Room availability
            # Check if the room is already taken at this time.
            if any(entry['room'] == room for entry in scheduled_lessons_in_slot):
                return False

            # Constraint 3: Teacher availability
            # Check if the teacher is already teaching another class at this time.
            if any(entry['lesson'].subject_teacher.teacher == lesson.subject_teacher.teacher for entry in scheduled_lessons_in_slot):
                return False

            # Constraint 4: Class availability
            # Check if the class is already scheduled for another lesson at this time.
            if any(entry['lesson'].class_assigned == lesson.class_assigned for entry in scheduled_lessons_in_slot):
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
                        lesson=entry['lesson'],
                        day=day,
                        period=period,
                        room=entry['room']
                    )
                )
        
        # Use bulk_create for efficiency
        TimetableEntry.objects.bulk_create(entries_to_create)
        self.stdout.write(self.style.SUCCESS(f"Successfully saved {len(entries_to_create)} timetable entries."))

