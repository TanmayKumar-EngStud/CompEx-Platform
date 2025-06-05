import sys
import os
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
import io

class TerminalLogger:
    """
    Captures all terminal output (stdout and stderr) and writes it to a log file
    while still displaying it on the terminal.
    """
    
    def __init__(self, logs_dir="logs"):
        self.logs_dir = logs_dir
        self.ensure_logs_directory()
        self.log_file_path = self.create_log_file()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.log_file = None
        
    def ensure_logs_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
    
    def create_log_file(self):
        """Create timestamped log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"question_generation_{timestamp}.log"
        log_filepath = os.path.join(self.logs_dir, log_filename)
        return log_filepath
    
    def start_logging(self):
        """Start capturing all terminal output to log file"""
        try:
            self.log_file = open(self.log_file_path, 'w', encoding='utf-8')
            sys.stdout = TeeOutput(self.original_stdout, self.log_file)
            sys.stderr = TeeOutput(self.original_stderr, self.log_file)
            print(f"=== Question Generation Session Started ===")
            print(f"Log file: {self.log_file_path}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
        except Exception as e:
            print(f"Failed to start logging: {e}")
            self.stop_logging()
    
    def stop_logging(self):
        """Stop capturing terminal output and restore original streams"""
        try:
            if self.log_file:
                print("=" * 80)
                print(f"=== Question Generation Session Ended ===")
                print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 80)
                
            # Restore original streams
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
            
            # Close log file
            if self.log_file:
                self.log_file.close()
                self.log_file = None
                
            print(f"Log file saved: {self.log_file_path}")
        except Exception as e:
            print(f"Error stopping logger: {e}")

class TeeOutput:
    """
    A class that writes to both terminal and log file simultaneously
    """
    
    def __init__(self, terminal, log_file):
        self.terminal = terminal
        self.log_file = log_file
    
    def write(self, message):
        # Write to terminal
        self.terminal.write(message)
        self.terminal.flush()
        
        # Write to log file
        if self.log_file:
            try:
                self.log_file.write(message)
                self.log_file.flush()
            except Exception:
                pass  # Silently ignore log file write errors
    
    def flush(self):
        self.terminal.flush()
        if self.log_file:
            try:
                self.log_file.flush()
            except Exception:
                pass
    
    def __getattr__(self, name):
        # Delegate any other attributes to the terminal
        return getattr(self.terminal, name)

# Global logger instance
_terminal_logger = None

def start_terminal_logging():
    """Initialize and start terminal logging"""
    global _terminal_logger
    _terminal_logger = TerminalLogger()
    _terminal_logger.start_logging()
    return _terminal_logger

def stop_terminal_logging():
    """Stop terminal logging"""
    global _terminal_logger
    if _terminal_logger:
        _terminal_logger.stop_logging()
        _terminal_logger = None