from PySide6.QtWidgets import QApplication, QToolTip
from PySide6.QtGui import QFont

class TooltipManager:
    """Centralized manager for application tooltips"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.setup_tooltip_style()
        
    def setup_tooltip_style(self):
        """Configure global tooltip appearance"""
        QToolTip.setFont(QFont('Roboto', 10))
        
        # Style tooltips with a modern dark theme
        # Get the current application instance
        app = QApplication.instance()
        if app:
            app.setStyleSheet("""
                QToolTip {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 8px;
                    opacity: 230;
                    font-size: 10pt;
                }
            """)
    
    def set_tooltip(self, widget, text, role="default"):
        """Apply tooltip to a widget with optional role-based styling"""
        if not self.enabled:
            return
            
        if role == "password":
            text = "🔒 " + text
        elif role == "security":
            text = "🛡️ " + text
        elif role == "info":
            text = "ℹ️ " + text
        elif role == "warning":
            text = "⚠️ " + text
            
        widget.setToolTip(text)
    
    def enable_tooltips(self):
        """Enable tooltips system-wide"""
        self.enabled = True
        
    def disable_tooltips(self):
        """Disable tooltips system-wide"""
        self.enabled = False
        QToolTip.hideText()  # Hide any visible tooltips
