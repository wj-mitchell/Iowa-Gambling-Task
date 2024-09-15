import pygame
import random
import csv
import time
import re
from datetime import datetime
import pandas as pd

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BACKGROUND_COLOR = (169, 169, 169)
TEXT_COLOR = (0, 0, 0)
GAIN_COLOR = (0, 255, 0)
LOSS_COLOR = (255, 0, 0)
CARD_SIZE_MULTIPLIER = 2.5
CARD_WIDTH = 100 * CARD_SIZE_MULTIPLIER
CARD_HEIGHT = 150 * CARD_SIZE_MULTIPLIER
CARD_SELECTION = 22 * CARD_SIZE_MULTIPLIER
POS_COL_L = 300
POS_COL_R = 1325
POS_ROW_TOP = 150
POS_ROW_BOTTOM = 650
DECK_POSITIONS = {
    '1': (POS_COL_L, POS_ROW_TOP),
    '2': (POS_COL_R, POS_ROW_TOP),
    '3': (POS_COL_L, POS_ROW_BOTTOM),
    '4': (POS_COL_R, POS_ROW_BOTTOM)
}
FEEDBACK_FONT_SIZE = 48
SCORE_FONT_SIZE = 56
MISC_FONT_SIZE = 36
LABEL_FONT_SIZE = 72
LINE_HEIGHT = FEEDBACK_FONT_SIZE + 5  # Space between lines
INITIAL_BALANCE = 2000
TRIAL_WAIT_TIME = 2  # Reduced wait time to 2 seconds

# Load card images
card_images = {
    '1': pygame.image.load('assets/card_blue_unselected.png'),
    '2': pygame.image.load('assets/card_red_unselected.png'),
    '3': pygame.image.load('assets/card_green_unselected.png'),
    '4': pygame.image.load('assets/card_yellow_unselected.png')
}

# Load selected card images
selected_card_images = {
    '1': pygame.image.load('assets/card_blue_selected.png'),
    '2': pygame.image.load('assets/card_red_selected.png'),
    '3': pygame.image.load('assets/card_green_selected.png'),
    '4': pygame.image.load('assets/card_yellow_selected.png')
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
trial_count = pygame.font.Font(None, SCORE_FONT_SIZE)
misc_font = pygame.font.Font(None, MISC_FONT_SIZE)
label_font = pygame.font.Font(None, LABEL_FONT_SIZE)

# Load the fixed reward schedule from the CSV file
fixed_schedule_df = pd.read_csv('reward_schedule.csv')

# Deck class
class Deck:
    def __init__(self, rewards, penalties, fixed_rewards=None, fixed_penalties=None):
        self.rewards = rewards
        self.penalties = penalties
        self.selected_count = 0
        self.fixed_rewards = fixed_rewards
        self.fixed_penalties = fixed_penalties

    def draw_card(self, fixed_schedule):
        if fixed_schedule:
            reward = self.fixed_rewards[self.selected_count]
            penalty = self.fixed_penalties[self.selected_count]
        else:
            reward = random.choice(self.rewards)
            penalty = random.choice(self.penalties)
        self.selected_count += 1
        return reward, penalty

# IowaGamblingTask class
class IowaGamblingTask:
    def __init__(self, pid, fixed_schedule):
        if fixed_schedule:
            self.decks = {
                '1': Deck(rewards=[], penalties=[], fixed_rewards=fixed_schedule_df['DeckA_Rewards'].tolist(), fixed_penalties=fixed_schedule_df['DeckA_Penalties'].tolist()),
                '2': Deck(rewards=[], penalties=[], fixed_rewards=fixed_schedule_df['DeckB_Rewards'].tolist(), fixed_penalties=fixed_schedule_df['DeckB_Penalties'].tolist()),
                '3': Deck(rewards=[], penalties=[], fixed_rewards=fixed_schedule_df['DeckC_Rewards'].tolist(), fixed_penalties=fixed_schedule_df['DeckC_Penalties'].tolist()),
                '4': Deck(rewards=[], penalties=[], fixed_rewards=fixed_schedule_df['DeckD_Rewards'].tolist(), fixed_penalties=fixed_schedule_df['DeckD_Penalties'].tolist())
            }
        else:
            self.decks = {
                '1': Deck(rewards=[100] * 50 + [50] * 50, penalties=[0] * 90 + [-250] * 10),
                '2': Deck(rewards=[100] * 50 + [50] * 50, penalties=[0] * 90 + [-1250] * 10),
                '3': Deck(rewards=[50] * 70 + [50] * 30, penalties=[0] * 90 + [-50] * 10),
                '4': Deck(rewards=[50] * 70 + [50] * 30, penalties=[0] * 90 + [-250] * 10)
            }
        self.total_score = INITIAL_BALANCE
        self.choices = []
        self.trial_data = []
        self.pid = pid
        self.fixed_schedule = fixed_schedule

    def draw_card_from_deck(self, choice, start_time, reaction_time, limit):
        if choice in self.decks:
            if self.decks[choice].selected_count < limit:
                reward, penalty = self.decks[choice].draw_card(self.fixed_schedule)
                net_reward = reward - penalty
                self.total_score += net_reward
                self.choices.append(choice)
                self.trial_data.append((len(self.choices), choice, reward, penalty, net_reward, self.total_score, reaction_time, start_time))
                return reward, penalty, net_reward, None
            else:
                return None, None, None, True
        return None, None, None, None

    def summarize_results(self):
        print("\nTask Completed")
        print(f"Total Score: {self.total_score}")
        print(f"Choices: {self.choices}")

    def save_data(self):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f'data/IGT_{self.pid}_{date_str}.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Trial', 'Deck Choice', 'Reward', 'Penalty', 'Net Reward', 'Total Score', 'Trial Duration (s)', 'Start Time'])
            writer.writerows(self.trial_data)

