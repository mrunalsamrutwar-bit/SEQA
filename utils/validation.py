def validate_dfd(project, level_id=None):
    """
    Validates a DFD diagram (or specific level) according to standard DFD syntax & semantics rules.
    Returns:
        dict: {
            'is_valid': bool,
            'summary': {
                'total_components': int,
                'total_processes': int,
                'total_datastores': int,
                'total_entities': int,
                'total_flows': int,
                'errors_count': int,
                'warnings_count': int,
                'passed_count': int
            },
            'rules': [
                {
                    'id': str,
                    'category': str,
                    'title': str,
                    'description': str,
                    'status': 'passed' | 'warning' | 'error',
                    'items': [ {'message': str, 'component_id': int, 'flow_id': int, 'suggestion': str} ]
                }
            ],
            'issues': [
                {
                    'type': 'error' | 'warning',
                    'code': str,
                    'title': str,
                    'message': str,
                    'component_id': int | None,
                    'flow_id': int | None,
                    'suggestion': str
                }
            ]
        }
    """
    # Filter components and flows by level if level_id provided
    if level_id is not None:
        components = [c for c in project.components if c.level_id == level_id]
        flows = [f for f in project.data_flows if f.level_id == level_id]
        current_level = next((lvl for lvl in project.levels if lvl.id == level_id), None)
        level_number = current_level.level_number if current_level else 0
    else:
        components = list(project.components)
        flows = list(project.data_flows)
        level_number = 0

    comp_map = {c.id: c for c in components}
    
    processes = [c for c in components if c.component_type == 'process']
    datastores = [c for c in components if c.component_type == 'datastore']
    entities = [c for c in components if c.component_type == 'entity']

    # Map incoming and outgoing flows for each component
    incoming_flows = {c.id: [] for c in components}
    outgoing_flows = {c.id: [] for c in components}

    dangling_flows = []
    for f in flows:
        if f.source_id not in comp_map or f.destination_id not in comp_map:
            dangling_flows.append(f)
        else:
            outgoing_flows[f.source_id].append(f)
            incoming_flows[f.destination_id].append(f)
            if f.is_bidirectional:
                incoming_flows[f.source_id].append(f)
                outgoing_flows[f.destination_id].append(f)

    issues = []
    rules = []

    # -------------------------------------------------------------
    # Rule 1: Process Flow Completeness (Black Holes & Miracle Processes)
    # -------------------------------------------------------------
    rule1_items = []
    for p in processes:
        inc = incoming_flows.get(p.id, [])
        out = outgoing_flows.get(p.id, [])
        
        # Miracle / Spontaneous Generation (Outputs but no Inputs)
        if len(out) > 0 and len(inc) == 0:
            msg = f"Process '{p.component_identifier} {p.name}' is a Miracle / Spontaneous Generation process (has outputs but no input data flows)."
            sugg = f"Add an incoming data flow from an External Entity or Data Store to feed process '{p.name}'."
            rule1_items.append({'message': msg, 'component_id': p.id, 'suggestion': sugg, 'type': 'error'})
            issues.append({'type': 'error', 'code': 'MIRACLE_PROCESS', 'title': 'Miracle Process', 'message': msg, 'component_id': p.id, 'suggestion': sugg})

        # Black Hole (Inputs but no Outputs)
        elif len(inc) > 0 and len(out) == 0:
            msg = f"Process '{p.component_identifier} {p.name}' is a Black Hole process (receives inputs but generates no output data flows)."
            sugg = f"Add an outgoing data flow from process '{p.name}' to a Data Store or External Entity."
            rule1_items.append({'message': msg, 'component_id': p.id, 'suggestion': sugg, 'type': 'error'})
            issues.append({'type': 'error', 'code': 'BLACK_HOLE', 'title': 'Black Hole Process', 'message': msg, 'component_id': p.id, 'suggestion': sugg})

    rules.append({
        'id': 'RULE_PROCESS_INTEGRITY',
        'category': 'Process Rules',
        'title': 'Process Input & Output Balance',
        'description': 'Every process must receive input data and produce output data (no Black Holes or Miracles).',
        'status': 'error' if any(i['type'] == 'error' for i in rule1_items) else 'passed',
        'items': rule1_items
    })

    # -------------------------------------------------------------
    # Rule 2: Illegal Direct Connections (Entity-to-Entity, Store-to-Store, Entity-to-Store)
    # -------------------------------------------------------------
    rule2_items = []
    for f in flows:
        src = comp_map.get(f.source_id)
        dst = comp_map.get(f.destination_id)
        if not src or not dst:
            continue

        # Entity to Entity
        if src.component_type == 'entity' and dst.component_type == 'entity':
            msg = f"Illegal Direct Flow: External Entity '{src.name}' directly sends data to External Entity '{dst.name}' via flow '{f.flow_name}'."
            sugg = "External entities must communicate through a Process. Insert a processing node between them."
            rule2_items.append({'message': msg, 'flow_id': f.id, 'suggestion': sugg, 'type': 'error'})
            issues.append({'type': 'error', 'code': 'ENTITY_TO_ENTITY', 'title': 'Entity-to-Entity Flow', 'message': msg, 'flow_id': f.id, 'suggestion': sugg})

        # Store to Store
        elif src.component_type == 'datastore' and dst.component_type == 'datastore':
            msg = f"Illegal Direct Flow: Data Store '{src.name}' directly communicates with Data Store '{dst.name}' via flow '{f.flow_name}'."
            sugg = "Data cannot move autonomously between data stores without a Process. Route through a transformation process."
            rule2_items.append({'message': msg, 'flow_id': f.id, 'suggestion': sugg, 'type': 'error'})
            issues.append({'type': 'error', 'code': 'STORE_TO_STORE', 'title': 'Store-to-Store Flow', 'message': msg, 'flow_id': f.id, 'suggestion': sugg})

        # Entity to Store directly (or Store to Entity directly without process)
        elif (src.component_type == 'entity' and dst.component_type == 'datastore') or (src.component_type == 'datastore' and dst.component_type == 'entity'):
            msg = f"Illegal Direct Flow: External Entity '{src.name}' directly accesses Data Store '{dst.name}' via flow '{f.flow_name}'."
            sugg = "External entities cannot read/write directly to data stores. Insert an authentication or CRUD process in between."
            rule2_items.append({'message': msg, 'flow_id': f.id, 'suggestion': sugg, 'type': 'error'})
            issues.append({'type': 'error', 'code': 'ENTITY_STORE_DIRECT', 'title': 'Direct Entity-Store Flow', 'message': msg, 'flow_id': f.id, 'suggestion': sugg})

    rules.append({
        'id': 'RULE_CONNECTION_SYNTAX',
        'category': 'Data Flow Rules',
        'title': 'Strict Node Connection Syntax',
        'description': 'Data flows must pass through at least one Process; direct Entity-to-Entity, Store-to-Store, and Entity-to-Store flows are forbidden.',
        'status': 'error' if any(i['type'] == 'error' for i in rule2_items) else 'passed',
        'items': rule2_items
    })

    # -------------------------------------------------------------
    # Rule 3: Isolated / Orphan Components
    # -------------------------------------------------------------
    rule3_items = []
    for c in components:
        inc = incoming_flows.get(c.id, [])
        out = outgoing_flows.get(c.id, [])
        if len(inc) == 0 and len(out) == 0:
            type_label = c.component_type.capitalize()
            msg = f"Orphan Component: {type_label} '{c.component_identifier} {c.name}' has 0 connections."
            sugg = f"Connect '{c.name}' to relevant processes with data flows, or delete it if unused."
            rule3_items.append({'message': msg, 'component_id': c.id, 'suggestion': sugg, 'type': 'warning'})
            issues.append({'type': 'warning', 'code': 'ORPHAN_COMPONENT', 'title': f'Orphan {type_label}', 'message': msg, 'component_id': c.id, 'suggestion': sugg})

    rules.append({
        'id': 'RULE_ORPHAN_COMPONENTS',
        'category': 'Topology Rules',
        'title': 'Connected Topology & No Orphan Nodes',
        'description': 'All components on the canvas should participate in data flow interactions.',
        'status': 'warning' if len(rule3_items) > 0 else 'passed',
        'items': rule3_items
    })

    # -------------------------------------------------------------
    # Rule 4: Data Flow Completeness (Names & Dangling Flows)
    # -------------------------------------------------------------
    rule4_items = []
    if dangling_flows:
        for f in dangling_flows:
            msg = f"Dangling Flow '{f.flow_name}' references deleted or non-existent components."
            sugg = "Reconnect flow to valid source/destination or remove flow."
            rule4_items.append({'message': msg, 'flow_id': f.id, 'suggestion': sugg, 'type': 'error'})
            issues.append({'type': 'error', 'code': 'DANGLING_FLOW', 'title': 'Dangling Flow', 'message': msg, 'flow_id': f.id, 'suggestion': sugg})

    for f in flows:
        if not f.flow_name or f.flow_name.strip() == '' or f.flow_name.lower() in ['untitled flow', 'new flow', 'flow']:
            msg = f"Data Flow (ID: {f.flow_identifier}) lacks a descriptive noun/data payload label."
            sugg = "Provide a meaningful name for the data packet (e.g., 'User Credentials', 'Order Invoice')."
            rule4_items.append({'message': msg, 'flow_id': f.id, 'suggestion': sugg, 'type': 'warning'})
            issues.append({'type': 'warning', 'code': 'UNNAMED_FLOW', 'title': 'Unnamed Data Flow', 'message': msg, 'flow_id': f.id, 'suggestion': sugg})

    rules.append({
        'id': 'RULE_FLOW_COMPLETENESS',
        'category': 'Data Flow Rules',
        'title': 'Data Flow Naming & Continuity',
        'description': 'Every data flow must have a descriptive label representing the data structure transmitted and valid anchors.',
        'status': 'error' if any(i['type'] == 'error' for i in rule4_items) else ('warning' if rule4_items else 'passed'),
        'items': rule4_items
    })

    # -------------------------------------------------------------
    # Rule 5: Unique Identifiers & Numbering Convention
    # -------------------------------------------------------------
    rule5_items = []
    seen_identifiers = {}
    for c in components:
        ident = (c.component_identifier or '').strip()
        if not ident:
            msg = f"Component '{c.name}' is missing an Identifier."
            sugg = f"Assign an ID (e.g., 1.0 for Process, E1 for Entity, D1 for Data Store)."
            rule5_items.append({'message': msg, 'component_id': c.id, 'suggestion': sugg, 'type': 'warning'})
            issues.append({'type': 'warning', 'code': 'MISSING_ID', 'title': 'Missing Identifier', 'message': msg, 'component_id': c.id, 'suggestion': sugg})
        else:
            if ident in seen_identifiers:
                msg = f"Duplicate Identifier '{ident}' found on both '{seen_identifiers[ident].name}' and '{c.name}'."
                sugg = "Ensure every component has a distinct identifier within the DFD level."
                rule5_items.append({'message': msg, 'component_id': c.id, 'suggestion': sugg, 'type': 'warning'})
                issues.append({'type': 'warning', 'code': 'DUPLICATE_ID', 'title': 'Duplicate Identifier', 'message': msg, 'component_id': c.id, 'suggestion': sugg})
            else:
                seen_identifiers[ident] = c

    rules.append({
        'id': 'RULE_UNIQUE_IDENTIFIERS',
        'category': 'Identification Rules',
        'title': 'Unique Identifiers & Numbering',
        'description': 'Components should possess distinct numbering codes (e.g. 1.0, 2.0 for processes, D1, D2 for stores, E1, E2 for entities).',
        'status': 'warning' if len(rule5_items) > 0 else 'passed',
        'items': rule5_items
    })

    # -------------------------------------------------------------
    # Rule 6: Context Diagram (Level 0) Specific Standard Rules
    # -------------------------------------------------------------
    rule6_items = []
    if level_number == 0:
        if len(processes) == 0:
            msg = "Context Diagram (Level 0) must contain exactly 1 central system process representing the entire system boundary."
            sugg = "Add a single central process (e.g., '0.0 System Name') to represent the system scope."
            rule6_items.append({'message': msg, 'suggestion': sugg, 'type': 'error'})
            issues.append({'type': 'error', 'code': 'L0_NO_PROCESS', 'title': 'Missing Context Process', 'message': msg, 'suggestion': sugg})
        elif len(processes) > 1:
            msg = f"Context Diagram (Level 0) has {len(processes)} processes. Standard DFD Level 0 specifies exactly 1 high-level System Process."
            sugg = "Consolidate into 1 central System Process (e.g. '0.0 Online Shopping System') and decompose into multiple processes at Level 1."
            rule6_items.append({'message': msg, 'suggestion': sugg, 'type': 'warning'})
            issues.append({'type': 'warning', 'code': 'L0_MULTIPLE_PROCESSES', 'title': 'Multiple Processes in Level 0', 'message': msg, 'suggestion': sugg})

        if len(datastores) > 0:
            msg = f"Context Diagram (Level 0) contains {len(datastores)} Data Stores. Standard DFD Level 0 hides internal data stores within the system boundary."
            sugg = "Consider moving data stores to Level 1 diagram and only showing external entities interacting with the central system."
            rule6_items.append({'message': msg, 'suggestion': sugg, 'type': 'warning'})
            issues.append({'type': 'warning', 'code': 'L0_DATASTORE_EXPOSED', 'title': 'Data Store in Context Diagram', 'message': msg, 'suggestion': sugg})

        if len(entities) == 0:
            msg = "Context Diagram has no External Entities. A system must interact with at least one external user, role, or external system."
            sugg = "Add External Entities (e.g., 'Customer', 'Admin', 'Payment Gateway')."
            rule6_items.append({'message': msg, 'suggestion': sugg, 'type': 'warning'})
            issues.append({'type': 'warning', 'code': 'L0_NO_ENTITIES', 'title': 'No External Entities', 'message': msg, 'suggestion': sugg})

    rules.append({
        'id': 'RULE_LEVEL_SPECIFIC',
        'category': 'Standard DFD Level Guidelines',
        'title': f'Level {level_number} Standard Structure Compliance',
        'description': f'Adherence to standard decomposition rules for Level {level_number}.',
        'status': 'error' if any(i['type'] == 'error' for i in rule6_items) else ('warning' if rule6_items else 'passed'),
        'items': rule6_items
    })

    # Summary calculations
    errors_count = len([i for i in issues if i['type'] == 'error'])
    warnings_count = len([i for i in issues if i['type'] == 'warning'])
    passed_rules = len([r for r in rules if r['status'] == 'passed'])

    return {
        'is_valid': errors_count == 0,
        'summary': {
            'total_components': len(components),
            'total_processes': len(processes),
            'total_datastores': len(datastores),
            'total_entities': len(entities),
            'total_flows': len(flows),
            'errors_count': errors_count,
            'warnings_count': warnings_count,
            'passed_count': passed_rules,
            'total_rules': len(rules),
            'compliance_score': max(0, int(100 - (errors_count * 20 + warnings_count * 5)))
        },
        'rules': rules,
        'issues': issues
    }
