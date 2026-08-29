from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.models.event import Event
from backend.models.registration import Registration
from backend.services.auth_service import hash_password

def seed_database_if_empty(db: Session):
    """
    Check if the database has any users or events.
    If empty, insert demo admin, students, college events, and registrations.
    """
    user_count = db.query(User).count()
    if user_count > 0:
        return  # Already seeded

    print("[*] Database is empty. Seeding demo users, events, and registrations...")

    # 1. Create Admin
    admin_user = User(
        name="Campus Event Admin",
        email="admin@college.edu",
        hashed_password=hash_password("adminpassword123"),
        student_id="ADM-001",
        department="Academic & Event Affairs",
        role="ADMIN"
    )
    db.add(admin_user)

    # 2. Create 5 Students
    students_data = [
        ("Rahul Sharma", "rahul@student.edu", "student123", "CS-2024-001", "Computer Science"),
        ("Priya Patel", "priya@student.edu", "student123", "IT-2024-042", "Information Technology"),
        ("Aman Verma", "aman@student.edu", "student123", "EC-2024-018", "Electronics & Comm."),
        ("Sneha Reddy", "sneha@student.edu", "student123", "ME-2024-029", "Mechanical Eng."),
        ("Vikram Singh", "vikram@student.edu", "student123", "CV-2024-015", "Civil Eng.")
    ]

    created_students = []
    for name, email, pwd, s_id, dept in students_data:
        student = User(
            name=name,
            email=email,
            hashed_password=hash_password(pwd),
            student_id=s_id,
            department=dept,
            role="STUDENT"
        )
        db.add(student)
        created_students.append(student)

    db.flush()  # populate student IDs

    # 3. Create Sample Events with dynamic upcoming dates
    today = date.today()

    events_data = [
        {
            "title": "TechFest 2026: Annual Tech Extravaganza",
            "description": "The premier college technology festival featuring keynote talks from tech leaders, robotics display, drone racing, and coding competitions with cash prizes.",
            "category": "Technical",
            "venue": "Main University Auditorium & Labs",
            "event_date": (today + timedelta(days=5)).isoformat(),
            "start_time": "09:30",
            "end_time": "17:00",
            "capacity": 150,
            "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80",
            "organizer": "Department of Computer Science & IEEE Student Branch"
        },
        {
            "title": "CodeSprint 24-Hour National Hackathon",
            "description": "Collaborate in teams of 2 to 4 to build innovative real-world software & AI solutions. Mentorship, swag, free food, and internship opportunities provided.",
            "category": "Hackathon",
            "venue": "Innovation & Incubation Hub, Floor 3",
            "event_date": (today + timedelta(days=12)).isoformat(),
            "start_time": "10:00",
            "end_time": "18:00",
            "capacity": 60,
            "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&auto=format&fit=crop&q=80",
            "organizer": "Coding & Algorithms Club"
        },
        {
            "title": "Hands-On Generative AI & LLM Workshop",
            "description": "Learn to fine-tune open-source models, build RAG pipelines, and integrate AI into web applications using modern Python frameworks.",
            "category": "Workshop",
            "venue": "Computer Lab 4, Tech Block",
            "event_date": (today + timedelta(days=8)).isoformat(),
            "start_time": "14:00",
            "end_time": "17:30",
            "capacity": 45,
            "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=80",
            "organizer": "AI & Data Science Society"
        },
        {
            "title": "Euphoria 2026: Annual Cultural Gala & Concert",
            "description": "A night of thrilling live music performances, fashion show, beatboxing, inter-college battle of bands, and authentic food stalls.",
            "category": "Cultural",
            "venue": "University Open Air Amphitheatre",
            "event_date": (today + timedelta(days=15)).isoformat(),
            "start_time": "18:00",
            "end_time": "22:30",
            "capacity": 300,
            "image_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&auto=format&fit=crop&q=80",
            "organizer": "College Cultural Council"
        },
        {
            "title": "Annual Inter-Department Sports Championship",
            "description": "Compete for the college championship trophy across Football, Basketball, Badminton, Table Tennis, and Sprint Relays.",
            "category": "Sports",
            "venue": "University Sports Complex & Ground",
            "event_date": (today + timedelta(days=20)).isoformat(),
            "start_time": "08:00",
            "end_time": "16:00",
            "capacity": 200,
            "image_url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&auto=format&fit=crop&q=80",
            "organizer": "Department of Physical Education"
        },
        {
            "title": "VentureVibe: Startup & Entrepreneurship Summit",
            "description": "Connect with top angel investors, college alumni startup founders, and pitch your startup idea for seed grants up to $10,000.",
            "category": "Seminar",
            "venue": "Executive Seminar Hall, Admin Block",
            "event_date": (today + timedelta(days=25)).isoformat(),
            "start_time": "11:00",
            "end_time": "15:30",
            "capacity": 100,
            "image_url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&auto=format&fit=crop&q=80",
            "organizer": "E-Cell & Entrepreneurship Club"
        },
        {
            "title": "LensCraft 2026: Campus Photography Contest",
            "description": "Showcase your visual storytelling skills. Themes include 'Campus Architecture', 'Moments of Joy', and 'Shadows & Light'. Winner exhibits in campus gallery.",
            "category": "Competition",
            "venue": "Fine Arts Gallery & Studio",
            "event_date": (today + timedelta(days=7)).isoformat(),
            "start_time": "10:00",
            "end_time": "13:00",
            "capacity": 50,
            "image_url": "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800&auto=format&fit=crop&q=80",
            "organizer": "College Photography Club"
        },
        {
            "title": "RoboWars: Ultimate Autonomous & RC Bot Clash",
            "description": "Watch customized combat robots battle it out in a bulletproof arena for glory. Includes wired, wireless, and autonomous obstacle track race.",
            "category": "Technical",
            "venue": "Mechanical Workshop Arena",
            "event_date": (today + timedelta(days=18)).isoformat(),
            "start_time": "13:00",
            "end_time": "17:00",
            "capacity": 80,
            "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop&q=80",
            "organizer": "Robotics & Automation Society"
        },
        {
            "title": "CyberShield: Ethical Hacking & Security Bootcamp",
            "description": "Learn vulnerability assessment, penetration testing fundamentals, web application security, and network packet sniffing in a safe sandbox.",
            "category": "Workshop",
            "venue": "Cyber Security Lab 2",
            "event_date": (today + timedelta(days=10)).isoformat(),
            "start_time": "14:00",
            "end_time": "18:00",
            "capacity": 40,
            "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80",
            "organizer": "Cyber Security Club"
        }
    ]

    created_events = []
    for ev_info in events_data:
        event = Event(**ev_info)
        db.add(event)
        created_events.append(event)

    db.flush()

    # 4. Create Sample Registrations
    # Rahul registers for TechFest, CodeSprint, AI Workshop
    # Priya registers for TechFest, Cultural Night, LensCraft
    # Aman registers for CodeSprint, RoboWars, CyberShield
    # Sneha registers for Sports Championship, AI Workshop
    # Vikram registers for Sports Championship, TechFest
    sample_registrations = [
        (created_students[0].id, created_events[0].id),
        (created_students[0].id, created_events[1].id),
        (created_students[0].id, created_events[2].id),
        (created_students[1].id, created_events[0].id),
        (created_students[1].id, created_events[3].id),
        (created_students[1].id, created_events[6].id),
        (created_students[2].id, created_events[1].id),
        (created_students[2].id, created_events[7].id),
        (created_students[2].id, created_events[8].id),
        (created_students[3].id, created_events[4].id),
        (created_students[3].id, created_events[2].id),
        (created_students[4].id, created_events[4].id),
        (created_students[4].id, created_events[0].id),
    ]

    for user_id, event_id in sample_registrations:
        reg = Registration(
            user_id=user_id,
            event_id=event_id,
            status="CONFIRMED"
        )
        db.add(reg)

    db.commit()
    print("[+] Database seeded successfully with demo data!")
