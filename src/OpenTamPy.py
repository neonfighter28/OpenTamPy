import calendar
import datetime
import json
import logging
import re
from functools import cache
from typing import Any, Dict, Generator, List, Tuple

from PIL import Image, JpegImagePlugin
import io
import base64

import munch
import requests
from bs4 import BeautifulSoup  # type: ignore

class Munch(munch.Munch):
    """
    Override factory to allow for hashing of munch objects
    """
    def __hash__(self):
        return hash(frozenset(self.toDict()))


def munchify(x):
    """
    Override munchify to use new Munch class defined before
    """
    return munch.munchify(x, factory=Munch)


# Exceptions
class OpenTamPyException(Exception):
    """Base exception for this library"""


class IntranetConnectionError(OpenTamPyException):
    """Could not connect to server"""


class FailedRequest(OpenTamPyException):
    """Request returned error code"""


class AuthenticationError(OpenTamPyException):
    """Could not authenticate"""


class WrongWebpageReturned(OpenTamPyException):
    """Intranet returned default page, that cannot be parsed"""


class UserIdNotMatching(OpenTamPyException):
    """couldn't find matching PersonID to userId"""


class BadStatusCode(OpenTamPyException):
    """Intranet returned bad status code"""


class BadTimestamp(OpenTamPyException):
    """Bad timestamp. Make sure your timestamp is UNIX-like"""


class MissingPermission(OpenTamPyException):
    """Not high enough permission"""


_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:87.0) \
    Gecko/20100101 Firefox/87.0'
}
_HEADERS_XMLREQUEST = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:87.0) \
    Gecko/20100101 Firefox/87.0',
    'X-Requested-With': 'XMLHttpRequest'
}

_BASE_URL = "https://intranet.tam.ch/"

# Global regexes

# lookbehind -> csrfToken.=.\' and grabs the next word
_REGEX_CSRFTOKEN = r"(?<=csrfToken=\')\w+"
# All characters between curly braces after string gridDataAndConfiguration,
# matches some whitespaces at the end
_REGEX_ABSENCES = \
    r"(?<=gridDataAndConfiguration:){.*},front"

# Logger settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

logging.getLogger("requests.packages.urllib3").setLevel(logging.ERROR)

_FORMAT = '%(asctime)-5s %(levelname)s | %(funcName)30s | %(message)s'
logging.basicConfig(format=_FORMAT, datefmt="%H:%M:%S")


@cache
def _get_mon_and_sun() -> Tuple[str, str]:
    """Get the month and Sun of the current week.

    Returns:
        str, str: UNIX timestamp of previous monday/sunday
    """

    today = datetime.date.today()
    diff = today.weekday()
    # todays date - todays weekday = monday of current week
    prev_mon = str((calendar.timegm(
        (today - datetime.timedelta(diff)).timetuple()) - 7200)) + "000"
    # todays date - today as weekday + 7 = next sunday
    next_sun = f"{int(prev_mon) + 691200}000"
    logger.debug("%s", f"Monday: {prev_mon}, Sunday: {next_sun}")
    return prev_mon, next_sun


def _match_username_to_user_id(username: str, students: List[Any]) -> int:
    """Attempt to match the username in the student's personId .

    Args:
        username (str): username passed to init
        students (List[Any]): list of students from get_resources()

    Returns:
        int: user_id
    """
    # assuming format of every username is FIRSTNAME.LASTNAME
    firstname, lastname = username.split(".")
    for i in students:
        # if "lastname, firstname" equals the personId in the same format
        if f"{lastname.lower().strip()}, {firstname.lower().strip()}" == i.name.lower():
            return i.personId
    logger.error("Couldn't match username to personId")
    raise UserIdNotMatching()


def _verify_response_code(name, response):
    """Wrapper to check response code and return same object

    Args:
        name (str): Name of endpoint getting called
        response: requests.response object

    Raises:
        AssertionError: Response code was not ok

    Returns:
        requests.response: same object as passed through
    """
    assert response.ok, f"Error {response.status_code}"

    logger.debug("%s", f"Endpoint: {name:<25}| {response.status_code = :>4}")
    return response


