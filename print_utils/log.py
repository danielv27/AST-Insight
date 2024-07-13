from colorama import init, Fore, Style
import re


# Initialize colorama
init(autoreset=True)

def log(node, message, level="error"):
    if level == "error":
        level_str = f"{Fore.RED}{Style.BRIGHT}Error:{Style.RESET_ALL}"
    elif level == "warning":
        level_str = f"{Fore.YELLOW}{Style.BRIGHT}Warning:{Style.RESET_ALL}"
    elif level == "info":
        level_str = f"{Fore.BLUE}{Style.BRIGHT}Info:{Style.RESET_ALL}"
    elif level == "fixed":
        level_str = f"{Fore.GREEN}{Style.BRIGHT}Fixed:{Style.RESET_ALL}"
    else:
        level_str = "Message"

    
    coord_str = f"{Fore.CYAN}{node.coord}{Style.RESET_ALL}" if node.coord else ""
    
    message = f"{level_str} {coord_str}: {message}"
    print(message)
    
