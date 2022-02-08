# This script prints all exams between two given dates

import OpenTamPy # pylint: disable=import-error
from creds import username, password, school # pylint: disable=import-error

# authenticating
client = OpenTamPy.Intranet(username, password, school, debug=True)

# check if there is an exam -> https://opentampy.readthedocs.io/api.html#lesson.hasExam
for lesson in client.get_timetable(start_date="20.12.21", end_date="25.02.22"):
    if "(!)" in lesson.title:
        print(f"Exam on the {lesson.lessonDate}, during {lesson.title}")
