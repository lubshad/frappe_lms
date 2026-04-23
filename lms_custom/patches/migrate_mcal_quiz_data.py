"""
Migration patch to create LMS Quiz and LMS Question data
from the mcal_backup_28.dump PostgreSQL dump.

Hierarchy:
  exam_backend_exam                → LMS Quiz
  exam_backend_question (exam_id)  → LMS Question  (linked via LMS Quiz Question)
  exam_backend_choice (question_id)→ LMS Question options (option_1..4, is_correct_1..4)

Column layout (tab-delimited COPY blocks):
  exam_backend_exam:     id[0], title[3], is_published[7], total_mark[10], pass_mark[11], show_result[12]
  exam_backend_question: id[0], question[3], choice_type[6], mark[8], exam_id[15]
  exam_backend_choice:   id[0], choice[3], is_correct[5], exam_id[10], question_id[11]

Note: HTML content in question/choice text fields may contain embedded tab characters,
which can shift column offsets.  The parser handles this by accepting positional
column indices from the right-hand side for reliable trailing fields.
"""

import os
import re

import frappe


# ---------------------------------------------------------------------------
# Dump parser helpers
# ---------------------------------------------------------------------------

def _col_count(content: str, table: str) -> int:
    """Return the number of declared columns for a table."""
    pattern = rf"COPY public\.{re.escape(table)} \(([^)]+)\) FROM stdin;"
    match = re.search(pattern, content)
    if not match:
        return 0
    return len(match.group(1).split(","))


def _extract_table(content: str, table: str) -> list[list[str]]:
    """Return rows (list-of-string-fields) from a COPY … FROM stdin block.

    The dump may be in PostgreSQL custom binary format where the standard ``\\.``
    terminator is absent.  Instead we locate the COPY header, then scan lines
    forward collecting only those that split into exactly ``expected_cols`` tab-
    delimited fields — stopping as soon as we see a line that clearly belongs to
    a different block (another COPY header, SQL keyword, or non-printable data).
    """
    expected_cols = _col_count(content, table)
    if not expected_cols:
        return []

    header_pattern = rf"COPY public\.{re.escape(table)} \([^)]+\) FROM stdin;\n"
    hm = re.search(header_pattern, content)
    if not hm:
        return []

    rows: list[list[str]] = []
    start = hm.end()
    # Scan subsequent lines
    for line in content[start:].split("\n"):
        # Stop on known non-data lines
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in (r"\.", "."):
            break
        if stripped.startswith("COPY ") or stripped.startswith("--") or stripped.startswith("ALTER ") or stripped.startswith("SET "):
            break
        fields = line.split("\t")
        if len(fields) == expected_cols:
            rows.append(fields)
        elif rows:
            # We already collected some rows and now see something that doesn't
            # fit — likely binary garbage; stop here.
            break
    return rows


def _str(val: str) -> str:
    v = val.strip()
    return "" if v in (r"\N",) else v


def _int(val: str) -> int | None:
    v = val.strip()
    return None if v in (r"\N", "") else int(v)


def _bool(val: str) -> bool:
    return val.strip().lower() in ("t", "true", "1")


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
# Data loaders
# ---------------------------------------------------------------------------

def _load_dump(dump_path: str) -> dict:
    with open(dump_path, encoding="utf-8", errors="replace") as fh:
        content = fh.read()

    expected_exam_cols = _col_count(content, "exam_backend_exam")    # 20
    expected_q_cols    = _col_count(content, "exam_backend_question") # 21
    expected_ch_cols   = _col_count(content, "exam_backend_choice")   # 12

    # --- Exams ---------------------------------------------------------------
    # Columns: id[0] … title[3] … is_published[7] … total_mark[10] pass_mark[11] show_result[12]
    exams: dict[int, dict] = {}
    for r in _extract_table(content, "exam_backend_exam"):
        if len(r) < expected_exam_cols:
            continue
        eid         = int(r[0])
        title       = _str(r[3])
        published   = _bool(r[7])
        total_mark  = _int(r[10]) or 0
        pass_mark   = _int(r[11]) or 0
        show_ans    = _bool(r[12])
        passing_pct = round(pass_mark / total_mark * 100) if total_mark else 0
        exams[eid] = {
            "id": eid,
            "title": title,
            "published": published,
            "total_mark": total_mark,
            "passing_percentage": passing_pct,
            "show_answers": show_ans,
        }

    # --- Questions -----------------------------------------------------------
    # Columns: id[0] … question[3] … choice_type[6] … mark[8] … exam_id[15]
    questions: dict[int, dict] = {}
    for r in _extract_table(content, "exam_backend_question"):
        if len(r) < expected_q_cols:
            continue
        qid         = int(r[0])
        question    = _str(r[3])
        choice_type = _str(r[6])
        mark        = _int(r[8]) or 1
        exam_id     = _int(r[15])
        if exam_id is None:
            continue
        questions[qid] = {
            "id": qid,
            "question": question,
            "choice_type": choice_type,  # "CHECKBOX" → multiple, else single
            "mark": mark,
            "exam_id": exam_id,
        }

    # --- Choices -------------------------------------------------------------
    # Columns: id[0] … choice[3] … is_correct[5] … exam_id[10] … question_id[11]
    choices_by_question: dict[int, list[dict]] = {}
    for r in _extract_table(content, "exam_backend_choice"):
        if len(r) < expected_ch_cols:
            continue
        try:
            question_id = _int(r[11])
            is_correct  = _bool(r[5])
            choice_text = _str(r[3])
        except (IndexError, ValueError):
            continue
        if question_id is None:
            continue
        choices_by_question.setdefault(question_id, []).append({
            "choice": choice_text,
            "is_correct": is_correct,
        })

    return {
        "exams": exams,
        "questions": questions,
        "choices_by_question": choices_by_question,
    }


