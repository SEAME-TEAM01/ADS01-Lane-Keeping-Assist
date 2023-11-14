import  os
from    util.colors \
        import  *

TERM_SIZE = os.get_terminal_size().columns

def print_base(option, color, text):
    reset = RESET
    print(f"{BOLD}{color}{option}{reset}  {text}")

def print_info(text, is_first_line=True):
    option = "[INFORMT]"
    color = CYAN
    if is_first_line is False:
        option = "         "
    print_base(
        option,
        color,
        text
    )

def print_warning(text, is_first_line=True):
    option = "[WARNING]"
    color = YELLOW
    if is_first_line is False:
        option = "         "
    print_base(
        option,
        color,
        text
    )

def print_failure(text, is_first_line=True):
    option = "[FAILURE]"
    color = RED
    if is_first_line is False:
        option = "         "
    print_base(
        option,
        color,
        text
    )

def print_success(text, is_first_line=True):
    option = "[SUCCESS]"
    color = GREEN
    if is_first_line is False:
        option = "         "
    print_base(
        option,
        color,
        text
    )

def print_term_size_line():
    print('-' * TERM_SIZE)

def print_end():
    print()