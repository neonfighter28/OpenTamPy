# OpenTamPy

[![Documentation Status](https://readthedocs.org/projects/opentampy/badge/?version=latest)](https://opentampy.readthedocs.io/?badge=latest)
![build](https://github.com/neonfighter28/OpenTamPy/actions/workflows/main.yml/badge.svg)

## A Python Library to simplify the access to the [Intranet](https://intranet.tam.ch/) website

[Full Documentation](https://opentampy.readthedocs.io/)

Example snippet, more can be found in the documentation as well as in [examples](https://github.com/neonfighter28/OpenTamPy/tree/master/examples)/

```python
from OpenTamPy import Intranet

    username = "YOURUSERNAME"
    password = "YOURPASSWORD"
    school = "krm"

    instance = Intranet(username, password, school)
    timetable = instance.get_timetable()
    for lesson in timetable:
        print(lesson.courseName)
```
## Requirements

>Python 3.10<

>requests

>beautifulsoup4

>pillow

>munch

## Development

### Installing with pip

`python3 -m pip install OpenTamPy`

### Installing from source

1. Clone the repo from [https://github.com/neonfighter28/OpenTamPy](https://github.com/neonfighter28/OpenTamPy)
2. Install dependencies from requirements.txt with `pip install -r requirements.txt`

### Check typehints and pep8

Please make sure your PR is pep8 compliant. More about pep8 can be found [here](https://pep8.org/)

1. Make sure you have ``mypy`` and ``pycodestyle`` installed
2. run ``mypy ./src/OpenTamPy.py``
3. run ``pycodestyle OpenTamPy.py --max-line-length=119``

### Pushing to GitHub

1. Fork the project
2. Commit your changes
3. Create a Pull Request
