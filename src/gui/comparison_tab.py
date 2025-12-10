"""Comparison tab for AHP criteria comparison."""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import logging
from typing import List, Callable

from ..algorithms.ahp import AHPCalculator
from ..algorithms.validator import ConsistencyValidator
from .components.matrix_input import MatrixInputWidget

logger = logging.getLogger(__name__)


class ComparisonTab(ttk.Frame):
    """Tab for criteria pairwise comparison."""
    
    def __init__(self, parent, criteria_names: List[str], on_weights_calculated: Callable):
        """Initialize comparison tab.
        
        Args:
            parent: Parent widget
            criteria_names: List of criterion names
            on_weights_calculated: Callback when weights are calculated
        """
        super().__init__(parent)
        
        self.criteria_names = criteria_names
        self.on_weights_calculated = on_weights_calculated
        
        self.ahp_calculator = AHPCalculator()
        self.validator = ConsistencyValidator()
        
        self.comparison_matrix = None
        self.criteria_weights = None
        self.consistency_ratio = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create tab widgets."""
        # Create scrollable frame
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_scroll_region(event):
            # Update scroll region
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update canvas window width
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas (Windows)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind mousewheel for Linux
        def _on_button4(event):
            canvas.yview_scroll(-1, "units")
        def _on_button5(event):
            canvas.yview_scroll(1, "units")
        canvas.bind_all("<Button-4>", _on_button4)
        canvas.bind_all("<Button-5>", _on_button5)
        
        # Store canvas reference for cleanup
        self._canvas = canvas
        
        # Main container (inside scrollable frame)
        main_frame = ttk.Frame(scrollable_frame, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="So sánh cặp các tiêu chí",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=10)
        
        # Short instructions
        instructions = (
            "Hướng dẫn: So sánh cặp tiêu chí theo thang Saaty (1-9). "
            "Chỉ cần điền các ô màu trắng (phần trên đường chéo). "
            "1=Ngang nhau, 3=Hơn một chút, 5=Hơn, 7=Hơn nhiều, 9=Cực kỳ. "
            "Dùng phân số (1/3, 1/5...) nếu tiêu chí cột quan trọng hơn."
        )
        
        instructions_label = ttk.Label(
            main_frame,
            text=instructions,
            font=('Arial', 9),
            justify='left',
            background='#F0F8FF',
            padding=8,
            wraplength=800
        )
        instructions_label.pack(fill='x', pady=5)
        
        # Matrix input frame - limit height
        matrix_frame = ttk.LabelFrame(main_frame, text="Ma trận so sánh", padding=10)
        matrix_frame.pack(fill='both', expand=False, pady=10)
        
        # Matrix input widget - limit expansion
        self.matrix_input = MatrixInputWidget(
            matrix_frame,
            size=len(self.criteria_names),
            labels=self.criteria_names,
            on_change=self.on_matrix_change
        )
        self.matrix_input.pack(fill='both', expand=False)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Kết quả", padding=10)
        results_frame.pack(fill='x', pady=10)
        
        # Consistency ratio display
        cr_frame = ttk.Frame(results_frame)
        cr_frame.pack(fill='x', pady=5)
        
        ttk.Label(cr_frame, text="Consistency Ratio (CR):", font=('Arial', 10, 'bold')).pack(side='left')
        self.cr_label = ttk.Label(cr_frame, text="Chưa tính", font=('Arial', 10))
        self.cr_label.pack(side='left', padx=10)
        
        self.cr_status_label = ttk.Label(cr_frame, text="", font=('Arial', 10))
        self.cr_status_label.pack(side='left')
        
        # Weights display
        weights_frame = ttk.Frame(results_frame)
        weights_frame.pack(fill='both', expand=False, pady=5)
        
        ttk.Label(weights_frame, text="Trọng số tiêu chí:", font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.weights_text = tk.Text(weights_frame, height=8, width=50, font=('Courier', 9))
        self.weights_text.pack(fill='both', expand=False, pady=5)
        self.weights_text.config(state='disabled')
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            buttons_frame,
            text="Tính trọng số",
            command=self.calculate_weights
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Kiểm tra nhất quán",
            command=self.check_consistency
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Ví dụ",
            command=self.load_example
        ).pack(side='left', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Xóa",
            command=self.clear_matrix
        ).pack(side='left', padx=5)
    
    def on_matrix_change(self):
        """Handle matrix change event."""
        # Reset results
        self.cr_label.config(text="Chưa tính")
        self.cr_status_label.config(text="")
        self.criteria_weights = None
    
    def calculate_weights(self):
        """Calculate criteria weights from comparison matrix."""
        try:
            # Validate matrix
            if not self.matrix_input.validate():
                messagebox.showerror("Lỗi", "Ma trận chứa giá trị không hợp lệ")
                return
            
            # Get matrix
            self.comparison_matrix = self.matrix_input.get_matrix()
            
            # Calculate weights
            self.criteria_weights, self.consistency_ratio, is_consistent = \
                self.ahp_calculator.calculate_criteria_weights(self.comparison_matrix)
            
            # Display CR
            self.cr_label.config(text=f"{self.consistency_ratio:.4f}")
            
            if is_consistent:
                self.cr_status_label.config(
                    text="✓ Nhất quán",
                    foreground='green'
                )
            else:
                self.cr_status_label.config(
                    text="✗ Không nhất quán (CR >= 0.1)",
                    foreground='red'
                )
                messagebox.showwarning(
                    "Cảnh báo",
                    f"Ma trận không nhất quán (CR = {self.consistency_ratio:.4f}).\n"
                    "Vui lòng xem xét lại các so sánh."
                )
            
            # Display weights
            self.display_weights()
            
            # Notify parent
            if self.on_weights_calculated:
                self.on_weights_calculated(self.criteria_weights, self.consistency_ratio)
            
            messagebox.showinfo("Thành công", "Đã tính toán trọng số tiêu chí!")
        
        except Exception as e:
            logger.error(f"Error calculating weights: {e}")
            messagebox.showerror("Lỗi", f"Không thể tính trọng số: {e}")
    
    def check_consistency(self):
        """Check matrix consistency."""
        try:
            # Get matrix
            matrix = self.matrix_input.get_matrix()
            
            # Calculate weights (needed for CR)
            weights = self.ahp_calculator.calculate_weights_geometric_mean(matrix)
            
            # Check consistency
            is_consistent, cr = self.validator.is_consistent(matrix, weights)
            
            # Display result
            self.cr_label.config(text=f"{cr:.4f}")
            
            if is_consistent:
                self.cr_status_label.config(
                    text="✓ Nhất quán",
                    foreground='green'
                )
                messagebox.showinfo(
                    "Kết quả",
                    f"Ma trận nhất quán!\nConsistency Ratio = {cr:.4f} < 0.1"
                )
            else:
                self.cr_status_label.config(
                    text="✗ Không nhất quán",
                    foreground='red'
                )
                
                # Find specific inconsistencies
                inconsistencies = self.validator.find_inconsistencies(matrix, self.criteria_names)
                
                # Build detailed message
                message = f"Ma trận không nhất quán!\n\n"
                message += f"Consistency Ratio (CR) = {cr:.4f}\n"
                message += f"CR nên < 0.1 để đáng tin cậy\n\n"
                
                if cr >= 0.1 and cr < 0.2:
                    message += "⚠️ CR hơi cao - có một số mâu thuẫn nhỏ\n\n"
                elif cr >= 0.2:
                    message += "❌ CR rất cao - có nhiều mâu thuẫn lớn\n\n"
                
                if inconsistencies:
                    message += "Các mâu thuẫn phát hiện:\n"
                    message += "=" * 50 + "\n\n"
                    
                    # Show top 5 most significant inconsistencies
                    sorted_incons = sorted(inconsistencies, key=lambda x: abs(np.log(x['ratio'])), reverse=True)
                    for i, inc in enumerate(sorted_incons[:5], 1):
                        message += f"{i}. {inc['description']}\n\n"
                    
                    message += "💡 Gợi ý: Xem xét lại các so sánh trên để điều chỉnh.\n"
                    message += "   Ví dụ: Nếu A > B và B > C, thì A nên > C."
                else:
                    message += "💡 Gợi ý: Hãy xem xét lại các so sánh, đặc biệt là các giá trị lớn (7, 9).\n"
                    message += "   Thử giảm các giá trị xuống (ví dụ: 9 → 7, 7 → 5) để giảm mâu thuẫn."
                
                messagebox.showwarning("Kết quả", message)
        
        except Exception as e:
            logger.error(f"Error checking consistency: {e}")
            messagebox.showerror("Lỗi", f"Không thể kiểm tra nhất quán: {e}")
    
    def display_weights(self):
        """Display calculated weights."""
        if self.criteria_weights is None:
            return
        
        self.weights_text.config(state='normal')
        self.weights_text.delete(1.0, tk.END)
        
        # Header
        self.weights_text.insert(tk.END, f"{'Tiêu chí':<20} {'Trọng số':>10} {'%':>8}\n")
        self.weights_text.insert(tk.END, "-" * 40 + "\n")
        
        # Weights
        for i, criterion in enumerate(self.criteria_names):
            weight = self.criteria_weights[i]
            self.weights_text.insert(
                tk.END,
                f"{criterion:<20} {weight:>10.4f} {weight*100:>7.2f}%\n"
            )
        
        # Total
        self.weights_text.insert(tk.END, "-" * 40 + "\n")
        self.weights_text.insert(tk.END, f"{'Tổng':<20} {np.sum(self.criteria_weights):>10.4f} {100:>7.2f}%\n")
        
        self.weights_text.config(state='disabled')
    
    def load_example(self):
        """Load example comparison matrix."""
        try:
            # Get example matrix
            example_matrix = self.ahp_calculator.create_example_matrix(len(self.criteria_names))
            
            # Set matrix
            self.matrix_input.set_matrix(example_matrix)
            
            messagebox.showinfo("Thông báo", "Đã tải ma trận ví dụ!")
        
        except Exception as e:
            logger.error(f"Error loading example: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải ví dụ: {e}")
    
    def clear_matrix(self):
        """Clear comparison matrix."""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả?"):
            self.matrix_input.clear()
            self.cr_label.config(text="Chưa tính")
            self.cr_status_label.config(text="")
            self.criteria_weights = None
            
            self.weights_text.config(state='normal')
            self.weights_text.delete(1.0, tk.END)
            self.weights_text.config(state='disabled')
    
    def get_weights(self):
        """Get calculated weights.
        
        Returns:
            Tuple of (weights, consistency_ratio)
        """
        return self.criteria_weights, self.consistency_ratio
    
    def set_matrix(self, matrix: np.ndarray):
        """Set comparison matrix.
        
        Args:
            matrix: Comparison matrix
        """
        self.matrix_input.set_matrix(matrix)

