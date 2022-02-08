from OpenTamPy import Intranet # pylint: disable=import-error, no-name-in-module
from creds import username, password, schoolcode # pylint: disable=import-error, no-name-in-module
from datetime import datetime


# Test generators
def loop(x):
    for i in x:
        print(
f"""
########## Return data ##########
{i}
""")
        break

instance = Intranet(username, password, schoolcode, debug=True)

with open("test.jpg", "wb") as file:
    img = instance.get_person_picture()
    img.save("test.png")

print("Calling timetable function...")
x = instance.get_timetable(start_date="05.12.21", end_date="23.02.22")
for lesson in x:
    if "(!)" in lesson.title:
        print(f"Exam on the {lesson.lessonDate}, during {lesson.title}")

print("Calling get_absences()...")
x = instance.get_absences()
loop(x)
print("Calling get_class_mates()...")
x = instance.get_class_mates()
loop(x)
print("Calling get_class_teachers()...")
x = instance.get_class_teachers()
loop(x)


# Test other functions
print("Calling get_resources()...")
resources = instance.get_resources()
# print(resources)

# prepare arguments
for lesson in instance.get_timetable():
    # requires arguments
    print("Calling get_lesson_absence_data()...")
    x = instance.get_lesson_absence_data(lesson)
    print("Calling get_additional_homework_info()")
    x = instance.get_additional_homework_info(lesson)
    break