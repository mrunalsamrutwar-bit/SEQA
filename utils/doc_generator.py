from utils.validation import validate_dfd

def generate_project_documentation(project, level_id=None):
    """
    Compiles structured, comprehensive software engineering DFD documentation
    from the project data model, including data dictionaries, component catalogs,
    and process specifications.
    """
    if level_id is not None:
        components = [c for c in project.components if c.level_id == level_id]
        flows = [f for f in project.data_flows if f.level_id == level_id]
        current_level = next((lvl for lvl in project.levels if lvl.id == level_id), None)
        level_name = current_level.level_name if current_level else project.dfd_level
    else:
        components = list(project.components)
        flows = list(project.data_flows)
        level_name = project.dfd_level

    comp_map = {c.id: c for c in components}
    
    processes = [c for c in components if c.component_type == 'process']
    datastores = [c for c in components if c.component_type == 'datastore']
    entities = [c for c in components if c.component_type == 'entity']

    # Build flow relations map
    inbound_flows = {c.id: [] for c in components}
    outbound_flows = {c.id: [] for c in components}

    for f in flows:
        if f.source_id in comp_map and f.destination_id in comp_map:
            outbound_flows[f.source_id].append(f)
            inbound_flows[f.destination_id].append(f)
            if f.is_bidirectional:
                inbound_flows[f.source_id].append(f)
                outbound_flows[f.destination_id].append(f)

    # Run validation for the compliance section
    validation_res = validate_dfd(project, level_id)

    # 1. External Entities Details
    entities_data = []
    for e in sorted(entities, key=lambda x: x.component_identifier or x.name):
        meta = e.get_metadata()
        in_names = [f.flow_name for f in inbound_flows.get(e.id, [])]
        out_names = [f.flow_name for f in outbound_flows.get(e.id, [])]
        entities_data.append({
            'id': e.component_identifier or 'E?',
            'name': e.name,
            'type': meta.get('entity_type', 'External User / Role'),
            'description': e.description or 'External boundary actor interacting with system processes.',
            'inbound_flows': in_names,
            'outbound_flows': out_names
        })

    # 2. Processes Details
    processes_data = []
    for p in sorted(processes, key=lambda x: x.component_identifier or x.name):
        meta = p.get_metadata()
        in_items = []
        for f in inbound_flows.get(p.id, []):
            src = comp_map.get(f.source_id)
            src_lbl = f"{src.component_identifier} ({src.name})" if src else "External"
            in_items.append(f"{f.flow_name} [from {src_lbl}]")

        out_items = []
        for f in outbound_flows.get(p.id, []):
            dst = comp_map.get(f.destination_id)
            dst_lbl = f"{dst.component_identifier} ({dst.name})" if dst else "External"
            out_items.append(f"{f.flow_name} [to {dst_lbl}]")

        # Detailed narrative generation
        in_str = ", ".join([f.flow_name for f in inbound_flows.get(p.id, [])]) or "triggers"
        out_str = ", ".join([f.flow_name for f in outbound_flows.get(p.id, [])]) or "resulting actions"
        detailed_narrative = (
            f"The '{p.name}' process accepts {in_str} as input. "
            f"It executes business logic to validate, transform, and compute operations, "
            f"subsequently emitting {out_str}. {p.description or ''}"
        ).strip()

        processes_data.append({
            'id': p.component_identifier or 'P?',
            'name': p.name,
            'description': p.description or 'Core operational transformation process.',
            'detailed_narrative': detailed_narrative,
            'inputs': in_items,
            'outputs': out_items,
            'sub_processes': meta.get('sub_processes', [])
        })

    # 3. Data Stores Details
    datastores_data = []
    for d in sorted(datastores, key=lambda x: x.component_identifier or x.name):
        meta = d.get_metadata()
        readers = []
        writers = []
        for f in outbound_flows.get(d.id, []):
            dst = comp_map.get(f.destination_id)
            if dst:
                readers.append(f"{dst.component_identifier} {dst.name} ({f.flow_name})")
        for f in inbound_flows.get(d.id, []):
            src = comp_map.get(f.source_id)
            if src:
                writers.append(f"{src.component_identifier} {src.name} ({f.flow_name})")

        datastores_data.append({
            'id': d.component_identifier or 'D?',
            'name': d.name,
            'storage_type': meta.get('storage_type', 'Relational / Persistent Store'),
            'description': d.description or 'Persistent repository maintaining records.',
            'schema_fields': meta.get('schema_fields', 'id, created_at, updated_at, attributes_payload'),
            'readers': readers,
            'writers': writers
        })

    # 4. Data Flows Matrix & Data Dictionary
    data_flows_data = []
    for f in sorted(flows, key=lambda x: x.flow_identifier or x.flow_name):
        src = comp_map.get(f.source_id)
        dst = comp_map.get(f.destination_id)
        src_label = f"[{src.component_type.capitalize()}] {src.component_identifier} {src.name}" if src else "Unknown Source"
        dst_label = f"[{dst.component_type.capitalize()}] {dst.component_identifier} {dst.name}" if dst else "Unknown Destination"
        data_flows_data.append({
            'id': f.flow_identifier or 'F?',
            'name': f.flow_name,
            'source': src_label,
            'destination': dst_label,
            'data_type': f.data_type or 'Structured Payload',
            'description': f.description or f"Transfers {f.flow_name} between {src.name if src else 'source'} and {dst.name if dst else 'destination'}.",
            'is_bidirectional': f.is_bidirectional
        })

    # Generate Markdown Output string as well
    md_lines = [
        f"# System Data Flow Diagram Documentation: {project.name}",
        f"**System Name:** {project.system_name}  ",
        f"**Author:** {project.author} | **Version:** {project.version} | **DFD Level:** {level_name}  ",
        f"**Generated:** {project.updated_at.strftime('%Y-%m-%d %H:%M:%S') if project.updated_at else ''}  ",
        "\n---\n",
        "## 1. System Overview & Scope",
        project.description or f"This document presents the functional Data Flow architecture for {project.system_name}.",
        "\n### Summary Metrics",
        f"- **Processes:** {len(processes)}",
        f"- **Data Stores:** {len(datastores)}",
        f"- **External Entities:** {len(entities)}",
        f"- **Data Flows:** {len(flows)}",
        f"- **Validation Compliance Score:** {validation_res['summary']['compliance_score']}%",
        "\n---\n",
        "## 2. External Entities Catalog",
        "External entities represent sources or destinations of data external to the system boundaries.",
        "\n| Identifier | Entity Name | Category / Type | Inbound Flows | Outbound Flows | Description |",
        "|------------|-------------|-----------------|---------------|----------------|-------------|"
    ]

    for e in entities_data:
        in_s = ", ".join(e['inbound_flows']) or "None"
        out_s = ", ".join(e['outbound_flows']) or "None"
        md_lines.append(f"| **{e['id']}** | {e['name']} | {e['type']} | {in_s} | {out_s} | {e['description']} |")

    md_lines.extend([
        "\n---\n",
        "## 3. Processes & Functional Transformations",
        "Processes transform incoming data flows into outgoing data flows via algorithmic or business rules.",
        "\n| Process ID | Process Name | Inbound Data | Outbound Data | Description |",
        "|------------|--------------|--------------|---------------|-------------|"
    ])

    for p in processes_data:
        in_s = "<br>".join(p['inputs']) or "None"
        out_s = "<br>".join(p['outputs']) or "None"
        md_lines.append(f"| **{p['id']}** | {p['name']} | {in_s} | {out_s} | {p['description']} |")

    md_lines.extend([
        "\n---\n",
        "## 4. Data Stores & Persistence Repositories",
        "Data stores represent resting state information repositories (databases, file systems, tables).",
        "\n| Store ID | Data Store Name | Storage Technology | Read Access By | Written Access By | Description |",
        "|----------|-----------------|--------------------|----------------|-------------------|-------------|"
    ])

    for d in datastores_data:
        r_s = ", ".join(d['readers']) or "None"
        w_s = ", ".join(d['writers']) or "None"
        md_lines.append(f"| **{d['id']}** | {d['name']} | {d['storage_type']} | {r_s} | {w_s} | {d['description']} |")

    md_lines.extend([
        "\n---\n",
        "## 5. Data Flow Matrix & Data Dictionary",
        "Comprehensive matrix of all data exchanges occurring across system processes and stores.",
        "\n| Flow ID | Flow Name / Data Item | Origin Source | Target Destination | Payload Data Type | Purpose & Description |",
        "|---------|-----------------------|---------------|--------------------|-------------------|-----------------------|"
    ])

    for f in data_flows_data:
        md_lines.append(f"| **{f['id']}** | {f['name']} | {f['source']} | {f['destination']} | {f['data_type']} | {f['description']} |")

    md_lines.extend([
        "\n---\n",
        "## 6. Detailed Process Narrative Specifications"
    ])

    for p in processes_data:
        md_lines.extend([
            f"\n### Process {p['id']}: {p['name']}",
            f"**Description:** {p['description']}",
            f"\n**Functional Logic Narrative:**",
            f"> {p['detailed_narrative']}",
            f"\n- **Inputs Received:** {', '.join(p['inputs']) if p['inputs'] else 'None'}",
            f"- **Outputs Emitted:** {', '.join(p['outputs']) if p['outputs'] else 'None'}"
        ])

    md_lines.extend([
        "\n---\n",
        "## 7. DFD Validation & Compliance Audit",
        f"**Overall Compliance Score:** {validation_res['summary']['compliance_score']}%  ",
        f"**Total Errors:** {validation_res['summary']['errors_count']} | **Total Warnings:** {validation_res['summary']['warnings_count']} | **Passed Rules:** {validation_res['summary']['passed_count']}/{validation_res['summary']['total_rules']}",
        "\n### Audit Issues List"
    ])

    if not validation_res['issues']:
        md_lines.append("\n✓ **Perfect DFD Architecture:** All standard rules passed with 0 errors and 0 warnings.")
    else:
        for iss in validation_res['issues']:
            badge = "❌ [ERROR]" if iss['type'] == 'error' else "⚠️ [WARNING]"
            md_lines.append(f"- {badge} **{iss['title']}:** {iss['message']} *(Suggestion: {iss['suggestion']})*")

    return {
        'project_meta': {
            'id': project.id,
            'name': project.name,
            'system_name': project.system_name,
            'author': project.author,
            'version': project.version,
            'dfd_level': level_name,
            'description': project.description,
            'updated_at': project.updated_at.strftime('%B %d, %Y') if project.updated_at else ''
        },
        'summary_metrics': {
            'processes_count': len(processes),
            'datastores_count': len(datastores),
            'entities_count': len(entities),
            'flows_count': len(flows),
            'compliance_score': validation_res['summary']['compliance_score'],
            'errors_count': validation_res['summary']['errors_count'],
            'warnings_count': validation_res['summary']['warnings_count']
        },
        'entities': entities_data,
        'processes': processes_data,
        'datastores': datastores_data,
        'data_flows': data_flows_data,
        'validation': validation_res,
        'markdown_text': "\n".join(md_lines)
    }
