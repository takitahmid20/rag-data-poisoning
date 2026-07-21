import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "preliminary_experiment_report.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Running Header (Page 2+)
        if self._pageNumber > 1:
            self.drawString(45, 755, "United International University - CSE 4531 (Sec C) | Group 06 Report")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(45, 748, 567, 748)

        # Running Footer (All Pages)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(45, 38, 567, 38)
        
        self.drawString(45, 25, "Summer 2026 | CSE 4531 (Section C) - Group 06")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(567, 25, page_text)
        self.restoreState()

# Vector Flowcharts
def create_diagram_1():
    d = Drawing(520, 36)
    boxes = ["User Query", "Embedding", "Vector DB", "Retriever", "Gemini LLM", "Correct Response"]
    widths = [70, 65, 65, 65, 70, 90]
    
    x = 5
    for i, (text, w) in enumerate(zip(boxes, widths)):
        bg_color = colors.HexColor("#EBF8FF") if i < 5 else colors.HexColor("#C6F6D5")
        border_color = colors.HexColor("#3182CE") if i < 5 else colors.HexColor("#2F855A")
        text_color = colors.HexColor("#2B6CB0") if i < 5 else colors.HexColor("#22543D")
        
        d.add(Rect(x, 6, w, 24, rx=3, ry=3, fillColor=bg_color, strokeColor=border_color, strokeWidth=1))
        d.add(String(x + w/2, 14, text, fontName="Helvetica-Bold", fontSize=7, textAnchor="middle", fillColor=text_color))
        
        if i < len(boxes) - 1:
            arrow_x = x + w
            d.add(Line(arrow_x, 18, arrow_x + 12, 18, strokeColor=colors.HexColor("#718096"), strokeWidth=1))
            d.add(Polygon([arrow_x + 12, 18, arrow_x + 8, 21, arrow_x + 8, 15], fillColor=colors.HexColor("#718096"), strokeColor=colors.HexColor("#718096")))
            x += w + 13
    return d

def create_diagram_2():
    d = Drawing(520, 40)
    
    d.add(Rect(5, 8, 70, 24, rx=3, ry=3, fillColor=colors.HexColor("#EBF8FF"), strokeColor=colors.HexColor("#3182CE"), strokeWidth=1))
    d.add(String(40, 16, "User Query", fontName="Helvetica-Bold", fontSize=7, textAnchor="middle", fillColor=colors.HexColor("#2B6CB0")))
    
    d.add(Line(75, 20, 87, 20, strokeColor=colors.HexColor("#718096"), strokeWidth=1))
    d.add(Polygon([87, 20, 83, 23, 83, 17], fillColor=colors.HexColor("#718096"), strokeColor=colors.HexColor("#718096")))
    
    d.add(Rect(87, 8, 65, 24, rx=3, ry=3, fillColor=colors.HexColor("#EBF8FF"), strokeColor=colors.HexColor("#3182CE"), strokeWidth=1))
    d.add(String(119.5, 16, "Retriever", fontName="Helvetica-Bold", fontSize=7, textAnchor="middle", fillColor=colors.HexColor("#2B6CB0")))

    d.add(Line(152, 20, 164, 20, strokeColor=colors.HexColor("#718096"), strokeWidth=1))
    d.add(Polygon([164, 20, 160, 23, 160, 17], fillColor=colors.HexColor("#718096"), strokeColor=colors.HexColor("#718096")))

    d.add(Rect(164, 2, 120, 36, rx=3, ry=3, fillColor=colors.HexColor("#FEFCBF"), strokeColor=colors.HexColor("#D69E2E"), strokeWidth=1))
    d.add(String(224, 25, "Retrieved Context:", fontName="Helvetica-Bold", fontSize=6.5, textAnchor="middle", fillColor=colors.HexColor("#744210")))
    d.add(String(224, 16, "• Trusted Policies", fontName="Helvetica", fontSize=6, textAnchor="middle", fillColor=colors.HexColor("#744210")))
    d.add(String(224, 7, "• Outdated VPN Guide", fontName="Helvetica-Bold", fontSize=6, textAnchor="middle", fillColor=colors.HexColor("#C53030")))

    d.add(Line(284, 20, 296, 20, strokeColor=colors.HexColor("#718096"), strokeWidth=1))
    d.add(Polygon([296, 20, 292, 23, 292, 17], fillColor=colors.HexColor("#718096"), strokeColor=colors.HexColor("#718096")))

    d.add(Rect(296, 8, 65, 24, rx=3, ry=3, fillColor=colors.HexColor("#EBF8FF"), strokeColor=colors.HexColor("#3182CE"), strokeWidth=1))
    d.add(String(328.5, 16, "Gemini LLM", fontName="Helvetica-Bold", fontSize=7, textAnchor="middle", fillColor=colors.HexColor("#2B6CB0")))

    d.add(Line(361, 20, 373, 20, strokeColor=colors.HexColor("#718096"), strokeWidth=1))
    d.add(Polygon([373, 20, 369, 23, 369, 17], fillColor=colors.HexColor("#718096"), strokeColor=colors.HexColor("#718096")))

    d.add(Rect(373, 5, 142, 30, rx=3, ry=3, fillColor=colors.HexColor("#FED7D7"), strokeColor=colors.HexColor("#E53E3E"), strokeWidth=1))
    d.add(String(444, 20, "Potentially Inconsistent /", fontName="Helvetica-Bold", fontSize=6.5, textAnchor="middle", fillColor=colors.HexColor("#9B2C2C")))
    d.add(String(444, 10, "Conflicting Response", fontName="Helvetica-Bold", fontSize=6.5, textAnchor="middle", fillColor=colors.HexColor("#9B2C2C")))

    return d

def create_diagram_3():
    d = Drawing(520, 36)
    
    steps = [
        ("PDF Upload", "#E2E8F0", "#4A5568", "#2D3748", 60),
        ("Metadata Check", "#EBF8FF", "#3182CE", "#2B6CB0", 72),
        ("Trust Validation", "#EBF8FF", "#3182CE", "#2B6CB0", 75),
        ("Consistency Check", "#EBF8FF", "#3182CE", "#2B6CB0", 82),
        ("Risk Score", "#ED8936", "#DD6B20", "#FFFFFF", 58),
    ]
    
    x = 5
    for i, (text, bg, border, font_c, w) in enumerate(steps):
        d.add(Rect(x, 6, w, 24, rx=3, ry=3, fillColor=colors.HexColor(bg), strokeColor=colors.HexColor(border), strokeWidth=1))
        d.add(String(x + w/2, 14, text, fontName="Helvetica-Bold", fontSize=6.5, textAnchor="middle", fillColor=colors.HexColor(font_c)))
        
        arrow_x = x + w
        d.add(Line(arrow_x, 18, arrow_x + 10, 18, strokeColor=colors.HexColor("#718096"), strokeWidth=1))
        d.add(Polygon([arrow_x + 10, 18, arrow_x + 6, 21, arrow_x + 6, 15], fillColor=colors.HexColor("#718096"), strokeColor=colors.HexColor("#718096")))
        x += w + 11

    d.add(Rect(x, 1, 95, 34, rx=3, ry=3, fillColor=colors.HexColor("#F7FAFC"), strokeColor=colors.HexColor("#A0AEC0"), strokeWidth=1))
    d.add(String(x + 47.5, 24, "[ Trusted? ]", fontName="Helvetica-Bold", fontSize=6.5, textAnchor="middle", fillColor=colors.HexColor("#2D3748")))
    d.add(String(x + 47.5, 15, "YES ➔ Vector DB", fontName="Helvetica-Bold", fontSize=6, textAnchor="middle", fillColor=colors.HexColor("#2F855A")))
    d.add(String(x + 47.5, 6, "NO ➔ Quarantine", fontName="Helvetica-Bold", fontSize=6, textAnchor="middle", fillColor=colors.HexColor("#C53030")))

    return d

