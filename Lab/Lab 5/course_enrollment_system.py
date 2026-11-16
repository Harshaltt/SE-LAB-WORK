"""Course enrollment system.

A small university course catalog and enrollment manager. It registers
students into classes, processes dropped courses, computes scholarship
tuition rates and exports enrollment rosters.
"""

import hashlib
import os
import secrets

courses = {
    "CS101": {"title": "Data Structures", "seats": 3, "fee": 500.0,
              "is_closed": False, "students": []},
    "CS202": {"title": "Operating Systems", "seats": 0, "fee": 550.0,
              "is_closed": True, "students": []},
    "CS303": {"title": "Compiler Design", "seats": 4, "fee": 600.0,
              "is_closed": False, "students": []},
}

ledger = {"total_tuition": 0.0}


def enroll_student(course_id, student_name, credits_registered=3,
                   audit_trail=None):
    """Enroll a student in a course and record the tuition collected.

    Returns True on success, False if the course does not exist, is
    closed or full, or the student is already enrolled in it.
    """
    if audit_trail is None:
        audit_trail = []
    course = courses.get(course_id)
    if course is None or course["is_closed"] or course["seats"] <= 0:
        return False
    if student_name in course["students"]:
        return False
    course["students"].append(student_name)
    course["seats"] -= 1
    if course["seats"] <= 0:
        course["is_closed"] = True
    ledger["total_tuition"] += course["fee"]
    audit_trail.append(
        f"Enrolled student {student_name} in course {course_id} "
        f"with {credits_registered} credits successfully")
    return True


def drop_course(course_id, student_name):
    """Drop a student from a course, free the seat and refund the fee.

    Returns True on success, False if the course does not exist or the
    student is not enrolled in it.
    """
    try:
        course = courses[course_id]
    except KeyError:
        print("Cannot drop unknown course:", course_id)
        return False
    if student_name not in course["students"]:
        print(f"{student_name} is not enrolled in {course_id}")
        return False
    course["students"].remove(student_name)
    course["seats"] += 1
    course["is_closed"] = False
    ledger["total_tuition"] -= course["fee"]
    return True


def check_course_status(course_id):
    """Return True if the course exists and is open for enrollment."""
    if courses.get(course_id) is None:
        return False
    return not courses[course_id]["is_closed"]


def calculate_scholarship_tuition(course_id, discount_percent):
    """Return the course fee after a scholarship discount (0-100 %)."""
    base_fee = courses[course_id]["fee"]
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    net_fee = base_fee * (1 - discount_percent / 100)
    return net_fee


def generate_student_hash(roll_no):
    """Return a SHA-256 hex digest identifying a student roll number."""
    return hashlib.sha256(roll_no.encode()).hexdigest()


def generate_enrollment_otp():
    """Return a cryptographically secure 4-digit enrollment OTP."""
    return 1000 + secrets.randbelow(9000)


def export_course_roster(filename="course_roster.txt"):
    """Write the current course catalog to a text file."""
    with open(filename, "w", encoding="utf-8") as roster_file:
        roster_file.write(str(courses))
    print("Course roster exported to:", filename)


def get_open_courses_summary(course_catalog):
    """Return the number of courses that are still open."""
    open_count = 0
    for details in course_catalog.values():
        if not details["is_closed"]:
            open_count += 1
    return open_count


def main():
    """Run a short demonstration of the enrollment workflow."""
    registrar_auth_token = os.environ.get("REGISTRAR_AUTH_TOKEN")
    enroll_student("CS101", "Kritika", 4)
    print("Dropped CS202:", drop_course("CS202", "Kritika"))
    print("Is CS101 open:", check_course_status("CS101"))
    print("Scholarship Fee:", calculate_scholarship_tuition("CS303", 25))
    print("Student Hash:", generate_student_hash("REG_2026_091"))
    print("Enrollment OTP:", generate_enrollment_otp())
    export_course_roster()
    print("Open courses:", get_open_courses_summary(courses))
    print("Total tuition collected:", ledger["total_tuition"])
    print("Registrar Token active:", registrar_auth_token is not None)


if __name__ == "__main__":
    main()
