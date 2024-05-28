import pygame
import random
import csv
import time
import re
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
## --- Screen ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BACKGROUND_COLOR = (169, 169, 169)

##  --- Colors ---
TEXT_COLOR = (0, 0, 0)
GAIN_COLOR = (0, 255, 0)
LOSS_COLOR = (255, 0, 0)

## --- Images ---
CARD_SIZE_MULTIPLIER = 2.5
CARD_WIDTH = 100 * CARD_SIZE_MULTIPLIER
CARD_HEIGHT = 150 * CARD_SIZE_MULTIPLIER
CARD_SELECTION = 22 * CARD_SIZE_MULTIPLIER
POS_COL_L = 300
POS_COL_R = 1325
POS_ROW_TOP = 150
POS_ROW_BOTTOM = 650
DECK_POSITIONS = {
    'A': (POS_COL_L, POS_ROW_TOP),
    'B': (POS_COL_R, POS_ROW_TOP),
    'C': (POS_COL_L, POS_ROW_BOTTOM),
    'D': (POS_COL_R, POS_ROW_BOTTOM)
}

## --- Text ---
FEEDBACK_FONT_SIZE = 48
SCORE_FONT_SIZE = 56
MISC_FONT_SIZE = 36
LABEL_FONT_SIZE = 72
LINE_HEIGHT = FEEDBACK_FONT_SIZE + 5  # Space between lines

## --- Task ---
INITIAL_BALANCE = 2000
TRIAL_WAIT_TIME = 2

# Load unselected card images
card_images = {
    'A': pygame.image.load('assets/card_blue_unselected.png'),
    'B': pygame.image.load('assets/card_red_unselected.png'),
    'C': pygame.image.load('assets/card_green_unselected.png'),
    'D': pygame.image.load('assets/card_yellow_unselected.png')
}

# Load selected card images
selected_card_images = {
    'A': pygame.image.load('assets/card_blue_selected.png'),
    'B': pygame.image.load('assets/card_red_selected.png'),
    'C': pygame.image.load('assets/card_green_selected.png'),
    'D': pygame.image.load('assets/card_yellow_selected.png')
}

# Resize card images
for key in card_images:
    card_images[key] = pygame.transform.scale(card_images[key], (CARD_WIDTH, CARD_HEIGHT))
    selected_card_images[key] = pygame.transform.scale(selected_card_images[key], (CARD_WIDTH + CARD_SELECTION, CARD_HEIGHT + CARD_SELECTION))

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Iowa Gambling Task")

# Font setup
feedback_font = pygame.font.Font(None, FEEDBACK_FONT_SIZE)
score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
misc_font = pygame.font.Font(None, MISC_FONT_SIZE)
label_font = pygame.font.Font(None, LABEL_FONT_SIZE)

# Defining deck class
class Deck:
    def __init__(self, rewards, penalties):
        self.rewards = rewards
        self.penalties = penalties
        self.selected_count = 0

    def draw_card(self):
        reward = random.choice(self.rewards)
        penalty = random.choice(self.penalties)
        return reward, penalty

# Defining task class
class IowaGamblingTask:
    def __init__(self, pid):
        self.decks = {
            'A': Deck(rewards=[100] * 50 + [50] * 50, penalties=[0] * 90 + [-250] * 10),
            'B': Deck(rewards=[100] * 50 + [50] * 50, penalties=[0] * 90 + [-1250] * 10),
            'C': Deck(rewards=[50] * 70 + [50] * 30, penalties=[0] * 90 + [-50] * 10),
            'D': Deck(rewards=[50] * 70 + [50] * 30, penalties=[0] * 90 + [-250] * 10)
        }
        self.total_score = INITIAL_BALANCE
        self.choices = []
        self.trial_data = []
        self.pid = pid

    def draw_card_from_deck(self, choice):
        if choice in self.decks and self.decks[choice].selected_count < 40:
            reward, penalty = self.decks[choice].draw_card()
            net_reward = reward + penalty
            self.total_score += net_reward
            self.choices.append(choice)
            self.trial_data.append((len(self.choices), choice, reward, penalty, net_reward, self.total_score))
            self.decks[choice].selected_count += 1
            return reward, penalty, net_reward
        return None, None, None

    def summarize_results(self):
        print("\nTask Completed")
        print(f"Total Score: {self.total_score}")
        print(f"Choices: {self.choices}")

    def save_data(self):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f'data/IGT_{self.pid}_{date_str}.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Trial', 'Deck Choice', 'Reward', 'Penalty', 'Net Reward', 'Total Score'])
            writer.writerows(self.trial_data)

# PID validation function
def is_valid_pid(pid):
    return bool(re.match(r'^[A-Z]{2}-\d{4}$', pid))