class Intranet:
    """
    Class method for creating Intranet.
    """

    def __init__(self, username: str,
                 password: str, schoolcode: str, debug=False) -> None:
        """Initialize the session .

        Args:
            username (str): username for the intranet
            password (str): password for the intranet
            schoolcode (str): examples: "krm" for MNG, "krr" for RGZH
            debug (bool, optional): Defaults to False.
            no_cache (bool, optional): Whether caching should be disabled. Defaults to False

        Raises:
            IntranetConnectionError: Connection failure
        """
        _DEBUG = bool(debug)
        if _DEBUG:
            logger.setLevel(logging.DEBUG)

        self._BASE_URL = _BASE_URL + schoolcode + "/"

        self.username = username
        self.password = password
        self.session = requests.Session()

        logger.debug("%s", f"Username set to: {self.username}")
        logger.debug("%s", "Password has been set")
        logger.debug("%s", f"URL has been set to {self._BASE_URL}")

        # Authentication
        try:
            response = _verify_response_code(
                "base-url", self.session.get(_BASE_URL)
            )
            soup = BeautifulSoup(response.content, 'html.parser')
            self._hash = soup.input['value']
        except Exception:
            raise IntranetConnectionError("Cannot connect to server, exiting")

        logger.debug("%s", f"{self._hash = }")

        # Authenticating with Intranet
        _verify_response_code("authentication", self.session.post(
            self._BASE_URL,
            headers=_HEADERS,
            data={
                'hash': f'{self._hash}',
                'loginschool': f'{schoolcode}',
                'loginuser': f'{username}',
                'loginpassword': f'{password}'
            },
            timeout=20
        ))

        classbook_response = _verify_response_code(
            "classbook_response",
            self.session.get(
                f"{self._BASE_URL}timetable/classbook",
                headers=_HEADERS
            )
        )

        self._csrf_token = re.search(
            pattern=_REGEX_CSRFTOKEN,
            string=str(classbook_response.content.decode())
        ).group()  # type: ignore
        self.resources = self.get_resources()
        self.user_id = _match_username_to_user_id(
            self.username, self.resources.students)

        logger.debug("%s", "Init passed")
        logger.debug("%s", f"{self._csrf_token = }")
        logger.debug("%s", f"{self.user_id = }")

    @cache
    def get_resources(self) -> Munch:
        """
        Gets various resources from the Intranet

        Raises:
            AuthenticationError: Could not authenticate

        Returns:
            [munch.Munch]: Object to call attributes from
        """

        response = _verify_response_code(
            "get-resources",
            self.session.post(
                f"{self._BASE_URL}timetable/ajax-get-resources",
                headers=_HEADERS_XMLREQUEST,
                data={
                    "periodId": "75",
                    "csrfToken": self._csrf_token
                }
            )
        )

        try:
            return munchify(response.json()['data'])
        except json.decoder.JSONDecodeError:
            raise AuthenticationError("Could not authenticate")

    @cache
    def get_timetable(self, start_date=0, end_date=0, user_id=None,
                      timeout=20) \
            -> Generator[Munch, Dict[str, Any], None]:
        """Get the timetable.

        Args:
            start_date (int, optional): Unix timestamp of start date, in ms. Defaults to 0.
            end_date (int, optional): Unix timestamp of end date, in ms. Defaults to 0.
            user_id (int, optional): User id of student to fetch timetable for. Defaults to None.
            timeout (int, optional): Timeout for the request. Defaults to 20.

        Raises:
            BadTimestamp: UNIX timestamp is bad
            AssertionError: Intranet returned a bad status code | start_date is before end_data

        Yields:
            [munch.Munch]: Object to call attributes from
        """

        # If the user inputs a custom uid, dont overwrite the old one
        if user_id is None:
            user_id = self.user_id

        logger.debug("%s", f"get_timetable() called, using {user_id = }")

        # Logic for getting start as well as endDate
        start_date = str(start_date)
        end_date = str(end_date)
        if start_date == '0' and end_date == '0':
            start_date, end_date = _get_mon_and_sun()
        else:
            try:
                time = datetime.datetime.strptime(start_date, "%d.%m.%y")
                start_date = int(time.timestamp())*1000
                time = datetime.datetime.strptime(end_date, "%d.%m.%y")
                end_date = int(time.timestamp())*1000
                try:
                    assert start_date < end_date  # Verify that startdate is before enddate
                except AssertionError:
                    logger.fatal("%s", "startdate needs to be before enddate")
            except ValueError:
                raise BadTimestamp(
                    f"Bad timestamp, format needs to be 'DD.MM.YY'. ({start_date = }, {end_date = })"
                )

        logger.debug("%s", f"{start_date = }")
        logger.debug("%s", f"{end_date = }")

        # Request to get timetable, aswell as loading it
        logger.debug("%s", "requesting timetable...")
        response = _verify_response_code(
            "ajax-get-timetable",
            self.session.post(
                f"{self._BASE_URL}timetable/ajax-get-timetable",
                headers=_HEADERS_XMLREQUEST,
                data={
                    'startDate': f'{start_date}',
                    'endDate': f'{end_date}',
                    'studentId[]': f'{user_id}',
                    'holidaysOnly': '0'
                },
                timeout=timeout
            )
        )

        data = response.json()

        # Logic to choose return type, aswell as to verify status code
        assert data['status'] == 1, f"Bad status code ({data['status']})"

        for lesson in data['data']:
            yield munchify(lesson)

    @cache
    def get_absences(self) -> Generator[Munch, Dict[str, Any], None]:
        """
        Get the absences of the current user .

        Yields:
            [munch.Munch]: Object to call attributes from
        """

        # Requesting all absences
        response = _verify_response_code(
            "absence-data",
            self.session.get(
                f"{self._BASE_URL}list/index/list/112",
                headers=_HEADERS
            )
        )

        # Matching for regex
        data = json.loads(
            re.search( # type: ignore
                _REGEX_ABSENCES,
                str(response.content)
            ).group()[:-6].replace("\\\\", "\\")
        )['data']['data']  # type: ignore

        for obj in data:
            yield munchify(obj)

    @cache
    def _get_lesson_absence_data(self, lesson: Munch) -> Dict[str, Any]:
        """Get the absence data for a given lesson

        Args:
            lesson: lesson to get absence data for

        Raises:
            UserIdNotMatching: UserID doesn't exist
            WrongWebpageReturned: Intranet returned the wrong webpage

        Returns:
            dict: returns a dictionary with information for the timetable
        """

        logger.debug("%s", "get_lesson_absence_data called")

        # create prepared_name as the following: "Name, +Vorname" for userId of
        # self
        prepared_name = None
        for i in self.get_class_mates():
            if str(self.user_id) == str(i.PersonID):
                prepared_name = i.Name + ",+" + i.Vorname

        assert prepared_name is not None, "Couldn't find matching PersonID to user_id\
             while trying to create prepared_name"
        logger.debug("%s", f"{prepared_name = }")

        absence_data = _verify_response_code(
            "absence-data-lesson",
            self.session.post(
                f"{self._BASE_URL}timetable/ajax-get-lesson-students-absence-data",
                headers=_HEADERS_XMLREQUEST,
                data={
                    "timetableId": f"{lesson.id}",
                    "CourseId": f"{lesson.courseId}",
                    "Date": f"{lesson.lessonDate}",
                    "StartTime": f"{lesson.lessonStart}",
                    "EndTime": f"{lesson.lessonEnd}",
                    "Students[0][studentId]": f"{self.user_id}",
                    "Students[0][studentName]": f"{prepared_name}",
                    "csrfToken": f"{self._csrf_token}"
                }
            )
        )

        try:
            return json.loads(
                str(absence_data.content)[2:-1]
                .replace("\\\\", "\\")
            )

        except json.decoder.JSONDecodeError:
            raise WrongWebpageReturned(
                "Intranet returned reauth page. This is likely an authentication error"
            )

    @cache
    def get_lesson_absence_data(self, lesson: Munch) -> List[Munch] | Dict[str, Any]:
        """
        Returns a list of absence data for a given lesson .

        Args:
            lesson: lesson to get absence data for

        Returns:
            list: returns a list of 'munch.Munch' objects, if a list was passed through
            munch.Munch: returns an object to call attributes from
        """

        # if multiple lessons get passed through as a list, return list
        if isinstance(lesson, list):
            return [munchify(self._get_lesson_absence_data(obj)) for obj in lesson]
        else:
            return self._get_lesson_absence_data(lesson)

    @cache
    def get_additional_homework_info(self, lesson) -> Munch:
        """
        Get the extra Homework Info for a given lesson .

        Args:
            lesson: Lesson to get Homework Info for

        Returns:
            munch.Munch: object to call attributes from
        """

        logger.debug(
            "%s", "called get_additional_homework_info, trying to reach inet")

        response = _verify_response_code(
            "homework-data",
            self.session.post(
                f"{self._BASE_URL}timetable/ajax-get-lesson-home-work-data",
                headers=_HEADERS_XMLREQUEST,
                data={
                    "timetableClassBookId": f"{lesson.courseId}",
                    "csrfToken": f"{self._csrf_token}"
                }
            )
        )

        return munchify(response.json()['data'])

    def set_homework_data(self, lesson: Munch, title: str, description: str) -> Munch:
        """
        Sets the HomeworkData for the given lesson.

        Args:
            lesson: lesson to set Homeworkdata for
            title (str): title to be set
            description (str): description to be set

        Raises:
            MissingPermission: Permissions aren't high enough to set Homework data

        Returns:
            munch.Munch: Object to call attributes from
        """

        response = _verify_response_code(
            "ajax-save-lesson-home-work-data",
            self.session.post(
                f"{self._BASE_URL}timetable/ajax-save-lesson-home-work-data",
                headers=_HEADERS_XMLREQUEST,
                data={
                    "timetableClassBookId": f"{lesson.classId[0]}",
                    "timetableId": f"{lesson.id}",
                    "homeWorkData[title]": f"{title}",
                    "homeWorkData[description]": f"{description}",
                    "csrfToken": f"{self._csrf_token}"
                }
            )
        )

        content = munchify(response.json())

        # Intranet will return empty list if permissions aren't high enough
        assert content.data != [], "Missing permissions"
        return content

    def get_person_picture(self, studentid: int | str = None) -> JpegImagePlugin.JpegImageFile:
        """Gets the student picture

        Args:
            studentid (int | str, optional): student_id to fetch the profile picture for. Defaults to None.

        Returns:
            PIL.JpegImagePlugin.JpegImageFile: Profile Picture of student
        """
        studentid = self.user_id if studentid == None else studentid
        response = self.session.post(
            f"{self._BASE_URL}list/get-person-picture",
            headers=_HEADERS_XMLREQUEST,
            data={
                "person": studentid,
                "csrfToken": self._csrf_token
            }
        )
        return Image.open(io.BytesIO(base64.b64decode(response.content)))

    def delete_homework_info(self, lesson: Munch) -> Munch:
        """
        Deletes the homework info for a lesson.

        Args:
            lesson: Lesson to delete homeworkdata for

        Returns:
            munch.Munch: New homeworkdata for the lesson
        """

        return self.set_homework_data(lesson, "", "")

    @cache
    def get_class_mates(self) -> Generator[Munch, Dict[str, Any], None]:
        """
        Get all class Mates.

        Yields:
            munch.Munch: Object to call attributes from. Contains information for classmate
        """

        logger.debug("%s", "called get_class_mates")

        response = self.session.get(
            f"{self._BASE_URL}list/index/list/45",
            headers=_HEADERS
        )
        _verify_response_code("get-class-mates", response)
        # extracting json
        data = json.loads(
            re.search(_REGEX_ABSENCES, str(response.content)) # type: ignore
            .group()[:-6]
            .replace("\\\\", "\\")
        )['data']['data']

        logger.debug("%s", "got response and matched regex, \
                        appending to cache and returning...")

        for obj in data:
            yield munchify(obj)

    @cache
    def get_class_teachers(self) -> Generator[Munch, Dict[str, Any], None]:
        """
        Get a list of classTeacher objects from the Intranet

        Yields:
            munch.Munch: object to call attributes from
        """

        logger.debug("%s", "called get_class_teachers, trying to reach inet")

        response = _verify_response_code(
            "get-class-teachers",
            self.session.get(
                f"{self._BASE_URL}list/index/list/46",
                headers=_HEADERS
            )
        )

        content = re.search(
            _REGEX_ABSENCES,
            str(response.content.decode())
        ).group()[:-6]  # type: ignore
        # json is double-escaped, remove excess backslashes
        content = json.loads(str(content).replace("\\\\", "\\"))[
            'data']['data']
        logger.debug("%s", "got response and matched regex, returning...")
        for obj in content:
            yield munchify(obj)

