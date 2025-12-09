"""Main application window."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import json
from pathlib import Path
from typing import List

from ..config.settings import Settings
from ..config.database import DatabaseConnection
from ..models.tour import Tour
from ..models.preference import UserPreference
from ..services.tour_service import TourService
from ..services.recommendation_service import RecommendationService
from .comparison_tab import ComparisonTab
from .weights_tab import WeightsTab
from .results_tab import ResultsTab
from .components.loading_dialog import run_with_loading

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        self.root = tk.Tk()
        self.root.title(Settings.APP_NAME)
        self.root.geometry(f"{Settings.WINDOW_WIDTH}x{Settings.WINDOW_HEIGHT}")
        
        # Services
        self.tour_service = TourService()
        self.recommendation_service = RecommendationService()
        
        # Data
        self.criteria = []
        self.criteria_names = []
        self.tours = []
        self.current_preference = UserPreference()
        
        # Initialize
        self.setup_styles()
        self.create_menu()
        self.create_widgets()
        self.load_data()
    
    def setup_styles(self):
        """Setup ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TLabel', background='white')
        style.configure('TFrame', background='white')
        style.configure('TLabelframe', background='white')
        style.configure('TLabelframe.Label', background='white', font=('Arial', 10, 'bold'))
    
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Lưu preferences", command=self.save_preferences)
        file_menu.add_command(label="Tải preferences", command=self.load_preferences)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.quit_app)
        
        # Calculate menu
        calc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tính toán", menu=calc_menu)
        calc_menu.add_command(label="Tính gợi ý", command=self.calculate_recommendations)
        calc_menu.add_command(label="Làm mới dữ liệu", command=self.load_data)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Hướng dẫn", command=self.show_help)
        help_menu.add_command(label="Về chúng tôi", command=self.show_about)
    
    def create_widgets(self):
        """Create main widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Comparison
        self.comparison_tab = ComparisonTab(
            self.notebook,
            self.criteria_names,
            self.on_criteria_weights_calculated
        )
        self.notebook.add(self.comparison_tab, text="1. So sánh tiêu chí")
        
        # Tab 2: TOPSIS weights
        self.weights_tab = WeightsTab(
            self.notebook,
            self.on_topsis_weights_changed
        )
        self.notebook.add(self.weights_tab, text="2. Trọng số TOPSIS")
        
        # Tab 3: Results
        self.results_tab = ResultsTab(
            self.notebook,
            self.criteria_names
        )
        self.notebook.add(self.results_tab, text="3. Kết quả")
        
        # Bottom frame with calculate button
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            bottom_frame,
            text="Tính toán gợi ý Tour",
            command=self.calculate_recommendations,
            style='Accent.TButton'
        ).pack(side='right', padx=5)
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Sẵn sàng",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_data(self):
        """Load data from database."""
        try:
            # Test database connection
            if not DatabaseConnection.test_connection():
                messagebox.showerror(
                    "Lỗi kết nối",
                    "Không thể kết nối database!\n\n"
                    "Vui lòng kiểm tra:\n"
                    "1. Docker container đang chạy\n"
                    "2. Cấu hình trong file .env\n"
                    "3. MySQL service đã khởi động"
                )
                return
            
            # Load criteria
            self.criteria = self.tour_service.get_all_criteria()
            self.criteria_names = [c.name for c in self.criteria]
            
            # Load tours
            self.tours = self.tour_service.get_all_tours()
            
            # Update status
            self.status_bar.config(
                text=f"Đã tải {len(self.criteria)} tiêu chí và {len(self.tours)} tours"
            )
            
            logger.info(f"Loaded {len(self.criteria)} criteria and {len(self.tours)} tours")
            
            # Recreate tabs with new criteria
            if self.criteria_names:
                self.recreate_tabs()
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {e}")
    
    def recreate_tabs(self):
        """Recreate tabs with updated criteria."""
        # Remove old tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Create new tabs
        self.comparison_tab = ComparisonTab(
            self.notebook,
            self.criteria_names,
            self.on_criteria_weights_calculated
        )
        self.notebook.add(self.comparison_tab, text="1. So sánh tiêu chí")
        
        self.weights_tab = WeightsTab(
            self.notebook,
            self.on_topsis_weights_changed
        )
        self.notebook.add(self.weights_tab, text="2. Trọng số TOPSIS")
        
        self.results_tab = ResultsTab(
            self.notebook,
            self.criteria_names
        )
        self.notebook.add(self.results_tab, text="3. Kết quả")
    
    def on_criteria_weights_calculated(self, weights, consistency_ratio):
        """Handle criteria weights calculation.
        
        Args:
            weights: Calculated weights
            consistency_ratio: CR value
        """
        self.current_preference.criteria_weights = weights
        self.current_preference.consistency_ratio = consistency_ratio
        logger.info(f"Criteria weights updated: {weights}, CR={consistency_ratio}")
    
    def on_topsis_weights_changed(self, weights):
        """Handle TOPSIS weights change.
        
        Args:
            weights: TOPSIS weights dictionary
        """
        self.current_preference.topsis_weights = weights
        logger.info(f"TOPSIS weights updated: {weights}")
    
    def calculate_recommendations(self):
        """Calculate tour recommendations."""
        try:
            # Validate criteria weights
            if self.current_preference.criteria_weights is None:
                messagebox.showwarning(
                    "Cảnh báo",
                    "Vui lòng tính toán trọng số tiêu chí trước!\n\n"
                    "Đi đến Tab 1 và nhấn 'Tính trọng số'"
                )
                self.notebook.select(0)
                return
            
            # Validate consistency
            if self.current_preference.consistency_ratio >= 0.1:
                if not messagebox.askyesno(
                    "Cảnh báo",
                    f"Ma trận so sánh không nhất quán (CR = {self.current_preference.consistency_ratio:.4f}).\n\n"
                    "Bạn có muốn tiếp tục?"
                ):
                    return
            
            # Validate TOPSIS weights
            if not self.weights_tab.validate_weights():
                messagebox.showwarning(
                    "Cảnh báo",
                    "Tổng trọng số TOPSIS phải bằng 1.0!\n\n"
                    "Vui lòng điều chỉnh trong Tab 2"
                )
                self.notebook.select(1)
                return
            
            # Check if tours loaded
            if not self.tours:
                messagebox.showwarning("Cảnh báo", "Không có tour nào trong database!")
                return
            
            # Calculate recommendations with loading dialog
            def calculate():
                recommended_tours = self.recommendation_service.recommend_tours(
                    self.tours,
                    self.current_preference,
                    self.criteria_names
                )
                return recommended_tours
            
            recommended_tours = run_with_loading(
                self.root,
                calculate,
                title="Đang tính toán...",
                message="Đang tính toán gợi ý tour..."
            )
            
            # Display results
            self.results_tab.display_results(recommended_tours)
            
            # Switch to results tab
            self.notebook.select(2)
            
            # Update status
            self.status_bar.config(text=f"Đã tính toán {len(recommended_tours)} tours")
            
            messagebox.showinfo(
                "Thành công",
                f"Đã tính toán gợi ý cho {len(recommended_tours)} tours!\n\n"
                f"Top 3:\n"
                f"1. {recommended_tours[0].name} (TOPSIS: {recommended_tours[0].topsis_score:.4f})\n"
                f"2. {recommended_tours[1].name} (TOPSIS: {recommended_tours[1].topsis_score:.4f})\n"
                f"3. {recommended_tours[2].name} (TOPSIS: {recommended_tours[2].topsis_score:.4f})"
            )
        
        except Exception as e:
            logger.error(f"Error calculating recommendations: {e}")
            messagebox.showerror("Lỗi", f"Không thể tính toán gợi ý: {e}")
    
    def save_preferences(self):
        """Save user preferences."""
        try:
            # Check if preferences exist
            if self.current_preference.criteria_weights is None:
                messagebox.showwarning("Cảnh báo", "Chưa có preferences để lưu!")
                return
            
            # Ask for user name
            user_name = tk.simpledialog.askstring(
                "Lưu preferences",
                "Nhập tên để lưu preferences:",
                parent=self.root
            )
            
            if not user_name:
                return
            
            # Get comparison matrix
            self.current_preference.comparison_matrix = self.comparison_tab.matrix_input.get_matrix()
            
            # Save to database
            preference_json = self.current_preference.to_json()
            preference_id = self.tour_service.save_user_preference(user_name, preference_json)
            
            # Also save to file
            Settings.ensure_directories()
            file_path = Settings.SAVED_PREFERENCES_DIR / f"{user_name}_{preference_id}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_preference.to_dict(), f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Thành công", f"Đã lưu preferences với ID: {preference_id}")
            logger.info(f"Saved preferences for user '{user_name}' with ID {preference_id}")
        
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
            messagebox.showerror("Lỗi", f"Không thể lưu preferences: {e}")
    
    def load_preferences(self):
        """Load user preferences."""
        try:
            # Ask for file
            file_path = filedialog.askopenfilename(
                title="Chọn file preferences",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=Settings.SAVED_PREFERENCES_DIR
            )
            
            if not file_path:
                return
            
            # Load from file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create preference object
            preference = UserPreference(
                comparison_matrix=data.get('comparison_matrix'),
                criteria_weights=data.get('criteria_weights'),
                consistency_ratio=data.get('consistency_ratio'),
                topsis_weights=data.get('topsis_weights', {})
            )
            
            # Update current preference
            self.current_preference = preference
            
            # Update UI
            if preference.comparison_matrix is not None:
                import numpy as np
                self.comparison_tab.set_matrix(np.array(preference.comparison_matrix))
            
            if preference.topsis_weights:
                self.weights_tab.set_weights(preference.topsis_weights)
            
            messagebox.showinfo("Thành công", "Đã tải preferences!")
            logger.info(f"Loaded preferences from {file_path}")
        
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải preferences: {e}")
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
HƯỚNG DẪN SỬ DỤNG

1. So sánh tiêu chí (Tab 1):
   - So sánh từng cặp tiêu chí theo thang Saaty (1-9)
   - Nhấn "Tính trọng số" để tính toán
   - Kiểm tra CR < 0.1 (nhất quán)

2. Trọng số TOPSIS (Tab 2):
   - Điều chỉnh trọng số cho 3 tiêu chí
   - Tổng phải bằng 1.0
   - Sử dụng preset nếu cần

3. Kết quả (Tab 3):
   - Xem danh sách tour được đề xuất
   - Double-click để xem chi tiết
   - Xuất CSV hoặc PDF

4. Tính toán:
   - Nhấn nút "Tính toán gợi ý Tour"
   - Xem kết quả trong Tab 3
        """
        
        messagebox.showinfo("Hướng dẫn", help_text)
    
    def show_about(self):
        """Show about dialog."""
        about_text = f"""
{Settings.APP_NAME}
Version 1.0.0

Hệ thống gợi ý tour du lịch sử dụng:
- AHP (Analytic Hierarchy Process)
- TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)

Phát triển bởi: Tour Recommendation Team
        """
        
        messagebox.showinfo("Về chúng tôi", about_text)
    
    def quit_app(self):
        """Quit application."""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát?"):
            DatabaseConnection.close_pool()
            self.root.quit()
    
    def run(self):
        """Run the application."""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

