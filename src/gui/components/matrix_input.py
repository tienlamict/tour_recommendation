"""Matrix input widget for AHP comparisons."""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from typing import List, Callable, Optional

from ...utils.helpers import parse_fraction, validate_saaty_value


class MatrixInputWidget(ttk.Frame):
    """Widget for inputting pairwise comparison matrix."""
    
    def __init__(
        self,
        parent,
        size: int,
        labels: List[str],
        on_change: Optional[Callable] = None
    ):
        """Initialize matrix input widget.
        
        Args:
            parent: Parent widget
            size: Size of matrix (n x n)
            labels: Labels for rows/columns
            on_change: Callback when matrix changes
        """
        super().__init__(parent)
        
        self.size = size
        self.labels = labels
        self.on_change = on_change
        
        # Entry widgets
        self.entries = {}
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create matrix input widgets."""
        # Create canvas with scrollbar
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        
        # Frame inside canvas
        self.matrix_frame = ttk.Frame(canvas)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Pack scrollbars and canvas
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=self.matrix_frame, anchor="nw")
        
        # Update scroll region when frame size changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.matrix_frame.bind("<Configure>", on_frame_configure)
        
        # Create matrix grid
        self.create_matrix_grid()
    
    def create_matrix_grid(self):
        """Create the matrix grid with labels and entries."""
        # Top-left corner (empty)
        ttk.Label(self.matrix_frame, text="", width=15).grid(row=0, column=0, padx=5, pady=5)
        
        # Column headers
        for j, label in enumerate(self.labels, 1):
            header = ttk.Label(
                self.matrix_frame,
                text=label,
                font=('Arial', 9, 'bold'),
                width=12
            )
            header.grid(row=0, column=j, padx=5, pady=5)
        
        # Rows
        for i in range(self.size):
            # Row header
            header = ttk.Label(
                self.matrix_frame,
                text=self.labels[i],
                font=('Arial', 9, 'bold'),
                width=15,
                anchor='w'
            )
            header.grid(row=i+1, column=0, padx=5, pady=5, sticky='w')
            
            # Entries
            for j in range(self.size):
                if i == j:
                    # Diagonal: always 1
                    label = ttk.Label(
                        self.matrix_frame,
                        text="1",
                        font=('Arial', 9),
                        width=10,
                        anchor='center',
                        background='#E8E8E8'
                    )
                    label.grid(row=i+1, column=j+1, padx=2, pady=2)
                elif i < j:
                    # Upper triangle: editable
                    entry = ttk.Entry(
                        self.matrix_frame,
                        width=10,
                        font=('Arial', 9),
                        justify='center'
                    )
                    entry.grid(row=i+1, column=j+1, padx=2, pady=2)
                    entry.insert(0, "1")
                    
                    # Bind change event
                    entry.bind('<FocusOut>', lambda e, r=i, c=j: self.on_entry_change(r, c))
                    entry.bind('<Return>', lambda e, r=i, c=j: self.on_entry_change(r, c))
                    
                    # Store entry
                    self.entries[(i, j)] = entry
                    
                    # Tooltip with detailed explanation
                    tooltip_text = (
                        f"Ô này: So sánh '{self.labels[i]}' với '{self.labels[j]}'\n\n"
                        f"Nếu '{self.labels[i]}' quan trọng hơn '{self.labels[j]}':\n"
                        f"  • Nhập 1 = Ngang nhau\n"
                        f"  • Nhập 3 = {self.labels[i]} hơn một chút\n"
                        f"  • Nhập 5 = {self.labels[i]} hơn rõ rệt\n"
                        f"  • Nhập 7 = {self.labels[i]} hơn nhiều\n"
                        f"  • Nhập 9 = {self.labels[i]} cực kỳ quan trọng\n\n"
                        f"Nếu '{self.labels[j]}' quan trọng hơn: Nhập phân số (1/3, 1/5, 1/7, 1/9)"
                    )
                    self.create_tooltip(entry, tooltip_text)
                else:
                    # Lower triangle: auto-calculated (reciprocal)
                    label = ttk.Label(
                        self.matrix_frame,
                        text="1",
                        font=('Arial', 9),
                        width=10,
                        anchor='center',
                        background='#F0F0F0'
                    )
                    label.grid(row=i+1, column=j+1, padx=2, pady=2)
                    
                    # Store label for updates
                    self.entries[(i, j)] = label
    
    def create_tooltip(self, widget, text):
        """Create tooltip for widget.
        
        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
        """
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            
            # Calculate position (avoid going off screen)
            x = event.x_root + 15
            y = event.y_root + 15
            screen_width = tooltip.winfo_screenwidth()
            screen_height = tooltip.winfo_screenheight()
            
            # Adjust if too far right
            if x > screen_width - 300:
                x = event.x_root - 320
            
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(
                tooltip,
                text=text,
                background="#FFFFCC",
                relief='solid',
                borderwidth=2,
                padx=10,
                pady=8,
                font=('Arial', 9),
                justify='left',
                wraplength=280
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def on_entry_change(self, row: int, col: int):
        """Handle entry change event.
        
        Args:
            row: Row index
            col: Column index
        """
        entry = self.entries[(row, col)]
        value_str = entry.get().strip()
        
        try:
            # Parse value (supports fractions like "1/3")
            value = parse_fraction(value_str)
            
            # Validate Saaty scale
            if not validate_saaty_value(value):
                raise ValueError(f"Giá trị phải trong khoảng 1/9 đến 9")
            
            # Update reciprocal value in lower triangle
            reciprocal = 1.0 / value
            reciprocal_label = self.entries[(col, row)]
            
            if reciprocal < 1:
                reciprocal_label.config(text=f"1/{1/reciprocal:.1f}")
            else:
                reciprocal_label.config(text=f"{reciprocal:.3f}")
            
            # Call change callback
            if self.on_change:
                self.on_change()
        
        except ValueError as e:
            messagebox.showerror("Lỗi nhập liệu", str(e))
            entry.delete(0, tk.END)
            entry.insert(0, "1")
    
    def get_matrix(self) -> np.ndarray:
        """Get the comparison matrix.
        
        Returns:
            Numpy array of comparison matrix
        """
        matrix = np.ones((self.size, self.size))
        
        for i in range(self.size):
            for j in range(self.size):
                if i < j:
                    # Upper triangle: get from entry
                    entry = self.entries[(i, j)]
                    value_str = entry.get().strip()
                    try:
                        value = parse_fraction(value_str)
                        matrix[i][j] = value
                        matrix[j][i] = 1.0 / value
                    except ValueError:
                        matrix[i][j] = 1.0
                        matrix[j][i] = 1.0
        
        return matrix
    
    def set_matrix(self, matrix: np.ndarray):
        """Set the comparison matrix.
        
        Args:
            matrix: Numpy array of comparison matrix
        """
        if matrix.shape != (self.size, self.size):
            raise ValueError(f"Matrix size mismatch: expected {self.size}x{self.size}")
        
        for i in range(self.size):
            for j in range(i + 1, self.size):
                entry = self.entries[(i, j)]
                value = matrix[i][j]
                
                entry.delete(0, tk.END)
                
                # Format value
                if value < 1:
                    entry.insert(0, f"1/{1/value:.1f}")
                else:
                    entry.insert(0, f"{value:.3f}")
                
                # Update reciprocal
                self.on_entry_change(i, j)
    
    def clear(self):
        """Clear all entries to default value (1)."""
        for i in range(self.size):
            for j in range(i + 1, self.size):
                entry = self.entries[(i, j)]
                entry.delete(0, tk.END)
                entry.insert(0, "1")
                self.on_entry_change(i, j)
    
    def validate(self) -> bool:
        """Validate all entries.
        
        Returns:
            True if all entries are valid
        """
        for i in range(self.size):
            for j in range(i + 1, self.size):
                entry = self.entries[(i, j)]
                value_str = entry.get().strip()
                
                try:
                    value = parse_fraction(value_str)
                    if not validate_saaty_value(value):
                        return False
                except ValueError:
                    return False
        
        return True

