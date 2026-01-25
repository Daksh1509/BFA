# File: generate_sample_proposals.py
# Run: python generate_sample_proposals.py

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime

# ============================================
# GOOD PROPOSAL: AI Chatbot
# ============================================

def create_good_proposal():
    pdf_path = "good_proposal_chatbot.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=1  # Center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=10,
        spaceBefore=10
    )
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    story = []
    
    # Title
    story.append(Paragraph("Business Proposal: AI-Powered Customer Support Chatbot", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Header info
    header_data = [
        ["Date:", "January 26, 2026"],
        ["Prepared by:", "Innovation Team"],
        ["Company:", "TechVenture Solutions"]
    ]
    header_table = Table(header_data, colWidths=[2*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#1f4788')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(
        "We propose to develop and deploy an <b>AI-powered customer support chatbot</b> for our e-commerce platform "
        "to reduce support costs, improve response time, and increase customer satisfaction. The chatbot will handle 60% "
        "of routine inquiries, allowing our support team to focus on complex issues.",
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    summary_data = [
        ["Total Investment:", "$85,000"],
        ["Expected ROI:", "220% in Year 1"],
        ["Payback Period:", "4.5 months"]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#e8f0f7')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.grey)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Problem Statement
    story.append(Paragraph("Problem Statement", heading_style))
    story.append(Paragraph("<b>Current Challenges:</b>", normal_style))
    challenges = [
        "Support Team Overload: 12-person team handles 500+ inquiries daily → 24–48 hour delays",
        "High Operating Costs: $480,000/year (salaries + tools + infrastructure)",
        "Poor CSAT: 35% report slow responses; NPS 42 (industry avg: 65)",
        "Scalability Issues: Adding staff costs $55,000/year per person"
    ]
    for challenge in challenges:
        story.append(Paragraph(f"• {challenge}", normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Solution
    story.append(Paragraph("Proposed Solution", heading_style))
    story.append(Paragraph("<b>Features:</b>", normal_style))
    features = [
        "Multilingual Support (English, Spanish, French, Mandarin)",
        "NLU with Groq Llama 3.1 LLM",
        "Real-time order database integration",
        "Human escalation for complex issues",
        "24/7 availability across time zones",
        "Machine learning improvements over time"
    ]
    for feature in features:
        story.append(Paragraph(f"• {feature}", normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Financial Projections
    story.append(Paragraph("Financial Projections", heading_style))
    fin_data = [
        ["Metric", "Year 1 Impact"],
        ["Cost Savings (reduced team)", "$233,500"],
        ["Revenue Gains (retention + NPS)", "$300,000"],
        ["Total Benefit", "$533,500"],
        ["ROI", "528%"],
        ["Payback Period", "1.1 months"]
    ]
    fin_table = Table(fin_data, colWidths=[3*inch, 2*inch])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0f0f0'))
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Timeline
    story.append(Paragraph("Implementation Timeline", heading_style))
    timeline_data = [
        ["Phase", "Duration", "Key Activities"],
        ["Planning & Setup", "2 weeks", "Requirements, architecture, AWS setup"],
        ["Development", "8 weeks", "Build backend, train model, integrate"],
        ["Testing", "3 weeks", "QA, UAT, beta deployment (10% traffic)"],
        ["Launch", "2 weeks", "Full rollout, team training, monitoring"],
        ["Total", "15 weeks", "Go-live: mid-May 2026"]
    ]
    timeline_table = Table(timeline_data, colWidths=[1.5*inch, 1.5*inch, 2.5*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f9f9f9'))
    ]))
    story.append(timeline_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Risks
    story.append(Paragraph("Risk Assessment", heading_style))
    risks = [
        "Poor AI accuracy → Mitigate: Start simple, human escalation",
        "Integration delays → Mitigate: API exists, add buffer time",
        "Rate limits → Mitigate: Queuing system for spikes",
        "Data security → Mitigate: Encryption, GDPR compliance"
    ]
    for risk in risks:
        story.append(Paragraph(f"• {risk}", normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Conclusion
    story.append(Paragraph("Conclusion", heading_style))
    story.append(Paragraph(
        "The AI chatbot is a <b>low-risk, high-return investment</b> with a 4.5-month payback period and 220% Year 1 ROI. "
        "Recommend immediate approval. Target launch: May 2026.",
        normal_style
    ))
    
    doc.build(story)
    print(f"✅ Good proposal PDF created: {pdf_path}")


# ============================================
# BAD PROPOSAL: Flying Car Rental
# ============================================

def create_bad_proposal():
    pdf_path = "bad_proposal_flying_cars.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#8b0000'),  # Dark red for bad
        spaceAfter=12,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#c41e3a'),
        spaceAfter=10,
        spaceBefore=10
    )
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    story = []
    
    # Title
    story.append(Paragraph("Business Proposal: Flying Car Rental Service", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Header info
    header_data = [
        ["Date:", "January 26, 2026"],
        ["Prepared by:", "SkyDream Team"],
        ["Company:", "FutureTrans Inc."]
    ]
    header_table = Table(header_data, colWidths=[2*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#8b0000')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(
        "We propose launching a <b>flying car rental service</b> in major US cities. Customers rent autonomous flying cars "
        "via app for $29/hour. Fleet of 50 autonomous flying vehicles with custom drone rotors.",
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    summary_data = [
        ["Total Investment:", "$2.5 million"],
        ["Expected ROI:", "1,200% in Year 1"],
        ["Payback Period:", "1 month"]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#ffe8e8')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.red)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Problem Statement
    story.append(Paragraph("Problem Statement", heading_style))
    story.append(Paragraph(
        "Ground traffic sucks. Flying cars solve it. People hate sitting in cars.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Market Opportunity
    story.append(Paragraph("Market Opportunity", heading_style))
    opportunities = [
        "TAM: $500 billion global mobility market",
        "Target: Urban millennials who hate traffic",
        "Competitors: None (we're first!)",
        "Demand: Obvious (everyone wants flying cars)"
    ]
    for opp in opportunities:
        story.append(Paragraph(f"• {opp}", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Solution
    story.append(Paragraph("Solution", heading_style))
    story.append(Paragraph("<b>Flying Car Fleet:</b>", normal_style))
    solution = [
        "50 autonomous flying cars (Tesla Cyberquad + drone rotors)",
        "App-based booking (Uber-like interface)",
        "Vertical takeoff/landing from rooftops",
        "AI autopilot powered by ChatGPT",
        "2-hour battery flight time"
    ]
    for sol in solution:
        story.append(Paragraph(f"• {sol}", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Financial Projections
    story.append(Paragraph("Financial Projections", heading_style))
    fin_data = [
        ["Metric", "Projection"],
        ["Daily rentals per car", "20"],
        ["Daily revenue per car", "$29/hour × 24 hours = $696"],
        ["Fleet daily revenue", "$696 × 50 = $34,800/day"],
        ["Annual revenue", "$34,800 × 365 = $12.7M"],
        ["ROI", "1,200% (Year 1)"],
        ["Payback", "1 month"]
    ]
    fin_table = Table(fin_data, colWidths=[3*inch, 2*inch])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#8b0000')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.red),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffe8e8'))
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Costs
    story.append(Paragraph("Costs (Year 1)", heading_style))
    costs = [
        "Flying cars: $20k each × 50 = $1.0M",
        "App development: $50k (outsourced to India)",
        "Insurance: $100k (estimated)",
        "Marketing: $50k",
        "Total: $1.2M → Profit: $11.5M → ROI: 1,058%"
    ]
    for cost in costs:
        story.append(Paragraph(f"• {cost}", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Team
    story.append(Paragraph("Team", heading_style))
    team = [
        "CEO: Founder (ex-Uber driver, 2 years experience)",
        "CTO: Cousin (plays drone racing games, self-taught programmer)",
        "Marketing: Interns from college"
    ]
    for member in team:
        story.append(Paragraph(f"• {member}", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Timeline
    story.append(Paragraph("Timeline", heading_style))
    timeline = [
        "Month 1: Build prototype",
        "Month 2: FAA certification",
        "Month 3: Launch NYC/SF/LA"
    ]
    for item in timeline:
        story.append(Paragraph(f"• {item}", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Risk
    story.append(Paragraph("Risk Assessment", heading_style))
    story.append(Paragraph("• No risks identified. First-mover advantage.", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Conclusion
    story.append(Paragraph("Conclusion", heading_style))
    story.append(Paragraph(
        "Flying cars = future. Everyone wants them. Invest now and become billionaire!",
        normal_style
    ))
    
    doc.build(story)
    print(f"✅ Bad proposal PDF created: {pdf_path}")


if __name__ == "__main__":
    print("Generating sample business proposals...\n")
    create_good_proposal()
    create_bad_proposal()
    print("\n✅ Both PDFs ready! Test them in your feasibility analyzer.")
