"""
logger.py
Utility untuk logging di seluruh aplikasi dengan format yang informatif dan berwarna
"""

import logging
import sys
import os
from pathlib import Path


# ============================================================================
# ANSI COLOR CODES
# ============================================================================

class ColorCodes:
    """ANSI color codes untuk terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


# ============================================================================
# CUSTOM FORMATTER WITH COLORS
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """Custom formatter dengan warna untuk console output"""
    
    # Mapping level ke warna
    LEVEL_COLORS = {
        'DEBUG': ColorCodes.CYAN,
        'INFO': ColorCodes.GREEN,
        'WARNING': ColorCodes.BRIGHT_YELLOW,
        'ERROR': ColorCodes.BRIGHT_RED,
        'CRITICAL': ColorCodes.RED + ColorCodes.BOLD,
    }
    
    def format(self, record):
        """Format log record dengan warna"""
        
        # Dapatkan warna berdasarkan level
        level_color = self.LEVEL_COLORS.get(record.levelname, ColorCodes.WHITE)
        
        # Format timestamp
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        
        # Format module name (singkat)
        module_name = record.name.split('.')[-1]
        
        # Buat format string dengan warna
        if record.levelname == 'INFO':
            # INFO: lebih sederhana dan rapi
            formatted = (
                f"{ColorCodes.BRIGHT_CYAN}[{timestamp}]{ColorCodes.RESET} "
                f"{level_color}●{ColorCodes.RESET} "
                f"{ColorCodes.BRIGHT_WHITE}{record.getMessage()}{ColorCodes.RESET}"
            )
        elif record.levelname == 'DEBUG':
            # DEBUG: dengan module name
            formatted = (
                f"{ColorCodes.CYAN}[{timestamp}]{ColorCodes.RESET} "
                f"{level_color}◆{ColorCodes.RESET} "
                f"{ColorCodes.CYAN}{module_name}{ColorCodes.RESET} "
                f"{record.getMessage()}"
            )
        elif record.levelname in ('WARNING', 'ERROR', 'CRITICAL'):
            # WARNING/ERROR/CRITICAL: lebih menonjol
            formatted = (
                f"{ColorCodes.BRIGHT_YELLOW}[{timestamp}]{ColorCodes.RESET} "
                f"{level_color}⚠ {record.levelname}{ColorCodes.RESET} "
                f"{ColorCodes.BRIGHT_WHITE}{module_name}{ColorCodes.RESET} "
                f"{record.getMessage()}"
            )
        else:
            # Default format
            formatted = (
                f"[{timestamp}] {level_color}{record.levelname}{ColorCodes.RESET} "
                f"{module_name} {record.getMessage()}"
            )
        
        return formatted


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Path untuk log file
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"


def get_logger(name):
    """
    Mendapatkan logger instance dengan konfigurasi standar dan format yang informatif.
    
    Parameter:
    - name: Nama logger (biasanya __name__)
    
    Return:
    - logging.Logger: Logger instance
    
    Notes:
    - Dalam Flask debug mode dengan reloader, fungsi ini bisa dipanggil berkali-kali
    - Pengecekan WERKZEUG_RUN_MAIN memastikan logger hanya disetup sekali pada main process
    - Pengecekan logger.handlers mencegah duplikasi handler
    """
    
    logger = logging.getLogger(name)
    
    # ========================================================================
    # CHECK IF LOGGER ALREADY CONFIGURED
    # ========================================================================
    # Jika logger sudah memiliki handler dan bukan reloader parent process, return saja
    if logger.handlers:
        return logger
    
    # ========================================================================
    # SKIP LOGGER SETUP JIKA RELOADER PARENT PROCESS
    # ========================================================================
    # WERKZEUG_RUN_MAIN akan ada dan bernilai 'true' hanya pada main server process
    # Jika tidak ada, berarti ini adalah reloader parent process - skip setup
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        # Ini adalah reloader parent process, return logger tanpa handler
        # Handler akan disetup pada actual server process
        return logger
    
    # Set level
    logger.setLevel(logging.DEBUG)
    
    # ========================================================================
    # Console Handler (stdout) - dengan warna
    # ========================================================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # ========================================================================
    # File Handler (file logging) - tanpa warna
    # ========================================================================
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    except Exception as e:
        if logger.handlers:  # Only log if console handler exists
            logger.warning(f"Could not create file handler: {e}")
    
    return logger


# ============================================================================
# HELPER FUNCTIONS FOR STRUCTURED LOGGING
# ============================================================================

def log_section(logger, title, char='=', width=70):
    """
    Log section header untuk memisahkan bagian-bagian penting.
    
    Parameter:
    - logger: Logger instance
    - title: Judul section
    - char: Karakter untuk border (default: '=')
    - width: Lebar total (default: 70)
    """
    border = char * width
    logger.info(f"\n{border}")
    logger.info(f"{title.center(width)}")
    logger.info(f"{border}\n")


def log_success(logger, message):
    """Log pesan sukses dengan simbol checkmark"""
    logger.info(f"✓ {message}")


def log_error(logger, message):
    """Log pesan error dengan simbol X"""
    logger.error(f"✗ {message}")


def log_warning(logger, message):
    """Log pesan warning dengan simbol warning"""
    logger.warning(f"⚠ {message}")


def log_info(logger, message):
    """Log pesan info dengan simbol bullet"""
    logger.info(f"• {message}")


def log_metric(logger, name, value, unit=""):
    """
    Log metrik dengan format yang rapi.
    
    Parameter:
    - logger: Logger instance
    - name: Nama metrik
    - value: Nilai metrik
    - unit: Unit (opsional)
    """
    if unit:
        logger.info(f"  {name}: {value} {unit}")
    else:
        logger.info(f"  {name}: {value}")
