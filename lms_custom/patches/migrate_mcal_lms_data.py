"""
Migration patch to create LMS data (Programs, Courses, Chapters, Lessons)
from the mcal_backup_28.dump PostgreSQL dump.

Hierarchy:
  folldy_admin_program          → LMS Program
  folldy_admin_level (depth 2)  → LMS Course  (subjects: PHYSICS, CHEMISTRY, …)
  folldy_admin_level (depth 3)  → Course Chapter
  base_presentation             → Course Lesson (linked via folldy_admin_level_presentations)
"""

import os
import re

import frappe


# ---------------------------------------------------------------------------
# Dump parser
# ---------------------------------------------------------------------------

def _extract_table(content: str, table: str) -> list[list[str]]:
    """Return rows (list-of-string-fields) from a COPY … FROM stdin block."""
    pattern = rf"COPY public\.{re.escape(table)} \([^)]+\) FROM stdin;\n(.*?)\\\."
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []
    return [line.split("\t") for line in match.group(1).strip().split("\n") if line]


def _int(val: str) -> int | None:
    return None if val.strip() in (r"\N", "") else int(val.strip())


def _load_dump(dump_path: str) -> dict:
    with open(dump_path, encoding="utf-8", errors="replace") as fh:
        content = fh.read()

    programs = [
        {"id": int(r[0]), "name": r[1].strip(), "level_id": _int(r[2])}
        for r in _extract_table(content, "folldy_admin_program")
        if len(r) >= 3
    ]

    levels: dict[int, dict] = {
        int(r[0]): {"id": int(r[0]), "order": int(r[1]), "name": r[2].strip(), "parent_id": _int(r[6])}
        for r in _extract_table(content, "folldy_admin_level")
        if len(r) >= 7
    }

    presentations: dict[int, dict] = {
        int(r[0]): {"title": r[1].strip(), "video_id": r[13].strip() if len(r) > 13 and r[13].strip() not in (r"\N", "") else None}
        for r in _extract_table(content, "base_presentation")
        if len(r) >= 2
    }

    lp_rows = sorted(
        [
            {"sort": int(r[1]), "level_id": int(r[2]), "pres_id": int(r[3])}
            for r in _extract_table(content, "folldy_admin_level_presentations")
            if len(r) >= 4
        ],
        key=lambda x: (x["level_id"], x["sort"]),
    )
    level_presentations: dict[int, list[int]] = {}
    for lp in lp_rows:
        level_presentations.setdefault(lp["level_id"], []).append(lp["pres_id"])

    return {
        "programs": programs,
        "levels": levels,
        "presentations": presentations,
        "level_presentations": level_presentations,
    }


# ---------------------------------------------------------------------------
# Frappe document helpers (idempotent)
# ---------------------------------------------------------------------------

def _get_or_create(doctype: str, filters: dict, data: dict) -> str:
    name = frappe.db.get_value(doctype, filters)
    if name:
        return name
    doc = frappe.get_doc({"doctype": doctype, **data})
    doc.insert(ignore_permissions=True)
    return doc.name


# ---------------------------------------------------------------------------
# Main execute
# ---------------------------------------------------------------------------

def clear_lms_data() -> None:
    # child tables of LMS Course / Course Chapter / LMS Program
    for child_table in ("Lesson Reference", "Chapter Reference", "LMS Program Course"):
        frappe.db.delete(child_table)
    for doctype in ("Course Lesson", "Course Chapter", "LMS Course", "LMS Program"):
        frappe.db.delete(doctype)
    frappe.db.commit()
    print("LMS data cleared.")


