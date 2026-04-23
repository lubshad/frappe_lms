import frappe

def create_aptitude_test():
    print("Creating Higher Secondary Aptitude Test...")

    exam_title = "Higher Secondary Aptitude Test"
    if frappe.db.exists("Exam", exam_title):
        print(f"Exam '{exam_title}' already exists. Skipping.")
        return

    data = [
        ("Quantitative Aptitude", [
            ("The ratio of two numbers is 3:4. If their sum is 70, what is the larger number?", ["30", "40", "35", "45"], "40", "Let numbers be 3x and 4x. 3x + 4x = 70 => 7x = 70 => x = 10. Larger number is 4x = 40."),
            ("A car travels at 72 km/h. How many meters per second is this speed?", ["15 m/s", "20 m/s", "25 m/s", "30 m/s"], "20 m/s", "72 * (5/18) = 20 m/s."),
            ("A shopkeeper bought a chair for $50 and sold it for $60. What is the profit percentage?", ["10%", "15%", "20%", "25%"], "20%", "Profit = 10. (10/50)*100 = 20%."),
            ("If 5x + 10 = 35, what is the value of x?", ["4", "5", "6", "7"], "5", "5x = 25. x = 5."),
            ("What is the average of the first five prime numbers?", ["5.2", "5.4", "5.6", "5.8"], "5.6", "2, 3, 5, 7, 11 sum to 28. 28/5 = 5.6.")
        ]),
        ("Logical Reasoning", [
            ("Series: 7, 10, 8, 11, 9, 12, ... What number should come next?", ["7", "10", "12", "13"], "10", "+3, -2 pattern."),
            ("SCD, TEF, UGH, ____, WKL. What follows UGH?", ["VJI", "VIJ", "IJV", "JIV"], "VIJ", "S-T-U-V-W pattern."),
            ("Pointing to a photograph, a man says: 'I have no brother or sister but that man's father is my father's son.' Whose photo?", ["Father", "Son", "Himself", "Nephew"], "Son", "My father's son = Me. That man's father = Me."),
            ("If LIGHT is MJHIT, how is DARK coded?", ["EBSL", "ECSL", "EBRL", "EBSK"], "EBSL", "Simple +1 shift."),
            ("Which one is the odd one out?", ["Square", "Circle", "Triangle", "Sphere"], "Sphere", "Sphere is 3D.")
        ]),
        ("Verbal Ability", [
            ("Synonym of 'Fragile'?", ["Strong", "Weak", "Delicate", "Tough"], "Delicate", "Fragile = Delicate."),
            ("Antonym of 'Gloomy'?", ["Bright", "Sad", "Dull", "Dark"], "Bright", "Gloomy opposite is Bright."),
            ("Identify the correctly spelled word:", ["Accommodate", "Acomodate", "Accomodate", "Acommodate"], "Accommodate", "Double c, double m."),
            ("Neither the teacher nor the students ____ present yesterday.", ["is", "was", "were", "are"], "were", "Agrees with the closer subject 'students'."),
            ("What does the idiom 'Piece of cake' mean?", ["Very tasty", "Easy", "Small portion", "Gift"], "Easy", "Idiom for easy task.")
        ]),
        ("General Knowledge", [
            ("Largest ocean on Earth?", ["Atlantic", "Indian", "Pacific", "Arctic"], "Pacific", "Pacific Ocean is largest."),
            ("Who wrote 'Discovery of India'?", ["Gandhi", "Nehru", "Radhakrishnan", "Tagore"], "Nehru", "Jawaharlal Nehru wrote it."),
            ("Which organ in the human body filters blood?", ["Heart", "Lungs", "Kidney", "Liver"], "Kidney", "Kidney filters blood."),
            ("Capital of Australia?", ["Sydney", "Melbourne", "Canberra", "Perth"], "Canberra", "Canberra is the capital."),
            ("First man to step on the Moon?", ["Buzz Aldrin", "Neil Armstrong", "Yuri Gagarin", "Michael Collins"], "Neil Armstrong", "He stepped on it in 1969.")
        ]),
        ("Data Interpretation", [
            ("Science: 40, Commerce: 30, Arts: 30. Percentage of Science students?", ["30%", "40%", "50%", "60%"], "40%", "(40/100)*100 = 40%."),
            ("If 10% of 40 Science students fail, how many passed?", ["30", "34", "36", "38"], "36", "40 - 4 = 36."),
            ("Ratio of Commerce students to Arts students?", ["1:1", "1:2", "2:1", "3:4"], "1:1", "30:30 = 1:1."),
            ("Total students in the class?", ["70", "80", "90", "100"], "100", "40+30+30 = 100."),
            ("Which stream has the highest number of students?", ["Science", "Commerce", "Arts", "Equal"], "Science", "Science has 40.")
        ])
    ]

    exam = frappe.new_doc("Exam")
    exam.title = exam_title
    exam.passing_percentage = 40
    exam.show_results = 1

    for idx, (section_title, questions) in enumerate(data):
        quiz = frappe.new_doc("LMS Quiz")
        quiz.title = f"HS Aptitude - {section_title}"
        quiz.passing_percentage = 40
        quiz.duration = 10

        for q_text, opts, correct, expl in questions:
            q_doc = frappe.new_doc("LMS Question")
            q_doc.question = q_text
            q_doc.type = "Choices"
            q_doc.course_group = section_title
            for i, o in enumerate(opts, 1):
                setattr(q_doc, f"option_{i}", o)
                if o == correct:
                    setattr(q_doc, f"is_correct_{i}", 1)
                    setattr(q_doc, f"explanation_{i}", expl)
            q_doc.insert(ignore_permissions=True)
            quiz.append("questions", {"question": q_doc.name, "marks": 1})

        quiz.insert(ignore_permissions=True)
        
        exam.append("sections", {
            "quiz": quiz.name,
            "section_title": section_title,
            "sequence": idx + 1,
            "mandatory": 1
        })

    exam.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Test Created Successfully.")

if __name__ == "__main__":
    create_aptitude_test()
