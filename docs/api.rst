API Reference
=============

The following section gives you a clearer insight into the functions of OpenTamPy

.. note:: As objects are constructed directly from their Intranet response, there is no guarantee that their attributes will persist over all time. Therefore it is considered best practice to implement a try-except block for AttributeErrors

The Intranet class
-------------------

OpenTamPy is based on this class and a few helper functions, to help you achieve your goal. All functions and attributes of the library can be called from this class
For an asynchronous version of this class refer to :doc:`async`

.. class:: Intranet(username, password, school, debug=False)

    This is the base class from where you can call all the libraries functions from. To be able to do this, you need to create an instance of this class first.

    :param username: Your Intranet username. This is only used for authentication purposes
    :type username: str
    :param password: Your Intranet password. This is only used for authentication purposes
    :type password: str
    :param school: Your schoolcode. Ex: ``krm`` for MNG, ``krr`` for RGZH. Can be found in the URL. Ex: In ``https://intranet.tam.ch/krm/``, where ``krm`` would be the schoolcode
    :type school: str
    :param debug: Whether logging should be set to debug. Defaults to False
    :type debug: bool

    .. function:: get_timetable(start_date=0, end_date=0, user_id=None, timeout=20)

        :param start_date: Start of the timebracket as 'DD.MM.YY', defaults to last monday
        :type start_date: int
        :param end_date: End of the timebracket as 'DD.MM.YY', defaults to next sunday
        :param user_id: Fetch timetable for any student with the given Id
        :param timeout: Passed through to the request, increase if you request large amounts of data, as it might take longer to process than the default.
        :type timeout: int

        It is possible to fetch someone elses timetable if only their studentID is given, which can be acquired by running `get_class_mates`. Whether this is intentional or not is unclear, so this might be removed at any time

        :yield: :class:`lesson`

    .. function:: get_absences()

        This function fetches a list of all absences and returns an Iterator containing objects from which you can get information very easily.

        .. code-block:: python3

            instance = Intranet(username, password)
            absenceIterator = instance.get_absences()
            for absence in absenceIterator:
                print("Name of teacher", absence.Lehrperson)

        :return: :class:`absence`

    .. function:: get_lesson_absence_data(lesson)

        This function fetches the absence data corresponding to the :class:`lesson` passed through
        You can also pass through a list of :class:`lesson` objects, and the function will return a list of the corresponding values

        :param lesson: :class:`lesson`
        :return: If the parameter was a lesson, returns a list of :class:`lesson` object, otherwise only a :class:`lesson` object

    .. function:: get_class_mates()

        This function fetches a list of each classMate and yields it back

        :yield: :class:`ClassMate`

    .. function:: get_class_teachers()

        This function fetches a list of each teacher and yields it back

        :yield: :class:`teacher`

    .. function:: set_homework_data(lesson, title, description)

        :param title: Title for absence to be set
        :type title: str
        :param description: Description for absence to be set
        :type description: str
        :raise MissingPermission: Not enough permissions

        Set homework data for passed through lesson, returns new homework data

    .. function:: delete_homework_info(lesson)

        :param lesson: Lesson object for which the absence should be deleted
        :raise MissingPermission: Not enough permissions

        Deletes all homework associated with that lesson

    .. function:: get_additional_homework_info(lesson)

        :param lesson: Lesson object for which the homework info should be fetched

The resource object
-------------------

