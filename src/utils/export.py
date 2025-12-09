"""Export functionality for CSV and PDF."""

import csv
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ..models.tour import Tour

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting tour recommendations."""
    
    @staticmethod
    def export_to_csv(tours: List[Tour], output_path: Path) -> None:
        """Export tours to CSV file.
        
        Args:
            tours: List of tours to export
            output_path: Path to output CSV file
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'STT', 'Tên Tour', 'Điểm đến', 'Số ngày', 'Giá (VNĐ)',
                    'Độ khó', 'Điểm AHP', 'Điểm TOPSIS'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for i, tour in enumerate(tours, 1):
                    writer.writerow({
                        'STT': i,
                        'Tên Tour': tour.name,
                        'Điểm đến': tour.destination,
                        'Số ngày': tour.duration,
                        'Giá (VNĐ)': f"{tour.price:,.0f}",
                        'Độ khó': tour.difficulty_level,
                        'Điểm AHP': f"{tour.ahp_score:.4f}" if tour.ahp_score else '',
                        'Điểm TOPSIS': f"{tour.topsis_score:.4f}" if tour.topsis_score else ''
                    })
            
            logger.info(f"Exported {len(tours)} tours to CSV: {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    @staticmethod
    def export_to_pdf(
        tours: List[Tour],
        output_path: Path,
        criteria_names: List[str] = None,
        user_name: str = None
    ) -> None:
        """Export tours to PDF file.
        
        Args:
            tours: List of tours to export
            output_path: Path to output PDF file
            criteria_names: Optional list of criteria names
            user_name: Optional user name
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            # Container for elements
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#34495E'),
                spaceAfter=12
            )
            
            # Title
            title = Paragraph("KẾT QUẢ GỢI Ý TOUR DU LỊCH", title_style)
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Metadata
            if user_name:
                meta = Paragraph(f"<b>Người dùng:</b> {user_name}", styles['Normal'])
                elements.append(meta)
            
            date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            date_para = Paragraph(f"<b>Ngày tạo:</b> {date_str}", styles['Normal'])
            elements.append(date_para)
            elements.append(Spacer(1, 20))
            
            # Summary
            summary_heading = Paragraph("TỔNG QUAN", heading_style)
            elements.append(summary_heading)
            
            summary_text = f"Tổng số tour được đề xuất: <b>{len(tours)}</b><br/>"
            if tours:
                avg_price = sum(t.price for t in tours) / len(tours)
                summary_text += f"Giá trung bình: <b>{avg_price:,.0f} VNĐ</b><br/>"
                avg_duration = sum(t.duration for t in tours) / len(tours)
                summary_text += f"Thời gian trung bình: <b>{avg_duration:.1f} ngày</b>"
            
            summary_para = Paragraph(summary_text, styles['Normal'])
            elements.append(summary_para)
            elements.append(Spacer(1, 20))
            
            # Tours table
            table_heading = Paragraph("DANH SÁCH TOUR ĐỀ XUẤT", heading_style)
            elements.append(table_heading)
            
            # Table data
            table_data = [
                ['STT', 'Tên Tour', 'Điểm đến', 'Ngày', 'Giá (triệu)', 'AHP', 'TOPSIS']
            ]
            
            for i, tour in enumerate(tours, 1):
                table_data.append([
                    str(i),
                    tour.name[:30],  # Truncate long names
                    tour.destination,
                    str(tour.duration),
                    f"{tour.price/1_000_000:.1f}",
                    f"{tour.ahp_score:.3f}" if tour.ahp_score else '-',
                    f"{tour.topsis_score:.3f}" if tour.topsis_score else '-'
                ])
            
            # Create table
            table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1.2*inch, 0.6*inch, 0.8*inch, 0.7*inch, 0.7*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # Top 5 detailed info
            if len(tours) > 0:
                elements.append(PageBreak())
                detail_heading = Paragraph("CHI TIẾT TOP 5 TOUR", heading_style)
                elements.append(detail_heading)
                elements.append(Spacer(1, 12))
                
                for i, tour in enumerate(tours[:5], 1):
                    # Tour name
                    tour_title = Paragraph(f"<b>{i}. {tour.name}</b>", styles['Heading3'])
                    elements.append(tour_title)
                    
                    # Tour details
                    details = f"""
                    <b>Điểm đến:</b> {tour.destination}<br/>
                    <b>Thời gian:</b> {tour.duration} ngày<br/>
                    <b>Giá:</b> {tour.price:,.0f} VNĐ<br/>
                    <b>Độ khó:</b> {tour.difficulty_level}<br/>
                    <b>Mùa phù hợp:</b> {tour.season or 'Quanh năm'}<br/>
                    <b>Điểm AHP:</b> {tour.ahp_score:.4f}<br/>
                    <b>Điểm TOPSIS:</b> {tour.topsis_score:.4f}
                    """
                    
                    if tour.description:
                        details += f"<br/><b>Mô tả:</b> {tour.description[:200]}..."
                    
                    details_para = Paragraph(details, styles['Normal'])
                    elements.append(details_para)
                    
                    # Criteria scores
                    if criteria_names and tour.criterion_scores:
                        criteria_text = "<b>Điểm theo tiêu chí:</b><br/>"
                        for criterion in criteria_names:
                            score = tour.get_criterion_score(criterion)
                            criteria_text += f"  • {criterion}: {score:.1f}/10<br/>"
                        
                        criteria_para = Paragraph(criteria_text, styles['Normal'])
                        elements.append(criteria_para)
                    
                    elements.append(Spacer(1, 20))
            
            # Footer
            footer_text = "---<br/>Báo cáo được tạo bởi Hệ thống Gợi ý Tour Du lịch (AHP + TOPSIS)"
            footer = Paragraph(footer_text, styles['Normal'])
            elements.append(Spacer(1, 30))
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"Exported {len(tours)} tours to PDF: {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise

