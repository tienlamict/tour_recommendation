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
        
        # Instructions with visual guide
        instructions_text = """CÁCH SỬ DỤNG MA TRẬN SO SÁNH:

Bước 1: Nhìn vào ma trận bên dưới. Bạn chỉ cần điền các ô màu trắng (phần trên đường chéo).

Bước 2: Với mỗi ô, tự hỏi: "Tiêu chí ở hàng có quan trọng hơn tiêu chí ở cột không?"

Bước 3: Nhập giá trị theo thang Saaty:
  • Nhập 1  = Hai tiêu chí ngang nhau quan trọng
  • Nhập 3  = Tiêu chí hàng quan trọng hơn một chút
  • Nhập 5  = Tiêu chí hàng quan trọng hơn
  • Nhập 7  = Tiêu chí hàng quan trọng hơn nhiều  
  • Nhập 9  = Tiêu chí hàng cực kỳ quan trọng hơn
  • Nhập 1/3, 1/5, 1/7, 1/9 = Nếu tiêu chí cột quan trọng hơn

VÍ DỤ: Nếu bạn nghĩ "Phong cảnh" quan trọng hơn "Mua sắm" rõ rệt → Nhập 5
        Ô tương ứng (Mua sắm, Phong cảnh) tự động sẽ là 1/5 = 0.2
        """
        
        instructions_label = tk.Text(
            main_frame,
            height=12,
            width=80,
            font=('Arial', 9),
            wrap='word',
            background='#F0F8FF',
            relief='flat',
            padx=10,
            pady=10,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground='#4A90E2'
        )
        instructions_label.insert('1.0', instructions_text)
        instructions_label.config(state='disabled')
        instructions_label.pack(fill='x', pady=10)
        
        # Visual example frame
        example_frame = ttk.LabelFrame(main_frame, text="📌 Ví dụ minh họa", padding=10)
        example_frame.pack(fill='x', pady=5)
        
        example_text = (
            "Giả sử bạn muốn so sánh các tiêu chí:\n\n"
            "• Ô (Phong cảnh, Văn hóa): Bạn nghĩ Phong cảnh quan trọng hơn Văn hóa một chút\n"
            "  → Nhập: 3\n"
            "  → Ô (Văn hóa, Phong cảnh) tự động = 1/3\n\n"
            "• Ô (Thư giãn, Mạo hiểm): Bạn rất thích thư giãn, không thích mạo hiểm\n"
            "  → Nhập: 7 (Thư giãn quan trọng hơn nhiều)\n"
            "  → Ô (Mạo hiểm, Thư giãn) tự động = 1/7\n\n"
            "💡 Lưu ý: Chỉ cần điền phần trên (màu trắng), phần dưới tự động tính!"
        )
        
        example_label = tk.Text(
            example_frame,
            height=10,
            width=80,
            font=('Arial', 9),
            wrap='word',
            background='#FFF9E6',
            relief='flat',
            padx=10,
            pady=10
        )
        example_label.insert('1.0', example_text)
        example_label.config(state='disabled')
        example_label.pack(fill='x')
        
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
                messagebox.showwarning(
                    "Kết quả",
                    f"Ma trận không nhất quán!\nConsistency Ratio = {cr:.4f} >= 0.1\n\n"
                    "Vui lòng xem xét lại các so sánh."
                )
        
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

