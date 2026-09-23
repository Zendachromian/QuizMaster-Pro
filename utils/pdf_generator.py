from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io

def generate_monthly_report_pdf(user_data, report_data):
    """
    Generate PDF monthly report for user
    """
    buffer = io.BytesIO()
    
    # Setup PDF doc
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # My custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#007bff')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6c757d')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#495057')
    )
    
    # Story list to hold all content
    story = []
    
    # Header
    story.append(Paragraph("QuizMaster Pro", title_style))
    story.append(Paragraph("Monthly Quiz Report", subtitle_style))
    story.append(Paragraph(f"{report_data.get('month_year', 'Report')}", subtitle_style))
    story.append(Spacer(1, 20))
    
    # User greeting
    story.append(Paragraph(f"Hi {user_data.get('full_name', 'Student')}!", heading_style))
    story.append(Paragraph("Here's your quiz performance summary for the month:", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Statistics Table
    stats_data = [
        ['Metric', 'Value'],
        ['Quizzes Completed', str(report_data.get('total_attempts', 0))],
        ['Average Score', f"{report_data.get('average_score', 0):.1f}%"],
        ['Best Score', f"{report_data.get('best_score', 0):.1f}%"],
        ['Average Time per Quiz', f"{report_data.get('avg_time_per_quiz', 0)/60:.1f} minutes"]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    story.append(Paragraph("Performance Summary", heading_style))
    story.append(stats_table)
    story.append(Spacer(1, 30))
    
    # Subject-wise Performance
    if 'subject_stats' in report_data and report_data['subject_stats']:
        story.append(Paragraph("Subject-wise Performance", heading_style))
        
        subject_data = [['Subject', 'Quizzes Taken', 'Average Score', 'Best Score']]
        for subject, scores in report_data['subject_stats'].items():
            subject_data.append([
                subject,
                str(len(scores)),
                f"{sum(scores)/len(scores):.1f}%",
                f"{max(scores):.1f}%"
            ])
        
        subject_table = Table(subject_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        subject_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(subject_table)
        story.append(Spacer(1, 30))
    
    # Performance Rating
    performance_rating = report_data.get('performance_rating', 'Keep Learning!')
    story.append(Paragraph("Performance Rating", heading_style))
    
    rating_style = ParagraphStyle(
        'Rating',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_CENTER,
        backColor=colors.HexColor('#e7f3ff'),
        borderColor=colors.HexColor('#007bff'),
        borderWidth=1,
        borderPadding=10
    )
    
    story.append(Paragraph(f"<b>{performance_rating}</b>", rating_style))
    story.append(Paragraph("Keep up the great work! Continue learning and improving your scores.", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Call to Action
    story.append(Paragraph("Ready for more challenges?", heading_style))
    story.append(Paragraph("Log in to QuizMaster Pro and take more quizzes to continue improving your knowledge!", styles['Normal']))
    story.append(Spacer(1, 40))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6c757d')
    )
    
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", footer_style))
    story.append(Paragraph("Best regards,<br/>QuizMaster Team", footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Get the value of the BytesIO buffer and return
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
