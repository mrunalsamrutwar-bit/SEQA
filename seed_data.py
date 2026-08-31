import json
from database import db, User, Project, DfdLevel, Component, DataFlow, ActivityLog

TEMPLATES_DATA = [
    {
        'id': 'tpl_online_shopping',
        'name': 'Online Shopping System',
        'category': 'E-Commerce & Retail',
        'description': 'Comprehensive multi-level DFD for e-commerce covering user authentication, product catalog browsing, cart checkout, payment processing, and order fulfillment.',
        'system_name': 'E-Commerce Shopping Portal',
        'dfd_level': 'Level 1',
        'tags': 'E-Commerce, Shopping, Orders, Payment',
        'levels': [
            {
                'level_number': 0,
                'level_name': 'Level 0 – Context Diagram',
                'parent_process_id': None,
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Customer', 'desc': 'Online shopper browsing and purchasing products', 'x': 80, 'y': 180, 'meta': {'entity_type': 'End User'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Payment Gateway', 'desc': 'External payment service provider', 'x': 680, 'y': 80, 'meta': {'entity_type': 'Third-Party System'}},
                    {'type': 'entity', 'identifier': 'E3', 'name': 'System Administrator', 'desc': 'Manages catalog, inventory, and orders', 'x': 680, 'y': 280, 'meta': {'entity_type': 'Internal Staff'}},
                    {'type': 'process', 'identifier': '0.0', 'name': 'Online Shopping System', 'desc': 'Central e-commerce processing system boundary', 'x': 380, 'y': 180, 'meta': {}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Login & Order Request', 'desc': 'Customer submits credentials and cart checkout', 'src': 'E1', 'dst': '0.0', 'type': 'JSON Payload'},
                    {'identifier': 'F2', 'name': 'Order Confirmation & Invoice', 'desc': 'System returns purchase receipt and status', 'src': '0.0', 'dst': 'E1', 'type': 'PDF / JSON'},
                    {'identifier': 'F3', 'name': 'Payment Charge Request', 'desc': 'System transmits encrypted payment token', 'src': '0.0', 'dst': 'E2', 'type': 'Encrypted Token'},
                    {'identifier': 'F4', 'name': 'Payment Auth & Settlement', 'desc': 'Payment gateway confirms transaction status', 'src': 'E2', 'dst': '0.0', 'type': 'Webhook / Callback'},
                    {'identifier': 'F5', 'name': 'Inventory & Product Updates', 'desc': 'Admin creates products and updates stock', 'src': 'E3', 'dst': '0.0', 'type': 'Admin Payload'},
                    {'identifier': 'F6', 'name': 'Sales & Analytics Reports', 'desc': 'System generates real-time business reports', 'src': '0.0', 'dst': 'E3', 'type': 'Report Data'}
                ]
            },
            {
                'level_number': 1,
                'level_name': 'Level 1 – Main Processes',
                'parent_process_id': '0.0',
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Customer', 'desc': 'Browses items and places orders', 'x': 60, 'y': 180, 'meta': {'entity_type': 'End User'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Payment Gateway', 'desc': 'Secure external processor', 'x': 860, 'y': 360, 'meta': {'entity_type': 'Third-Party System'}},
                    {'type': 'entity', 'identifier': 'E3', 'name': 'Admin Staff', 'desc': 'Manages catalog inventory', 'x': 60, 'y': 440, 'meta': {'entity_type': 'Internal Staff'}},
                    
                    {'type': 'process', 'identifier': '1.0', 'name': 'User Authentication', 'desc': 'Authenticates customer and admin logins', 'x': 320, 'y': 80, 'meta': {}},
                    {'type': 'process', 'identifier': '2.0', 'name': 'Product & Catalog Browsing', 'desc': 'Searches, filters, and displays products', 'x': 320, 'y': 240, 'meta': {}},
                    {'type': 'process', 'identifier': '3.0', 'name': 'Order Processing', 'desc': 'Handles cart checkout, order calculation, and fulfillment', 'x': 580, 'y': 240, 'meta': {}},
                    {'type': 'process', 'identifier': '4.0', 'name': 'Payment Settlement', 'desc': 'Coordinates tokenized payment authorization', 'x': 580, 'y': 420, 'meta': {}},

                    {'type': 'datastore', 'identifier': 'D1', 'name': 'User Database', 'desc': 'Stores user profiles, roles, and credentials', 'x': 600, 'y': 80, 'meta': {'storage_type': 'PostgreSQL'}},
                    {'type': 'datastore', 'identifier': 'D2', 'name': 'Product Database', 'desc': 'Stores product details, prices, and stock inventory', 'x': 60, 'y': 320, 'meta': {'storage_type': 'PostgreSQL / Redis'}},
                    {'type': 'datastore', 'identifier': 'D3', 'name': 'Order Database', 'desc': 'Stores line items, shipping status, and history', 'x': 860, 'y': 180, 'meta': {'storage_type': 'PostgreSQL'}},
                    {'type': 'datastore', 'identifier': 'D4', 'name': 'Transaction Database', 'desc': 'Stores payment receipts and audit trail', 'x': 860, 'y': 520, 'meta': {'storage_type': 'PostgreSQL'}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Login Credentials', 'desc': 'Username & password hash', 'src': 'E1', 'dst': '1.0', 'type': 'Credentials'},
                    {'identifier': 'F2', 'name': 'User Profile Query', 'desc': 'Validates user account data', 'src': '1.0', 'dst': 'D1', 'type': 'SQL Query'},
                    {'identifier': 'F3', 'name': 'Auth Token & Session', 'desc': 'Returns verified JWT token', 'src': '1.0', 'dst': 'E1', 'type': 'JWT Token'},
                    
                    {'identifier': 'F4', 'name': 'Product Search Query', 'desc': 'Filters and search keywords', 'src': 'E1', 'dst': '2.0', 'type': 'Search Request'},
                    {'identifier': 'F5', 'name': 'Fetch Product Catalog', 'desc': 'Reads available stock and pricing', 'src': 'D2', 'dst': '2.0', 'type': 'Catalog Records'},
                    {'identifier': 'F6', 'name': 'Product Listing & Details', 'desc': 'Displays item information to user', 'src': '2.0', 'dst': 'E1', 'type': 'Product Catalog'},
                    {'identifier': 'F7', 'name': 'Catalog Updates', 'desc': 'Admin updates inventory quantities', 'src': 'E3', 'dst': '2.0', 'type': 'Inventory Update'},
                    {'identifier': 'F8', 'name': 'Save Product Info', 'desc': 'Persists updated item data', 'src': '2.0', 'dst': 'D2', 'type': 'Product Write'},

                    {'identifier': 'F9', 'name': 'Cart Checkout Request', 'desc': 'Customer confirms cart items', 'src': 'E1', 'dst': '3.0', 'type': 'Order Payload'},
                    {'identifier': 'F10', 'name': 'Create Order Record', 'desc': 'Saves pending order with line items', 'src': '3.0', 'dst': 'D3', 'type': 'Order Record'},
                    {'identifier': 'F11', 'name': 'Trigger Payment', 'desc': 'Passes invoice amount to payment process', 'src': '3.0', 'dst': '4.0', 'type': 'Payment Amount'},
                    
                    {'identifier': 'F12', 'name': 'Authorize Payment Request', 'desc': 'Sends token to gateway', 'src': '4.0', 'dst': 'E2', 'type': 'Payment Token'},
                    {'identifier': 'F13', 'name': 'Payment Status Callback', 'desc': 'Gateway returns success/failure code', 'src': 'E2', 'dst': '4.0', 'type': 'Webhook'},
                    {'identifier': 'F14', 'name': 'Save Transaction Log', 'desc': 'Records payment receipt in DB', 'src': '4.0', 'dst': 'D4', 'type': 'Transaction Record'},
                    {'identifier': 'F15', 'name': 'Update Order Status (Paid)', 'desc': 'Marks order as confirmed and paid', 'src': '4.0', 'dst': '3.0', 'type': 'Payment Confirmation'},
                    {'identifier': 'F16', 'name': 'Order Receipt & Confirmation', 'desc': 'Delivers final invoice to customer', 'src': '3.0', 'dst': 'E1', 'type': 'Invoice Receipt'}
                ]
            }
        ]
    },
    {
        'id': 'tpl_hospital_management',
        'name': 'Hospital & Patient Care System',
        'category': 'Healthcare & Medical',
        'description': 'Comprehensive medical workflow diagram managing patient appointments, clinical electronic health records (EHR), lab diagnostic orders, and automated insurance billing.',
        'system_name': 'Healthcare Operations & EHR Portal',
        'dfd_level': 'Level 1',
        'tags': 'Healthcare, Hospital, Patient, EHR, Medical',
        'levels': [
            {
                'level_number': 0,
                'level_name': 'Level 0 – Context Diagram',
                'parent_process_id': None,
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Patient', 'desc': 'Registers, books visits, and receives prescriptions', 'x': 80, 'y': 180, 'meta': {'entity_type': 'End User'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Doctor / Clinician', 'desc': 'Conducts consultations and orders lab tests', 'x': 680, 'y': 80, 'meta': {'entity_type': 'Medical Staff'}},
                    {'type': 'entity', 'identifier': 'E3', 'name': 'Diagnostic Laboratory', 'desc': 'Executes blood/imaging tests and delivers results', 'x': 680, 'y': 280, 'meta': {'entity_type': 'Diagnostic Dept'}},
                    {'type': 'process', 'identifier': '0.0', 'name': 'Hospital Care Management System', 'desc': 'Unified hospital information system', 'x': 380, 'y': 180, 'meta': {}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Appointment Request & Vitals', 'desc': 'Patient books slot', 'src': 'E1', 'dst': '0.0', 'type': 'Appointment Data'},
                    {'identifier': 'F2', 'name': 'Prescription & Visit Summary', 'desc': 'Medical instructions for patient', 'src': '0.0', 'dst': 'E1', 'type': 'Medical Summary'},
                    {'identifier': 'F3', 'name': 'Clinical Notes & Test Orders', 'desc': 'Doctor diagnosis and treatment plan', 'src': 'E2', 'dst': '0.0', 'type': 'Diagnosis Payload'},
                    {'identifier': 'F4', 'name': 'Patient EHR History', 'desc': 'System presents patient past records to clinician', 'src': '0.0', 'dst': 'E2', 'type': 'EHR Record'},
                    {'identifier': 'F5', 'name': 'Lab Test Orders', 'desc': 'Dispatches required investigations', 'src': '0.0', 'dst': 'E3', 'type': 'Lab Specimen Order'},
                    {'identifier': 'F6', 'name': 'Verified Lab Reports', 'desc': 'Diagnostic lab uploads verified findings', 'src': 'E3', 'dst': '0.0', 'type': 'Lab Results'}
                ]
            },
            {
                'level_number': 1,
                'level_name': 'Level 1 – Main Processes',
                'parent_process_id': '0.0',
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Patient', 'desc': 'Healthcare recipient', 'x': 60, 'y': 140, 'meta': {'entity_type': 'End User'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Doctor', 'desc': 'Physician evaluating clinical cases', 'x': 60, 'y': 420, 'meta': {'entity_type': 'Medical Staff'}},
                    {'type': 'entity', 'identifier': 'E3', 'name': 'Insurance Provider', 'desc': 'Third party insurer for claims processing', 'x': 860, 'y': 420, 'meta': {'entity_type': 'External Agency'}},

                    {'type': 'process', 'identifier': '1.0', 'name': 'Appointment Scheduling', 'desc': 'Coordinates doctor schedules and slot allocations', 'x': 320, 'y': 100, 'meta': {}},
                    {'type': 'process', 'identifier': '2.0', 'name': 'Clinical Diagnosis & EHR', 'desc': 'Records symptoms, diagnoses, and prescriptions', 'x': 320, 'y': 340, 'meta': {}},
                    {'type': 'process', 'identifier': '3.0', 'name': 'Laboratory Test Processing', 'desc': 'Manages diagnostic orders and test telemetry', 'x': 600, 'y': 200, 'meta': {}},
                    {'type': 'process', 'identifier': '4.0', 'name': 'Billing & Claims Settlement', 'desc': 'Generates itemized invoice and insurance claims', 'x': 600, 'y': 420, 'meta': {}},

                    {'type': 'datastore', 'identifier': 'D1', 'name': 'Patient Records DB', 'desc': 'Master demographic and identity records', 'x': 60, 'y': 260, 'meta': {'storage_type': 'Encrypted HIPAA DB'}},
                    {'type': 'datastore', 'identifier': 'D2', 'name': 'Appointment Schedule DB', 'desc': 'Clinician calendar and room reservations', 'x': 580, 'y': 60, 'meta': {'storage_type': 'PostgreSQL'}},
                    {'type': 'datastore', 'identifier': 'D3', 'name': 'Medical History (EHR) DB', 'desc': 'Prescriptions, clinical notes, past treatments', 'x': 860, 'y': 160, 'meta': {'storage_type': 'Secure FHIR DB'}},
                    {'type': 'datastore', 'identifier': 'D4', 'name': 'Billing & Claims DB', 'desc': 'Invoices, co-pay receipts, claim approvals', 'x': 860, 'y': 560, 'meta': {'storage_type': 'SQL Database'}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Booking Request', 'desc': 'Patient requests consultation slot', 'src': 'E1', 'dst': '1.0', 'type': 'Appointment Request'},
                    {'identifier': 'F2', 'name': 'Schedule Slot & Verify', 'desc': 'Reserves doctor slot in calendar', 'src': '1.0', 'dst': 'D2', 'type': 'Calendar Entry'},
                    {'identifier': 'F3', 'name': 'Appointment Confirmation', 'desc': 'Notifies patient with appointment ticket', 'src': '1.0', 'dst': 'E1', 'type': 'Booking Ticket'},
                    
                    {'identifier': 'F4', 'name': 'Clinical Notes & Diagnosis', 'desc': 'Doctor logs physical findings and notes', 'src': 'E2', 'dst': '2.0', 'type': 'Consultation Notes'},
                    {'identifier': 'F5', 'name': 'Fetch Past Medical History', 'desc': 'Retrieves previous clinical timeline', 'src': 'D3', 'dst': '2.0', 'type': 'Historical EHR'},
                    {'identifier': 'F6', 'name': 'Save Diagnosis & Prescription', 'desc': 'Writes current treatment to permanent EHR', 'src': '2.0', 'dst': 'D3', 'type': 'EHR Record'},
                    {'identifier': 'F7', 'name': 'Provide Prescription to Patient', 'desc': 'Gives medication list to patient', 'src': '2.0', 'dst': 'E1', 'type': 'Prescription Slip'},

                    {'identifier': 'F8', 'name': 'Order Lab Investigation', 'desc': 'Doctor requests pathology panel', 'src': '2.0', 'dst': '3.0', 'type': 'Lab Order'},
                    {'identifier': 'F9', 'name': 'Store Diagnostic Results', 'desc': 'Attaches lab results to patient history', 'src': '3.0', 'dst': 'D3', 'type': 'Lab Findings'},

                    {'identifier': 'F10', 'name': 'Billable Items & Services', 'desc': 'Sends consultation and lab costs to billing', 'src': '2.0', 'dst': '4.0', 'type': 'Cost Items'},
                    {'identifier': 'F11', 'name': 'Submit Insurance Claim', 'desc': 'Sends ICD-10 diagnostic claim packet', 'src': '4.0', 'dst': 'E3', 'type': 'Insurance Claim'},
                    {'identifier': 'F12', 'name': 'Claim Adjudication & Payout', 'desc': 'Insurer approves and settles payment', 'src': 'E3', 'dst': '4.0', 'type': 'Settlement Notice'},
                    {'identifier': 'F13', 'name': 'Save Invoice & Payment', 'desc': 'Records financial ledger entry', 'src': '4.0', 'dst': 'D4', 'type': 'Invoice Record'},
                    {'identifier': 'F14', 'name': 'Final Hospital Bill Receipt', 'desc': 'Provides clear receipt to patient', 'src': '4.0', 'dst': 'E1', 'type': 'Final Receipt'}
                ]
            }
        ]
    },
    {
        'id': 'tpl_banking_system',
        'name': 'Banking & Fund Transfer System',
        'category': 'Finance & Banking',
        'description': 'Mission-critical financial DFD illustrating account balance inquiries, real-time fund transfers, fraud detection scoring, and transaction ledger auditing.',
        'system_name': 'Core Banking Transaction Engine',
        'dfd_level': 'Level 1',
        'tags': 'Banking, Finance, Ledger, Fraud Detection',
        'levels': [
            {
                'level_number': 0,
                'level_name': 'Level 0 – Context Diagram',
                'parent_process_id': None,
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Account Holder', 'desc': 'Bank customer initiating transfers and inquiries', 'x': 80, 'y': 180, 'meta': {'entity_type': 'Customer'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Interbank Clearing Network (ACH/SWIFT)', 'desc': 'External interbank clearinghouse', 'x': 680, 'y': 80, 'meta': {'entity_type': 'Clearing House'}},
                    {'type': 'entity', 'identifier': 'E3', 'name': 'Central Bank Compliance', 'desc': 'Regulatory audit reporting body', 'x': 680, 'y': 280, 'meta': {'entity_type': 'Regulatory Authority'}},
                    {'type': 'process', 'identifier': '0.0', 'name': 'Core Banking & Payment System', 'desc': 'High-availability core banking system boundary', 'x': 380, 'y': 180, 'meta': {}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Transfer Instruction & PIN', 'desc': 'Customer commands transfer with authorization', 'src': 'E1', 'dst': '0.0', 'type': 'Transfer Payload'},
                    {'identifier': 'F2', 'name': 'Transaction Receipt & Balance SMS', 'desc': 'System confirms debit and updated balance', 'src': '0.0', 'dst': 'E1', 'type': 'Confirmation SMS'},
                    {'identifier': 'F3', 'name': 'External Wire Settlement', 'desc': 'Routes interbank settlement message', 'src': '0.0', 'dst': 'E2', 'type': 'SWIFT / ISO 20022'},
                    {'identifier': 'F4', 'name': 'Inbound Clearing Credit', 'desc': 'Receives external deposit clearance', 'src': 'E2', 'dst': '0.0', 'type': 'Clearing Credit'},
                    {'identifier': 'F5', 'name': 'Regulatory AML Audit Log', 'desc': 'Automated anti-money laundering reporting', 'src': '0.0', 'dst': 'E3', 'type': 'AML Compliance Report'}
                ]
            },
            {
                'level_number': 1,
                'level_name': 'Level 1 – Main Processes',
                'parent_process_id': '0.0',
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Account Holder', 'desc': 'Bank customer', 'x': 60, 'y': 180, 'meta': {'entity_type': 'Customer'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Central Clearing Network', 'desc': 'ACH / SWIFT Network', 'x': 860, 'y': 360, 'meta': {'entity_type': 'Clearing House'}},
                    
                    {'type': 'process', 'identifier': '1.0', 'name': 'Customer Authentication & 2FA', 'desc': 'Validates biometrics, PIN, and OTP tokens', 'x': 320, 'y': 80, 'meta': {}},
                    {'type': 'process', 'identifier': '2.0', 'name': 'Fraud Risk Scoring', 'desc': 'Evaluates transaction anomaly signals in real-time', 'x': 320, 'y': 280, 'meta': {}},
                    {'type': 'process', 'identifier': '3.0', 'name': 'Fund Transfer Execution', 'desc': 'Performs double-entry debit/credit ledger operations', 'x': 580, 'y': 280, 'meta': {}},
                    {'type': 'process', 'identifier': '4.0', 'name': 'Audit & Statement Generation', 'desc': 'Produces certified account statements and audit traces', 'x': 580, 'y': 480, 'meta': {}},

                    {'type': 'datastore', 'identifier': 'D1', 'name': 'Customer Account DB', 'desc': 'Master account balances, limits, and profiles', 'x': 600, 'y': 80, 'meta': {'storage_type': 'Oracle DB / High Availability'}},
                    {'type': 'datastore', 'identifier': 'D2', 'name': 'Fraud Rules Engine DB', 'desc': 'Risk heuristics, velocity thresholds, blacklists', 'x': 60, 'y': 420, 'meta': {'storage_type': 'Redis / In-Memory'}},
                    {'type': 'datastore', 'identifier': 'D3', 'name': 'General Ledger & Transactions DB', 'desc': 'Immutable financial transaction ledger', 'x': 860, 'y': 160, 'meta': {'storage_type': 'Immutable Ledger DB'}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Auth Credentials & OTP', 'desc': 'Login credentials with second factor', 'src': 'E1', 'dst': '1.0', 'type': 'Credentials'},
                    {'identifier': 'F2', 'name': 'Verify Account & Status', 'desc': 'Checks active status and KYC tier', 'src': '1.0', 'dst': 'D1', 'type': 'Account Verification'},
                    {'identifier': 'F3', 'name': 'Session Security Token', 'desc': 'Authenticated session issued', 'src': '1.0', 'dst': 'E1', 'type': 'Secure Session'},

                    {'identifier': 'F4', 'name': 'Transfer Request', 'desc': 'Destination account, amount, currency', 'src': 'E1', 'dst': '2.0', 'type': 'Transfer Instruction'},
                    {'identifier': 'F5', 'name': 'Fetch Risk Heuristics', 'desc': 'Reads anomaly and blacklist rules', 'src': 'D2', 'dst': '2.0', 'type': 'Risk Parameters'},
                    {'identifier': 'F6', 'name': 'Approved Risk Assessment', 'desc': 'Passes clean transaction to ledger engine', 'src': '2.0', 'dst': '3.0', 'type': 'Approved Transaction'},

                    {'identifier': 'F7', 'name': 'Debit Source Balance', 'desc': 'Deducts funds from payer account', 'src': '3.0', 'dst': 'D1', 'type': 'Debit Ledger'},
                    {'identifier': 'F8', 'name': 'Record Immutable Ledger Entry', 'desc': 'Appends transaction record into ledger', 'src': '3.0', 'dst': 'D3', 'type': 'Ledger Record'},
                    {'identifier': 'F9', 'name': 'Interbank Clearing Wire', 'desc': 'Transmits external bank settlement message', 'src': '3.0', 'dst': 'E2', 'type': 'SWIFT Wire'},
                    {'identifier': 'F10', 'name': 'Transfer Receipt & Confirmation', 'desc': 'Sends real-time confirmation receipt', 'src': '3.0', 'dst': 'E1', 'type': 'Transfer Receipt'},

                    {'identifier': 'F11', 'name': 'Fetch Ledger Transactions', 'desc': 'Queries historical records for period', 'src': 'D3', 'dst': '4.0', 'type': 'Statement Query'},
                    {'identifier': 'F12', 'name': 'Monthly Account Statement', 'desc': 'Delivers itemized statement to customer', 'src': '4.0', 'dst': 'E1', 'type': 'PDF Statement'}
                ]
            }
        ]
    },
    {
        'id': 'tpl_university_management',
        'name': 'University Student & Course System',
        'category': 'Education & Academia',
        'description': 'Academic administration DFD covering student admission, course registration, prerequisite validation, grade processing, and transcript generation.',
        'system_name': 'Campus Student Information System (SIS)',
        'dfd_level': 'Level 1',
        'tags': 'University, Education, Student, Grades, Courses',
        'levels': [
            {
                'level_number': 0,
                'level_name': 'Level 0 – Context Diagram',
                'parent_process_id': None,
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Student', 'desc': 'Enrolls in classes, views grades, pays fees', 'x': 80, 'y': 180, 'meta': {'entity_type': 'Student'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Faculty / Professor', 'desc': 'Submits attendance, assignments, and exam grades', 'x': 680, 'y': 80, 'meta': {'entity_type': 'Faculty'}},
                    {'type': 'entity', 'identifier': 'E3', 'name': 'University Registrar', 'desc': 'Oversees curriculum catalog, graduation, and transcripts', 'x': 680, 'y': 280, 'meta': {'entity_type': 'Staff'}},
                    {'type': 'process', 'identifier': '0.0', 'name': 'Campus Information System', 'desc': 'Central university administrative software', 'x': 380, 'y': 180, 'meta': {}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Course Enrollment Request', 'desc': 'Selected semester courses', 'src': 'E1', 'dst': '0.0', 'type': 'Enrollment Form'},
                    {'identifier': 'F2', 'name': 'Class Schedule & Grade Report', 'desc': 'Timetable and academic transcript', 'src': '0.0', 'dst': 'E1', 'type': 'Academic Report'},
                    {'identifier': 'F3', 'name': 'Final Grades & Attendance', 'desc': 'Instructor grade book submission', 'src': 'E2', 'dst': '0.0', 'type': 'Grade Matrix'},
                    {'identifier': 'F4', 'name': 'Course Roster & Student List', 'desc': 'List of enrolled students per course', 'src': '0.0', 'dst': 'E2', 'type': 'Roster Data'},
                    {'identifier': 'F5', 'name': 'Curriculum & Degree Rules', 'desc': 'Academic degree requirement updates', 'src': 'E3', 'dst': '0.0', 'type': 'Curriculum Specs'},
                    {'identifier': 'F6', 'name': 'Graduation Audit Report', 'desc': 'Degree progress evaluation', 'src': '0.0', 'dst': 'E3', 'type': 'Audit Report'}
                ]
            },
            {
                'level_number': 1,
                'level_name': 'Level 1 – Main Processes',
                'parent_process_id': '0.0',
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Student', 'desc': 'University student', 'x': 60, 'y': 140, 'meta': {'entity_type': 'Student'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Faculty Member', 'desc': 'Course instructor', 'x': 860, 'y': 380, 'meta': {'entity_type': 'Faculty'}},

                    {'type': 'process', 'identifier': '1.0', 'name': 'Student Admission & Registration', 'desc': 'Creates student account, assigns roll number and major', 'x': 320, 'y': 80, 'meta': {}},
                    {'type': 'process', 'identifier': '2.0', 'name': 'Course Enrollment & Prerequisite Check', 'desc': 'Validates prerequisites and available class seats', 'x': 320, 'y': 280, 'meta': {}},
                    {'type': 'process', 'identifier': '3.0', 'name': 'Grade Recording & GPA Computation', 'desc': 'Calculates semester GPA and cumulative CGPA', 'x': 600, 'y': 280, 'meta': {}},
                    {'type': 'process', 'identifier': '4.0', 'name': 'Fee Payment & Financial Clearance', 'desc': 'Processes tuition payments and generates fee receipts', 'x': 600, 'y': 480, 'meta': {}},

                    {'type': 'datastore', 'identifier': 'D1', 'name': 'Student Records DB', 'desc': 'Personal info, enrolled major, and academic status', 'x': 60, 'y': 360, 'meta': {'storage_type': 'MySQL DB'}},
                    {'type': 'datastore', 'identifier': 'D2', 'name': 'Course Catalog DB', 'desc': 'Course codes, syllabi, prerequisites, and max capacities', 'x': 600, 'y': 80, 'meta': {'storage_type': 'MySQL DB'}},
                    {'type': 'datastore', 'identifier': 'D3', 'name': 'Academic Grades DB', 'desc': 'Official transcripts, letter grades, and credits earned', 'x': 860, 'y': 160, 'meta': {'storage_type': 'MySQL DB'}},
                    {'type': 'datastore', 'identifier': 'D4', 'name': 'Tuition & Fee Accounts DB', 'desc': 'Dues ledger, fee receipts, and scholarship records', 'x': 860, 'y': 560, 'meta': {'storage_type': 'SQL DB'}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Application & Bio Data', 'desc': 'Student registration submission', 'src': 'E1', 'dst': '1.0', 'type': 'Student Profile'},
                    {'identifier': 'F2', 'name': 'Create Student Record', 'desc': 'Stores new student profile in database', 'src': '1.0', 'dst': 'D1', 'type': 'Student Record'},
                    {'identifier': 'F3', 'name': 'Admission Card & ID', 'desc': 'Delivers student credential and ID', 'src': '1.0', 'dst': 'E1', 'type': 'ID Card'},

                    {'identifier': 'F4', 'name': 'Course Selection Form', 'desc': 'Chosen elective and core courses', 'src': 'E1', 'dst': '2.0', 'type': 'Course List'},
                    {'identifier': 'F5', 'name': 'Check Course Availability', 'desc': 'Verifies prerequisites and open seats', 'src': 'D2', 'dst': '2.0', 'type': 'Catalog Query'},
                    {'identifier': 'F6', 'name': 'Confirmed Schedule', 'desc': 'Returns weekly timetable to student', 'src': '2.0', 'dst': 'E1', 'type': 'Timetable'},

                    {'identifier': 'F7', 'name': 'Exam Scores & Grades', 'desc': 'Professor inputs semester marks', 'src': 'E2', 'dst': '3.0', 'type': 'Grade Matrix'},
                    {'identifier': 'F8', 'name': 'Store Official Transcript', 'desc': 'Writes computed GPA to records', 'src': '3.0', 'dst': 'D3', 'type': 'Transcript Record'},
                    {'identifier': 'F9', 'name': 'Semester Grade Sheet', 'desc': 'Provides formal report card to student', 'src': '3.0', 'dst': 'E1', 'type': 'Report Card'},

                    {'identifier': 'F10', 'name': 'Tuition Payment', 'desc': 'Student pays semester fees', 'src': 'E1', 'dst': '4.0', 'type': 'Payment Data'},
                    {'identifier': 'F11', 'name': 'Save Fee Receipt Record', 'desc': 'Records clearance in finance ledger', 'src': '4.0', 'dst': 'D4', 'type': 'Financial Clearance'},
                    {'identifier': 'F12', 'name': 'Fee Clearance Receipt', 'desc': 'Delivers paid tuition voucher', 'src': '4.0', 'dst': 'E1', 'type': 'Payment Receipt'}
                ]
            }
        ]
    },
    {
        'id': 'tpl_library_system',
        'name': 'Library Management & Catalog System',
        'category': 'Information Systems',
        'description': 'Standard library operations DFD detailing book search, issue/return transactions, barcode checkout, and overdue fine calculation.',
        'system_name': 'Automated Library Information System',
        'dfd_level': 'Level 1',
        'tags': 'Library, Books, Catalog, Circulation',
        'levels': [
            {
                'level_number': 0,
                'level_name': 'Level 0 – Context Diagram',
                'parent_process_id': None,
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Library Member', 'desc': 'Searches, borrows, and returns books', 'x': 80, 'y': 180, 'meta': {'entity_type': 'Member'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Librarian Staff', 'desc': 'Acquires books, catalogs titles, manages inventory', 'x': 680, 'y': 180, 'meta': {'entity_type': 'Staff'}},
                    {'type': 'process', 'identifier': '0.0', 'name': 'Library Circulation System', 'desc': 'Core library management system boundary', 'x': 380, 'y': 180, 'meta': {}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Book Search & Borrow Request', 'desc': 'Member searches titles and presents membership card', 'src': 'E1', 'dst': '0.0', 'type': 'Borrow Request'},
                    {'identifier': 'F2', 'name': 'Issued Book & Due Date Slip', 'desc': 'System confirms loan and due date', 'src': '0.0', 'dst': 'E1', 'type': 'Issue Slip'},
                    {'identifier': 'F3', 'name': 'New Book Acquisitions & Catalog Data', 'desc': 'Librarian registers new ISBN titles', 'src': 'E2', 'dst': '0.0', 'type': 'Book Metadata'},
                    {'identifier': 'F4', 'name': 'Overdue Books & Circulation Reports', 'desc': 'System provides overdue fine report', 'src': '0.0', 'dst': 'E2', 'type': 'Inventory Report'}
                ]
            }
        ]
    },
    {
        'id': 'tpl_online_exam',
        'name': 'Online Examination & Assessment System',
        'category': 'Education & Testing',
        'description': 'Robust assessment DFD featuring question bank randomization, live candidate proctoring, auto-grading engine, and certificate generation.',
        'system_name': 'Computer-Based Testing (CBT) Platform',
        'dfd_level': 'Level 1',
        'tags': 'Exam, Assessment, Testing, Proctoring',
        'levels': [
            {
                'level_number': 0,
                'level_name': 'Level 0 – Context Diagram',
                'parent_process_id': None,
                'components': [
                    {'type': 'entity', 'identifier': 'E1', 'name': 'Exam Candidate', 'desc': 'Student taking assessment', 'x': 80, 'y': 180, 'meta': {'entity_type': 'Student'}},
                    {'type': 'entity', 'identifier': 'E2', 'name': 'Exam Proctor / Examiner', 'desc': 'Monitors test sessions and verifies test integrity', 'x': 680, 'y': 80, 'meta': {'entity_type': 'Examiner'}},
                    {'type': 'entity', 'identifier': 'E3', 'name': 'Certification Authority', 'desc': 'Issues digital accredited credentials', 'x': 680, 'y': 280, 'meta': {'entity_type': 'Authority'}},
                    {'type': 'process', 'identifier': '0.0', 'name': 'Online Examination System', 'desc': 'Assessment delivery and automated grading platform', 'x': 380, 'y': 180, 'meta': {}}
                ],
                'flows': [
                    {'identifier': 'F1', 'name': 'Exam Key & Question Answers', 'desc': 'Candidate submits test responses', 'src': 'E1', 'dst': '0.0', 'type': 'Exam Answers'},
                    {'identifier': 'F2', 'name': 'Question Stream & Scorecard', 'desc': 'Live questions and final test result', 'src': '0.0', 'dst': 'E1', 'type': 'Test Questions / Score'},
                    {'identifier': 'F3', 'name': 'Question Bank & Answer Keys', 'desc': 'Examiner uploads question syllabus', 'src': 'E2', 'dst': '0.0', 'type': 'Item Bank'},
                    {'identifier': 'F4', 'name': 'Live Proctoring Video Feed', 'desc': 'Real-time telemetry and proctor alerts', 'src': '0.0', 'dst': 'E2', 'type': 'Proctor Stream'},
                    {'identifier': 'F5', 'name': 'Verified Score & Candidate Record', 'desc': 'Transmits passing scores for badge issuance', 'src': '0.0', 'dst': 'E3', 'type': 'Certificate Payload'}
                ]
            }
        ]
    }
]

