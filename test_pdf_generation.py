#!/usr/bin/env python3
"""
Test script for PDF report generation functionality
"""

from utils.pdf_generator import generate_monthly_report_pdf
import os

def test_pdf_generation():
    """Test the PDF generation functionality"""
    
    # Sample user data
    user_data = {
        'full_name': 'John Doe',
        'email': 'john.doe@example.com'
    }
    
    # Sample report data
    report_data = {
        'month_year': 'January 2025',
        'total_attempts': 15,
        'average_score': 85.5,
        'best_score': 95.0,
        'avg_time_per_quiz': 3600,  # 1 hour in seconds
        'subject_stats': {
            'Mathematics': [90, 85, 88, 92],
            'Science': [78, 82, 85, 89],
            'History': [75, 80, 83]
        },
        'performance_rating': 'Above Average'
    }
    
    print("🔧 Testing PDF generation...")
    
    try:
        # Generate PDF
        pdf_bytes = generate_monthly_report_pdf(user_data, report_data)
        
        # Save to file for verification
        output_path = 'test_monthly_report.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✅ PDF generated successfully!")
        print(f"📄 PDF saved as: {output_path}")
        print(f"📊 PDF size: {len(pdf_bytes)} bytes")
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
            print("🧹 Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n🎉 PDF generation test completed successfully!")
    else:
        print("\n💥 PDF generation test failed!")
