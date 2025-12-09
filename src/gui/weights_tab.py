"""Weights tab for TOPSIS criteria weights."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Callable, Dict

logger = logging.getLogger(__name__)


class WeightsTab(ttk.Frame):
    """Tab for TOPSIS criteria weights configuration."""
    
    def __init__(self, parent, on_weights_changed: Callable):
        """Initialize weights tab.
        
        Args:
            parent: Parent widget
            on_weights_changed: Callback when weights change
        """
        super().__init__(parent)
        
        self.on_weights_changed = on_weights_changed
        
        # Weight variables
        self.ahp_weight = tk.DoubleVar(value=0.5)
        self.price_weight = tk.DoubleVar(value=0.3)
        self.duration_weight = tk.DoubleVar(value=0.2)
        
        # Trace weight changes
        self.ahp_weight.trace_add('write', self.on_weight_change)
        self.price_weight.trace_add('write', self.on_weight_change)
        self.duration_weight.trace_add('write', self.on_weight_change)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Trọng số tiêu chí TOPSIS",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=10)
        
        # Instructions
        instructions = """
Điều chỉnh trọng số cho 3 tiêu chí quyết định cuối cùng:
  • Điểm AHP: Điểm chất lượng tour dựa trên sở thích của bạn
  • Giá: Chi phí tour (thấp hơn tốt hơn)
  • Thời gian: Số ngày tour (ngắn hơn tốt hơn)

Tổng trọng số phải bằng 1.0 (100%)
        """
        
        instructions_label = ttk.Label(
            main_frame,
            text=instructions,
            font=('Arial', 9),
            justify='left',
            background='#F0F8FF',
            padding=10
        )
        instructions_label.pack(fill='x', pady=10)
        
        # Sliders frame
        sliders_frame = ttk.LabelFrame(main_frame, text="Điều chỉnh trọng số", padding=20)
        sliders_frame.pack(fill='both', expand=True, pady=10)
        
        # AHP weight slider
        self.create_weight_slider(
            sliders_frame,
            "Điểm AHP (Chất lượng)",
            self.ahp_weight,
            row=0
        )
        
        # Price weight slider
        self.create_weight_slider(
            sliders_frame,
            "Giá (Chi phí)",
            self.price_weight,
            row=1
        )
        
        # Duration weight slider
        self.create_weight_slider(
            sliders_frame,
            "Thời gian (Số ngày)",
            self.duration_weight,
            row=2
        )
        
        # Total weight display
        total_frame = ttk.Frame(sliders_frame)
        total_frame.grid(row=3, column=0, columnspan=3, pady=20, sticky='ew')
        
        ttk.Label(
            total_frame,
            text="Tổng trọng số:",
            font=('Arial', 11, 'bold')
        ).pack(side='left', padx=10)
        
        self.total_label = ttk.Label(
            total_frame,
            text="1.000 (100%)",
            font=('Arial', 11),
            foreground='green'
        )
        self.total_label.pack(side='left')
        
        # Preset buttons frame
        presets_frame = ttk.LabelFrame(main_frame, text="Cài đặt nhanh", padding=10)
        presets_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            presets_frame,
            text="Ưu tiên chất lượng",
            command=self.preset_quality
        ).pack(side='left', padx=5, expand=True, fill='x')
        
        ttk.Button(
            presets_frame,
            text="Ưu tiên giá rẻ",
            command=self.preset_price
        ).pack(side='left', padx=5, expand=True, fill='x')
        
        ttk.Button(
            presets_frame,
            text="Ưu tiên thời gian ngắn",
            command=self.preset_duration
        ).pack(side='left', padx=5, expand=True, fill='x')
        
        ttk.Button(
            presets_frame,
            text="Cân bằng",
            command=self.preset_balanced
        ).pack(side='left', padx=5, expand=True, fill='x')
    
    def create_weight_slider(self, parent, label: str, variable: tk.DoubleVar, row: int):
        """Create a weight slider with label and value display.
        
        Args:
            parent: Parent widget
            label: Slider label
            variable: Variable to bind to
            row: Grid row
        """
        # Label
        ttk.Label(
            parent,
            text=label,
            font=('Arial', 10)
        ).grid(row=row, column=0, sticky='w', padx=10, pady=10)
        
        # Slider
        slider = ttk.Scale(
            parent,
            from_=0.0,
            to=1.0,
            orient='horizontal',
            variable=variable,
            length=300
        )
        slider.grid(row=row, column=1, padx=10, pady=10, sticky='ew')
        
        # Value label
        value_label = ttk.Label(
            parent,
            text=f"{variable.get():.3f}",
            font=('Arial', 10, 'bold'),
            width=8
        )
        value_label.grid(row=row, column=2, padx=10, pady=10)
        
        # Update value label when slider changes
        def update_label(*args):
            value_label.config(text=f"{variable.get():.3f}")
        
        variable.trace_add('write', update_label)
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def on_weight_change(self, *args):
        """Handle weight change event."""
        # Calculate total
        total = self.ahp_weight.get() + self.price_weight.get() + self.duration_weight.get()
        
        # Update total display
        self.total_label.config(text=f"{total:.3f} ({total*100:.1f}%)")
        
        # Change color based on validity
        if abs(total - 1.0) < 0.001:
            self.total_label.config(foreground='green')
        else:
            self.total_label.config(foreground='red')
        
        # Notify parent
        if self.on_weights_changed:
            self.on_weights_changed(self.get_weights())
    
    def preset_quality(self):
        """Preset: prioritize quality (AHP score)."""
        self.ahp_weight.set(0.7)
        self.price_weight.set(0.2)
        self.duration_weight.set(0.1)
    
    def preset_price(self):
        """Preset: prioritize low price."""
        self.ahp_weight.set(0.2)
        self.price_weight.set(0.6)
        self.duration_weight.set(0.2)
    
    def preset_duration(self):
        """Preset: prioritize short duration."""
        self.ahp_weight.set(0.2)
        self.price_weight.set(0.2)
        self.duration_weight.set(0.6)
    
    def preset_balanced(self):
        """Preset: balanced weights."""
        self.ahp_weight.set(0.5)
        self.price_weight.set(0.3)
        self.duration_weight.set(0.2)
    
    def get_weights(self) -> Dict[str, float]:
        """Get current weights.
        
        Returns:
            Dictionary with 'ahp', 'price', 'duration' keys
        """
        return {
            'ahp': self.ahp_weight.get(),
            'price': self.price_weight.get(),
            'duration': self.duration_weight.get()
        }
    
    def set_weights(self, weights: Dict[str, float]):
        """Set weights.
        
        Args:
            weights: Dictionary with 'ahp', 'price', 'duration' keys
        """
        self.ahp_weight.set(weights.get('ahp', 0.5))
        self.price_weight.set(weights.get('price', 0.3))
        self.duration_weight.set(weights.get('duration', 0.2))
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to 1.0.
        
        Returns:
            True if valid
        """
        total = self.ahp_weight.get() + self.price_weight.get() + self.duration_weight.get()
        return abs(total - 1.0) < 0.001

