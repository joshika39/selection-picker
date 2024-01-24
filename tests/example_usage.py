from pathlib import Path
import sys
import os

path_root = Path(__file__).parents[1]
sys.path.append(os.path.join(path_root, 'src'))

from selection_picker_joshika39 import *


items = ["item1", "item2", "item3", "item4", "item5"]
menu = SingleMenu("Good title", items)

# Get the user's choice
choice = menu.show()

# Print the choice
print(f'Single choice: {choice}')

mulit_menu = MultiMenu("Good title", items)

# Get the user's choice
choice = mulit_menu.show()

# Print the choice
print(f'Multi choice: {choice}')
