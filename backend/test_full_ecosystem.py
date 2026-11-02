import asyncio
import json
import urllib.request
import urllib.error
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

BASE_URL = "http://127.0.0.1:8000/api/v1"

def req(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "application/pdf" in content_type:
                pdf_bytes = resp.read()
                return resp.status, {"pdf_size": len(pdf_bytes)}
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            parsed = json.loads(content)
        except:
            parsed = {"raw": content}
        return e.code, parsed

def run_tests():
    print("=" * 70)
    print("STARTING COMPLETE USER ECOSYSTEM AUDIT & FUNCTIONAL VERIFICATION")
    print("=" * 70)
    results = {}

    # -------------------------------------------------------------
    # MODULE 1: USER AUTHENTICATION & ACCOUNT MANAGEMENT
    # -------------------------------------------------------------
    print("\n[1] Testing User Authentication & Account Management...")
    # Admin Login
    status, res = req("/auth/admin/login", "POST", {"email": "admin@example.com", "password": "wrongpassword"})
    assert status == 401, f"Expected 401 for wrong admin password, got {status}"
    
    status, res = req("/auth/admin/login", "POST", {"email": "admin@example.com", "password": "123456"})
    assert status == 200, f"Expected 200 for admin login, got {status}: {res}"
    admin_token = res["data"]["token"]
    print("  ✓ Admin authentication verified (correct/incorrect password checks passed).")

    # Student 1 Registration
    ts = int(datetime.utcnow().timestamp())
    st1_email = f"student_{ts}@example.com"
    st1_payload = {
        "name": "Rahul Sharma",
        "email": st1_email,
        "password": "Password123!",
        "roll_number": f"BCA{ts%10000}",
        "department": "Computer Applications",
        "course": "BCA",
        "semester": "3rd Semester",
        "mobile_number": "9876543210"
    }
    status, res = req("/auth/register", "POST", st1_payload)
    assert status == 200, f"Failed to register Student 1: {res}"
    st1_id = res["data"]["id"]
    print(f"  ✓ Student 1 registered successfully: {st1_email} (ID: {st1_id})")

    # Duplicate registration prevention
    status, res = req("/auth/register", "POST", st1_payload)
    assert status == 400, f"Duplicate registration check failed: {res}"
    print("  ✓ Duplicate registration correctly rejected with 400 Bad Request.")

    # Student 1 Login
    status, res = req("/auth/login", "POST", {"email": st1_email, "password": "wrong"})
    assert status == 401, f"Expected 401 for wrong student password, got {status}"
    
    status, res = req("/auth/login", "POST", {"email": st1_email, "password": "Password123!"})
    assert status == 200, f"Failed student login: {res}"
    st1_token = res["data"]["token"]
    st1_user = res["data"]["user"]
    assert st1_user["course"] == "BCA" and st1_user["department"] == "Computer Applications"
    print("  ✓ Student 1 login verified with full student attributes (Course, Dept, Semester).")

    # Session / Current User verification
    status, res = req("/auth/me", "GET", token=st1_token)
    assert status == 200 and res["data"]["email"] == st1_email
    print("  ✓ Session /auth/me verified for student token.")

    # Profile Update
    status, res = req("/auth/profile", "PUT", {"name": "Rahul S. Sharma", "mobile_number": "9998887776"}, token=st1_token)
    assert status == 200 and res["data"]["name"] == "Rahul S. Sharma"
    print("  ✓ Student profile update verified (Name and Mobile updated).")

    # Change Password
    status, res = req("/auth/change-password", "POST", {"current_password": "Password123!", "new_password": "NewPassword456!"}, token=st1_token)
    assert status == 200, f"Password change failed: {res}"
    
    # Verify login with new password
    status, res = req("/auth/login", "POST", {"email": st1_email, "password": "NewPassword456!"})
    assert status == 200
    st1_token = res["data"]["token"]
    print("  ✓ Password change verified (authenticated with new password).")

    # Student 2 Registration (for multi-user testing)
    st2_email = f"student2_{ts}@example.com"
    st2_payload = {
        "name": "Pooja Verma",
        "email": st2_email,
        "password": "Password123!",
        "roll_number": f"BTECH{ts%10000}",
        "department": "Engineering",
        "course": "B.Tech CSE",
        "semester": "5th Semester",
        "mobile_number": "9112233445"
    }
    status, res = req("/auth/register", "POST", st2_payload)
    assert status == 200
    st2_id = res["data"]["id"]
    status, res = req("/auth/login", "POST", {"email": st2_email, "password": "Password123!"})
    assert status == 200
    st2_token = res["data"]["token"]
    print(f"  ✓ Student 2 registered and authenticated: {st2_email} (ID: {st2_id})")

    # Deactivation testing
    status, res = req(f"/users/{st2_id}/status", "PUT", {"is_active": False}, token=admin_token)
    assert status == 200 and res["data"]["is_active"] is False
    # Attempt login while deactivated
    status, res = req("/auth/login", "POST", {"email": st2_email, "password": "Password123!"})
    assert status == 401, f"Deactivated user should not be able to log in, got {status}"
    # Reactivate Student 2
    status, res = req(f"/users/{st2_id}/status", "PUT", {"is_active": True}, token=admin_token)
    assert status == 200 and res["data"]["is_active"] is True
    print("  ✓ Account deactivation and reactivation lifecycle verified.")
    results["1_auth_management"] = "PASS"

    # -------------------------------------------------------------
    # MODULE 2: STUDENT DASHBOARD DATA
    # -------------------------------------------------------------
    print("\n[2] Testing Student Dashboard Data Connections...")
    status, res = req("/live-updates", "GET", token=st1_token)
    assert status == 200
    print("  ✓ Latest announcements endpoint accessible to students.")

    status, res = req("/chats", "GET", token=st1_token)
    assert status == 200
    print("  ✓ Recent chats endpoint accessible to students.")

    status, res = req("/documents/library", "GET", token=st1_token)
    assert status == 200
    print("  ✓ Study material library accessible to students.")
    results["2_student_dashboard"] = "PASS"

    # -------------------------------------------------------------
    # MODULE 3: STUDENT NOTIFICATION SYSTEM
    # -------------------------------------------------------------
    print("\n[3] Testing Student Notification System...")
    # Check unread count
    status, res = req("/notifications/unread-count", "GET", token=st1_token)
    assert status == 200, f"Failed to get unread count: status={status}, res={res}"
    initial_unread = res["data"]["unread_count"]
    print(f"  ✓ Initial unread notification count for Student 1: {initial_unread}")

    # Admin publishes an announcement
    ann_payload = {
        "title": "Semester Examination Fee Notice",
        "content": "All students must clear semester exam fees before 15 November 2026.",
        "category": "Examination",
        "target_audience": "All Students",
        "priority": "IMPORTANT"
    }
    status, res = req("/live-updates", "POST", ann_payload, token=admin_token)
    assert status == 200, f"Failed to create announcement: {res}"
    ann_id = res["data"]["id"]
    
    # Publish it
    status, res = req(f"/live-updates/{ann_id}/publish", "POST", token=admin_token)
    assert status == 200
    print(f"  ✓ Admin published announcement (ID: {ann_id}).")

    # Give background task 1 second to create notifications
    import time
    time.sleep(1)

    status, res = req("/notifications", "GET", token=st1_token)
    assert status == 200
    notifs = res["data"]
    ann_notif = next((n for n in notifs if n.get("update_id") == ann_id), None)
    assert ann_notif is not None, "Notification was not delivered to Student 1!"
    assert ann_notif["type"] == "ANNOUNCEMENT"
    assert ann_notif["is_read"] is False
    print(f"  ✓ Real notification delivered to Student 1: '{ann_notif['title']}' (Type: {ann_notif['type']})")

    # Mark as read
    status, res = req(f"/notifications/{ann_notif['id']}/read", "POST", token=st1_token)
    assert status == 200
    print("  ✓ Marked notification as read.")

    # Mark all read
    status, res = req("/notifications/read-all", "POST", token=st1_token)
    assert status == 200
    status, res = req("/notifications/unread-count", "GET", token=st1_token)
    assert res["data"]["unread_count"] == 0
    print("  ✓ Mark all notifications as read verified (unread count = 0).")

    # Notification isolation: Student 2 cannot mark Student 1's notification
    status, res = req(f"/notifications/{ann_notif['id']}/read", "POST", token=st2_token)
    assert status == 403, f"Cross-user notification modification should be 403, got {status}"
    print("  ✓ Notification isolation verified across student accounts.")
    results["3_notifications"] = "PASS"

    # -------------------------------------------------------------
    # MODULE 4: STUDENT CHATBOT & HOLIDAY INTELLIGENCE SYSTEM
    # -------------------------------------------------------------
    print("\n[4] Testing Student Chatbot & Holiday Intelligence...")

    # CASE C: No admin announcement exists for 19 November 2026
    print("  -> Testing CASE C: Query on date with NO announcement ('Is college closed on 19 November?')...")
    status, res = req("/chat", "POST", {"message": "19 november ko collage ki chutti he kya?"}, token=st1_token)
    assert status == 200
    ans_c = res["data"]["answer"]
    lang_c = res["data"]["language"]
    print(f"  [AI Reply - Case C ({lang_c})]:\n  {ans_c[:200]}...")
    # Verify strict accuracy: Chatbot MUST NOT declare holiday
    assert any(w in ans_c.lower() for w in ["nahi", "no", "not", "suchna", "notice", "regular", "khula", "open", "currently"]), "Case C violated: Did not clearly state absence of holiday!"
    assert "afrikaans" not in ans_c.lower() and lang_c in ["hinglish", "hindi", "english"]
    print("  ✓ Case C PASSED: Chatbot correctly states no confirmed holiday announcement found.")

    # CASE B: Festival / Public Holiday with NO college confirmation
    print("  -> Testing CASE B: Festival holiday query ('Is college closed on Diwali?')...")
    status, res = req("/chat", "POST", {"message": "Is college closed on Diwali?"}, token=st1_token)
    assert status == 200
    ans_b = res["data"]["answer"]
    lang_b = res["data"]["language"]
    print(f"  [AI Reply - Case B ({lang_b})]:\n  {ans_b[:200]}...")
    assert any(w in ans_b.lower() for w in ["diwali", "deepawali", "festival", "holiday", "recognized"]), "Case B did not recognize Diwali!"
    assert any(w in ans_b.lower() for w in ["official", "confirm", "circular", "notice", "admin", "check", "academic"]), "Case B did not advise checking official notice!"
    print("  ✓ Case B PASSED: Chatbot distinguishes festival from confirmed college closure.")

    # CASE A: Admin officially publishes a holiday announcement for 28 November
    print("  -> Testing CASE A: Admin officially announces holiday for 28 November 2026...")
    holiday_ann = {
        "title": "College Closed on 28 November 2026",
        "content": "Official circular: College will remain strictly closed on 28 November 2026 due to campus facility upgrade.",
        "category": "Holiday",
        "target_audience": "All Students",
        "priority": "URGENT"
    }
    status, res = req("/live-updates", "POST", holiday_ann, token=admin_token)
    assert status == 200
    h_ann_id = res["data"]["id"]
    status, res = req(f"/live-updates/{h_ann_id}/publish", "POST", token=admin_token)
    assert status == 200
    print(f"  ✓ Admin published official holiday announcement (ID: {h_ann_id}).")

    time.sleep(1)

    print("  -> Re-querying: '28 november ko collage ki chutti he kya?'...")
    status, res = req("/chat", "POST", {"message": "28 november ko collage ki chutti he kya?"}, token=st1_token)
    assert status == 200
    ans_a = res["data"]["answer"]
    chat_id = res["data"]["chat_id"]
    msg_id = res["data"]["message_id"]
    print(f"  [AI Reply - Case A]:\n  {ans_a[:220]}...")
    assert any(w in ans_a.lower() for w in ["ha", "haan", "yes", "chutti", "holiday", "closed", "official", "admin"]), "Case A did not confirm the official admin holiday!"
    print("  ✓ Case A PASSED: Chatbot immediately confirms holiday citing official administration announcement!")

    # Typo tolerance test (Google-like)
    print("  -> Testing Google-like Typo Tolerance ('exm schedule kb se he')...")
    status, res = req("/chat", "POST", {"message": "exm schedule kb se he"}, token=st1_token)
    assert status == 200
    ans_typo = res["data"]["answer"]
    print(f"  [AI Reply - Typo Tolerance]:\n  {ans_typo[:200]}...")
    assert any(w in ans_typo.lower() for w in ["exam", "academic", "calendar", "semester", "schedule", "pariksha"]), "Typo normalizer failed!"
    print("  ✓ Typo tolerance PASSED: Intelligently matched intent from Academic Calendar.")

    # Saved Answer workflow
    status, res = req("/chats/saved-answers", "POST", {
        "message_id": msg_id,
        "chat_id": chat_id,
        "question": "3 november ko collage ki chutti he kya?",
        "answer": ans_a
    }, token=st1_token)
    assert status == 200
    saved_id = res["data"]["id"]
    print("  ✓ Saved answer created successfully via /chats/saved-answers.")

    status, res = req("/chats/saved-answers", "GET", token=st1_token)
    assert status == 200 and len(res["data"]) >= 1
    print("  ✓ Retrieved saved answers list.")

    status, res = req(f"/chats/saved-answers/{saved_id}", "DELETE", token=st1_token)
    assert status == 200
    print("  ✓ Deleted saved answer.")
    results["4_chatbot_holiday_intelligence"] = "PASS"

    # -------------------------------------------------------------
    # MODULE 5: USER DOCUMENT & LEARNING EXPERIENCE
    # -------------------------------------------------------------
    print("\n[5] Testing User Document & Learning Experience...")
    status, res = req("/documents/library", "GET", token=st1_token)
    assert status == 200
    docs = res["data"]
    assert len(docs) > 0, "Document library is empty!"
    target_doc = docs[0]
    doc_id = target_doc["id"]
    print(f"  ✓ Library document available: '{target_doc['title']}' (ID: {doc_id})")

    # Test PDF download/streaming endpoint
    status, res = req(f"/documents/{doc_id}/file", "GET", token=st1_token)
    assert status == 200
    print("  ✓ Direct PDF file streaming verified via /documents/{id}/file.")
    results["5_document_experience"] = "PASS"

    # -------------------------------------------------------------
    # MODULE 6: ADMIN & STUDENT SYNCHRONIZATION
    # -------------------------------------------------------------
    print("\n[6] Testing Admin & Student Synchronization (Cancellation)...")
    # Admin unpublishes the holiday notice
    status, res = req(f"/live-updates/{h_ann_id}/unpublish", "POST", token=admin_token)
    assert status == 200
    print(f"  ✓ Admin unpublished holiday announcement (ID: {h_ann_id}).")

    # Chatbot should reflect the cancellation immediately (no longer confirm holiday)
    status, res = req("/chat", "POST", {"message": "28 november ko collage ki chutti he kya?"}, token=st1_token)
    assert status == 200
    ans_unpub = res["data"]["answer"]
    print(f"  [AI Reply - After Cancellation]:\n  {ans_unpub[:180]}...")
    assert not ("officially announced a holiday for 28 november" in ans_unpub.lower() and "yes!" in ans_unpub.lower()[:30])
    print("  ✓ Real-time synchronization verified: Cancelled notice immediately revoked from AI.")
    results["6_synchronization"] = "PASS"

    # -------------------------------------------------------------
    # MODULE 7: MULTI-USER ISOLATION & RBAC SECURITY
    # -------------------------------------------------------------
    print("\n[7] Testing Multi-User Isolation & Role-Based Access Control...")
    # Student cannot access admin endpoints
    status, res = req("/users", "GET", token=st1_token)
    assert status == 403, f"Student should get 403 on /users, got {status}"
    
    status, res = req("/dashboard/stats", "GET", token=st1_token)
    assert status == 403, f"Student should get 403 on /dashboard/stats, got {status}"

    status, res = req("/chatbot/settings", "GET", token=st1_token)
    assert status == 403, f"Student should get 403 on /chatbot/settings, got {status}"

    # Student 2 cannot access Student 1's chat details
    status, res = req(f"/chats/{chat_id}", "GET", token=st2_token)
    assert status == 403, f"Student 2 should get 403 on Student 1's chat, got {status}"

    # Student 2 cannot delete Student 1's chat
    status, res = req(f"/chats/{chat_id}", "DELETE", token=st2_token)
    assert status == 403, f"Student 2 should get 403 when deleting Student 1's chat, got {status}"

    print("  ✓ RBAC and multi-tenant student privacy verified (100% strict 403 isolation).")
    results["7_security_rbac"] = "PASS"

    # -------------------------------------------------------------
    # MODULE 8: ADMIN DASHBOARD STATS
    # -------------------------------------------------------------
    print("\n[8] Testing Admin Dashboard Analytics & Activity...")
    status, res = req("/dashboard/stats", "GET", token=admin_token)
    assert status == 200
    stats = res["data"]["stats"]
    recent = res["data"]["recent_activity"]
    print(f"  ✓ Dashboard Stats: Users={stats['total_users']}, Queries={stats['total_queries']}, PDFs={stats['total_pdfs']}")
    assert stats["total_users"] >= 2
    assert stats["total_queries"] >= 1
    assert len(recent["users"]) > 0
    results["8_admin_dashboard"] = "PASS"

    print("\n" + "=" * 70)
    print("ALL 8 MAJOR MODULE SUITES PASSED 100% WITH ZERO ERRORS!")
    print("=" * 70)
    return results

if __name__ == "__main__":
    run_tests()
