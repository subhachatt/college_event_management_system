import urllib.request
import urllib.error
import json
import sys

def run_tests():
    print("========================================")
    print("COLLEGE EVENT MANAGEMENT SYSTEM API TESTS")
    print("========================================")

    # 1. Health check
    res = urllib.request.urlopen("http://127.0.0.1:8000/")
    assert res.status == 200, "Root endpoint failed"
    print("[OK] 1. Backend health check: OK")

    # 2. Events listing
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/events")
    events = json.loads(res.read().decode())
    assert len(events) >= 8, f"Expected >= 8 events, got {len(events)}"
    print(f"[OK] 2. GET /api/events: OK ({len(events)} events loaded)")

    # 3. Student Login
    login_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/auth/login",
        data=json.dumps({"email": "rahul@student.edu", "password": "student123"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(login_req)
    student_auth = json.loads(res.read().decode())
    student_token = student_auth["access_token"]
    student_id = student_auth["user"]["id"]
    print(f"[OK] 3. Student Login: OK (Logged in as {student_auth['user']['name']})")

    # 4. Admin Login
    admin_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/auth/login",
        data=json.dumps({"email": "admin@college.edu", "password": "adminpassword123"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(admin_req)
    admin_auth = json.loads(res.read().decode())
    admin_token = admin_auth["access_token"]
    print(f"[OK] 4. Admin Login: OK (Logged in as {admin_auth['user']['name']})")

    # 5. Admin Dashboard Stats
    dash_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    res = urllib.request.urlopen(dash_req)
    stats = json.loads(res.read().decode())
    assert stats["total_students"] >= 5, "Stats check failed"
    print(f"[OK] 5. Admin Stats: OK (Students: {stats['total_students']}, Events: {stats['total_events']}, Active Regs: {stats['active_registrations']})")

    # 6. Student cannot access Admin Dashboard (403 Forbidden check)
    try:
        forbidden_req = urllib.request.Request(
            "http://127.0.0.1:8000/api/admin/dashboard",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        urllib.request.urlopen(forbidden_req)
        print("[FAIL] 6. Security Check Failed: Student accessed admin API")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        assert e.code == 403, f"Expected 403, got {e.code}"
        print("[OK] 6. Security Enforcement: OK (Student received 403 Forbidden on admin endpoint)")

    # 7. Student Registration for Event & Duplicate Prevention
    # Choose event 6 ("VentureVibe")
    reg_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/events/6/register",
        data=b"{}",
        headers={"Authorization": f"Bearer {student_token}", "Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(reg_req)
    reg_data = json.loads(res.read().decode())
    print(f"[OK] 7. Event Registration: OK (Registered for Event #6, Registration ID: {reg_data['id']})")

    # Duplicate check:
    try:
        urllib.request.urlopen(reg_req)
        print("[FAIL] 8. Duplicate Check Failed: Student registered twice")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        assert e.code == 409, f"Expected 409 Conflict, got {e.code}"
        print("[OK] 8. Duplicate Prevention: OK (409 Conflict returned)")

    # 9. Cancel Registration
    cancel_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/events/6/register",
        headers={"Authorization": f"Bearer {student_token}"},
        method="DELETE"
    )
    res = urllib.request.urlopen(cancel_req)
    assert res.status == 200, "Cancel registration failed"
    print("[OK] 9. Cancel Registration: OK")

    # 10. Student My Registrations
    my_regs_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/my-registrations",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    res = urllib.request.urlopen(my_regs_req)
    my_regs = json.loads(res.read().decode())
    print(f"[OK] 10. GET /api/my-registrations: OK ({len(my_regs)} registrations retrieved)")

    # 11. Admin Participant List
    parts_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/admin/events/1/participants",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    res = urllib.request.urlopen(parts_req)
    parts_data = json.loads(res.read().decode())
    print(f"[OK] 11. GET /api/admin/events/1/participants: OK ({parts_data['total_participants']} attendees found)")

    # 12. Create New Student via Register Endpoint
    new_student_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/auth/register",
        data=json.dumps({
            "name": "Ananya Sen",
            "email": "ananya@student.edu",
            "password": "studentpass123",
            "student_id": "CS-2025-099",
            "department": "Computer Science"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        res = urllib.request.urlopen(new_student_req)
        new_auth = json.loads(res.read().decode())
        print(f"[OK] 12. Student Registration Endpoint: OK (Created user '{new_auth['user']['name']}')")
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("[OK] 12. Student Registration Endpoint: User already created in previous test run")
        else:
            raise e

    print("========================================")
    print("ALL 12 VERIFICATION SUITES PASSED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    run_tests()
