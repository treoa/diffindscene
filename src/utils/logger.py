import os
import sys
import inspect
import datetime
from pathlib import Path
from typing import Literal, Optional, Dict

class CustomLogger:
    _instance: Optional['CustomLogger'] = None
    _initialized: bool = False
    
    # ANSI escape codes for colors
    COLORS = {
        'debug': '\033[93m',  # Yellow
        'error': '\033[91m',  # Red
        'pass': '\033[92m',   # Green
        'info': '\033[0m'     # Default white
    }
    END_COLOR = '\033[0m'
    
    def __new__(cls, log_dir: Optional[str] = None) -> 'CustomLogger':
        """
        Create a singleton instance of the logger.
        
        Args:
            log_dir (str, optional): Directory path where log files will be stored.
                                   If not provided, logs will be stored in './logs'.
        
        Returns:
            CustomLogger: The singleton instance of the logger.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: Optional[str] = None) -> None:
        """
        Initialize the logger (only once) with an optional custom log directory.
        
        Args:
            log_dir (str, optional): Directory path where log files will be stored.
                                   If not provided, logs will be stored in './logs'.
        """
        # Only initialize once
        if not self._initialized:
            # Set up log directory
            self.log_dir = Path(log_dir) if log_dir else Path('./logs')
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create new log file with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file = self.log_dir / f'app_{timestamp}.log'
            
            self._initialized = True
    
    def _get_caller_info(self) -> str:
        """Get information about the file and line number that called the logger."""
        # Get the frame of the caller (2 frames up from current frame)
        frame = inspect.currentframe()
        if frame is not None:
            caller_frame = frame.f_back
            if caller_frame is not None:
                caller_frame = caller_frame.f_back
                if caller_frame is not None:
                    filename = os.path.basename(caller_frame.f_code.co_filename)
                    line_number = caller_frame.f_lineno
                    return f"{filename}:{line_number}"
        return "unknown:0"
    
    def print(self, 
             level: Literal['debug', 'error', 'pass', 'info'],
             message: str) -> None:
        """
        Print a colored message to the terminal and log it to a file.
        
        Args:
            level: The logging level ('debug', 'error', 'pass', or 'info')
            message: The message to be logged
        """
        # Validate level
        if level not in self.COLORS:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(self.COLORS.keys())}")
        
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Get caller information
        caller_info = self._get_caller_info()
        
        # Create the formatted message
        formatted_msg = f"{timestamp} - {caller_info} - {level.upper()} - {message}"
        
        # Print colored message to terminal
        color = self.COLORS[level]
        print(f"{color}{formatted_msg}{self.END_COLOR}")
        
        # Write to log file (without color codes)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(formatted_msg + '\n')

# Example usage in different service classes:
class File1ServiceClass:
    def __init__(self):
        self.logger = CustomLogger()  # Will return the same instance
        
    def do_something(self):
        self.logger.print('info', 'Doing something in File1ServiceClass')

class File2ServiceClass:
    def __init__(self):
        self.logger = CustomLogger()  # Will return the same instance
        
    def do_something_else(self):
        self.logger.print('debug', 'Doing something in File2ServiceClass')