.. class:: resource

    .. attribute:: classes
        :type: list

        list contains :class:`class` objects documented below

        .. class:: class

            .. attribute:: classCommonName
                :type: str

            .. attribute:: classId
                :type: int

            .. attribute:: classLevel
                :type: str

            .. attribute:: className
                :type: str

            .. attribute:: classShort
                :type: str

            .. attribute:: occupied
                :type: int

            .. attribute:: periodId
                :type: int

    .. attribute:: courses
        :type: list

        list contains :class:`course` objects documented below

        .. class :: course

            .. attribute:: course
                :type: str

                Name of the course. Ex: ``Anwendungen der Mathematik``

            .. attribute:: courseId
                :type: int

            .. attribute:: courseShort
                :type: str

                Short name of the course. Ex: ``AM``

            .. attribute:: courseShortWithClasses
                :type: str

                Short Name containing classes. Ex: ``AM (6x, 6x, 6x, 6x)``

            .. attribute:: periodId
                :type: str

            .. attribute:: studentId
                :type: list[int]

                List of all students

            .. attribute:: studentName
                :type: str

                All student names separated by a semicolon

            .. attribute:: subjectId
                :type: int

    .. attribute:: resources
        :type: list

        .. class :: resource

            .. attribute:: description
                :type: str

                Description of resource

            .. attribute:: resource
                :type: str

                Resource

            .. attribute:: resourceCategory
                :type: str

            .. attribute:: resourceId
                :type: int

            .. attribute:: sort1
                :type: str

            .. attribute:: sort2
                :type: str

    .. attribute:: rooms
        :type: list

        list containing :class:`room` objects

        .. class:: room

            .. attribute:: building
                :type: str

            .. attribute:: description
                :type: str

            .. attribute:: occupied
                :type: int

            .. attribute:: room
                :type: str

            .. attribute:: roomCategory
                :type: str

            .. attribute:: roomId
                :type: int

            .. attribute:: sort1
                :type: str

    .. attribute:: students
        :type: list

        List containing :class:`student` objects

    .. attribute:: teachers
        :type: list

        List containing :class:`teacher` objects

        .. class:: teacher

            .. attribute:: acronym
                :type: str

            .. attribute:: name
                :type: str

                Name of the teacher

            .. attribute:: occupied
                :type: int

            .. attribute:: personId
                :type: int

                ID of teacher


The absence object
-------------------
This object contains attributes constructed directly from an intranet response, which contains multiple absence objects.
Each absence object represents one absence and thereby its attributes.
The following attributes are documented, but may change at any time without notice


.. class:: absence()

    .. attribute:: Kurs_Anlass
        :type: str

        Name of the course

    .. attribute:: Datum
        :type: str

        Date of the absence in the format DD.MM.YYYY

    .. attribute:: Zeit_Anzahl_Lekt
        :type: str

        Time of the start of the absence in the format HH:MM

    .. attribute:: Lehrperson
        :type: str

        Name of the teacher

    .. attribute:: Absenzgruppe
        :type: str

        Type of the absence, seems to be mostly "Absenz"

    .. attribute:: Status
        :type: str

        Whether the absence has been excused or not

    .. attribute:: PersonID
        :type: str

        Intranet ID for the person you're fetching the absence of

    .. attribute:: AbsenceEventID
        :type: str

        Intranet ID for the absence itself


The lesson object
-------------------
This object contains attributes constructed directly from an intranet response, which contains multiple timetable objects.
Each absence object represents a lesson and thereby its attributes.
The following attributes are documented, but may change at any time without notice, as the Intranet changes quite frequently. I will do my best to keep this documentation updated

.. note: Every attribute exists twice, one as the normal attribute and another escaped version of said attribute. This is due to the intranet returning those aswell