# ---------------------------------------------------------------------------
# Clear helpers
# ---------------------------------------------------------------------------

def clear_quiz_data() -> None:
    """Remove all LMS Quiz / Question data — useful for a clean re-run."""
    frappe.db.delete("LMS Quiz Question")
    for doctype in ("LMS Quiz", "LMS Question"):
        frappe.db.delete(doctype)
    frappe.db.commit()
    print("LMS Quiz & Question data cleared.")


# ---------------------------------------------------------------------------
# Main execute
# ---------------------------------------------------------------------------

def execute() -> None:
    dump_path = os.path.normpath(
        os.path.join(frappe.get_app_path("exam"), "..", "mcal_backup_28.dump")
    )

    if not os.path.exists(dump_path):
        frappe.log_error(
            f"mcal_backup_28.dump not found at {dump_path}. Skipping quiz migration.",
            "migrate_mcal_quiz_data",
        )
        return

    d = _load_dump(dump_path)
    exams              = d["exams"]
    questions          = d["questions"]
    choices_by_question = d["choices_by_question"]

    # Group questions by exam
    exam_questions: dict[int, list[dict]] = {}
    for q in questions.values():
        exam_questions.setdefault(q["exam_id"], []).append(q)

    for exam in exams.values():
        eid = exam["id"]

        # --- Create LMS Quiz -------------------------------------------------
        quiz_name = _get_or_create(
            "LMS Quiz",
            {"title": exam["title"]},
            {
                "title": exam["title"],
                "passing_percentage": exam["passing_percentage"],
                "show_answers": int(exam["show_answers"]),
            },
        )

        # --- Create LMS Questions and link to Quiz ---------------------------
        quiz_doc = frappe.get_doc("LMS Quiz", quiz_name)
        existing_question_names = {row.question for row in quiz_doc.questions}

        for q in exam_questions.get(eid, []):
            # Build up to 4 unique options; need at least 2 with ≥1 correct for "Choices"
            choices = choices_by_question.get(q["id"], [])
            seen_texts: set[str] = set()
            deduped: list[dict] = []
            for c in choices:
                text = c["choice"].strip()
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    deduped.append(c)
            options: list[dict] = deduped[:4]
            valid_choices = len(options) >= 2 and any(o["is_correct"] for o in options)
            q_type = "Choices" if valid_choices else "Open Ended"

            question_data: dict = {
                "question": q["question"],
                "type": q_type,
            }

            if q_type == "Choices":
                question_data["multiple"] = int(q["choice_type"].upper() == "CHECKBOX")
                for idx, opt in enumerate(options, start=1):
                    question_data[f"option_{idx}"] = opt["choice"]
                    question_data[f"is_correct_{idx}"] = int(opt["is_correct"])
            else:
                frappe.log_error(
                    f"Question id={q['id']} could not be parsed as Choices "
                    f"(got {len(options)} options). Created as 'Open Ended'.",
                    "migrate_mcal_quiz_data: open ended fallback",
                )

            # LMS Question is identified by its question text + type
            # (no unique constraint — use get_value with question text)
            lms_q_name = frappe.db.get_value(
                "LMS Question", {"question": q["question"], "type": q_type}
            )
            if not lms_q_name:
                lms_q_doc = frappe.get_doc({"doctype": "LMS Question", **question_data})
                lms_q_doc.insert(ignore_permissions=True)
                lms_q_name = lms_q_doc.name

            # Attach question to quiz if not already there
            if lms_q_name not in existing_question_names:
                quiz_doc.append("questions", {
                    "question": lms_q_name,
                    "marks": q["mark"],
                })
                existing_question_names.add(lms_q_name)

        if quiz_doc.get("questions"):
            quiz_doc.flags.ignore_links = True
            quiz_doc.save(ignore_permissions=True)

    frappe.db.commit()
