import frappe
import re
import hmac
import hashlib
import time
from frappe.utils import get_url, get_fullname, flt, cint, strip_html, cstr
from fuzzywuzzy import fuzz
import json

@frappe.whitelist(allow_guest=True)
def get_quiz_with_questions(quiz_name: str, include_answers: bool | str = False) -> dict:
    from frappe.utils import cint
    include_answers = cint(include_answers)
    
    # For security, only allow authenticated users to see answers
    if include_answers and frappe.session.user == "Guest":
        include_answers = False

    try:
        quiz = frappe.get_doc("LMS Quiz", quiz_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Quiz {quiz_name} not found", frappe.DoesNotExistError)
        
    quiz_dict = quiz.as_dict()
    
    # Map fields for compatibility with existing flutter model
    if "passing_percentage" in quiz_dict:
        quiz_dict["passing_score"] = quiz_dict["passing_percentage"]
    
    if "duration" in quiz_dict and quiz_dict["duration"]:
        try:
            # Convert minutes (LMS Quiz) to seconds (Flutter model)
            minutes = int(quiz_dict["duration"])
            quiz_dict["duration"] = minutes * 60
            quiz_dict["is_time_bound"] = 1 if minutes > 0 else 0
        except (ValueError, TypeError):
            quiz_dict["is_time_bound"] = 0
    else:
        quiz_dict["is_time_bound"] = 0

    questions = []
    
    # Use current request's host to ensure the client can reach it
    base_url = get_url()
    request = getattr(frappe.local, "request", None)
    if request and request.host:
        scheme = request.scheme or "http"
        base_url = f"{scheme}://{request.host}"
    
    for row in quiz.get("questions", []):
        if row.question:
            try:
                question = frappe.get_doc("LMS Question", row.question)
                q_dict = question.as_dict()
                
                # Format question HTML
                if q_dict.get("question"):
                    q_dict["question"] = expand_relative_urls(q_dict["question"], base_url)
                
                # Construct options list from option_1..4 fields
                q_dict["options"] = []
                for i in range(1, 5):
                    option_text = q_dict.get(f"option_{i}")
                    if option_text:
                        opt_dict = {
                            "name": f"Option {i}",
                            "option": expand_relative_urls(option_text, base_url),
                        }
                        if include_answers:
                            opt_dict["is_correct"] = q_dict.get(f"is_correct_{i}")
                            opt_dict["explanation"] = q_dict.get(f"explanation_{i}")
                        q_dict["options"].append(opt_dict)
                
                # Remove sensitive information like possibility_x, is_correct_x, and explanation_x if not requested
                if not include_answers:
                    for i in range(1, 5):
                        q_dict.pop(f"possibility_{i}", None)
                        q_dict.pop(f"is_correct_{i}", None)
                        q_dict.pop(f"explanation_{i}", None)

                # Map old question_type field
                if q_dict.get("type") == "Choices":
                    q_dict["question_type"] = "Multiple Correct Answer" if q_dict.get("multiple") else "Single Correct Answer"
                else:
                    q_dict["question_type"] = q_dict.get("type")

                questions.append(q_dict)
            except Exception:
                pass
                
    quiz_dict["questions"] = questions
    return quiz_dict


@frappe.whitelist()
def get_csrf_token() -> str:
    """
    Returns the current session's CSRF token.
    Whitelisted to allow Flutter client to fetch it after establishing a session.
    """
    return frappe.sessions.get_csrf_token()



@frappe.whitelist()
def get_program_courses() -> list[dict]:
    """
    Returns a list of published courses associated with a specific program.
    Used by the Flutter app to show courses filtered by user's selected program.
    """
    user = frappe.get_doc("User", frappe.session.user)
    program_name = user.get("selected_program")

    if not program_name:
        return []

    program_courses = frappe.get_all(
        "LMS Program Course",
        filters={"parent": program_name},
        pluck="course"
    )

    if not program_courses:
        return []

    courses = frappe.get_all(
        "LMS Course",
        filters={
            "name": ["in", program_courses],
            "published": 1
        },
        fields=["name", "title", "description", "short_introduction", "image", "category", "rating", "lessons", "enrollments"]
    )

    return courses

@frappe.whitelist()
def get_student_courses() -> list[dict]:
    """
    Returns a list of courses associated with the student's enrollments (direct or batch).
    Used by the Flutter app to show courses the user is enrolled in.
    """
    user = frappe.session.user
    
    # 1. Get courses from direct enrollments
    direct_courses = frappe.get_all(
        "LMS Enrollment",
        filters={"member": user},
        pluck="course"
    )
    
    # 2. Get batches the user is enrolled in
    enrolled_batches = frappe.get_all(
        "LMS Batch Enrollment",
        filters={"member": user},
        pluck="batch"
    )
    
    all_course_names = set(direct_courses)
    
    if enrolled_batches:
        # Get programs from these batches
        batches = frappe.get_all(
            "LMS Batch",
            filters={"name": ["in", enrolled_batches]},
            fields=["name", "program"]
        )
        
        programs = [b.program for b in batches if b.program]
        if programs:
            program_courses = frappe.get_all(
                "LMS Program Course",
                filters={"parent": ["in", programs]},
                pluck="course"
            )
            for c in program_courses:
                if c:
                    all_course_names.add(c)
            
        # Also check direct courses in Batch child table
        for batch_name in enrolled_batches:
            try:
                batch_doc = frappe.get_doc("LMS Batch", batch_name)
                if hasattr(batch_doc, "courses"):
                    for b_course in batch_doc.courses:
                        if b_course.course:
                            all_course_names.add(b_course.course)
            except Exception:
                pass

    if not all_course_names:
        return []

    # Get full course details
    # Note: We don't filter by 'published' here because if a student is enrolled,
    # they should have access regardless of public catalog status.
    courses = frappe.get_all(
        "LMS Course",
        filters={
            "name": ["in", list(all_course_names)]
        },
        fields=["name", "title", "description", "short_introduction", "image", "category", "rating", "lessons", "enrollments"]
    )

    return courses

@frappe.whitelist()
def get_course_details(course_name: str) -> dict:
    """
    Returns the full structure of an LMS Course including chapters and lessons.
    """
    try:
        course = frappe.get_doc("LMS Course", course_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Course {course_name} not found", frappe.DoesNotExistError)
        
    course_dict = course.as_dict()
    
    # Use current request's host for expanding URLs if needed
    base_url = get_url()
    request = getattr(frappe.local, "request", None)
    if request and request.host:
        scheme = request.scheme or "http"
        base_url = f"{scheme}://{request.host}"
        
    if course_dict.get("description"):
        course_dict["description"] = expand_relative_urls(course_dict["description"], base_url)

    chapters = []
    for row in course.get("chapters", []):
        if not row.chapter:
            continue
        try:
            chapter_doc = frappe.get_doc("Course Chapter", row.chapter)
            chapter_dict = {
                "name": chapter_doc.name,
                "title": chapter_doc.title,
                "lessons": []
            }
            
            for lesson_row in chapter_doc.get("lessons", []):
                if not lesson_row.lesson:
                    continue
                try:
                    lesson_doc = frappe.get_doc("Course Lesson", lesson_row.lesson)
                    chapter_dict["lessons"].append({
                        "name": lesson_doc.name,
                        "title": lesson_doc.title,
                        "youtube": lesson_doc.youtube,
                        "quiz_id": lesson_doc.quiz_id,
                        "body": lesson_doc.body,
                    })
                except Exception:
                    pass
            chapters.append(chapter_dict)
        except Exception:
            pass
    
    course_dict["chapters"] = chapters
    return course_dict


@frappe.whitelist()
def update_program_course_order(program_name: str, course_names: list | str) -> str:
    """
    Updates the order of courses in an LMS Program based on the list of course names provided.
    """
    if isinstance(course_names, str):
        course_names = json.loads(course_names)

    try:
        program = frappe.get_doc("LMS Program", program_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Program {program_name} not found", frappe.DoesNotExistError)

    new_courses = [{"course": course_name} for course_name in course_names]
    program.set("program_courses", new_courses)
    program.save(ignore_permissions=True)
    return "Success"


@frappe.whitelist()
def update_chapter_order(course_name: str, chapter_names: list | str) -> str:
    """
    Updates the order of chapters in an LMS Course based on the list of chapter names provided.
    """
    if isinstance(chapter_names, str):
        chapter_names = json.loads(chapter_names)

    try:
        course = frappe.get_doc("LMS Course", course_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Course {course_name} not found", frappe.DoesNotExistError)

    new_chapters = []
    for chapter_name in chapter_names:
        new_chapters.append({"chapter": chapter_name})

    course.set("chapters", new_chapters)
    course.save(ignore_permissions=True)
    return "Success"


@frappe.whitelist()
def update_lesson_order(chapter_name: str, lesson_names: list | str) -> str:
    """
    Updates the order of lessons in an LMS Chapter based on the list of lesson names provided.
    """
    if isinstance(lesson_names, str):
        lesson_names = json.loads(lesson_names)

    try:
        chapter = frappe.get_doc("Course Chapter", chapter_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Chapter {chapter_name} not found", frappe.DoesNotExistError)

    new_lessons = [{"lesson": lesson_name} for lesson_name in lesson_names]
    chapter.set("lessons", new_lessons)
    chapter.save(ignore_permissions=True)
    return "Success"


@frappe.whitelist()
def update_quiz_question_order(quiz_name: str, question_names: list | str) -> str:
    """
    Updates the order of questions in an LMS Quiz based on the list of question names provided.
    """
    if isinstance(question_names, str):
        question_names = json.loads(question_names)

    try:
        quiz = frappe.get_doc("LMS Quiz", quiz_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Quiz {quiz_name} not found", frappe.DoesNotExistError)

    new_questions = [{"question": q_name} for q_name in question_names]
    quiz.set("questions", new_questions)
    quiz.save(ignore_permissions=True)
    return "Success"


@frappe.whitelist()
def get_quiz_details(quiz_name: str) -> dict:
    """
    Returns quiz details with question text for each question.
    """
    try:
        quiz = frappe.get_doc("LMS Quiz", quiz_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Quiz {quiz_name} not found", frappe.DoesNotExistError)

    quiz_data = quiz.as_dict()
    
    # Include question text for each child
    for q_row in quiz_data.get("questions", []):
        if q_row.get("question"):
            # Get only the question field from LMS Question
            q_content = frappe.db.get_value("LMS Question", q_row["question"], "question")
            q_row["question_text"] = q_content or ""
            
    return quiz_data


@frappe.whitelist()
def get_courses_for_picker(
    search: str = "",
    program_name: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list:
    """
    Returns courses filtered by program with optional search.
    Accepts program_name as query param to avoid URL path issues with special characters.
    """
    course_names = None

    if program_name:
        try:
            program = frappe.get_doc("LMS Program", program_name)
            course_names = [row.course for row in program.get("program_courses", []) if row.course]
        except frappe.DoesNotExistError:
            return []

    filters: list = []
    if course_names is not None:
        if not course_names:
            return []
        filters.append(["name", "in", course_names])
    if search:
        filters.append(["title", "like", f"%{search}%"])

    courses = frappe.get_list(
        "LMS Course",
        fields=["name", "title", "published", "lessons"],
        filters=filters,
        limit_page_length=limit,
        limit_start=offset,
        order_by="creation desc",
    )
    return courses


@frappe.whitelist()
def get_all_chapters(
    search: str = "",
    course_name: str = "",
    program_name: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list:
    """
    Returns chapters filtered by course and/or program with optional search.
    Falls back to all chapters if no filter provided.
    """
    chapter_names = None

    if course_name:
        # Get chapters belonging to this specific course
        course = frappe.get_doc("LMS Course", course_name)
        chapter_names = [row.chapter for row in course.get("chapters", []) if row.chapter]
    elif program_name:
        # Get all courses in the program, then collect their chapters
        program = frappe.get_doc("LMS Program", program_name)
        course_names = [row.course for row in program.get("program_courses", []) if row.course]
        chapter_names = []
        for cname in course_names:
            try:
                course = frappe.get_doc("LMS Course", cname)
                chapter_names.extend([row.chapter for row in course.get("chapters", []) if row.chapter])
            except frappe.DoesNotExistError:
                continue

    filters: list = []
    if chapter_names is not None:
        if not chapter_names:
            return []
        filters.append(["name", "in", chapter_names])
    if search:
        filters.append(["title", "like", f"%{search}%"])

    chapters = frappe.get_list(
        "Course Chapter",
        fields=["name", "title"],
        filters=filters,
        limit_page_length=limit,
        limit_start=offset,
        order_by="creation desc",
    )
    return chapters


@frappe.whitelist()
def get_all_lessons(
    search: str = "",
    chapter_name: str = "",
    course_name: str = "",
    program_name: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list:
    """
    Returns lessons filtered by chapter, course, and/or program with optional search.
    """
    lesson_names = None

    if chapter_name:
        # Lessons in this specific chapter
        try:
            chapter = frappe.get_doc("Course Chapter", chapter_name)
            lesson_names = [row.lesson for row in chapter.get("lessons", []) if row.lesson]
        except frappe.DoesNotExistError:
            return []
    elif course_name:
        # Lessons in all chapters of this course
        try:
            course = frappe.get_doc("LMS Course", course_name)
            chapter_names = [row.chapter for row in course.get("chapters", []) if row.chapter]
            lesson_names = []
            for cname in chapter_names:
                try:
                    chapter = frappe.get_doc("Course Chapter", cname)
                    lesson_names.extend([row.lesson for row in chapter.get("lessons", []) if row.lesson])
                except frappe.DoesNotExistError:
                    continue
        except frappe.DoesNotExistError:
            return []
    elif program_name:
        # Lessons in all courses of this program
        try:
            program = frappe.get_doc("LMS Program", program_name)
            course_names = [row.course for row in program.get("program_courses", []) if row.course]
            lesson_names = []
            for crs_name in course_names:
                try:
                    course = frappe.get_doc("LMS Course", crs_name)
                    chapter_names = [row.chapter for row in course.get("chapters", []) if row.chapter]
                    for cname in chapter_names:
                        try:
                            chapter = frappe.get_doc("Course Chapter", cname)
                            lesson_names.extend([row.lesson for row in chapter.get("lessons", []) if row.lesson])
                        except frappe.DoesNotExistError:
                            continue
                except frappe.DoesNotExistError:
                    continue
        except frappe.DoesNotExistError:
            return []

    filters: list = []
    if lesson_names is not None:
        if not lesson_names:
            return []
        filters.append(["name", "in", lesson_names])
    if search:
        filters.append(["title", "like", f"%{search}%"])

    lessons = frappe.get_list(
        "Course Lesson",
        fields=["name", "title", "youtube", "quiz_id", "chapter"],
        filters=filters,
        limit_page_length=limit,
        limit_start=offset,
        order_by="creation desc",
    )
    return lessons


@frappe.whitelist()
def get_all_questions(
    search: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list:
    """
    Returns questions with optional search.
    """
    filters: list = []
    if search:
        filters.append(["question", "like", f"%{search}%"])

    questions = frappe.get_list(
        "LMS Question",
        fields=["name", "question", "type"],
        filters=filters,
        limit_page_length=limit,
        limit_start=offset,
        order_by="creation desc",
    )
    return questions


@frappe.whitelist()
def get_course_chapters(course_name: str) -> list:
    """
    Returns the list of chapters for a course in the correct order.
    """
    try:
        course = frappe.get_doc("LMS Course", course_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Course {course_name} not found", frappe.DoesNotExistError)

    chapters = []
    for row in course.get("chapters", []):
        if not row.chapter:
            continue
        try:
            chapter_doc = frappe.get_doc("Course Chapter", row.chapter)
            chapters.append({
                "name": chapter_doc.name,
                "title": chapter_doc.title,
                "lessons": [
                    {
                        "name": l.name,
                        "lesson": l.lesson,
                        "lesson_title": frappe.db.get_value("Course Lesson", l.lesson, "title"),
                        "idx": l.idx
                    }
                    for l in chapter_doc.get("lessons", []) if l.lesson
                ]
            })
        except frappe.DoesNotExistError:
            continue
            
    return chapters


@frappe.whitelist()
def get_course_lesson_details(lesson_name: str) -> dict:
    """
    Returns a course lesson with enough detail for the Flutter lesson screen.
    """
    try:
        lesson = frappe.get_doc("Course Lesson", lesson_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Lesson {lesson_name} not found", frappe.DoesNotExistError)

    base_url = get_url()
    request = getattr(frappe.local, "request", None)
    if request and request.host:
        scheme = request.scheme or "http"
        base_url = f"{scheme}://{request.host}"

    chapter_title = frappe.db.get_value("Course Chapter", lesson.chapter, "title")
    course_title = frappe.db.get_value("LMS Course", lesson.course, "title")

    body = lesson.body or ""
    content = lesson.content or ""
    instructor_notes = lesson.instructor_notes or ""
    question = lesson.question or ""

    return {
        "name": lesson.name,
        "title": lesson.title,
        "chapter": lesson.chapter,
        "chapter_title": chapter_title,
        "course": lesson.course,
        "course_title": course_title,
        "youtube": lesson.youtube,
        "quiz_id": lesson.quiz_id,
        "body": expand_relative_urls(body, base_url) if body else "",
        "content": expand_relative_urls(content, base_url) if content else "",
        "instructor_notes": expand_relative_urls(instructor_notes, base_url)
        if instructor_notes
        else "",
        "question": expand_relative_urls(question, base_url) if question else "",
    }


@frappe.whitelist()
def get_question_details(question: str) -> dict:
    """
    Returns the LMS Question details with all relative URLs in HTML fields expanded to signed absolute URLs.
    """
    try:
        doc = frappe.get_doc("LMS Question", question)
    except frappe.DoesNotExistError:
        frappe.throw(f"Question {question} not found", frappe.DoesNotExistError)

    q_dict = doc.as_dict()
    
    base_url = get_url()
    request = getattr(frappe.local, "request", None)
    if request and request.host:
        scheme = request.scheme or "http"
        base_url = f"{scheme}://{request.host}"

    # Expand relative URLs in all potential HTML fields
    html_fields = [
        "question",
        "option_1", "option_2", "option_3", "option_4",
        "explanation_1", "explanation_2", "explanation_3", "explanation_4",
        "possibility_1", "possibility_2", "possibility_3", "possibility_4"
    ]

    for field in html_fields:
        if q_dict.get(field):
            q_dict[field] = expand_relative_urls(q_dict[field], base_url)

    return q_dict


@frappe.whitelist()
def submit_quiz_result(
    quiz_name: str,
    results: list | str | None = None,
) -> dict:
    """
    Submits a quiz result by delegating to the LMS module's submit_quiz.
    This ensures all LMS-side effects (progress tracking, scoring) are preserved.
    """
    if not results:
        frappe.throw("Results are required for submission")
        
    if isinstance(results, str):
        results = json.loads(results)

    # Use custom submission logic to handle Text Editor fields and User Input correctly
    return custom_submit_quiz(quiz=quiz_name, results=results)

def custom_submit_quiz(quiz: str, results: list):
    from lms.lms.doctype.lms_quiz.lms_quiz import create_submission, save_progress_after_quiz
    
    quiz_details = frappe.db.get_value(
        "LMS Quiz",
        quiz,
        [
            "name",
            "total_marks",
            "passing_percentage",
            "lesson",
            "course",
            "enable_negative_marking",
            "marks_to_cut",
        ],
        as_dict=1,
    )

    data = custom_process_results(results, quiz_details)
    results = data["results"]
    score = data["score"]
    is_open_ended = data["is_open_ended"]

    score_out_of = quiz_details.total_marks
    percentage = (score / score_out_of) * 100 if score_out_of else 0
    submission = create_submission(quiz, results, score_out_of, quiz_details.passing_percentage)
    save_progress_after_quiz(quiz_details, percentage)

    return {
        "score": score,
        "score_out_of": score_out_of,
        "submission": submission.name,
        "pass": percentage >= quiz_details.passing_percentage,
        "percentage": percentage,
        "is_open_ended": is_open_ended,
    }

def custom_process_results(results: list, quiz_details: dict):
    score = 0
    is_open_ended = False

    for result in results:
        question_details = frappe.db.get_value(
            "LMS Quiz Question",
            {"parent": quiz_details.name, "question": result["question_name"]},
            ["question", "marks", "question_detail", "type"],
            as_dict=1,
        )
        if not question_details:
             continue
             
        result["question_name"] = question_details.question
        result["question"] = question_details.question_detail
        result["marks_out_of"] = question_details.marks

        if question_details.type != "Open Ended":
            correct = custom_verify_answer(question_details.question, result["answer"])
            
            # For LMS storage compatibility, join list into string
            if isinstance(result["answer"], list):
                result["answer"] = ", ".join(result["answer"])
                
            if correct:
                result["marks"] = question_details.marks
            else:
                result["marks"] = -quiz_details.marks_to_cut if quiz_details.enable_negative_marking else 0

            score += result["marks"]
            result["is_correct"] = 1 if correct else 0

        else:
            is_open_ended = True
            result["is_correct"] = 0
            # Note: We don't bother with _save_file for open ended here as it's from LMS core
            if isinstance(result["answer"], list):
                 result["answer"] = result["answer"][0]

    return {
        "results": results,
        "score": score,
        "is_open_ended": is_open_ended,
    }

def custom_verify_answer(question: str, answer: list):
    question_details = custom_get_question_details(question)
    if not question_details:
        return False
        
    correct = False

    if question_details.get("type") == "User Input":
        ans_str = answer[0] if answer else ""
        return custom_check_input_answers(question, ans_str)

    # Clean the answers from client (they might have absolute URLs or extra HTML from Text Editor)
    clean_answers = [strip_html(a or "").strip() for a in answer]

    if question_details.multiple:
        for num in range(1, 5):
            opt_text = strip_html(question_details.get(f"option_{num}") or "").strip()
            if opt_text and opt_text in clean_answers:
                correct = question_details.get(f"is_correct_{num}")
                if not correct:
                    return False
            if question_details.get(f"is_correct_{num}") and opt_text not in clean_answers:
                return False
        return True

    for num in range(1, 5):
        opt_text = strip_html(question_details.get(f"option_{num}") or "").strip()
        if opt_text and opt_text in clean_answers:
            correct = question_details.get(f"is_correct_{num}")
    return correct

def custom_get_question_details(question: str):
    fields = ["multiple", "type"]
    for num in range(1, 5):
        fields.append(f"option_{cstr(num)}")
        fields.append(f"is_correct_{cstr(num)}")
        fields.append(f"possibility_{cstr(num)}")

    return frappe.db.get_value("LMS Question", question, fields, as_dict=1)

def custom_check_input_answers(question: str, answer: str):
    fields = []
    for num in range(1, 5):
        fields.append(f"possibility_{cstr(num)}")

    question_details = frappe.db.get_value("LMS Question", question, fields, as_dict=1)
    if not question_details:
        return 0
        
    # Strip HTML from user answer
    clean_answer = strip_html(answer or "").strip().lower()
    
    for num in range(1, 5):
        current_possibility = question_details.get(f"possibility_{num}")
        if current_possibility:
            # Strip HTML from stored possibility
            clean_possibility = strip_html(current_possibility).strip().lower()
            if clean_possibility and fuzz.token_sort_ratio(clean_possibility, clean_answer) > 85:
                return 1
    return 0

@frappe.whitelist()
def get_quiz_submissions(quiz_name: str | None = None, limit: int | str = 20):
    """
    Returns the quiz submission history for the current user.
    """
    user = frappe.session.user
    filters = {"member": user}
    if quiz_name:
        filters["quiz"] = quiz_name
        
    submissions = frappe.get_list(
        "LMS Quiz Submission",
        filters=filters,
        fields=["name", "quiz", "quiz_title", "score", "score_out_of", "percentage", "creation"],
        limit=cint(limit),
        order_by="creation desc"
    )
    return submissions

@frappe.whitelist(allow_guest=True)
def get_signed_file(file_url: str, expiry: str, signature: str):
    """
    Whitelisted method to serve a file using a signed URL.
    Verifies expiry and HMAC signature before serving the file content.
    """
    # Verify expiry
    if int(expiry) < time.time():
        frappe.throw("Signed URL has expired", frappe.PermissionError)
        
    # Verify Signature
    secret = frappe.conf.get("encryption_key") or "secret"
    data = f"{file_url}{expiry}"
    expected_signature = hmac.new(
        secret.encode(), 
        data.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        frappe.throw("Invalid signature for this file", frappe.PermissionError)
        
    # Serve file content
    try:
        from frappe.utils.file_manager import get_file
        # Strip trailing query parameters (e.g. ?fid=xyz) for disk resolution
        actual_file_url = file_url.split('?')[0]
        fname, fcontent = get_file(actual_file_url)
        
        frappe.response.filename = fname
        frappe.response.filecontent = fcontent
        frappe.response.type = "binary"
        
        # Set cache control to avoid re-verifying frequently
        frappe.response.headers = {
            "Cache-Control": "public, max-age=86400"
        }
    except Exception as e:
        frappe.throw(f"Error reading file {file_url}: {str(e)}", frappe.DoesNotExistError)

def generate_signed_url(file_path: str, base_url: str) -> str:
    """
    Generates a signed URL for a file path.
    The URL includes an expiry timestamp and an HMAC signature.
    """
    # 7-day expiry
    expiry = int(time.time() + (7 * 24 * 60 * 60))
    secret = frappe.conf.get("encryption_key") or "secret"
    data = f"{file_path}{expiry}"
    signature = hmac.new(
        secret.encode(), 
        data.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    # Construct the signed API endpoint URL
    return (
        f"{base_url}/api/method/exam.api.get_signed_file"
        f"?file_url={file_path}&expiry={expiry}&signature={signature}"
    )

def expand_relative_urls(html_content: str, base_url: str) -> str:
    """
    Finds src="/..." and href="/..." and turns them into absolute URLs
    using the site's base_url.
    Handles single/double quotes and ensures we don't duplicate slashes.
    """
    if not html_content:
        return html_content
    
    # Better regex: only match if it starts with / and NOT //
    # Replaces the leading / with {base_url}/ 
    # (assuming base_url doesn't end in /)
    if base_url.endswith('/'):
        base_url = base_url[:-1]

    def _replace(match):
        prefix = match.group(1) # src= or href=
        quote = match.group(2) # " or '
        path = match.group(3) # /files/x.png
        
        if path.startswith('/') and not path.startswith('//'):
            # Generate a signed URL for the relative path
            signed_url = generate_signed_url(path, base_url)
            return f'{prefix}{quote}{signed_url}{quote}'
        return match.group(0)

    # (src|href)= ("|') (/...) \2
    pattern = r'(\b(?:src|href)=)(["\'])(/.*?)\2'
    return re.sub(pattern, _replace, html_content)


@frappe.whitelist()
def duplicate_program(program_name: str, include_children: bool | str = False) -> str:
    """
    Duplicates an LMS Program.
    If include_children is true, it recursively duplicates courses, chapters, and lessons.
    """
    from frappe.utils import cint
    include_children = cint(include_children)

    old_program = frappe.get_doc("LMS Program", program_name)
    new_program = frappe.copy_doc(old_program)
    new_program.title = f"{old_program.title} (Copy)"
    new_program.published = 0

    if include_children:
        new_courses = []
        for row in old_program.get("program_courses") or []:
            if not row.course:
                continue
            try:
                old_course = frappe.get_doc("LMS Course", row.course)
                new_course = duplicate_course_with_children(old_course)
                new_courses.append({"course": new_course.name})
            except frappe.DoesNotExistError:
                continue
        new_program.set("program_courses", new_courses)

    new_program.insert()
    return new_program.name

@frappe.whitelist()
def duplicate_course(course_name: str, include_children: bool | str = False) -> str:
    """
    Duplicates an LMS Course.
    If include_children is true, it recursively duplicates chapters and lessons.
    """
    from frappe.utils import cint
    include_children = cint(include_children)

    old_course = frappe.get_doc("LMS Course", course_name)
    if include_children:
        return duplicate_course_with_children(old_course).name
    else:
        new_course = frappe.copy_doc(old_course)
        new_course.title = f"{old_course.title} (Copy)"
        new_course.published = 0
        new_course.insert()
        return new_course.name


def duplicate_course_with_children(old_course):
    new_course = frappe.copy_doc(old_course)
    new_course.title = f"{old_course.title} (Copy)"
    new_course.published = 0

    new_chapters = []
    for row in old_course.get("chapters") or []:
        if not row.chapter:
            continue
        try:
            old_chapter = frappe.get_doc("Course Chapter", row.chapter)
            new_chapter = duplicate_chapter_with_children(old_chapter)
            new_chapters.append({"chapter": new_chapter.name})
        except frappe.DoesNotExistError:
            continue
    new_course.set("chapters", new_chapters)
    new_course.insert()
    return new_course


@frappe.whitelist()
def duplicate_chapter(chapter_name: str, include_children: bool | str = False) -> str:
    """
    Duplicates a Course Chapter.
    If include_children is true, it recursively duplicates lessons.
    """
    from frappe.utils import cint
    include_children = cint(include_children)

    old_chapter = frappe.get_doc("Course Chapter", chapter_name)
    if include_children:
        return duplicate_chapter_with_children(old_chapter).name
    else:
        new_chapter = frappe.copy_doc(old_chapter)
        new_chapter.title = f"{old_chapter.title} (Copy)"
        new_chapter.insert()
        return new_chapter.name


def duplicate_chapter_with_children(old_chapter):
    new_chapter = frappe.copy_doc(old_chapter)
    new_chapter.title = f"{old_chapter.title} (Copy)"

    new_lessons = []
    for row in old_chapter.get("lessons") or []:
        if not row.lesson:
            continue
        try:
            old_lesson = frappe.get_doc("Course Lesson", row.lesson)
            new_lesson = frappe.copy_doc(old_lesson)
            new_lesson.title = f"{old_lesson.title} (Copy)"
            new_lesson.insert()
            new_lessons.append({"lesson": new_lesson.name})
        except frappe.DoesNotExistError:
            continue

    new_chapter.set("lessons", new_lessons)
    new_chapter.insert()
    return new_chapter


def clear_user_selected_program(doc, method):
    """
    Clears the selected_program field on User when a program is deleted.
    Called when an LMS Program is deleted to nullify selected_program 
    on the User so that no dangling links are left.
    """
    frappe.db.sql(
        "update tabUser set selected_program = null where selected_program = %s", doc.name
    )
    frappe.db.sql(
        """
        UPDATE `tabUser`
        SET `selected_program` = NULL
        WHERE `selected_program` = %s
        """,
        (doc.name,),
    )


@frappe.whitelist()
def get_mentors_list(
    search: str | None = None,
    filters: list | str | None = None,
    limit_start: int | str = 0,
    limit_page_length: int | str = 20,
) -> list[dict]:
    """
    Returns a unified list of Mentor enrollments grouped by member.
    """
    if isinstance(filters, str):
        filters = json.loads(filters)
    if not filters:
        filters = []

    # Process custom course filter
    course_filter = None
    for f in filters:
        if isinstance(f, list) and len(f) == 3:
            if f[0] == "course" and f[1] == "=":
                course_filter = f[2]

    # Build WHERE conditions
    conditions = ["member_type = 'Mentor'"]
    args = {}
    
    if search:
        conditions.append("(member_name LIKE %(search)s OR member LIKE %(search)s)")
        args["search"] = f"%{search}%"
        
    if course_filter:
        conditions.append("member IN (SELECT member FROM `tabLMS Enrollment` WHERE member_type='Mentor' AND course=%(course)s)")
        args["course"] = course_filter

    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT 
            member, 
            MAX(member_name) as member_name, 
            MAX(name) as name,
            AVG(progress) as progress
        FROM `tabLMS Enrollment`
        WHERE {where_clause}
        GROUP BY member
        ORDER BY MAX(creation) DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """
    
    args.update({
        "limit": cint(limit_page_length),
        "offset": cint(limit_start)
    })
    
    mentors = frappe.db.sql(query, args, as_dict=True)
    
    # Attach courses to each distinct mentor
    if mentors:
        member_ids = [m.member for m in mentors]
        all_enrollments = frappe.get_all(
            "LMS Enrollment",
            filters={"member": ["in", member_ids], "member_type": "Mentor"},
            fields=["member", "course"]
        )
        
        # Group courses by member
        member_courses = {}
        for row in all_enrollments:
            if row.member not in member_courses:
                member_courses[row.member] = []
            if row.course:
                member_courses[row.member].append({"course": row.course})
                
        # Attach to result
        for m in mentors:
            courses = member_courses.get(m.member, [])
            m.courses = courses
            m.course = courses[0]["course"] if courses else None

    return mentors

@frappe.whitelist()
def get_mentors_count(
    search: str | None = None,
    filters: list | str | None = None,
) -> int:
    """Returns total distinct mentors matching the filters for pagination."""
    if isinstance(filters, str):
        filters = json.loads(filters)
    if not filters:
        filters = []

    course_filter = None
    for f in filters:
        if isinstance(f, list) and len(f) == 3:
            if f[0] == "course" and f[1] == "=":
                course_filter = f[2]

    conditions = ["member_type = 'Mentor'"]
    args = {}
    
    if search:
        conditions.append("(member_name LIKE %(search)s OR member LIKE %(search)s)")
        args["search"] = f"%{search}%"
        
    if course_filter:
        conditions.append("member IN (SELECT member FROM `tabLMS Enrollment` WHERE member_type='Mentor' AND course=%(course)s)")
        args["course"] = course_filter

    where_clause = " AND ".join(conditions)
    query = f"SELECT COUNT(DISTINCT member) FROM `tabLMS Enrollment` WHERE {where_clause}"
    
    count = frappe.db.sql(query, args)[0][0]
    return count or 0

@frappe.whitelist()
def get_mentor_detail(member: str) -> dict:
    """Returns unified mentor enrollment details."""
    enrollments = frappe.get_all("LMS Enrollment", filters={"member": member, "member_type": "Mentor"}, fields=["name", "course", "member_name", "progress"])
    
    if not enrollments:
        # It's a new mentor or completely removed
        member_name = frappe.db.get_value("User", member, "full_name") or member
        return {
            "name": member,
            "member": member,
            "member_name": member_name,
            "courses": [],
            "progress": 0,
            "member_type": "Mentor",
            "course": None,
        }
        
    res_courses = []
    for e in enrollments:
        if not e.course:
            continue
        title = frappe.db.get_value("LMS Course", e.course, "title") or e.course
        res_courses.append({
            "name": e.course, # ID
            "title": title
        })
        
    return {
        "name": member,
        "member": member,
        "member_name": enrollments[0].member_name,
        "courses": res_courses,
        "progress": sum([e.progress for e in enrollments]) / len(enrollments) if enrollments else 0,
        "member_type": "Mentor",
        "course": enrollments[0].course if enrollments else None,
    }


@frappe.whitelist()
def save_mentor_enrollments(member: str, courses: list | str, member_name: str | None = None) -> str:
    """Creates, deletes, or updates LMS Enrollments for a mentor syncing the assigned courses."""
    if isinstance(courses, str):
        courses = json.loads(courses)
        
    existing = frappe.get_all(
        "LMS Enrollment", 
        filters={"member": member, "member_type": "Mentor"}, 
        fields=["name", "course"]
    )
    existing_courses = {e.course: e.name for e in existing}
    
    # Ignore empty strings or null courses
    target_courses = set([c.get("course") for c in courses if c.get("course")])
    
    for course_name, enrollment_name in existing_courses.items():
        if course_name not in target_courses:
            frappe.delete_doc("LMS Enrollment", enrollment_name, ignore_permissions=True)
            
    for course_name in target_courses:
        if course_name not in existing_courses:
            doc = frappe.new_doc("LMS Enrollment")
            doc.member = member
            doc.course = course_name
            doc.member_type = "Mentor"
            if member_name:
                doc.member_name = member_name
            try:
                doc.insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(title="Failed to auto enroll Mentor", message=str(e))
                pass
    return "Success"

@frappe.whitelist()
def delete_mentor(member: str) -> str:
    """Deletes all mentor enrollments for a given member."""
    frappe.has_permission("LMS Enrollment", "delete", throw=True)
    enrollments = frappe.get_all("LMS Enrollment", filters={"member": member, "member_type": "Mentor"}, fields=["name"])
    for e in enrollments:
        frappe.delete_doc("LMS Enrollment", e.name, ignore_permissions=True)
    return "Success"
@frappe.whitelist()
def get_instructors(search: str = "", course: str = "", limit: int = 20, offset: int = 0) -> dict:
    """
    Returns a unique list of instructors (mentors) from LMS Enrollment with their courses.
    Supports pagination, search by member name or full name, and course filtering.
    """
    from frappe.utils import cint
    limit = cint(limit)
    offset = cint(offset)

    # 1. Base filters for unique mentors
    filters = {"member_type": "Mentor"}
    
    if course:
        filters["course"] = course

    if search:
        matching_users = frappe.get_all(
            "User",
            filters={
                "name": ["like", f"%{search}%"],
                "full_name": ["like", f"%{search}%"]
            },
            pluck="name"
        )
        if not matching_users:
            return {"results": [], "total": 0}
        filters["member"] = ["in", matching_users]

    # 2. Get unique members with pagination
    unique_members = frappe.get_all(
        "LMS Enrollment",
        filters=filters,
        fields=["member"],
        group_by="member",
        limit_page_length=limit,
        limit_start=offset,
        order_by="creation desc"
    )

    # 3. Get total count of unique mentors for this filter
    where_sql = "WHERE member_type = 'Mentor'"
    params = []
    
    if course:
        where_sql += " AND course = %s"
        params.append(course)
        
    if search:
        where_sql += " AND (member IN (SELECT name FROM `tabUser` WHERE full_name LIKE %s OR name LIKE %s))"
        params.extend([f"%{search}%", f"%{search}%"])

    
    total_res = frappe.db.sql(f"SELECT COUNT(DISTINCT member) FROM `tabLMS Enrollment` {where_sql}", params)
    total_unique = total_res[0][0] if total_res else 0

    results = []
    for member_row in unique_members:
        m_id = member_row.member
        if not m_id:
            continue

        user_info = frappe.db.get_value("User", m_id, ["full_name", "user_image", "email"], as_dict=True)
        
        instructor = {
            "name": m_id,
            "full_name": user_info.full_name if user_info else m_id,
            "email": user_info.email if user_info else m_id,
            "image": user_info.user_image if user_info else None,
            "courses": []
        }

        # 4. Fetch all courses for this mentor
        enrollments = frappe.get_all(
            "LMS Enrollment",
            filters={"member": m_id, "member_type": "Mentor"},
            fields=["course"]
        )
        
        for e in enrollments:
            if not e.course:
                continue
            
            course_title = frappe.db.get_value("LMS Course", e.course, "title")
            if course_title:
                # Avoid duplicates
                if not any(c["name"] == e.course for c in instructor["courses"]):
                    instructor["courses"].append({
                        "name": e.course,
                        "title": course_title
                    })
        
        results.append(instructor)



    return {
        "results": results,
        "total": total_unique
    }

@frappe.whitelist()
def bulk_delete_mentors(members: list | str) -> str:
    """
    Deletes all mentor enrollments for multiple members at once.
    'members' can be a list or a JSON string list of member emails.
    """
    frappe.has_permission("LMS Enrollment", "delete", throw=True)
    
    if isinstance(members, str):
        members = json.loads(members)
        
    if not members:
        return "Success"
        
    # Find all enrollments for these members
    enrollments = frappe.get_all(
        "LMS Enrollment", 
        filters={
            "member": ["in", members], 
            "member_type": "Mentor"
        }, 
        fields=["name"]
    )
    
    for e in enrollments:
        frappe.delete_doc("LMS Enrollment", e.name, ignore_permissions=True)
        
    return "Success"