def init_seed_data(app):
    """
    Initializes database tables, creates default admin user, and creates
    the full demo 'Online Shopping System' project on first launch.
    """
    with app.app_context():
        db.create_all()

        # 1. Check or create demo admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@dfdarchitect.io',
                full_name='Mrunal (Lead Systems Architect)',
                role='Principal Software Architect',
                preferences_json=json.dumps({
                    'theme': 'light',
                    'grid_visible': True,
                    'snap_to_grid': True,
                    'grid_size': 20,
                    'auto_save': True,
                    'notation_style': 'gane_sarson' # or 'yourdon_demarcos'
                })
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

        # 2. Check if Demo project exists, if not instantiate Online Shopping System demo
        demo_project = Project.query.filter_by(is_demo=True).first()
        if not demo_project and admin_user:
            instantiate_template(TEMPLATES_DATA[0], admin_user.id, is_demo=True)


def instantiate_template(template_data, user_id, project_name=None, is_demo=False):
    """
    Creates a full Project instance from template configuration.
    """
    proj_name = project_name or template_data['name']
    if is_demo:
        proj_name = f"Demo: {template_data['name']}"

    project = Project(
        user_id=user_id,
        name=proj_name,
        description=template_data['description'],
        system_name=template_data['system_name'],
        dfd_level=template_data['dfd_level'],
        author='Lead Software Architect',
        version='1.0.0',
        tags=template_data.get('tags', 'DFD, Architecture'),
        status='Completed' if is_demo else 'In Progress',
        is_demo=is_demo
    )
    db.session.add(project)
    db.session.flush()

    # Create levels, components, and flows
    for lvl_idx, lvl_data in enumerate(template_data.get('levels', [])):
        level = DfdLevel(
            project_id=project.id,
            level_number=lvl_data.get('level_number', lvl_idx),
            level_name=lvl_data.get('level_name', f"Level {lvl_idx}"),
            parent_process_id=lvl_data.get('parent_process_id'),
            notes=f"Decomposition hierarchy for {proj_name}."
        )
        db.session.add(level)
        db.session.flush()

        comp_ref_map = {} # identifier -> Component instance

        # Create components
        for comp_data in lvl_data.get('components', []):
            comp = Component(
                project_id=project.id,
                level_id=level.id,
                component_type=comp_data['type'],
                component_identifier=comp_data['identifier'],
                name=comp_data['name'],
                description=comp_data.get('desc', ''),
                pos_x=comp_data.get('x', 100.0),
                pos_y=comp_data.get('y', 100.0),
                width=160.0 if comp_data['type'] != 'process' else 140.0,
                height=80.0 if comp_data['type'] != 'process' else 90.0,
                metadata_json=json.dumps(comp_data.get('meta', {}))
            )
            db.session.add(comp)
            db.session.flush()
            comp_ref_map[comp_data['identifier']] = comp

        # Create data flows
        for flow_data in lvl_data.get('flows', []):
            src_comp = comp_ref_map.get(flow_data['src'])
            dst_comp = comp_ref_map.get(flow_data['dst'])
            if src_comp and dst_comp:
                flow = DataFlow(
                    project_id=project.id,
                    level_id=level.id,
                    flow_identifier=flow_data.get('identifier', 'F1'),
                    flow_name=flow_data['name'],
                    description=flow_data.get('desc', ''),
                    source_id=src_comp.id,
                    destination_id=dst_comp.id,
                    data_type=flow_data.get('type', 'Structured Payload'),
                    is_bidirectional=flow_data.get('is_bidirectional', False)
                )
                db.session.add(flow)

    # Add activity log
    log = ActivityLog(
        project_id=project.id,
        user_id=user_id,
        action='Created Project',
        details=f"Instantiated project '{proj_name}' from template '{template_data['name']}'."
    )
    db.session.add(log)
    db.session.commit()
    return project
