import urllib.request
import urllib.parse
import urllib.error
import json
import sys
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000"

passed = 0
failed = 0

def log_test(name, success, details=""):
    global passed, failed
    if success:
        passed += 1
        print(f"  [PASS] {name} {details}")
    else:
        failed += 1
        print(f"  [FAIL] {name} - {details}")

def make_req(endpoint, method="GET", body=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(body).encode('utf-8') if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode('utf-8')
            return resp.status, json.loads(resp_body) if resp_body else None
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(resp_body)
        except Exception:
            return e.code, resp_body
    except Exception as e:
        return 500, str(e)

print("\n" + "="*70)
print("COMPREHENSIVE FULL-SYSTEM VERIFICATION SUITE")
print("="*70)

# 1. Base Health & Swagger
print("\n--- 1. Base System & Docs ---")
status, res = make_req("/")
log_test("Root Endpoint /", status == 200 and res.get("status") == "healthy", f"Status: {status}")

status, res = make_req("/docs")
log_test("Swagger Docs /docs", status == 200, f"Status: {status}")

# 2. Authentication: Login Existing Demo Accounts
print("\n--- 2. Authentication & JWT ---")
status, student_auth = make_req("/api/auth/login", "POST", {
    "email": "rahul@student.edu",
    "password": "student123"
})
student_token = student_auth.get("access_token") if status == 200 else None
log_test("Student Login (Rahul)", status == 200 and student_token is not None, f"User: {student_auth.get('user', {}).get('name') if status == 200 else ''}")

status, admin_auth = make_req("/api/auth/login", "POST", {
    "email": "admin@college.edu",
    "password": "adminpassword123"
})
admin_token = admin_auth.get("access_token") if status == 200 else None
log_test("Admin Login", status == 200 and admin_token is not None, f"Role: {admin_auth.get('user', {}).get('role') if status == 200 else ''}")

# Login invalid credentials
status, res = make_req("/api/auth/login", "POST", {
    "email": "admin@college.edu",
    "password": "wrongpassword"
})
log_test("Login With Wrong Password (401)", status == 401, f"Expected 401, got {status}")

status, res = make_req("/api/auth/login", "POST", {
    "email": "nonexistent@college.edu",
    "password": "somepassword"
})
log_test("Login Non-existent User (401)", status == 401, f"Expected 401, got {status}")

# 3. Registration: Create New Student Account
print("\n--- 3. User Registration Flow ---")
import random
test_num = random.randint(1000, 9999)
new_email = f"teststudent_{test_num}@student.edu"
new_sid = f"TEST-{test_num}"

status, new_user_res = make_req("/api/auth/register", "POST", {
    "name": f"Test Student {test_num}",
    "email": new_email,
    "password": "securepass123",
    "student_id": new_sid,
    "department": "Computer Science"
})
new_user_token = new_user_res.get("access_token") if status == 201 else None
log_test("Register New Student (201)", status == 201 and new_user_token is not None, f"Email: {new_email}")

# Duplicate registration check
status, dup_res = make_req("/api/auth/register", "POST", {
    "name": "Duplicate Student",
    "email": new_email,
    "password": "securepass123"
})
log_test("Prevent Duplicate Email (409)", status == 409, f"Expected 409, got {status}")

status, dup_sid_res = make_req("/api/auth/register", "POST", {
    "name": "Duplicate SID",
    "email": f"other_{test_num}@student.edu",
    "password": "securepass123",
    "student_id": new_sid
})
log_test("Prevent Duplicate Student ID (409)", status == 409, f"Expected 409, got {status}")

# 4. User Profile endpoints (/api/users/me)
print("\n--- 4. User Profile Management ---")
status, profile = make_req("/api/users/me", "GET", token=new_user_token)
log_test("Get Own Profile (GET /api/users/me)", status == 200 and profile.get("email") == new_email, f"Name: {profile.get('name')}")

status, updated_profile = make_req("/api/users/me", "PUT", {
    "name": f"Updated Test Student {test_num}",
    "department": "Data Science"
}, token=new_user_token)
log_test("Update Own Profile (PUT /api/users/me)", status == 200 and updated_profile.get("department") == "Data Science", f"New Dept: {updated_profile.get('department')}")

# Unauthenticated profile access check
status, res = make_req("/api/users/me", "GET")
log_test("Profile Access Without Token (401)", status == 401, f"Expected 401, got {status}")

# 5. Events Catalog & Filtering
print("\n--- 5. Event Discovery & Filters ---")
status, all_events = make_req("/api/events")
log_test("List All Events (GET /api/events)", status == 200 and isinstance(all_events, list) and len(all_events) > 0, f"Found {len(all_events)} events")

status, search_events = make_req("/api/events?search=Hackathon")
log_test("Search Filter (?search=Hackathon)", status == 200 and any("Hackathon" in e["title"] or "Hackathon" in e["category"] for e in search_events), f"Found {len(search_events)} matches")

status, cat_events = make_req("/api/events?category=Technical")
log_test("Category Filter (?category=Technical)", status == 200 and all(e["category"] == "Technical" for e in cat_events), f"Found {len(cat_events)} technical events")

status, up_events = make_req("/api/events?date_filter=upcoming")
log_test("Date Filter Upcoming (?date_filter=upcoming)", status == 200, f"Found {len(up_events)} upcoming events")

status, past_events = make_req("/api/events?date_filter=past")
log_test("Date Filter Past (?date_filter=past)", status == 200, f"Found {len(past_events)} past events")

status, asc_events = make_req("/api/events?sort_by=date_asc")
status_desc, desc_events = make_req("/api/events?sort_by=date_desc")
log_test("Sorting (date_asc vs date_desc)", status == 200 and status_desc == 200, f"ASC first: {asc_events[0]['event_date']}, DESC first: {desc_events[0]['event_date']}")

# Detail view
first_event_id = all_events[0]["id"]
status, event_detail = make_req(f"/api/events/{first_event_id}")
log_test(f"Get Event Detail (/api/events/{first_event_id})", status == 200 and "available_seats" in event_detail, f"Title: {event_detail.get('title')}")

status, res = make_req("/api/events/999999")
log_test("Get Non-existent Event Detail (404)", status == 404, f"Expected 404, got {status}")

# 6. Admin Event CRUD Management
print("\n--- 6. Admin Event Management (CRUD) ---")
tomorrow = (date.today() + timedelta(days=10)).isoformat()
status, created_event = make_req("/api/events", "POST", {
    "title": f"Automated Test Symposium {test_num}",
    "description": "Comprehensive test event for automated verification.",
    "category": "Workshop",
    "venue": "Lab 404",
    "event_date": tomorrow,
    "start_time": "10:00",
    "end_time": "13:00",
    "capacity": 2, # Small capacity to test capacity limits
    "organizer": "QA Automated Testing Team"
}, token=admin_token)
created_event_id = created_event.get("id") if status == 201 else None
log_test("Admin Create Event (201)", status == 201 and created_event_id is not None, f"Event ID: {created_event_id}")

# Student attempting to create event -> Forbidden (403)
status, res = make_req("/api/events", "POST", {
    "title": "Unauthorized Event",
    "description": "Should fail",
    "category": "Workshop",
    "venue": "Lab 1",
    "event_date": tomorrow,
    "start_time": "10:00",
    "end_time": "12:00",
    "capacity": 50,
    "organizer": "Hacker"
}, token=student_token)
log_test("Student Forbidden From Creating Event (403)", status == 403, f"Expected 403, got {status}")

# Admin Update Event
status, updated_event = make_req(f"/api/events/{created_event_id}", "PUT", {
    "title": f"Automated Test Symposium (Updated) {test_num}",
    "venue": "Main Auditorium"
}, token=admin_token)
log_test("Admin Update Event (PUT)", status == 200 and updated_event.get("venue") == "Main Auditorium", f"New Venue: {updated_event.get('venue')}")

# 7. Student Registration Workflow, Duplicate Prevention & Capacity Enforcement
print("\n--- 7. Registration Workflow & Seat Capacity ---")
# Register Rahul (Student 1) for newly created event (capacity 2)
status, reg1 = make_req(f"/api/events/{created_event_id}/register", "POST", {}, token=student_token)
log_test("Student 1 Registers (Seat 1/2)", status == 201, f"Reg ID: {reg1.get('id') if status == 201 else ''}")

# Rahul attempts duplicate registration -> 409 Conflict
status, dup_reg = make_req(f"/api/events/{created_event_id}/register", "POST", {}, token=student_token)
log_test("Student 1 Duplicate Registration Blocked (409)", status == 409, f"Expected 409, got {status}")

# Register New Student (Seat 2/2)
status, reg2 = make_req(f"/api/events/{created_event_id}/register", "POST", {}, token=new_user_token)
log_test("Student 2 Registers (Seat 2/2 - Event Full)", status == 201, f"Reg ID: {reg2.get('id') if status == 201 else ''}")

# Priya (Student 3) attempts to register when capacity is 2/2 -> 409 Conflict (Full capacity)
status, priya_auth = make_req("/api/auth/login", "POST", {
    "email": "priya@student.edu",
    "password": "student123"
})
priya_token = priya_auth.get("access_token")
status, full_reg = make_req(f"/api/events/{created_event_id}/register", "POST", {}, token=priya_token)
log_test("Capacity Limit Enforcement on Full Event (409)", status == 409, f"Expected 409 (Event Full), got {status}")

# Check Event Detail shows is_full = True and 0 available seats
status, event_status = make_req(f"/api/events/{created_event_id}")
log_test("Event Reflects Full Capacity State", status == 200 and event_status.get("is_full") == True and event_status.get("available_seats") == 0, f"Available: {event_status.get('available_seats')}")

# Student 1 Cancels Registration
status, cancel_res = make_req(f"/api/events/{created_event_id}/register", "DELETE", token=student_token)
log_test("Student 1 Cancels Registration (DELETE)", status == 200, f"Msg: {cancel_res.get('message') if status == 200 else ''}")

# Now Priya can register since a seat opened up!
status, priya_reg = make_req(f"/api/events/{created_event_id}/register", "POST", {}, token=priya_token)
log_test("New Student Registers Into Freed Seat", status == 201, f"Reg ID: {priya_reg.get('id') if status == 201 else ''}")

# Check Student's My Registrations list
status, my_regs = make_req("/api/my-registrations", "GET", token=priya_token)
log_test("Get My Registrations (/api/my-registrations)", status == 200 and any(r["event_id"] == created_event_id for r in my_regs), f"Total Regs: {len(my_regs)}")

# 8. Admin Participants Roster & Stats
print("\n--- 8. Admin Roster & Analytics ---")
status, participants = make_req(f"/api/admin/events/{created_event_id}/participants", "GET", token=admin_token)
log_test("Admin Get Event Attendee Roster", status == 200 and participants.get("total_participants") >= 2, f"Attendees: {participants.get('total_participants')}")

# Student forbidden from viewing participants roster
status, res = make_req(f"/api/admin/events/{created_event_id}/participants", "GET", token=student_token)
log_test("Student Forbidden From Viewing Roster (403)", status == 403, f"Expected 403, got {status}")

# Admin Dashboard Analytics
status, admin_stats = make_req("/api/admin/dashboard", "GET", token=admin_token)
log_test("Admin Dashboard KPI Stats", status == 200 and "total_students" in admin_stats and "registrations_by_event" in admin_stats, f"Students: {admin_stats.get('total_students')}, Events: {admin_stats.get('total_events')}")

# Admin Users List
status, all_users = make_req("/api/admin/users", "GET", token=admin_token)
log_test("Admin Get All Users List", status == 200 and len(all_users) >= 5, f"Users Count: {len(all_users)}")

# 9. Clean up / Delete Test Event
print("\n--- 9. Delete Event & Cleanup ---")
status, del_res = make_req(f"/api/events/{created_event_id}", "DELETE", token=admin_token)
log_test("Admin Delete Event (DELETE)", status == 200, f"Msg: {del_res.get('message') if status == 200 else ''}")

# Verify deleted event is gone (404)
status, res = make_req(f"/api/events/{created_event_id}")
log_test("Deleted Event Returns 404", status == 404, f"Expected 404, got {status}")

print("\n" + "="*70)
print(f"VERIFICATION SUMMARY: {passed} PASSED, {failed} FAILED")
print("="*70)

if failed > 0:
    sys.exit(1)
else:
    sys.exit(0)