.. class:: lesson

    .. attribute:: id
        :type: int

        Intranet ID for the lesson

    .. attribute:: timetableElementId
        :type: int

        Intranet ID for the position in grid

    .. attribute:: holidayId
        :type: int

        *   - holidayId
            - Info

        *   - 0
            - No holiday

    .. attribute:: blockId
        :type: list[int]

        contains a list with other ids, that it is connected to in a block

    .. attribute:: blockTeacherId
        :type: list[int]

        contains a list of all teacher ids connected to the block

    .. attribute:: blockClassId
        :type: list[int]

        used to represent multiple lessons together with each id being a lesson, empty if theres no associated lessons

    .. attribute:: blockRoomId
        :type: list[int]

    .. attribute:: modId
        :type: int

    .. attribute:: periodId
        :type: int

    .. attribute:: start
        :type: str

        represented as "/Date(`UNIX timestamp`)/"

    .. attribute:: end
        :type: str

        represented as "/Date(`UNIX timestamp`)/"

    .. attribute:: lessonDate
        :type: str

        represented as "YYYY-MM-DD"

    .. attribute:: lessonStart
        :type: str

        represented as "HH:MM:SS"

    .. attribute:: lessonEnd
        :type: str

        represented as "HH:MM:SS"

    .. attribute:: lessonDuration
        :type: str

        Duration of lesson as "HH:MM:SS.000000".

    .. attribute:: nbrOfModifiedLesson
        :type: str

    .. attribute:: connectedId
        :type: None

        Appears to always be 'None'

    .. attribute:: isAllDay
        :type: int

    .. attribute:: timetableEntryTypeId
        :type: int

    .. attribute:: timetableEntryType
        :type: str

    .. attribute:: timetableEntryTypeLong
        :type: str

    **Known IDs:**

    .. list-table::
        :widths: 30 30 30 30
        :header-rows: 1

        *   - timetableEntryTypeId
            - timetableEntryType
            - timetableEntryTypeLong
            - timetableEntryTypeShort

        *   - 1
            - lesson
            - lesson
            - lesson

        *   - 11
            - substitution
            - canceled lesson
            - cancel

        *   - 12
            - substitution
            - block substitution
            - block

        *   - 15
            - substitution
            - holiday
            - holiday

        *   - 16
            - lesson
            - modified lesson
            - modlesson

    .. attribute:: messageId
        :type: int

        Id of the attribute ``message`` below

    .. attribute:: message
        :type: str

        Message by the Intranet. Some examples might be:

        - "Exkursion"
        - "Gesamtkonvent, Aula"
        - "Instrumentalunterricht findet statt!"

    .. attribute:: output
        :type: str

        Is either a newline or "None"

    .. attribute:: title
        :type: str

        Title of the lesson, some examples are "E", "F" or "M"

    .. attribute:: halfClassLesson
        :type: unknown/None

    .. attribute:: courseId
        :type: int

        Id of the course.

    .. attribute:: courseName
        :type: str

        Name of the course. Examples are "Ch", "D", "E" and "Sp"

    .. attribute:: course
        :type: str

        Long name of the course. Some examples are:

        - "Biologie, SP DjTj (4x )"
        - "Deutsch, GF DjTj (4x )"
        - "Mathematik, GF DjTj (4x )"

    .. attribute:: courseLong
        :type: str

        Empty string

    .. attribute:: isExamLesson
        :type: bool

        Always ``False`` even if lesson contains an exam

    .. attribute:: isCheckedLesson
        :type: bool

        Always ``False`` even if lesson is checked

    .. attribute:: lessonAbsenceCount
        :type: int

        Amount of absent people during the lesson

    .. attribute:: subjectId
        :type: int

        .. list-table::
            :widths: 30 30
            :header-rows: 1

            *   - ``subjectId``
                - ``subjectName``

            *   - 0
                - None

            *   - 1
                - Deutsch

            *   - 2
                - Französisch

            *   - 4
                - Englisch

            *   - 9
                - Mathematik

            *   - 12
                - Chemie

            *   - 13
                - Biologie

            *   - 15
                - Geschichte

            *   - 16
                - Einführung in Wirtschaft und Recht

            *   - 23
                - Sport

            *   - 24
                - Informatik

            *   - 37
                - Klassenstunde

            *   - 3, 5, 6, 7, 8, 10, 11, 14, 17-22, 25-36
                - unknown

    .. attribute:: subjectName
        :type: str

        Name of the subject

    .. attribute:: timegridId
        :type: int

    .. attribute:: classId
        :type: list[int]

        Id of the class. If it is a block, it contains multiple ids
        Can be mapped to className, as they directly correspond with each other.

        ex: ``classId`` "1618" belongs to ``className`` "4e"

    .. attribute:: className
        :type: str

        Name of the class. If there are multiple, they are sorted like "4a, 4b, 4c"
        Can be mapped to classId, as they directly correspond with each other.

        ex: ``classId`` "1618" belongs to ``className`` "4e"

    .. attribute:: profileId
        :type: int

        Profile Id

    .. attribute:: teamId
        :type: str

        Empty string

    .. attribute:: teacherId
        :type: list[int]

    .. attribute:: teacherAcronym
        :type: str

    .. attribute:: teacherFullName
        :type: list[str]

    .. attribute:: teacherLastName
        :type: str

        Empty string

    .. attribute:: teacherFirstName
        :type: str

        Empty string

    .. attribute:: connectedTeacherId
        :type: list[int]

    .. attribute:: connectedTeacherFullName
        :type: str

    .. attribute:: student
        :type: list[:class:`student`]

    .. attribute:: studentId
        :type: int

    .. attribute:: studentFullName
        :type: str

        Empty string

    .. attribute:: studentFirstname
        :type: str

        Empty string

    .. attribute:: roomId
        :type: list[int]

    .. attribute:: roomName
        :type: str

    .. attribute:: locationDescription
        :type: str

    .. attribute:: resourceId
        :type: list

    .. attribute:: timetableClassBookId
        :type: int

    .. attribute:: hasHomework
        :type: bool

    .. attribute:: hasHomeworkFiles
        :type: bool

    .. attribute:: hasExam
        :type: bool

        Whether the lesson is an exam lesson. As of 16/09/21, this is false even if there is an exam. The only way to check whether there is an exam is if the string "(!)" is contained in lesson.title

    .. attribute:: hasExamFiles
        :type: bool

    .. attribute:: privileges
        :type: unknown/None

    .. attribute:: resource
        :type: unknown/None

    .. attribute:: reservedResources
        :type: int

    .. attribute:: totalStock
        :type: int

    .. attribute:: school
        :type: str

    .. attribute:: relatedId
        :type: list[str]

