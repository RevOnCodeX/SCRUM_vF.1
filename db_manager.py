from firebase_setup import get_db

def get_firestore_client():
    return get_db()

# --- Teams & Roster ---
def get_all_teams():
    db = get_db()
    docs = db.collection('teams').stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_team_by_id(team_id):
    db = get_db()
    doc = db.collection('teams').document(str(team_id)).get()
    return {"id": doc.id, **doc.to_dict()} if doc.exists else None

def get_team_roster(team_id=None):
    db = get_db()
    query = db.collection('team_roster')
    if team_id:
        query = query.where('team_id', '==', int(team_id))
    docs = query.stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_employee_by_email(email):
    db = get_db()
    docs = db.collection('team_roster').where('email', '==', email.lower().strip()).limit(1).stream()
    for d in docs:
        return {"id": d.id, **d.to_dict()}
    return None

# --- Scrum & Sprint ---
def get_active_sprints(team_id):
    db = get_db()
    docs = db.collection('scrum_sprint').where('team_id', '==', int(team_id)).where('is_closed', '==', 0).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_sprint_items(sprint_id):
    db = get_db()
    docs = db.collection('scrum_sprint_item').where('sprint_id', '==', int(sprint_id)).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

# --- Leave Requests ---
def get_leave_requests(team_id=None, limit=100):
    db = get_db()
    query = db.collection('leave_requests').order_by('created_at', direction='DESCENDING').limit(limit)
    # Note: Firestore requires composite index for where + order_by. We'll do simple filter in memory if needed.
    docs = query.stream()
    results = [{"id": d.id, **d.to_dict()} for d in docs]
    if team_id:
        # In-memory filter for now to avoid needing composite indexes instantly
        results = [r for r in results if r.get('team_id') == int(team_id)]
    return results

def add_leave_request(data):
    db = get_db()
    _, doc_ref = db.collection('leave_requests').add(data)
    return doc_ref.id

def update_leave_status(leave_id, status, approver_email):
    db = get_db()
    db.collection('leave_requests').document(str(leave_id)).update({
        'status': status,
        'approved_by': approver_email
    })
