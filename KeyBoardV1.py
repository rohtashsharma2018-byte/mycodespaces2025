import pygame
import sys
from pygame.locals import *

class KeyboardTestApp:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1200, 650  # Increased height to accommodate arrow keys
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Keyboard Layout Tester")
        
        # Colors
        self.bg_color = (240, 240, 240)
        self.key_color = (200, 200, 200)
        self.key_pressed_color = (100, 200, 100)
        self.text_color = (50, 50, 50)
        self.border_color = (100, 100, 100)
        
        # Font
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Keyboard layout
        self.load_keyboard_layout()
        
        # Track pressed keys (will remain highlighted)
        self.pressed_keys = set()
        
        # Track toggle keys state
        self.caps_lock_on = False
        
        # Stats
        self.total_presses = 0
        self.last_key = None
        
    def load_keyboard_layout(self):
        # Define a standard QWERTY keyboard layout with arrow keys
        self.keyboard_layout = [
            ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', '', '', ''],
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace', '', '', ''],
            ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\', '', '', ''],
            ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter', '', '', '', ''],
            ['LShift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'RShift', '', '', '↑', '', ''],
            ['LCtrl', 'LWin', 'LAlt', 'Space', 'RAlt', 'RWin', 'RCtrl', '', '', '←', '↓', '→', '', '', '', '']
        ]
        
        # Key sizes
        self.key_sizes = {
            'Backspace': 2, 'Tab': 1.5, '\\': 1.5, 'Caps': 1.75, 
            'Enter': 2.25, 'LShift': 2.25, 'RShift': 2.25, 'Space': 5, 
            'LCtrl': 1.5, 'RCtrl': 1.5, 'LWin': 1.5, 'RWin': 1.5, 
            'LAlt': 1.5, 'RAlt': 1.5, 'Esc': 1,
            'F1': 1, 'F2': 1, 'F3': 1, 'F4': 1, 'F5': 1, 'F6': 1,
            'F7': 1, 'F8': 1, 'F9': 1, 'F10': 1, 'F11': 1, 'F12': 1,
            '↑': 1, '↓': 1, '←': 1, '→': 1, '': 0.5  # Arrow keys and empty keys
        }
        
        # Default key size
        self.default_key_width = 60
        self.key_height = 60
        self.key_gap = 5
        
        # Mapping from pygame key names to our layout names
        self.key_mapping = {
            'escape': 'Esc',
            'backspace': 'Backspace',
            'tab': 'Tab',
            'capslock': 'Caps',
            'return': 'Enter',
            'left shift': 'LShift',
            'right shift': 'RShift',
            'left ctrl': 'LCtrl',
            'right ctrl': 'RCtrl',
            'left alt': 'LAlt',
            'right alt': 'RAlt',
            'space': 'Space',
            'left meta': 'LWin',
            'right meta': 'RWin',
            'f1': 'F1',
            'f2': 'F2',
            'f3': 'F3',
            'f4': 'F4',
            'f5': 'F5',
            'f6': 'F6',
            'f7': 'F7',
            'f8': 'F8',
            'f9': 'F9',
            'f10': 'F10',
            'f11': 'F11',
            'f12': 'F12',
            '`': '`', 
            '1': '1', 
            '2': '2', 
            '3': '3', 
            '4': '4', 
            '5': '5', 
            '6': '6', 
            '7': '7', 
            '8': '8', 
            '9': '9', 
            '0': '0', 
            '-': '-', 
            '=': '=',
            '[': '[', 
            ']': ']', 
            '\\': '\\',
            ';': ';', 
            "'": "'",
            ',': ',', 
            '.': '.', 
            '/': '/',
            'a': 'a', 
            'b': 'b', 
            'c': 'c', 
            'd': 'd', 
            'e': 'e', 
            'f': 'f', 
            'g': 'g', 
            'h': 'h', 
            'i': 'i', 
            'j': 'j', 
            'k': 'k', 
            'l': 'l', 
            'm': 'm', 
            'n': 'n', 
            'o': 'o', 
            'p': 'p', 
            'q': 'q', 
            'r': 'r', 
            's': 's', 
            't': 't', 
            'u': 'u', 
            'v': 'v', 
            'w': 'w', 
            'x': 'x', 
            'y': 'y', 
            'z': 'z',
            'up': '↑',
            'down': '↓',
            'left': '←',
            'right': '→'
        }
        
    def draw_keyboard(self):
        # Draw background
        self.screen.fill(self.bg_color)
        
        # Draw title
        title = self.title_font.render("Keyboard Layout Test", True, self.text_color)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))
        
        # Draw instructions
        instructions = self.font.render("Press any key to test your keyboard. Press ESC to exit.", True, self.text_color)
        self.screen.blit(instructions, (self.width // 2 - instructions.get_width() // 2, 60))
        
        # Draw stats
        stats = self.font.render(f"Total presses: {self.total_presses} | Last key: {self.last_key if self.last_key else 'None'} | Caps Lock: {'ON' if self.caps_lock_on else 'OFF'}", 
                                True, self.text_color)
        self.screen.blit(stats, (self.width // 2 - stats.get_width() // 2, 90))
        
        # Draw keyboard
        start_x = 50
        start_y = 150
        
        for row_idx, row in enumerate(self.keyboard_layout):
            x = start_x
            y = start_y + row_idx * (self.key_height + self.key_gap)
            
            for key in row:
                # Get key width
                width = self.key_sizes.get(key, 1) * self.default_key_width
                
                # Skip drawing empty keys (they're just for spacing)
                if key != '':
                    # Draw key - handle Caps Lock separately as it's a toggle key
                    if key == 'Caps':
                        color = self.key_pressed_color if self.caps_lock_on else self.key_color
                    else:
                        color = self.key_pressed_color if key in self.pressed_keys else self.key_color
                    
                    pygame.draw.rect(self.screen, color, (x, y, width, self.key_height))
                    pygame.draw.rect(self.screen, self.border_color, (x, y, width, self.key_height), 2)
                    
                    # Draw key label (shorten some labels for better display)
                    display_label = key
                    if key == 'LShift': display_label = 'Shift'
                    if key == 'RShift': display_label = 'Shift'
                    if key == 'LCtrl': display_label = 'Ctrl'
                    if key == 'RCtrl': display_label = 'Ctrl'
                    if key == 'LWin': display_label = 'Win'
                    if key == 'RWin': display_label = 'Menu'
                    if key == 'LAlt': display_label = 'Alt'
                    if key == 'RAlt': display_label = 'Alt'
                    
                    key_label = self.font.render(display_label, True, self.text_color)
                    self.screen.blit(key_label, (x + width // 2 - key_label.get_width() // 2, 
                                                y + self.key_height // 2 - key_label.get_height() // 2))
                
                x += width + self.key_gap
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    
                    # Handle Caps Lock key (toggle key)
                    if event.key == K_CAPSLOCK:
                        self.caps_lock_on = not self.caps_lock_on
                        self.last_key = 'Caps'
                        self.total_presses += 1
                    
                    # Add key to pressed keys (will remain highlighted)
                    key_name = pygame.key.name(event.key)
                    mapped_key = self.key_mapping.get(key_name, key_name)
                    
                    if mapped_key not in self.pressed_keys and event.key != K_CAPSLOCK:
                        self.pressed_keys.add(mapped_key)
                        self.last_key = mapped_key
                        self.total_presses += 1
            
            self.draw_keyboard()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = KeyboardTestApp()
    app.run()