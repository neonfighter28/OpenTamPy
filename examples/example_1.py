"""
This example checks all absences, and prints it to stdout if any of them are from today
"""

import OpenTamPy
from datetime import datetime

from creds import username, password, school

# Initialize instance
instance = OpenTamPy.Intranet(username, password, school)

# Today as DD.MM.YY
today = datetime.today().strftime(r"%d.%m.%Y")
success = False

# Using yield to our advantage in a for loop to iterate over all absences
for absence in instance.get_absences():

    # Comparing today against the absence date
    if today == absence.Datum:
        # Print name of the course where the absence happened
        print(absence.Kurs_Anlass)
        # disables callback
        success = True

# Checking if we had any absences
if not success:
    print("No absences found")