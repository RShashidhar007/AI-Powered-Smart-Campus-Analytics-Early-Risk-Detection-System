"""
generate_data.py - Generate realistic synthetic student data for 5 departments x 4 semesters.
Run: python scripts/generate_data.py
"""
import os
import random
import csv

# Configuration
DEPARTMENTS = ['CSE', 'ECE', 'ME', 'CE', 'ISE']
SEMESTERS = [1, 2, 3, 4]
STUDENTS_PER_DEPT_SEM = 100  # 5 x 4 x 100 = 2,000 total

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'student_data.csv')

# Indian names pool
FIRST_NAMES = [
    'Aarav', 'Vivek', 'Rohan', 'Arjun', 'Karthik', 'Siddharth', 'Rahul', 'Amit',
    'Priya', 'Sneha', 'Ananya', 'Divya', 'Meera', 'Pooja', 'Neha', 'Riya',
    'Aditya', 'Vikram', 'Suresh', 'Mahesh', 'Deepak', 'Tanmay', 'Nikhil', 'Varun',
    'Kavya', 'Anjali', 'Shreya', 'Lakshmi', 'Sanjana', 'Ishita', 'Nandini', 'Bhavya',
    'Rajesh', 'Ganesh', 'Harish', 'Prasad', 'Venkat', 'Naveen', 'Sachin', 'Manish',
    'Swathi', 'Rashmita', 'Akshata', 'Chandana', 'Deepika', 'Gayathri', 'Jyothi', 'Keerthana',
    'Abhishek', 'Ajay', 'Akash', 'Anand', 'Arvind', 'Ashwin', 'Bharath', 'Chetan',
    'Darshan', 'Girish', 'Hari', 'Jagadish', 'Kiran', 'Manoj', 'Mohan', 'Murali',
    'Pavan', 'Rakesh', 'Ramesh', 'Sagar', 'Santhosh', 'Sharath', 'Shiva', 'Srinivas',
    'Tejas', 'Uday', 'Vinay', 'Vishal', 'Yashwanth', 'Yogesh', 'Pramod', 'Basavaraj',
]

LAST_NAMES = [
    'Sharma', 'Reddy', 'Kumar', 'Patil', 'Gowda', 'Rao', 'Naik', 'Joshi',
    'Kulkarni', 'Hegde', 'Shetty', 'Nair', 'Pillai', 'Yadav', 'Gupta', 'Singh',
    'Desai', 'Bhat', 'Kamath', 'Patel', 'Acharya', 'Deshpande', 'Iyer', 'Menon',
    'Murthy', 'Prasad', 'Raju', 'Shastri', 'Swamy', 'Tiwari', 'Verma', 'Mishra',
    'Chauhan', 'Dubey', 'Malhotra', 'Mehra', 'Kapoor', 'Saxena', 'Bansal', 'Aggarwal',
]

# Department-specific tuning
# Slight variations per department to make data realistic
DEPT_PROFILES = {
    'CSE': {'att_mean': 72, 'att_std': 18, 'marks_bias': 0},
    'ECE': {'att_mean': 70, 'att_std': 17, 'marks_bias': -2},
    'ME':  {'att_mean': 68, 'att_std': 19, 'marks_bias': -3},
    'CE':  {'att_mean': 71, 'att_std': 18, 'marks_bias': -1},
    'ISE': {'att_mean': 73, 'att_std': 17, 'marks_bias': 1},
}

# Semester-specific tuning (higher semesters slightly harder)
SEM_PROFILES = {
    1: {'diff_factor': 0.0},
    2: {'diff_factor': -1.0},
    3: {'diff_factor': -2.0},
    4: {'diff_factor': -3.0},
}


def _clamp(val, lo, hi):
    return max(lo, min(hi, val))


def generate_student(dept, semester, seq):
    dp = DEPT_PROFILES[dept]
    sp = SEM_PROFILES[semester]

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"

    usn = f"1RV21{dept}{semester}{seq:03d}"

    # Attendance
    attendance = random.gauss(dp['att_mean'], dp['att_std'])
    attendance = _clamp(round(attendance, 2), 15.0, 99.5)

    # Internal marks (0-50) - correlated with attendance
    base_internal = (attendance / 100) * 35 + random.gauss(10, 6) + dp['marks_bias'] + sp['diff_factor']
    internal_marks = _clamp(round(base_internal, 2), 5.0, 50.0)

    # Assignment score (0-50)
    assignment_score = _clamp(round(random.gauss(32, 10) + dp['marks_bias'], 2), 5.0, 50.0)

    # Quiz score (0-50)
    quiz_score = _clamp(round(random.gauss(30, 11) + dp['marks_bias'], 2), 5.0, 50.0)

    # Lab marks (0-50)
    lab_marks = _clamp(round(random.gauss(33, 9) + dp['marks_bias'], 2), 5.0, 50.0)

    # Semester marks (0-200) - strong correlation with internal + attendance
    base_sem = (internal_marks / 50) * 100 + (attendance / 100) * 60 + random.gauss(10, 15) + sp['diff_factor'] * 3
    semester_marks = _clamp(round(base_sem, 2), 30.0, 200.0)

    # Study hours per day
    study_hours = _clamp(round(random.gauss(3.5, 1.8), 2), 0.2, 9.5)

    return {
        'usn': usn,
        'name': name,
        'department': dept,
        'semester': semester,
        'attendance': attendance,
        'internal_marks': internal_marks,
        'assignment_score': assignment_score,
        'quiz_score': quiz_score,
        'lab_marks': lab_marks,
        'semester_marks': semester_marks,
        'study_hours': study_hours,
    }


def main():
    random.seed(42)  # Reproducible
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fields = ['usn', 'name', 'department', 'semester', 'attendance',
              'internal_marks', 'assignment_score', 'quiz_score',
              'lab_marks', 'semester_marks', 'study_hours']

    all_students = []
    for dept in DEPARTMENTS:
        for sem in SEMESTERS:
            for seq in range(1, STUDENTS_PER_DEPT_SEM + 1):
                student = generate_student(dept, sem, seq)
                all_students.append(student)

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_students)

    print(f"[OK] Generated {len(all_students)} students across {len(DEPARTMENTS)} departments x {len(SEMESTERS)} semesters")
    print(f"     Output: {OUTPUT_FILE}")
    print(f"     Shape:  {len(all_students)} rows x {len(fields)} columns")


if __name__ == '__main__':
    main()