# Async support #


class AsyncClient():
    """
    Class Method to use async functions from
    """

    def __init__(self, *args, **kwargs) -> None:
        self.instance = Intranet(*args, **kwargs)

    async def get_timetable(self, *args, **kwargs) -> Generator[Munch, Dict[str, Any], None]:
        """
        Get the timetable

        Args:
            start_date (int, optional): Date as DD.MM.YY. Defaults to last monday.
            end_date (int, optional): Date as DD.MM.YY. Defaults to next sunday.
            user_id (int, optional): User id of student to fetch timetable for. Defaults to None.
            timeout (int, optional): Timeout for the request. Defaults to 20.

        Raises:
            BadTimestamp: UNIX timestamp is bad
            BadStatusCode: Intranet returned a bad status code

        Yields:
            [munch.Munch]: Object to call attributes from
        """
        return self.instance.get_timetable(*args, **kwargs)

    async def get_resources(self) -> Munch:
        """
        Gets various resources from the Intranet

        Raises:
            AuthenticationError: Could not authenticate

        Returns:
            [munch.Munch]: Object to call attributes from
        """
        return self.instance.get_resources()

    async def get_class_teachers(self, **kwargs) -> Generator[Munch, Dict[str, Any], None]:
        """
        Get a list of classTeacher objects from the Intranet

        Yields:
            munch.Munch: object to call attributes from
        """
        return self.instance.get_class_teachers(**kwargs)

    async def get_class_mates(self) -> Generator[Munch, Dict[str, Any], None]:
        """
        Get all classmates.

        Yields:
            munch.Munch: Object to call attributes from. Contains information for classmate
        """
        return self.instance.get_class_mates()

    async def get_absences(self) -> Generator[Munch, Dict[str, Any], None]:
        """
        Get the absences of the current user .

        Yields:
            [munch.Munch]: Object to call attributes from
        """
        return self.instance.get_absences()

    async def get_lesson_absence_data(self, *args) -> List[Munch] | Dict[str, Any]:
        """
        Returns a list of absence data for a given lesson .

        Args:
            lesson: lesson to get absence data for

        Returns:
            list: returns a list of 'munch.Munch' objects a list was passed through
            munch.Munch: returns an object to call attributes from
        """
        return self.instance.get_lesson_absence_data(*args)

    async def get_additional_homework_info(self, *args) -> Munch:
        """
        Get the extra Homework Info for a given lesson .

        Args:
            lesson: Lesson to get Homework Info for

        Returns:
            munch.Munch: object to call attributes from
        """
        return self.instance.get_additional_homework_info(*args)

    async def set_homework_data(self, *args, **kwargs) -> Munch:
        """
        Sets the HomeworkData for the given lesson .

        Args:
            lesson: lesson to set Homeworkdata for
            title (str): title to be set
            description (str): description to be set

        Raises:
            MissingPermission: Permissions aren't high enough to set Homework data

        Returns:
            munch.Munch: Object to call attributes from
        """
        return self.instance.set_homework_data(*args, **kwargs)

    async def delete_homework_info(self, *args) -> Munch:
        """
        Deletes the homework info for a lesson.

        Args:
            lesson: Lesson to delete Homeworkdata for

        Returns:
            munch.Munch: New Homeworkdata for the lesson
        """
        return self.instance.delete_homework_info(*args)


if __name__ == "__main__":
    logger.error("%s", "Do not run this as main")
