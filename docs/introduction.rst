Introduction
=============

This is an introduction guide for OpenTamPy, a high-level API wrapper, written in :py: , designed to help in the creation of scripts that use data of the intranet.tam.ch.

Prerequisites
-------------

OpenTamPy works best with Python 3.9 and higher. Lower versions may work, but support is not guaranteed.

Installation guide
--------------------

This is a guide to install the library with `pip <https://pypi.org/project/pip/>`_

On Windows:

.. code-block:: shell

    $ py -3 -m pip install OpenTamPy

On other systems:

.. code-block:: shell

    $ python3 -m pip install OpenTamPy

If you're installing from source, to install all dependencies run the following command:

On Windows:

.. code-block:: shell

    $ py -3 -m pip install requirements.txt

On other systems:

.. code-block:: shell

    $ python3 -m pip install requirements.txt


A basic script
---------------

Simple example that fetches all lessons for the current week and prints their abbreviation

Save this as ``example.py``

.. code-block:: python3

    from OpenTamPy import Intranet

    username = "YOURUSERNAME"
    password = "YOURPASSWORD"
    school = "krm"

    instance = Intranet(username, password, school)
    timetable = instance.get_timetable()
    for lesson in timetable:
        print(lesson.courseName)

Lets walk through this:

1. The first line imports the package. If this raises a ``ModuleNotFoundError`` or an ``ImportError``, please make sure you have the library correctly installed
2. After this set the ``username`` and the ``password`` variable by replacing said strings. The schoolcode can be found as part of the URL. An example would be ``https://intranet.tam.ch/krm/``, ``krm`` would be the schoolcode
3. Initiate an instance of the Intranet class by calling the class with your authentication details. `instance` is now a `Intranet` object from which all of the libraries functions will be called. This object contains all the relevant information to communicate with the intranet.
4. Fetch the whole timetable for the current week. You could also pass arguments into the getTimetable function to specify the range of what should be returned
5. Iterate over the list of lessons and print the wanted attribute.

Now run the script with the following command:

On Windows:

.. code-block:: shell

    $ py -3 example.py

On other systems:

.. code-block:: shell

    $ python3 example.py