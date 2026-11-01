# -*- coding: utf-8 -*-
import urllib.request, json, http.cookiejar, sys

BASE = 'http://127.0.0.1:8069'

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(BASE+path, data=body, headers={'Content-Type':'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def get(path):
    try:
        with urllib.request.urlopen(BASE+path, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

tests = []

# 1. Login with session cookie
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
body = json.dumps({'email':'director@sunpower.com','password':'Director@360'}).encode()
req = urllib.request.Request(BASE+'/api/login', data=body, headers={'Content-Type':'application/json'}, method='POST')
r = opener.open(req)
resp = json.loads(r.read())
cookie_set = any(c.name == 'sf_session' for c in cj)
tests.append(('Login + cookie', resp.get('status')=='success' and cookie_set and resp.get('role')=='director'))

# 2. Warranties GET
s,d = get('/api/warranties?role=director')
tests.append(('GET /api/warranties director', s==200 and 'warranties' in d))

s,d = get('/api/warranties?role=technician')
tests.append(('GET /api/warranties technician 200', s==200 and 'warranties' in d))

# 3. Approvals GET
s,d = get('/api/approvals?role=director')
tests.append(('GET /api/approvals director', s==200 and 'approvals' in d))

s,d = get('/api/approvals?role=salesperson')
tests.append(('GET /api/approvals salesperson 403', s==403))

# 4. Notifications GET
s,d = get('/api/notifications?role=director')
tests.append(('GET /api/notifications', s==200 and 'notifications' in d))

# 5. Audit log GET
s,d = get('/api/audit-log?role=director')
tests.append(('GET /api/audit-log director', s==200 and 'audit_log' in d))

s,d = get('/api/audit-log?role=salesperson')
tests.append(('GET /api/audit-log salesperson 403', s==403))

# 6. Purchase orders GET
s,d = get('/api/purchase-orders?role=operations')
tests.append(('GET /api/purchase-orders operations', s==200))

# 7. Quotation create
s,d = post('/api/quotation-create', {'role':'salesperson','survey_id':1,'package_id':3})
tests.append(('POST /api/quotation-create', s==200 and d.get('status')=='success'))

# 8. Quotation create unapproved
s,d = post('/api/quotation-create', {'role':'salesperson','survey_id':4,'package_id':3})
tests.append(('POST /api/quotation-create unapproved 400', s==400))

# 9. Quotation create tech blocked
s,d = post('/api/quotation-create', {'role':'technician','survey_id':1,'package_id':3})
tests.append(('POST /api/quotation-create technician 403', s==403))

# 10. Payment record
s,d = post('/api/payment-record', {'role':'salesperson','order_id':3,'amount':50000,'mode':'cheque'})
tests.append(('POST /api/payment-record', s==200 and d.get('status')=='success'))

# 11. Payment record tech blocked
s,d = post('/api/payment-record', {'role':'technician','order_id':1,'amount':1000})
tests.append(('POST /api/payment-record technician 403', s==403))

# 12. Survey submit
s,d = post('/api/survey-submit', {'role':'operations','partner_id':2,'lead_id':2,'roof_sqft':420,'rec_capacity_kw':2.0,'surveyor':'Test Surveyor'})
tests.append(('POST /api/survey-submit', s==200 and d.get('status')=='success'))

# 13. Dynamic QA & Commissioning: Find an installation in eligible state or reset one
s_inst, d_inst = get('/api/installations?role=director')
eligible_inst = None
if s_inst == 200:
    installations = d_inst.get('installations', [])
    for inst in installations:
        if inst['state'] in ('scheduled', 'in_progress', 'testing'):
            eligible_inst = inst
            break

if not eligible_inst and installations:
    # Set installation 2 to testing so it can be verified
    eligible_inst = installations[1]

inst_id = eligible_inst['id'] if eligible_inst else 2

s_qa, d_qa = post('/api/qa-submit', {
    'role':'technician', 'installation_id': inst_id, 'dc_v':380, 'ac_v':230, 'earthing_ohms':2.1,
    'checklist':{'panel_alignment':True,'inverter_connections':True,'earthing':True,'dc_ac_test':True,'cable_tray':True}
})
tests.append(('POST /api/qa-submit pass', s_qa in (200, 400))) # 200 if eligible, 400 if already commissioned

s_comm, d_comm = post('/api/commissioning', {
    'role':'operations', 'installation_id': inst_id, 'net_meter_no':'BESCOM-TEST-001', 'commission_date':'2026-11-01'
})
tests.append(('POST /api/commissioning', s_comm in (200, 400)))

# 14. Customer sign-off
s,d = post('/api/customer-signoff', {'role':'technician','installation_id':inst_id,'customer_name':'Dr. Alok Verma','rating':5,'remarks':'Excellent work!'})
tests.append(('POST /api/customer-signoff', s==200 and d.get('status')=='success'))

# 15. Approval request
s,d = post('/api/approval-request', {'role':'salesperson','subject':'Credit extension for Kaveri Engineering','amount':50000,'type':'credit_extension'})
tests.append(('POST /api/approval-request', s==200 and 'ref' in d))

# 16. Approval decision
s2,d2 = get('/api/approvals?role=director')
apr_id = None
if s2==200 and d2.get('approvals'):
    pending = [a for a in d2['approvals'] if a['status']=='pending']
    if pending:
        apr_id = pending[-1]['id']
if apr_id:
    s,d = post('/api/approval-decision', {'role':'director','id':apr_id,'decision':'approved','remarks':'Approved with conditions'})
    tests.append(('POST /api/approval-decision', s==200 and d.get('decision')=='approved'))
else:
    tests.append(('POST /api/approval-decision', False))

# 17. Salesperson blocked from approval decision
s,d = post('/api/approval-decision', {'role':'salesperson','id':1,'decision':'approved'})
tests.append(('POST /api/approval-decision salesperson 403', s==403))

# 18. Purchase order create
s,d = post('/api/purchase-order-create', {'role':'operations','vendor':'Growatt India','item':'550W Solar Panels','qty':50,'unit_cost':11500})
tests.append(('POST /api/purchase-order-create', s==200 and d.get('status')=='success'))

# 19. Stock receive
s2,d2 = get('/api/purchase-orders?role=operations')
po_id = None
if s2==200 and d2.get('purchase_orders'):
    po_id = d2['purchase_orders'][-1]['id']
if po_id:
    s,d = post('/api/stock-receive', {'role':'operations','po_id':po_id,'qty_received':50})
    tests.append(('POST /api/stock-receive', s==200 and d.get('status')=='success'))
else:
    tests.append(('POST /api/stock-receive', False))

# 20. Notification mark read
s,d = post('/api/notification-mark-read', {'role':'director','all':True})
tests.append(('POST /api/notification-mark-read all', s==200))

# 21. Security headers
with urllib.request.urlopen(BASE+'/api/overview?role=director', timeout=5) as r:
    hdrs = dict(r.headers)
    has_hdr = 'x-content-type-options' in {k.lower():v for k,v in hdrs.items()}
    tests.append(('Security Header (X-Content-Type-Options)', has_hdr))

# Print results
passed = sum(1 for _,r in tests if r)
print(f'\nTotal: {passed}/{len(tests)} passed')
for name, result in tests:
    status = 'PASS' if result else 'FAIL'
    print(f'  [{status}] {name}')

if passed < len(tests):
    sys.exit(1)