# PID Input Screen
def get_pid():
    input_active = False
    pid = 'DD-'
    error_message = ''
    while True:
        screen.fill(BACKGROUND_COLOR)
        pid_text = misc_font.render("Enter Participant ID (format: DD-####):", True, TEXT_COLOR)
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        txt_surface = misc_font.render(pid, True, TEXT_COLOR)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(pid_text, (SCREEN_WIDTH // 2 - pid_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

        # Center the text in the input box
        screen.blit(txt_surface, (input_box.x + (input_box.width - txt_surface.get_width()) // 2, input_box.y + (input_box.height - txt_surface.get_height()) // 2))
        pygame.draw.rect(screen, TEXT_COLOR, input_box, 2)

        if error_message:
            error_surface = misc_font.render(error_message, True, LOSS_COLOR)
            screen.blit(error_surface, (SCREEN_WIDTH // 2 - error_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if is_valid_pid(pid):
                        return pid
                    else:
                        error_message = "Invalid format. Please enter as DD-####."
                elif event.key == pygame.K_BACKSPACE:
                    pid = pid[:-1]
                else:
                    pid += event.unicode

        pygame.display.flip()

# Function to render and display multi-line text with different colors
def render_multiline_text(lines, colors, feedback_font, surface, x, y):
    for i, (line, color) in enumerate(zip(lines, colors)):
        line_surface = feedback_font.render(line, True, color)
        surface.blit(line_surface, (x, y + i * LINE_HEIGHT))

# Instruction screen
def show_instructions():
    screen.fill(BACKGROUND_COLOR)
    instructions = [
        "Welcome to the Iowa Gambling Task.",
        "You will be selecting cards from four decks labeled A, B, C, and D.",
        "Each selection will result in a reward and/or a penalty.",
        "Your goal is to maximize your total score.",
        "You have 100 trials to complete the task.",
        "Press SPACE to begin."
    ]
    for i, line in enumerate(instructions):
        text = misc_font.render(line, True, TEXT_COLOR)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 100 + i * LINE_HEIGHT))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    return True

# Start screen
def show_start_screen():
    screen.fill(BACKGROUND_COLOR)
    start_text = misc_font.render("Press SPACE to begin", True, TEXT_COLOR)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    return True

# Main loop
def main():
    pid = get_pid()
    if not pid:
        return

    show_instructions()
    
    # if not show_start_screen():
    #     return
    
    task = IowaGamblingTask(pid)
    running = True
    trial = 0

    try:
        while running and trial < 100:
            start_time = time.time()
            screen.fill(BACKGROUND_COLOR)

            # Draw card images and labels
            for key, position in DECK_POSITIONS.items():
                screen.blit(card_images[key], position)
                label = label_font.render(key, True, TEXT_COLOR)
                label_rect = label.get_rect(center=(position[0] + CARD_WIDTH // 2, position[1] - 40))
                screen.blit(label, label_rect)

            # Display current total score
            score_text = score_font.render(f"Total Score: ${task.total_score}", True, TEXT_COLOR)
            screen.blit(score_text, (10, 10))

            # Event handling
            choice = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_a:
                        choice = 'A'
                    elif event.key == pygame.K_b:
                        choice = 'B'
                    elif event.key == pygame.K_c:
                        choice = 'C'
                    elif event.key == pygame.K_d:
                        choice = 'D'

            if choice:
                reward, penalty, net_reward = task.draw_card_from_deck(choice)
                if reward is not None:
                    trial += 1
                    trial_time = time.time() - start_time
                    task.trial_data[-1] = task.trial_data[-1] + (trial_time,)  # Add trial time to the last entry
                    print(f"Trial {trial}: Deck {choice}, Reward: {reward}, Penalty: {penalty}, Net reward: {net_reward}")
                    print(f"Total score: {task.total_score}")

                    # Display feedback and selected card
                    feedback_lines = [
                        f"WIN: ${reward}",
                        f"LOSE: ${penalty}",
                        f"NET: ${net_reward}"
                    ]
                    feedback_colors = [TEXT_COLOR, TEXT_COLOR, GAIN_COLOR if net_reward > 0 else (LOSS_COLOR if net_reward < 0 else TEXT_COLOR)]

                    # Calculate center position
                    original_position = DECK_POSITIONS[choice]
                    selected_image = selected_card_images[choice]
                    selected_rect = selected_image.get_rect(center=(original_position[0] + CARD_WIDTH // 2, original_position[1] + CARD_HEIGHT // 2))
                    
                    screen.blit(selected_image, selected_rect.topleft)
                    render_multiline_text(feedback_lines, feedback_colors, feedback_font, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
                    pygame.display.flip()
                    time.sleep(TRIAL_WAIT_TIME)  # Show feedback and selected card for 2 seconds

            pygame.display.flip()

    finally:
        task.summarize_results()
        task.save_data()

if __name__ == "__main__":
    main()
    pygame.quit()