def execute() -> None:
    dump_path = os.path.normpath(
        os.path.join(frappe.get_app_path("exam"), "..", "mcal_backup_28.dump")
    )

    if not os.path.exists(dump_path):
        frappe.log_error(
            f"mcal_backup_28.dump not found at {dump_path}. Skipping LMS migration.",
            "migrate_mcal_lms_data",
        )
        return

    d = _load_dump(dump_path)
    programs = d["programs"]
    levels = d["levels"]
    presentations = d["presentations"]
    level_presentations = d["level_presentations"]

    # Map program-level IDs (the top-level nodes each program points to)
    prog_level_ids = {p["level_id"] for p in programs if p["level_id"]}

    # Course levels  = direct children of program-level nodes  (e.g. PHYSICS, CHEMISTRY)
    course_levels = {
        lid: lv for lid, lv in levels.items() if lv["parent_id"] in prog_level_ids
    }

    # Chapter levels = direct children of course levels  (e.g. GRAVITATION, WAVES)
    chapter_levels = {
        lid: lv for lid, lv in levels.items() if lv["parent_id"] in course_levels
    }

    # course_level_id → sorted list of chapter-level entries
    course_to_chapters: dict[int, list[dict]] = {}
    for ch_lid, ch_lv in chapter_levels.items():
        course_to_chapters.setdefault(ch_lv["parent_id"], []).append(
            {"lid": ch_lid, "title": ch_lv["name"], "order": ch_lv["order"]}
        )
    for entries in course_to_chapters.values():
        entries.sort(key=lambda x: x["order"])

    # program_level_id → sorted list of course-level IDs
    prog_level_to_courses: dict[int, list[int]] = {}
    for lid, lv in sorted(course_levels.items(), key=lambda x: x[1]["order"]):
        prog_level_to_courses.setdefault(lv["parent_id"], []).append(lid)

    # course_title → created LMS Course doc name  (avoid duplicates across programs)
    course_doc_cache: dict[str, str] = {}

    for prog in programs:
        if not prog["level_id"]:
            continue  # orphan program — no level data, skip

        if prog["level_id"] not in prog_level_to_courses:
            # Dump the program's level node and its immediate children for diagnosis
            root_lv = levels.get(prog["level_id"])
            children = [lv for lv in levels.values() if lv["parent_id"] == prog["level_id"]]
            frappe.log_error(
                f"Program '{prog['name']}' (id={prog['id']}) has level_id={prog['level_id']} "
                f"but no course-level children were found.\n"
                f"Root level: {root_lv}\n"
                f"Direct children in levels table: {children}",
                "migrate_mcal_lms_data: missing courses",
            )
            continue

        course_doc_names: list[str] = []

        for course_lid in prog_level_to_courses.get(prog["level_id"], []):
            course_title = f"{course_levels[course_lid]['name']} - {prog['name']}"
            cache_key = course_title

            if cache_key not in course_doc_cache:
                # Create Course (empty first, chapters added after)
                course_name = _get_or_create(
                    "LMS Course",
                    {"title": course_title},
                    {
                        "title": course_title,
                        "published": 1,
                        "short_introduction": course_title,
                        "description": course_title,
                        "instructors": [{"instructor": frappe.session.user}],
                    },
                )
                course_doc_cache[cache_key] = course_name
            else:
                course_name = course_doc_cache[cache_key]

            chapter_doc_names: list[str] = []

            for ch in course_to_chapters.get(course_lid, []):
                chapter_name = _get_or_create(
                    "Course Chapter",
                    {"title": ch["title"], "course": course_name},
                    {"title": ch["title"], "course": course_name},
                )

                # Create lessons for this chapter
                lesson_doc_names: list[str] = []
                seen_titles: set[str] = set()

                for pres_id in level_presentations.get(ch["lid"], []):
                    pres = presentations.get(pres_id)
                    if not pres:
                        continue
                    lesson_title = pres["title"]
                    if not lesson_title or lesson_title in seen_titles:
                        continue
                    seen_titles.add(lesson_title)

                    vimeo_url = (
                        f"https://vimeo.com/{pres['video_id']}" if pres["video_id"] else None
                    )

                    lesson_name = _get_or_create(
                        "Course Lesson",
                        {"title": lesson_title, "chapter": chapter_name},
                        {
                            "title": lesson_title,
                            "chapter": chapter_name,
                            "course": course_name,
                            **({"youtube": vimeo_url} if vimeo_url else {}),
                        },
                    )
                    lesson_doc_names.append(lesson_name)

                # Attach lessons to chapter if any were created
                if lesson_doc_names:
                    ch_doc = frappe.get_doc("Course Chapter", chapter_name)
                    existing_lessons = {row.lesson for row in ch_doc.lessons}
                    new_lessons = [ln for ln in lesson_doc_names if ln not in existing_lessons]
                    if new_lessons:
                        for ln in new_lessons:
                            ch_doc.append("lessons", {"lesson": ln})
                        ch_doc.flags.ignore_links = True
                        ch_doc.save(ignore_permissions=True)

                chapter_doc_names.append(chapter_name)

            # Attach chapters to course
            if chapter_doc_names:
                course_doc = frappe.get_doc("LMS Course", course_name)
                existing_chapters = {row.chapter for row in course_doc.chapters}
                new_chapters = [cn for cn in chapter_doc_names if cn not in existing_chapters]
                if new_chapters:
                    for cn in new_chapters:
                        course_doc.append("chapters", {"chapter": cn})
                    course_doc.flags.ignore_links = True
                    course_doc.save(ignore_permissions=True)

            course_doc_names.append(course_name)

        # Create Program
        prog_name = _get_or_create(
            "LMS Program",
            {"title": prog["name"]},
            {"title": prog["name"], "published": 1},
        )
        # Attach courses to program
        if course_doc_names:
            prog_doc = frappe.get_doc("LMS Program", prog_name)
            existing_courses = {row.course for row in prog_doc.program_courses}
            new_courses = [cn for cn in course_doc_names if cn not in existing_courses]
            if new_courses:
                for cn in new_courses:
                    prog_doc.append("program_courses", {"course": cn})
                prog_doc.flags.ignore_links = True
                prog_doc.save(ignore_permissions=True)

    frappe.db.commit()
