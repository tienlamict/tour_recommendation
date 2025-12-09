"""Results tab for displaying tour recommendations."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import List
from pathlib import Path

from ..models.tour import Tour
from ..utils.export import ExportService

logger = logging.getLogger(__name__)


class ResultsTab(ttk.Frame):
    """Tab for displaying recommendation results."""
    
    def __init__(self, parent, criteria_names: List[str]):
        """Initialize results tab.
        
        Args:
            parent: Parent widget
            criteria_names: List of criterion names
        """
        super().__init__(parent)
        
        self.criteria_names = criteria_names
        self.tours = []
        self.export_service = ExportService()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Kết quả gợi ý Tour",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=5)
        
        ttk.Button(
            toolbar,
            text="Xuất CSV",
            command=self.export_csv
        ).pack(side='left', padx=5)
        
        ttk.Button(
            toolbar,
            text="Xuất PDF",
            command=self.export_pdf
        ).pack(side='left', padx=5)
        
        ttk.Button(
            toolbar,
            text="Làm mới",
            command=self.refresh
        ).pack(side='left', padx=5)
        
        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview for results
        columns = ('stt', 'name', 'destination', 'duration', 'price', 'ahp', 'topsis')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Column headings
        self.tree.heading('stt', text='STT')
        self.tree.heading('name', text='Tên Tour')
        self.tree.heading('destination', text='Điểm đến')
        self.tree.heading('duration', text='Số ngày')
        self.tree.heading('price', text='Giá')
        self.tree.heading('ahp', text='Điểm AHP')
        self.tree.heading('topsis', text='Điểm TOPSIS')
        
        # Column widths
        self.tree.column('stt', width=50, anchor='center')
        self.tree.column('name', width=200, anchor='w')
        self.tree.column('destination', width=120, anchor='w')
        self.tree.column('duration', width=80, anchor='center')
        self.tree.column('price', width=100, anchor='e')
        self.tree.column('ahp', width=100, anchor='center')
        self.tree.column('topsis', width=100, anchor='center')
        
        # Scrollbars
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.on_tour_double_click)
        
        # Status bar
        self.status_label = ttk.Label(
            main_frame,
            text="Chưa có kết quả. Vui lòng tính toán gợi ý.",
            font=('Arial', 9),
            foreground='gray'
        )
        self.status_label.pack(pady=5)
    
    def display_results(self, tours: List[Tour]):
        """Display tour results.
        
        Args:
            tours: List of tours to display
        """
        self.tours = tours
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add tours
        for i, tour in enumerate(tours, 1):
            self.tree.insert('', 'end', values=(
                i,
                tour.name,
                tour.destination,
                f"{tour.duration} ngày",
                tour.get_price_display(),
                f"{tour.ahp_score:.4f}" if tour.ahp_score else '-',
                f"{tour.topsis_score:.4f}" if tour.topsis_score else '-'
            ))
        
        # Update status
        self.status_label.config(
            text=f"Hiển thị {len(tours)} tour được đề xuất (sắp xếp theo điểm TOPSIS)",
            foreground='green'
        )
        
        logger.info(f"Displayed {len(tours)} tours in results tab")
    
    def on_tour_double_click(self, event):
        """Handle double-click on tour.
        
        Args:
            event: Click event
        """
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get selected tour
        item = self.tree.item(selection[0])
        stt = int(item['values'][0])
        tour = self.tours[stt - 1]
        
        # Show tour details
        self.show_tour_details(tour)
    
    def show_tour_details(self, tour: Tour):
        """Show detailed tour information.
        
        Args:
            tour: Tour to display
        """
        # Create detail window
        detail_window = tk.Toplevel(self)
        detail_window.title(f"Chi tiết: {tour.name}")
        detail_window.geometry("600x500")
        
        # Main frame
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Tour name
        ttk.Label(
            main_frame,
            text=tour.name,
            font=('Arial', 16, 'bold')
        ).pack(pady=10)
        
        # Basic info frame
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin cơ bản", padding=10)
        info_frame.pack(fill='x', pady=10)
        
        info_text = f"""
Điểm đến: {tour.destination}
Thời gian: {tour.duration} ngày
Giá: {tour.price:,.0f} VNĐ ({tour.get_price_display()})
Độ khó: {tour.get_difficulty_display()}
Số người tối đa: {tour.max_participants}
Mùa phù hợp: {tour.season or 'Quanh năm'}
        """
        
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')
        
        # Scores frame
        scores_frame = ttk.LabelFrame(main_frame, text="Điểm đánh giá", padding=10)
        scores_frame.pack(fill='x', pady=10)
        
        scores_text = f"""
Điểm AHP: {tour.ahp_score:.4f}
Điểm TOPSIS: {tour.topsis_score:.4f}
        """
        
        ttk.Label(scores_frame, text=scores_text, justify='left', font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # Criteria scores frame
        criteria_frame = ttk.LabelFrame(main_frame, text="Điểm theo tiêu chí", padding=10)
        criteria_frame.pack(fill='both', expand=True, pady=10)
        
        # Create text widget for criteria scores
        criteria_text = tk.Text(criteria_frame, height=8, width=50, font=('Courier', 9))
        criteria_text.pack(fill='both', expand=True)
        
        criteria_text.insert(tk.END, f"{'Tiêu chí':<20} {'Điểm':>10}\n")
        criteria_text.insert(tk.END, "-" * 32 + "\n")
        
        for criterion in self.criteria_names:
            score = tour.get_criterion_score(criterion)
            criteria_text.insert(tk.END, f"{criterion:<20} {score:>10.1f}/10\n")
        
        criteria_text.config(state='disabled')
        
        # Description
        if tour.description:
            desc_frame = ttk.LabelFrame(main_frame, text="Mô tả", padding=10)
            desc_frame.pack(fill='both', expand=True, pady=10)
            
            desc_text = tk.Text(desc_frame, height=5, width=50, wrap='word', font=('Arial', 9))
            desc_text.pack(fill='both', expand=True)
            desc_text.insert(tk.END, tour.description)
            desc_text.config(state='disabled')
        
        # Close button
        ttk.Button(
            main_frame,
            text="Đóng",
            command=detail_window.destroy
        ).pack(pady=10)
    
    def export_csv(self):
        """Export results to CSV."""
        if not self.tours:
            messagebox.showwarning("Cảnh báo", "Không có kết quả để xuất!")
            return
        
        try:
            # Ask for file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="tour_recommendations.csv"
            )
            
            if not file_path:
                return
            
            # Export
            self.export_service.export_to_csv(self.tours, Path(file_path))
            messagebox.showinfo("Thành công", f"Đã xuất kết quả ra file:\n{file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            messagebox.showerror("Lỗi", f"Không thể xuất CSV: {e}")
    
    def export_pdf(self):
        """Export results to PDF."""
        if not self.tours:
            messagebox.showwarning("Cảnh báo", "Không có kết quả để xuất!")
            return
        
        try:
            # Ask for file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile="tour_recommendations.pdf"
            )
            
            if not file_path:
                return
            
            # Export
            self.export_service.export_to_pdf(
                self.tours,
                Path(file_path),
                criteria_names=self.criteria_names
            )
            messagebox.showinfo("Thành công", f"Đã xuất kết quả ra file:\n{file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            messagebox.showerror("Lỗi", f"Không thể xuất PDF: {e}")
    
    def refresh(self):
        """Refresh results display."""
        if self.tours:
            self.display_results(self.tours)
    
    def clear(self):
        """Clear results."""
        self.tours = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_label.config(
            text="Chưa có kết quả. Vui lòng tính toán gợi ý.",
            foreground='gray'
        )

