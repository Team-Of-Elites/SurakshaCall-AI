"""
scripts/generate_pdf_guide.py

Generates a complete, beautiful Hinglish PDF documentation for SurakshaCall AI.
Target file: SurakshaCall_AI_Complete_Guide_Hinglish.pdf
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

def build_pdf():
    pdf_filename = "SurakshaCall_AI_Complete_Guide_Hinglish.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_COLOR = colors.HexColor("#1A365D")    # Dark Navy
    SECONDARY_COLOR = colors.HexColor("#2B6CB0")  # Royal Blue
    ACCENT_COLOR = colors.HexColor("#319795")     # Teal
    BG_LIGHT = colors.HexColor("#F7FAFC")         # Light Grey
    TEXT_DARK = colors.HexColor("#2D3748")        # Dark Grey
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY_COLOR,
        alignment=1, # Center
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=SECONDARY_COLOR,
        alignment=1,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY_COLOR,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY_COLOR,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2C5282"),
        backColor=colors.HexColor("#EDF2F7"),
        borderColor=colors.HexColor("#CBD5E0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=8
    )

    callout_style = ParagraphStyle(
        'CalloutStyle',
        parent=body_style,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2C5282"),
        backColor=colors.HexColor("#EBF8FF"),
        borderColor=colors.HexColor("#90CDF4"),
        borderWidth=1,
        borderPadding=10,
        spaceBefore=8,
        spaceAfter=12
    )

    story = []

    # Title & Header
    story.append(Paragraph("🛡️ SurakshaCall AI — Complete Project Guide", title_style))
    story.append(Paragraph("Audio Pipeline, Architecture, Tech Stack & Workflow (Hinglish Documentation)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceBefore=0, spaceAfter=15))

    # Section 1: Executive Summary & Project Goal
    story.append(Paragraph("1. Project Ka Maqsad Kya Hai? (Executive Summary)", h1_style))
    story.append(Paragraph(
        "<b>SurakshaCall AI</b> ek real-time voice scam detection platform hai. Iska main target phone calls me hone wale <b>scam aur financial frauds</b> (jaise Bank KYC update, OTP demand, Urgent PIN requirement) ko live detect karna aur user ko turant alert karna hai.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Main Features:</b>", body_style
    ))
    story.append(Paragraph("• <b>Live Voice Analysis:</b> Phone mic ya incoming audio stream se sound capture karna.", bullet_style))
    story.append(Paragraph("• <b>Real-time Speech-to-Text (STT):</b> Hindi, English aur Hinglish (code-mixed) voice ko text me badalna.", bullet_style))
    story.append(Paragraph("• <b>Scam Risk Classifier & Rules Engine:</b> Text me fraud keywords aur urgencies detection.", bullet_style))
    story.append(Paragraph("• <b>Privacy-First Local AI:</b> Audio file ko kisi cloud API par nahi bhejta; local `faster-whisper` AI model se process karta hai.", bullet_style))

    story.append(Spacer(1, 10))

    # Section 2: Architecture & Workflow
    story.append(Paragraph("2. Project Kaise Kaam Karta Hai? (Step-by-Step Architecture)", h1_style))
    story.append(Paragraph(
        "SurakshaCall AI 6 modular steps me kaam karta hai. Har step ek alag Python component handle karta hai:",
        body_style
    ))

    flow_data = [
        [Paragraph("<b>Step</b>", body_style), Paragraph("<b>Component / Module</b>", body_style), Paragraph("<b>Kya Kam Karta Hai?</b>", body_style)],
        [Paragraph("<b>Step 1</b>", body_style), Paragraph("Microphone / Replay Engine<br/><code>microphone.py / replay.py</code>", body_style), Paragraph("Live mic se 16 kHz PCM16 audio chunks record karta hai.", body_style)],
        [Paragraph("<b>Step 2</b>", body_style), Paragraph("Voice Activity Detector<br/><code>vad.py</code>", body_style), Paragraph("Audio me se Aawaaz (speech) aur Khamoshi (silence) ko alag karta hai taaki unnecessary processing na ho.", body_style)],
        [Paragraph("<b>Step 3</b>", body_style), Paragraph("Circular Ring Buffer<br/><code>ring_buffer.py</code>", body_style), Paragraph("RAM me 20-second audio save rakhta hai. File disk par write nahi hoti jisse performance fast rehti hai.", body_style)],
        [Paragraph("<b>Step 4</b>", body_style), Paragraph("Speech Transcriber (AI)<br/><code>transcriber.py</code>", body_style), Paragraph("<code>faster-whisper</code> AI model audio ko Hindi/Hinglish text me convert karta hai.", body_style)],
        [Paragraph("<b>Step 5</b>", body_style), Paragraph("Detection & Risk Engine<br/><code>detection/rules.py</code>", body_style), Paragraph("Text me OTP, PIN, Blocked Account, Urgency jaise fraud indicators check karta hai.", body_style)],
        [Paragraph("<b>Step 6</b>", body_style), Paragraph("FastAPI & WebSockets<br/><code>main.py / websocket/</code>", body_style), Paragraph("Frontend Web App / Dashboard par live Transcripts aur Alert Warnings bhejta hai.", body_style)],
    ]

    t_flow = Table(flow_data, colWidths=[50, 160, 310])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0, 1), (-1, 1), BG_LIGHT),
        ('BACKGROUND', (0, 3), (-1, 3), BG_LIGHT),
        ('BACKGROUND', (0, 5), (-1, 5), BG_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_flow)

    story.append(Spacer(1, 15))

    # Section 3: Tech Stack & Technical Decisions
    story.append(Paragraph("3. Tech Stack: Kya Use Kiya Hai, Kyu Kiya Hai?", h1_style))
    story.append(Paragraph(
        "Is project me kaun konsi libraries use hui hain aur unhe chun-ne ke piche kya technical logic tha:",
        body_style
    ))

    tech_data = [
        [Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Kyu Use Kiya? (Technical Reason)</b>", body_style)],
        [Paragraph("<b>faster-whisper</b>", body_style), Paragraph("Lightweight & fast CTranslate2 implementation of OpenAI Whisper. Local run hota hai, koi API cost nahi, Hindi/Hinglish recognition industry-best hai.", body_style)],
        [Paragraph("<b>Pydantic v2</b>", body_style), Paragraph("Strict data validation ke liye. All audio frames, events, aur detection results <code>BaseModel</code> & <code>@computed_field</code> se type-safe rehte hain.", body_style)],
        [Paragraph("<b>FastAPI + Uvicorn</b>", body_style), Paragraph("Python ka sabse fast asynchronous web framework. Real-time WebSockets aur REST API streaming ke liye optimal hai.", body_style)],
        [Paragraph("<b>sounddevice + numpy</b>", body_style), Paragraph("Microphone audio array capture karne ke liye. Low latency processing ke liye int16 PCM format compute hota hai.", body_style)],
        [Paragraph("<b>Pytest + pytest-asyncio</b>", body_style), Paragraph("Async pipeline ko test karne ke liye. Comprehensive unit test suite se regression bugs roka jata hai.", body_style)],
    ]

    t_tech = Table(tech_data, colWidths=[140, 380])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0, 1), (-1, 1), BG_LIGHT),
        ('BACKGROUND', (0, 3), (-1, 3), BG_LIGHT),
        ('BACKGROUND', (0, 5), (-1, 5), BG_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_tech)

    story.append(Spacer(1, 15))

    # Section 4: Key Files Reference
    story.append(Paragraph("4. Directory & Key Files Guide (Kon Si File Kya Karti Hai)", h1_style))
    
    files_info = [
        ("backend/app/audio/vad.py", "Voice Activity Detector — Speech vs Silence ko distinguish karta hai. Continuous background noise ko skip karta hai."),
        ("backend/app/audio/ring_buffer.py", "In-Memory Circular Buffer — 20 second ki PCM audio memory me rakhta hai (bina disk read/write ke)."),
        ("backend/app/audio/microphone.py", "Microphone Capture Service — Laptop mic se non-blocking continuous 16kHz stream lene ke liye."),
        ("backend/app/audio/replay.py", "Timed Replay Engine — Test WAV files ko real-time call ki tarah stream karke pipeline test karta hai."),
        ("backend/app/stt/transcriber.py", "Speech Transcriber — Audio chunk ko Whisper model me bhejta hai aur structured `TranscriptEvent` banata hai."),
        ("backend/app/stt/model_loader.py", "Singleton Model Loader — Whisper model ko memory me ek baar load karta hai, CUDA missing ho toh auto CPU int8 par fallback karta hai."),
        ("backend/app/detection/rules.py", "Rule-based Scam Detector — Fraud keywords, bank terms aur scam tactics Match karta hai."),
        ("backend/app/main.py", "FastAPI App Entrypoint — REST Endpoints, OpenAPI /docs, aur WebSockets ko initialize karta hai."),
    ]

    for fpath, desc in files_info:
        story.append(Paragraph(f"• <b><code>{fpath}</code></b>: {desc}", bullet_style))

    story.append(Spacer(1, 15))

    # Section 5: Commands Cheat Sheet
    story.append(Paragraph("5. Commands Cheat Sheet (Kis Command Ka Kya Use Hai)", h1_style))
    story.append(Paragraph("Aapko terminal me chalane ke liye sabhi essential commands:", body_style))

    cmd_data = [
        [Paragraph("<b>Command</b>", body_style), Paragraph("<b>Purpose / Kya Hoga?</b>", body_style)],
        [Paragraph("<code>py scripts/list_microphones.py</code>", code_style), Paragraph("Connected microphones ki list aur default active mic index check karne ke liye.", body_style)],
        [Paragraph("<code>py scripts/record_test_audio.py --duration 5 --output data/demo/live_mic_test.wav</code>", code_style), Paragraph("Mic se 5 second voice record karne aur volume auto-boost karke save karne ke liye.", body_style)],
        [Paragraph("<code>py scripts/test_live_transcription.py</code>", code_style), Paragraph("Live recorded voice ko Whisper AI se transcribe (Text conversion) test karne ke liye.", body_style)],
        [Paragraph("<code>py scripts/test_audio_pipeline.py</code>", code_style), Paragraph("Audio pipeline (VAD + Chunker + Whisper) ka end-to-end integration test chalane ke liye.", body_style)],
        [Paragraph("<code>py -m uvicorn backend.app.main:app --reload --port 8000</code>", code_style), Paragraph("FastAPI Live Backend Server start karne ke liye (Browser: <code>http://127.0.0.1:8000/docs</code>).", body_style)],
        [Paragraph("<code>py -m pytest tests/test_audio_pipeline.py</code>", code_style), Paragraph("Audio pipeline ke sabhi 13 unit tests run karne ke liye.", body_style)],
    ]

    t_cmd = Table(cmd_data, colWidths=[240, 280])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0, 1), (-1, 1), BG_LIGHT),
        ('BACKGROUND', (0, 3), (-1, 3), BG_LIGHT),
        ('BACKGROUND', (0, 5), (-1, 5), BG_LIGHT),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_cmd)

    story.append(Spacer(1, 15))

    # Section 6: How to Explain to Teammates (Presentation Script)
    story.append(Paragraph("6. Teammates Ko Samjhane Ke Liye 1-Minute Pitch Script", h1_style))
    callout_text = (
        "<b>🗣️ Aap Apne Teammates Ko Ye Bolein:</b><br/><br/>"
        "<i>\"Humara SurakshaCall AI project live phone calls me scam detection ke liye banaya gaya hai. "
        "Mera role Audio Pipeline Owner ka tha, aur maine audio stack ko complete aur test kar diya hai.<br/><br/>"
        "<b>Key Technical Deliverables:</b><br/>"
        "1. Humara VAD system khamoshi aur aawaaz ko alag karta hai taaki CPU/GPU power waste na ho.<br/>"
        "2. Humara In-Memory Ring Buffer 20s audio RAM me rakhta hai, bina kisi disk delay ke.<br/>"
        "3. Offline `faster-whisper` AI model Hindi aur Hinglish voice ko instantly text me convert karta hai.<br/>"
        "4. Maine 100% Unit Tests aur Live Microphone Testing complete kar di hai. Ab backend/frontend team hamare `TranscriptEvent` data stream ko easily consuming/displaying ke liye connect kar sakti hai.\"</i>"
    )
    story.append(Paragraph(callout_text, callout_style))

    # Build Document
    doc.build(story)
    print(f"[SUCCESS] PDF generated successfully: {os.path.abspath(pdf_filename)}")

if __name__ == "__main__":
    build_pdf()