# PID validation function
def is_valid_pid(pid):
    return bool(re.match(r'^[A-Z]{2}-\d{4}$', pid))

# PID Input Screen
def get_pid(win_width, win_height):
    input_active = False
    pid = 'DD-'
    error_message = ''
    while True:
        screen.fill(BACKGROUND_COLOR)
        pid_text = misc_font.render("Enter Participant ID (format: DD-####):", True, TEXT_COLOR)
        input_box = pygame.Rect(win_width // 2 - 100, win_height // 2, 200, 50)
        txt_surface = misc_font.render(pid, True, TEXT_COLOR)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(pid_text, (win_width // 2 - pid_text.get_width() // 2, win_height // 2 - 30))

        # Center the text in the input box
        screen.blit(txt_surface, (input_box.x + (input_box.width - txt_surface.get_width()) // 2, input_box.y + (input_box.height - txt_surface.get_height()) // 2))
        pygame.draw.rect(screen, TEXT_COLOR, input_box, 2)

        if error_message:
            error_surface = misc_font.render(error_message, True, LOSS_COLOR)
            screen.blit(error_surface, (win_width // 2 - error_surface.get_width() // 2, win_height // 2 + 70))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return None
                elif event.key == pygame.K_RETURN:
                    if is_valid_pid(pid):
                        return pid
                    else:
                        error_message = "Invalid format. Please enter as DD-####."
                elif event.key == pygame.K_BACKSPACE:
                    pid = pid[:-1]
                else:
                    pid += event.unicode

        pygame.display.flip()

# Schedule type selection screen
def get_schedule_type(win_width, win_height):
    while True:
        screen.fill(BACKGROUND_COLOR)
        text = misc_font.render("Choose Reward Schedule:", True, TEXT_COLOR)
        random_text = misc_font.render("1. Random", True, TEXT_COLOR)
        fixed_text = misc_font.render("2. Fixed", True, TEXT_COLOR)
        screen.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - 50))
        screen.blit(random_text, (win_width // 2 - random_text.get_width() // 2, win_height // 2))
        screen.blit(fixed_text, (win_width // 2 - fixed_text.get_width() // 2, win_height // 2 + 50))
        screen.blit(fixed_text, (win_width // 2 - fixed_text.get_width() // 2, win_height // 2 + 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return None
                elif event.key == pygame.K_1:
                    return False
                elif event.key == pygame.K_2:
                    return True

        pygame.display.flip()

# Function to render and display multi-line text with different colors
def render_multiline_text(lines, colors, feedback_font, surface, x, y, center=False):
    for i, (line, color) in enumerate(zip(lines, colors)):
        line_surface = feedback_font.render(line, True, color)
        if center:
            line_rect = line_surface.get_rect(center=(x, y + i * LINE_HEIGHT))
            surface.blit(line_surface, line_rect.topleft)
        else:
            surface.blit(line_surface, (x, y + i * LINE_HEIGHT))

# Instruction screen
def show_instructions(win_width, win_height):
    screen.fill(BACKGROUND_COLOR)
    instructions = [
        "In this task, you will be asked to repeatedly select a card from one of four decks.\nYou can select a card by pressing 1, 2, 3, or 4 on the keyboard.\n\nPress SPACE to continue.",
        "With each card, you can win some money, but you can also lose some.\nSome decks will be more profitable than others.\nTry to choose cards from the most profitable decks so that your total winnings will be as high as possible.\n\nPress SPACE to continue.",
        "You will get 100 chances to select a card from the deck that you think will give you the highest winnings.\nYour total earnings and the number of cards selected will be displayed on screen.\n\nPress SPACE to continue.",
        "You will start with $2000 and will be rewarded with $1 cash for every $500 you finish the game with.\n\nPress SPACE to begin.",
    ]
    
    for instruction in instructions:
        screen.fill(BACKGROUND_COLOR)
        text_lines = instruction.split("\n")
        
        # Render and display each line of text
        for i, line in enumerate(text_lines):
            text = misc_font.render(line, True, TEXT_COLOR)
            screen.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - 100 + i * LINE_HEIGHT))
        
        pygame.display.flip()
        
        # Clear the event queue to avoid any leftover space key presses
        pygame.event.clear()
        
        # Wait for user to press space to move to the next instruction
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting_for_input = False  # Move to next instruction

# Start screen
def show_start_screen(win_width, win_height):
    screen.fill(BACKGROUND_COLOR)
    start_text = misc_font.render("Press SPACE to begin", True, TEXT_COLOR)
    screen.blit(start_text, (win_width // 2 - start_text.get_width() // 2, win_height // 2))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False
                elif event.key == pygame.K_SPACE:
                    waiting = False
    return True

# Exit screen
def show_exit_screen(win_width, win_height):
    screen.fill(BACKGROUND_COLOR)
    exit_text = [
        "Thank you! The task is complete!",
        "Please let the researcher know that you are finished."
    ]
    for i, line in enumerate(exit_text):
        text = misc_font.render(line, True, TEXT_COLOR)
        screen.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - 50 + i * LINE_HEIGHT))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
    return

# Display fixation cross
def show_fixation_cross(win_width, win_height, duration=2):
    screen.fill(BACKGROUND_COLOR)
    cross_text = label_font.render('+', True, TEXT_COLOR)
    cross_rect = cross_text.get_rect(center=(win_width // 2, win_height // 2))
    screen.blit(cross_text, cross_rect)
    pygame.display.flip()
    time.sleep(duration)

# Main loop
def main(n_trials=100, 
         selection_limit=100, 
         win_height=SCREEN_HEIGHT, 
         win_width=SCREEN_WIDTH,
         iti_dur=0.5):
    pid = get_pid(win_width, win_height)
    if not pid:
        return
    
    # fixed_schedule = get_schedule_type(win_width, win_height)
    fixed_schedule = True
    if fixed_schedule is None:
        return

    if not show_start_screen(win_width, win_height):
        return
    
    show_instructions(win_width, win_height)

    task = IowaGamblingTask(pid, fixed_schedule)
    running = True
    trial = 0

    try:
        while running and trial < n_trials:
            start_time = datetime.now().strftime('%H:%M:%S')
            trial_start = time.time()
            screen.fill(BACKGROUND_COLOR)

            # Draw card images and labels
            for key, position in DECK_POSITIONS.items():
                screen.blit(card_images[key], position)
                label = label_font.render(key, True, TEXT_COLOR)
                label_rect = label.get_rect(center=(position[0] + CARD_WIDTH // 2, position[1] - 40))
                screen.blit(label, label_rect)

            # Display current total score
            trial_text = trial_count.render(f"Trials Remaining: {100-trial}", True, TEXT_COLOR)
            screen.blit(trial_text, (10, 10))
            score_text = score_font.render(f"Total Score: ${task.total_score}", True, TEXT_COLOR)
            screen.blit(score_text, (1550, 10))


            # Event handling
            choice = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_1:
                        choice = '1'
                    elif event.key == pygame.K_2:
                        choice = '2'
                    elif event.key == pygame.K_3:
                        choice = '3'
                    elif event.key == pygame.K_4:
                        choice = '4'

            if choice:
                reaction_time = time.time() - trial_start
                reward, penalty, net_reward, error_message = task.draw_card_from_deck(choice, start_time, reaction_time, limit=selection_limit)
                if error_message:
                    # Display error message
                    feedback_lines = [
                        f"Maximum number of selections ({selection_limit})", 
                        "for this deck has been reached.", 
                        "Please select another deck."
                    ]
                    feedback_colors = [LOSS_COLOR, LOSS_COLOR, LOSS_COLOR]
                    render_multiline_text(feedback_lines, feedback_colors, feedback_font, screen, win_width // 2 - 100, win_height // 2 - 50)
                else:
                    trial += 1
                    print(f"Trial {trial}: Deck {choice}, Reward: {reward}, Penalty: {penalty}, Net reward: {net_reward}")
                    print(f"Total score: {task.total_score}")

                    # Display feedback
                    feedback_lines = [
                        f"WIN: ${reward}",
                        f"LOSE: ${penalty}",
                        f"NET: ${net_reward}"
                    ]
                    feedback_colors = [TEXT_COLOR, TEXT_COLOR, GAIN_COLOR if net_reward > 0 else (LOSS_COLOR if net_reward < 0 else TEXT_COLOR)]

                    # Display selected card
                    original_position = DECK_POSITIONS[choice]
                    selected_image = selected_card_images[choice]
                    selected_rect = selected_image.get_rect(center=(original_position[0] + CARD_WIDTH // 2, original_position[1] + CARD_HEIGHT // 2))

                    screen.blit(selected_image, selected_rect.topleft)
                    render_multiline_text(feedback_lines, feedback_colors, feedback_font, screen, win_width // 2 - 100, win_height // 2 - 50)
                
                pygame.display.flip()
                time.sleep(TRIAL_WAIT_TIME)  # Show feedback and selected card for 2 seconds

                if iti_dur > 0:
                    show_fixation_cross(win_width, win_height, duration = iti_dur)

            pygame.display.flip()

    finally:
        task.summarize_results()
        task.save_data()
        show_exit_screen(win_width, win_height)

if __name__ == "__main__":
    main()
    pygame.quit()