The student object
-------------------
This object contains attributes constructed directly from an intranet response
Each student object represents a student and thereby its attributes.
The following attributes are documented, but may change at any time without notice


.. class:: student

    .. attribute:: studentId
        :type: int

    .. attribute:: studentName
        :type: str

The ClassMate object
--------------------
This object contains attributes constructed directly from an intranet response
Each object represents a student and thereby its attributes.
The following attributes are documented, but may change at any time without notice

.. class:: ClassMate

    .. attribute:: EMail
        :type: str

        Email of a student

    .. attribute:: Klasse
        :type: str

        Class the student is in

    .. attribute:: Mobile
        :type: str

        Phone number of student

    .. attribute:: Name
        :type: str

        Last name of student

    .. attribute:: PersonID
        :type: str

        Same as the studentId from :class:`student`, may possibly be used to request their timetable?

    .. attribute:: Telefon
        :type: str

        Phone number of student

    .. attribute:: Vorname
        :type: str

        First name of student

    .. attribute:: zust_SL
        :type: str

        responsible schoolmanager

The teacher object
--------------------
This object contains attributes constructed directly from an intranet response
Each object represents a student and thereby its attributes.
The following attributes are documented, but may change at any time without notice

.. class:: teacher

    .. attribute:: Adresse
        :type: str

        Address of teacher

    .. attribute:: CourseID
        :type: str

        Id of the course the teacher is responsible for

    .. attribute:: Email
        :type: str

        Email of the teacher

    .. attribute:: EndDate
        :type: str

        Date as DD.MM.YYYY

    .. attribute:: Kurs
        :type: str

        Name of the teachers course

    .. attribute:: Name
        :type: str

        Last name of the teacher

    .. attribute:: PLZOrt
        :type: str

        Place and Postcode of teacher

    .. attribute:: PersonID
        :type: str

        Id of teacher

    .. attribute:: StartDate
        :type: str

        Date as DD.MM.YYYY

    .. attribute:: Telefon
        :type: str

        Phone number of teacher

    .. attribute:: Vorname
        :type: str

        First name of teacher

