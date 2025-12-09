"""Loading dialog component."""

import tkinter as tk
from tkinter import ttk
import threading


class LoadingDialog:
    """Loading dialog with progress indicator."""
    
    def __init__(self, parent, title="Đang xử lý...", message="Vui lòng đợi..."):
        """Initialize loading dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Loading message
        """
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("300x100")
        self.center_window()
        
        # Remove window decorations
        self.dialog.resizable(False, False)
        
        # Message label
        self.message_label = ttk.Label(
            self.dialog,
            text=message,
            font=('Arial', 10)
        )
        self.message_label.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.dialog,
            mode='indeterminate',
            length=250
        )
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Cancel button (optional)
        self.cancelled = False
        
    def center_window(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate position
        dialog_width = 300
        dialog_height = 100
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def update_message(self, message: str):
        """Update loading message.
        
        Args:
            message: New message
        """
        self.message_label.config(text=message)
        self.dialog.update()
    
    def close(self):
        """Close the dialog."""
        self.progress.stop()
        self.dialog.grab_release()
        self.dialog.destroy()
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled.
        
        Returns:
            True if cancelled
        """
        return self.cancelled


def run_with_loading(parent, func, args=(), kwargs=None, 
                     title="Đang xử lý...", message="Vui lòng đợi..."):
    """Run a function with loading dialog.
    
    Args:
        parent: Parent window
        func: Function to run
        args: Function arguments
        kwargs: Function keyword arguments
        title: Dialog title
        message: Loading message
        
    Returns:
        Function result
    """
    if kwargs is None:
        kwargs = {}
    
    result = [None]
    exception = [None]
    
    def worker():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    # Create loading dialog
    loading = LoadingDialog(parent, title, message)
    
    # Start worker thread
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    
    # Wait for thread to complete
    while thread.is_alive():
        parent.update()
        loading.dialog.update()
    
    # Close dialog
    loading.close()
    
    # Check for exception
    if exception[0]:
        raise exception[0]
    
    return result[0]

