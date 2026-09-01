import io
import zipfile
import xml.sax.saxutils as saxutils
from datetime import datetime, timezone

def escape_xml(text):
    if text is None:
        return ""
    return saxutils.escape(str(text))

class PureDocxBuilder:
    """
    Pure Python Microsoft Word (.docx) document generator.
    Produces 100% standard-compliant OpenXML (.docx) files without requiring external C-extensions.
    """
    def __init__(self):
        self.body_xml = []
        
    def add_title(self, text):
        escaped = escape_xml(text)
        self.body_xml.append(f"""
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Title"/>
                <w:spacing w:before="120" w:after="80"/>
                <w:jc w:val="left"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    <w:b/>
                    <w:color w:val="1E3A8A"/>
                    <w:sz w:val="44"/>
                </w:rPr>
                <w:t>{escaped}</w:t>
            </w:r>
        </w:p>""")

    def add_subtitle(self, text):
        escaped = escape_xml(text)
        self.body_xml.append(f"""
        <w:p>
            <w:pPr>
                <w:spacing w:before="0" w:after="240"/>
                <w:jc w:val="left"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    <w:i/>
                    <w:color w:val="475569"/>
                    <w:sz w:val="26"/>
                </w:rPr>
                <w:t>{escaped}</w:t>
            </w:r>
        </w:p>""")

    def add_heading_1(self, text):
        escaped = escape_xml(text)
        self.body_xml.append(f"""
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
                <w:spacing w:before="360" w:after="120"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    <w:b/>
                    <w:color w:val="2563EB"/>
                    <w:sz w:val="30"/>
                </w:rPr>
                <w:t>{escaped}</w:t>
            </w:r>
        </w:p>""")

    def add_heading_2(self, text):
        escaped = escape_xml(text)
        self.body_xml.append(f"""
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading2"/>
                <w:spacing w:before="240" w:after="80"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    <w:b/>
                    <w:color w:val="1E293B"/>
                    <w:sz w:val="24"/>
                </w:rPr>
                <w:t>{escaped}</w:t>
            </w:r>
        </w:p>""")

    def add_paragraph(self, text, bold=False, italic=False, color="1E293B", space_after=120):
        escaped = escape_xml(text)
        b_tag = "<w:b/>" if bold else ""
        i_tag = "<w:i/>" if italic else ""
        self.body_xml.append(f"""
        <w:p>
            <w:pPr>
                <w:spacing w:before="0" w:after="{space_after}"/>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    {b_tag}
                    {i_tag}
                    <w:color w:val="{color}"/>
                    <w:sz w:val="21"/>
                </w:rPr>
                <w:t xml:space="preserve">{escaped}</w:t>
            </w:r>
        </w:p>""")

    def add_callout(self, text, bg_hex="EFF6FF", border_hex="2563EB"):
        escaped = escape_xml(text)
        self.body_xml.append(f"""
        <w:tbl>
            <w:tblPr>
                <w:tblW w:w="9360" w:type="dxa"/>
                <w:tblBorders>
                    <w:top w:val="none"/>
                    <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>
                    <w:bottom w:val="none"/>
                    <w:right w:val="none"/>
                </w:tblBorders>
                <w:tblCellMar>
                    <w:top w:w="120" w:type="dxa"/>
                    <w:left w:w="180" w:type="dxa"/>
                    <w:bottom w:w="120" w:type="dxa"/>
                    <w:right w:w="180" w:type="dxa"/>
                </w:tblCellMar>
            </w:tblPr>
            <w:tr>
                <w:tc>
                    <w:tcPr>
                        <w:shd w:val="clear" w:color="auto" w:fill="{bg_hex}"/>
                    </w:tcPr>
                    <w:p>
                        <w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr>
                        <w:r>
                            <w:rPr>
                                <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                                <w:color w:val="1E293B"/>
                                <w:sz w:val="20"/>
                            </w:rPr>
                            <w:t xml:space="preserve">{escaped}</w:t>
                        </w:r>
                    </w:p>
                </w:tc>
            </w:tr>
        </w:tbl>
        <w:p><w:pPr><w:spacing w:before="0" w:after="120"/></w:pPr></w:p>""")

    def add_table(self, headers, rows, col_widths=None):
        """
        Generates a professionally styled table with header formatting and alternating rows.
        col_widths: list of width percentages or integers in dxa (total approx 9360 dxa).
        """
        if not col_widths:
            col_widths = [int(9360 / max(1, len(headers)))] * len(headers)
        
        tbl_xml = ["""
        <w:tbl>
            <w:tblPr>
                <w:tblW w:w="9360" w:type="dxa"/>
                <w:tblBorders>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:bottom w:val="single" w:sz="8" w:space="0" w:color="94A3B8"/>
                    <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                </w:tblBorders>
                <w:tblCellMar>
                    <w:top w:w="100" w:type="dxa"/>
                    <w:left w:w="120" w:type="dxa"/>
                    <w:bottom w:w="100" w:type="dxa"/>
                    <w:right w:w="120" w:type="dxa"/>
                </w:tblCellMar>
            </w:tblPr>
        """]

        # Header Row
        tbl_xml.append("<w:tr>")
        for idx, h in enumerate(headers):
            w = col_widths[idx] if idx < len(col_widths) else 2000
            tbl_xml.append(f"""
            <w:tc>
                <w:tcPr>
                    <w:tcW w:w="{w}" w:type="dxa"/>
                    <w:shd w:val="clear" w:color="auto" w:fill="2563EB"/>
                </w:tcPr>
                <w:p>
                    <w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>
                    <w:r>
                        <w:rPr>
                            <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                            <w:b/>
                            <w:color w:val="FFFFFF"/>
                            <w:sz w:val="20"/>
                        </w:rPr>
                        <w:t>{escape_xml(h)}</w:t>
                    </w:r>
                </w:p>
            </w:tc>""")
        tbl_xml.append("</w:tr>")

        # Data Rows
        for r_idx, row in enumerate(rows):
            fill = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
            tbl_xml.append("<w:tr>")
            for idx, cell_val in enumerate(row):
                w = col_widths[idx] if idx < len(col_widths) else 2000
                tbl_xml.append(f"""
                <w:tc>
                    <w:tcPr>
                        <w:tcW w:w="{w}" w:type="dxa"/>
                        <w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>
                    </w:tcPr>
                    <w:p>
                        <w:pPr><w:spacing w:before="30" w:after="30"/></w:pPr>
                        <w:r>
                            <w:rPr>
                                <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                                <w:color w:val="1E293B"/>
                                <w:sz w:val="19"/>
                            </w:rPr>
                            <w:t xml:space="preserve">{escape_xml(cell_val)}</w:t>
                        </w:r>
                    </w:p>
                </w:tc>""")
            tbl_xml.append("</w:tr>")

        tbl_xml.append("</w:tbl>")
        tbl_xml.append('<w:p><w:pPr><w:spacing w:before="0" w:after="160"/></w:pPr></w:p>')
        self.body_xml.append("".join(tbl_xml))

    def build_docx_stream(self):
        """Assembles the complete .docx binary zip stream."""
        docx_buffer = io.BytesIO()

        content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

        package_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

        document_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

        styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:docDefaults>
        <w:rPrDefault>
            <w:rPr>
                <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" w:cs="Calibri"/>
                <w:sz w:val="22"/>
                <w:lang w:val="en-US"/>
            </w:rPr>
        </w:rPrDefault>
    </w:docDefaults>
