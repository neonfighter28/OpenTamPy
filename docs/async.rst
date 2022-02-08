Async
----------------------

OpenTamPy contains an async wrapper for each function documented below
Note that these don't increase performance, but simply wrap a function to call them asynchronously

Quick example of the usage of async:

.. code-block:: python3

    import asyncio
    from OpenTamPy import AsyncClient

    async def main():
        username = "YOURUSERNAME"
        password = "YOURPASSWORD"

        instance = AsyncClient(username, password)
        timetable = await instance.get_timetable()

        for lesson in timetable:
            print(lesson.courseName)

    asyncio.run(main())

.. class:: AsyncClient(username, password, school, debug=False)

    This is the base class from where you can call all the libraries async functions from. To be able to do this, you need to create an instance of this class first.

    :param username: Your Intranet username. This is only used for authentication purposes
    :type username: str
    :param password: Your Intranet password. This is only used for authentication purposes
    :type password: str
    :param school: Your schoolcode. Ex: ``krm`` for MNG, ``krr`` for RGZH. Can be found in the URL. Ex: In ``https://intranet.tam.ch/krm/``, where ``krm`` would be the schoolcode
    :type school: str
    :param debug: Whether logging should be set to debug. Defaults to False
    :type debug: bool

    .. function:: get_timetable(start_date=0, end_date=0, user_id=None)
        :async:

        :param start_date: Start of the timebracket as 'DD.MM.YY', defaults to last monday
        :type start_date: int
        :param end_date: End of the timebracket as 'DD.MM.YY', defaults to next sunday
        :param user_id: Fetch timetable for any student with the given Id
        :param timeout: Passed through to the request, increase if you request large amounts of data, as it might take longer to process than the default.
        :type timeout: int

        It is possible to fetch someone elses timetable if you only have their studentID, which can be acquired by running `get_class_mates`. Whether this is intentional or not is unclear, so this might be removed at any time

        :yield: :class:`lesson`

    .. function:: get_absences()
        :async:

        This function fetches a list of all absences and returns an Iterator containing objects from which you can get information very easily.

        .. code-block:: python3

            instance = Intranet(username, password)
            absence_iterator = instance.getAbsences()
            for absence in absence_iterator:
                print("Name of teacher", absence.Lehrperson)

        :return: :class:`absence`

    .. function:: get_lesson_absence_data(lesson)
        :async:

        This function fetches the absence data corresponding to the :class:`lesson` passed through
        You can also pass through a list of :class:`lesson` objects, and the function will return a list of the corresponding values

        :param lesson: :class:`lesson`

    .. function:: get_class_mates()
        :async:

        This function fetches a list of each classMate and yields it back

        :yield: :class:`ClassMate`

    .. function:: get_class_teachers()
        :async:

        This function fetches a list of each teacher and yields it back

        :yield: :class:`teacher`

    .. function:: set_homework_data(lesson, title, description)
        :async:

        :param title: Title for absence to be set
        :type title: str
        :param description: Description for absence to be set
        :type description: str
        :raise MissingPermission: Not enough permissions

        Set homework data for passed through lesson, returns new homework data

    .. function:: delete_homework_info(lesson)
        :async:

        :param lesson: Lesson object for which the absence should be deleted
        :raise MissingPermission: Not enough permissions

        Deletes all homework associated with that lesson
