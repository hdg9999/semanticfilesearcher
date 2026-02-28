import os
from PySide6.QtWidgets import QApplication

class StyleManager:
    """
    Manages loading and applying stylesheets for the application.
    Centralizes logic for reading QSS files from the standard directory structure.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StyleManager, cls).__new__(cls)
            import sys
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                cls._instance.base_path = os.path.join(sys._MEIPASS, "ui")
            else:
                cls._instance.base_path = os.path.dirname(os.path.abspath(__file__))
            cls._instance.styles_path = os.path.join(cls._instance.base_path, "resources", "styles")
            cls._instance.current_theme = "dark"
        return cls._instance

    def load_stylesheet(self, relative_path):
        """
        Loads a QSS file from the styles directory.
        Args:
            relative_path: Path relative to ui/resources/styles/
                           e.g., "themes/default.qss" or "components/tag_input.qss"
        Returns:
            The content of the QSS file, or empty string if not found.
        """
        full_path = os.path.join(self.styles_path, relative_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"Error loading stylesheet {relative_path}: {e}")
                return ""
        else:
            print(f"Stylesheet not found: {full_path}")
            return ""

    def apply_global_style(self, app: QApplication, theme=None):
        """Applies the global theme to the QApplication instance."""
        if theme:
            self.current_theme = theme
        
        # 'default' maps to 'dark' for backward compatibility, or strictly use 'dark'/'light'
        if self.current_theme == "default":
           self.current_theme = "dark"

        qss_content = self.load_stylesheet(f"themes/{self.current_theme}.qss")
        if qss_content:
            app.setStyleSheet(qss_content)

    def get_component_style(self, component_name):
        """
        Retrieves the style for a specific component.
        Args:
            component_name: Name of the component style file (without extension), 
                            e.g. "tag_input"
        """
        return self.load_stylesheet(f"components/{component_name}.qss")

    def get_current_theme(self):
        return self.current_theme

    def get_resource_path(self, relative_path):
        """
        Returns the absolute path to a resource relative to the ui directory.
        e.g relative_path = "resources/icons/queue.svg"
        """
        return os.path.join(self.base_path, relative_path)

    def get_icon_suffix(self):
        """
        Returns the suffix for icons based on the current theme.
        Dark theme uses white icons (_white.svg).
        Light theme uses dark icons (.svg).
        """
        return "_white" if self.current_theme == "dark" else ""