def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    PRIMARY = colors.HexColor("#1A365D")    # Dark Navy
    SECONDARY = colors.HexColor("#2B6CB0")  # Slate Blue
    NEUTRAL_DARK = colors.HexColor("#2D3748") # Charcoal
    BG_LIGHT = colors.HexColor("#F7FAFC")   # Off-white

    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=20,
        textColor=PRIMARY,
        spaceAfter=2
    )

    style_subtitle = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=SECONDARY,
        spaceAfter=6
    )

    style_h1 = ParagraphStyle(
        'Header1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13.5,
        textColor=PRIMARY,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Header2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=SECONDARY,
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=NEUTRAL_DARK,
        spaceAfter=3.5
    )

    style_meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=PRIMARY
    )

    style_meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=NEUTRAL_DARK
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=NEUTRAL_DARK
    )

    style_caption = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7,
        leading=8.5,
        alignment=1,
        textColor=colors.HexColor("#718096"),
        spaceBefore=1,
        spaceAfter=4
    )

    story = []

    # Title & Header
    story.append(Paragraph("Preliminary Experiment Results", style_title))
    story.append(Paragraph("Data Poisoning and Prompt Injection Attacks on Retrieval-Augmented Generation (RAG) Systems", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1.2, color=PRIMARY, spaceBefore=0, spaceAfter=5))

    meta_data = [
        [
            Paragraph("Course:", style_meta_label), Paragraph("CSE 4531 (C): Computer Security", style_meta_val),
            Paragraph("University:", style_meta_label), Paragraph("United International University", style_meta_val)
        ],
        [
            Paragraph("Group & Sec:", style_meta_label), Paragraph("Group ID: 06 (Section C)", style_meta_val),
            Paragraph("Semester & Date:", style_meta_label), Paragraph("Summer 2026 | 21 July 2026", style_meta_val)
        ],
        [
            Paragraph("Team Members:", style_meta_label),
            Paragraph("011222245 - Jakaria Molla &nbsp;&nbsp;|&nbsp;&nbsp; 011222177 - Easmin Akter Tule<br/>011222172 - Taki Tahmid &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp; 011222285 - Pranto Shahriar Bishal", style_meta_val),
            Paragraph("", style_meta_label),
            Paragraph("", style_meta_val)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[75, 185, 80, 182])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('SPAN', (1, 2), (3, 2)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 3))

    # 1. Purpose & Scope
    story.append(Paragraph("1. Purpose & Scope", style_h1))
    story.append(Paragraph(
        "This report documents the preliminary laboratory experiment conducted following our literature review for CSE 4531. "
        "The objective is to evaluate how injecting an untrusted or outdated document into a Retrieval-Augmented Generation (RAG) knowledge base "
        "affects vector document retrieval and the final synthesized response generated by Google Gemini. "
        "This is an initial experimental validation of RAG document trust risks, serving as the 21 July course milestone.",
        style_body
    ))

    # 2. Technical Setup
    story.append(Paragraph("2. Technical Setup", style_h1))
    tech_data = [
        [Paragraph("Component", style_table_header), Paragraph("Specification", style_table_header), Paragraph("Component", style_table_header), Paragraph("Specification", style_table_header)],
        [Paragraph("Programming Language", style_table_cell), Paragraph("Python 3.11+", style_table_cell), Paragraph("Vector Database", style_table_cell), Paragraph("ChromaDB", style_table_cell)],
        [Paragraph("Orchestration Framework", style_table_cell), Paragraph("LangChain", style_table_cell), Paragraph("Embedding Model", style_table_cell), Paragraph("Sentence Transformers (MiniLM-L6-v2)", style_table_cell)],
        [Paragraph("Language Model (LLM)", style_table_cell), Paragraph("Google Gemini API (1.5 Flash)", style_table_cell), Paragraph("Document Loader", style_table_cell), Paragraph("PyPDF Loader", style_table_cell)],
        [Paragraph("Trusted Policy Corpus", style_table_cell), Paragraph("5 PDF Documents", style_table_cell), Paragraph("Inconsistent Document", style_table_cell), Paragraph("1 Outdated PDF Manual", style_table_cell)]
    ]
    tech_table = Table(tech_data, colWidths=[110, 151, 110, 151])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 3))

    # 3. Experiment Design
    story.append(Paragraph("3. Experiment Design", style_h1))
    story.append(Paragraph(
        "<b>Phase 1 (Trusted Knowledge Base):</b> ChromaDB was populated with 5 official policies: <i>Password Policy</i>, <i>VPN Policy</i>, <i>MFA Standard</i>, <i>Leave Policy</i>, and <i>Security Guidelines</i>. Two baseline test queries were executed to record retrieval ranking and Gemini answers.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Phase 2 (Mixed Knowledge Base):</b> One inconsistent document (<i>outdated_vpn_policy.pdf</i>) containing conflicting guidance (plain-text password email reset, unencrypted setup ZIP download without MFA) was added. The exact same queries were re-evaluated to observe retrieval drift and context window contamination.",
        style_body
    ))

    # 4. Workflows & Visualizations
    story.append(Paragraph("4. Architectural Workflow Diagrams", style_h1))
    
    story.append(Paragraph("<b>Figure 1:</b> Baseline RAG Workflow (Phase 1: Trusted Corpus)", style_h2))
    story.append(create_diagram_1())
    story.append(Paragraph("Figure 1: Standard retrieval pipeline producing verified responses.", style_caption))

    story.append(Paragraph("<b>Figure 2:</b> Mixed Knowledge Base Workflow (Phase 2: Inconsistent Document Ingestion)", style_h2))
    story.append(create_diagram_2())
    story.append(Paragraph("Figure 2: Vector context window contamination resulting from unfiltered similarity search.", style_caption))

    # 5. Experimental Results
    story.append(Paragraph("5. Experimental Results & Observations", style_h1))
    
    results_data = [
        [
            Paragraph("Query", style_table_header),
            Paragraph("Retrieved Context (Phase 1: Trusted)", style_table_header),
            Paragraph("Retrieved Context (Phase 2: Mixed)", style_table_header),
            Paragraph("Retrieval & LLM Impact Observation", style_table_header)
        ],
        [
            Paragraph("<b>Q1: Password Reset Procedure</b>", style_table_cell),
            Paragraph("1. password_policy.pdf<br/>2. security_guidelines.pdf<br/>3. mfa_policy.pdf", style_table_cell),
            Paragraph("1. password_policy.pdf<br/><b>2. outdated_vpn_policy.pdf</b><br/>3. security_guidelines.pdf", style_table_cell),
            Paragraph("Outdated policy appeared in Top-3 results ($L_2$ distance 1.2883), introducing plain-text email reset instructions into Gemini's context window.", style_table_cell)
        ],
        [
            Paragraph("<b>Q2: VPN Access Configuration</b>", style_table_cell),
            Paragraph("1. vpn_policy.pdf<br/>2. leave_policy.pdf<br/>3. password_policy.pdf", style_table_cell),
            Paragraph("1. vpn_policy.pdf<br/><b>2. outdated_vpn_policy.pdf</b><br/>3. leave_policy.pdf", style_table_cell),
            Paragraph("Legacy guide ranked 2nd ($L_2$ distance 1.3300), supplying an unencrypted ZIP setup link and stating MFA is not required.", style_table_cell)
        ]
    ]

    results_table = Table(results_data, colWidths=[100, 135, 142, 145])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 2))

    story.append(Paragraph("Impact Analysis on Gemini Output", style_h2))
    story.append(Paragraph(
        "The Gemini responses remained mostly correct because official documents maintained top similarity scores. However, because the retrieved context now contained conflicting legacy directives, Gemini included these inconsistent statements in its synthesized output. This demonstrates that LLMs receive conflicting evidence if no document trust mechanism is applied.",
        style_body
    ))

    # 6. Discussion & Research Gap
    story.append(Paragraph("6. Discussion & Research Gap", style_h1))
    story.append(Paragraph(
        "<b>Discussion:</b> The retrieval stage is the first point where knowledge quality directly affects the generated response. Although Gemini attempted to generate reasonable answers, the presence of inconsistent documents demonstrates that document trustworthiness is a crucial security concern for RAG architectures.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Research Gap:</b> Current RAG systems generally assume indexed documents are trustworthy, and existing research mainly focuses on prompt filtering after retrieval. However, there is limited emphasis on validating documents before indexing. This project therefore proposes developing a lightweight document trust evaluation and sanitization framework capable of identifying suspicious documents before they become searchable inside the vector database.",
        style_body
    ))

    # 7. Proposed Future Defense & Conclusion
    story.append(Paragraph("7. Proposed Future Defense & Conclusion", style_h1))
    story.append(Paragraph("<b>Figure 3:</b> Proposed Pre-Indexing Trust Evaluation & Sanitization Framework", style_h2))
    story.append(create_diagram_3())
    story.append(Paragraph("Figure 3: Defensive pipeline validating document metadata, trust, and consistency prior to vector storage.", style_caption))

    story.append(Paragraph(
        "<b>Conclusion:</b> This preliminary experiment successfully demonstrated that introducing inconsistent documents changes retrieval behavior and may influence the context supplied to Gemini. Although a complete defense mechanism has not yet been implemented, the experiment provides a solid foundation for the next stages of our research.",
        style_body
    ))

    # Appendix
    story.append(Spacer(1, 2))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E0"), spaceBefore=2, spaceAfter=4))
    story.append(Paragraph(
        "<b>Appendix: Source Code Repository</b>: All experimental code and log data are available at: "
        '<font color="#2B6CB0"><u><a href="https://github.com/takitahmid20/rag-data-poisoning">https://github.com/takitahmid20/rag-data-poisoning</a></u></font>',
        style_body
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[✔] Generated professional PDF report: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