</w:styles>"""

        body_content = "".join(self.body_xml)
        document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <w:body>
        {body_content}
        <w:sectPr>
            <w:pgSz w:w="12240" w:h="15840"/>
            <w:pgMar w:top="1152" w:right="1152" w:bottom="1152" w:left="1152" w:header="720" w:footer="720" w:gutter="0"/>
            <w:cols w:space="720"/>
            <w:docGrid w:linePitch="360"/>
        </w:sectPr>
    </w:body>
</w:document>"""

        with zipfile.ZipFile(docx_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', content_types_xml)
            zf.writestr('_rels/.rels', package_rels_xml)
            zf.writestr('word/_rels/document.xml.rels', document_rels_xml)
            zf.writestr('word/styles.xml', styles_xml)
            zf.writestr('word/document.xml', document_xml)

        docx_buffer.seek(0)
        return docx_buffer


def generate_docx_stream(doc_data):
    """
    Generates a high-quality Microsoft Word (.docx) document in memory from project documentation data.
    """
    builder = PureDocxBuilder()

    meta = doc_data.get('project_meta', {})
    metrics = doc_data.get('summary_metrics', {})
    entities = doc_data.get('entities', [])
    processes = doc_data.get('processes', [])
    datastores = doc_data.get('datastores', [])
    flows = doc_data.get('data_flows', [])
    validation = doc_data.get('validation', {})
    narrative_specs = doc_data.get('narrative_specs', [])

    # Document Header & Title
    builder.add_title(meta.get('name', 'System Data Flow Diagram'))
    builder.add_subtitle(f"System Data Flow Diagram (DFD) Specification — {meta.get('dfd_level', 'Level 1')}")

    # Metadata Table
    builder.add_table(
        ["Specification Attribute", "System Value"],
        [
            ["System Name", meta.get('system_name', 'N/A')],
            ["Author / Architect", meta.get('author', 'Software Architect')],
            ["Version / Release", meta.get('version', '1.0.0')],
            ["DFD Level", meta.get('dfd_level', 'Level 1')],
            ["Tags / Modules", meta.get('tags', 'General')],
            ["Generated Date", meta.get('updated_at', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))]
        ],
        col_widths=[3200, 6160]
    )

    # 1. System Overview & Scope
    builder.add_heading_1("1. System Overview & Scope")
    desc = meta.get('description', 'This document specifies the functional data flow architecture and system decomposition.')
    builder.add_paragraph(desc)

    # 2. Executive Summary Metrics
    builder.add_heading_1("2. Executive Summary & Metrics")
    builder.add_table(
        ["Component Category", "Quantity", "Description / Role"],
        [
            ["External Entities", str(metrics.get('total_entities', 0)), "External systems, users, and data producers/consumers"],
            ["Processes", str(metrics.get('total_processes', 0)), "Business logic transformations & computational tasks"],
            ["Data Stores", str(metrics.get('total_datastores', 0)), "Persistent repositories, databases, and caches"],
            ["Data Flows", str(metrics.get('total_flows', 0)), "Directed information and payload transfer pathways"],
            ["Decomposition Levels", str(metrics.get('total_levels', 1)), "Hierarchy depth (Context Level 0 to detailed sub-processes)"],
            ["Compliance Score", f"{validation.get('summary', {}).get('compliance_score', 100)}%", "Standard DFD rule syntactic & semantic adherence"]
        ],
        col_widths=[2800, 1600, 4960]
    )

    # 3. External Entities Catalog
    builder.add_heading_1("3. External Entities & Actors Catalog")
    if entities:
        ent_rows = []
        for e in entities:
            ent_rows.append([
                e.get('identifier', '-'),
                e.get('name', '-'),
                e.get('entity_type', 'General Actor'),
                e.get('description', '-')
            ])
        builder.add_table(
            ["ID", "Entity Name", "Entity Category", "Description / System Role"],
            ent_rows,
            col_widths=[1100, 2500, 2200, 3560]
        )
    else:
        builder.add_paragraph("No external entities defined for this system level.", italic=True)

    # 4. Processes & Decomposition
    builder.add_heading_1("4. Processes & Functional Decomposition")
    if processes:
        proc_rows = []
        for p in processes:
            proc_rows.append([
                p.get('identifier', '-'),
                p.get('name', '-'),
                p.get('level_name', 'Level 1'),
                p.get('description', '-')
            ])
        builder.add_table(
            ["Process #", "Process Label", "Hierarchy Level", "Functional Description"],
            proc_rows,
            col_widths=[1300, 2600, 1800, 3660]
        )
    else:
        builder.add_paragraph("No process components defined.", italic=True)

    # 5. Data Stores & Schema
    builder.add_heading_1("5. Data Stores & Persistent Storage")
    if datastores:
        store_rows = []
        for d in datastores:
            store_rows.append([
                d.get('identifier', '-'),
                d.get('name', '-'),
                d.get('storage_type', 'Relational DB'),
                d.get('description', '-')
            ])
        builder.add_table(
            ["Store ID", "Data Store Label", "Storage Engine", "Storage Purpose & Contents"],
            store_rows,
            col_widths=[1200, 2500, 2000, 3660]
        )
    else:
        builder.add_paragraph("No data stores defined at this level.", italic=True)

    # 6. Data Flows & Data Dictionary
    builder.add_heading_1("6. Data Flows & Data Dictionary")
    if flows:
        flow_rows = []
        for f in flows:
            flow_rows.append([
                f.get('identifier', '-'),
                f.get('name', '-'),
                f.get('source_name', '-'),
                f.get('destination_name', '-'),
                f.get('data_type', 'Data Packet'),
                f.get('description', '-')
            ])
        builder.add_table(
            ["Flow ID", "Flow Name", "Source", "Destination", "Data Type", "Payload Description"],
            flow_rows,
            col_widths=[1000, 2000, 1600, 1600, 1400, 1760]
        )
    else:
        builder.add_paragraph("No data flows mapped.", italic=True)

    # 7. Narrative Process Specifications
    builder.add_heading_1("7. Detailed Process Specifications")
    if narrative_specs:
        for spec in narrative_specs:
            builder.add_heading_2(f"Process {spec.get('identifier', '')}: {spec.get('name', '')}")
            builder.add_paragraph(f"Description: {spec.get('description', 'N/A')}")
            
            inputs = ", ".join(spec.get('incoming_flows', [])) or "None (Requires Validation)"
            outputs = ", ".join(spec.get('outgoing_flows', [])) or "None (Requires Validation)"
            
            builder.add_callout(
                f"• Incoming Data Flows: {inputs}\n• Outgoing Data Flows: {outputs}\n• Transformation Logic: Receives incoming data, validates structure, processes transaction, and distributes results."
            )
    else:
        builder.add_paragraph("No detailed specifications available.", italic=True)

    # 8. Validation & Compliance Audit
    builder.add_heading_1("8. DFD Syntax & Rule Compliance Audit")
    summary = validation.get('summary', {})
    score = summary.get('compliance_score', 100)
    errors = summary.get('errors_count', 0)
    warnings = summary.get('warnings_count', 0)
    passed = summary.get('passed_count', 0)

    builder.add_callout(
        f"Validation Audit Result: {score}% Compliant\n• Rules Passed: {passed}\n• Semantic Warnings: {warnings}\n• Critical Errors: {errors}",
        bg_hex="F0FDF4" if errors == 0 else "FEF2F2",
        border_hex="059669" if errors == 0 else "DC2626"
    )

    issues = validation.get('issues', [])
    if issues:
        builder.add_heading_2("Identified Compliance Issues & Remediation")
        issue_rows = []
        for iss in issues:
            issue_rows.append([
                iss.get('type', 'Warning').upper(),
                iss.get('title', '-'),
                iss.get('message', '-'),
                iss.get('suggestion', '-')
            ])
        builder.add_table(
            ["Severity", "Rule Violation", "Detail", "Recommended Fix"],
            issue_rows,
            col_widths=[1200, 2200, 3200, 2760]
        )

    return builder.build_docx_stream()
