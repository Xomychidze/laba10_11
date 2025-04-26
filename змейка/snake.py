import pygame
import sys
import random as ran
import classGame
import psycopg2
from configparser import ConfigParser
from psycopg2 import sql

pygame.mixer.init()


# Музыка
monetka = pygame.mixer.Sound("змейка/z_uki-dlya-_ideo-z_uk-monetok-mario.mp3")


# Database configuration
def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in {filename}')
    return config

def get_db_connection():
    config = load_config()
    try:
        conn = psycopg2.connect(**config)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

# Database functions
def get_user(nickname):
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT nickname, level, score FROM snake WHERE nickname = %s"),
                [nickname]
            )
            user = cur.fetchone()
            return user
    except psycopg2.Error as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def create_user(nickname):
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("INSERT INTO snake (nickname, level, score) VALUES (%s, %s, %s)"),
                [nickname, 1, 0]
            )
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_user_score(nickname, score, level):
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        with conn.cursor() as cur:
            # Check if user exists
            cur.execute(
                sql.SQL("SELECT 1 FROM snake WHERE nickname = %s"),
                [nickname]
            )
            exists = cur.fetchone()
            
            if exists:
                # Update existing user
                cur.execute(
                    sql.SQL("UPDATE snake SET score = %s, level = %s WHERE nickname = %s"),
                    [score, level, nickname]
                )
            else:
                # Create new user
                cur.execute(
                    sql.SQL("INSERT INTO snake (nickname, level, score) VALUES (%s, %s, %s)"),
                    [nickname, level, score]
                )
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error updating score: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 1500, 800
BLACK = (0, 0, 0)
CELL_SIZE = 20
SPEED = 5
HAS_FOOD_SCREEN = False
INTERVAL = 2000

# Game variables
tick_speed = 13
level_up = True
play_game = True
food = False
monetka_music = False
time_set = 0
special_food = False
current_level = 1
username = ""
game_started = False

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Simple Snake')
start_time = pygame.time.get_ticks()

# Colors
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# Game arrays
obstacles = []
snake_pos = [100, 100]
snake_body = [[100, 100], [80, 100], [60, 100]]
direction = 'RIGHT'
change_to = direction

# UI
ui = classGame.UI_Count(WIDTH - 100, 20, 80, 40, (50, 50, 50), 36)
clock = pygame.time.Clock()

# Load snake head image
snake_head_img = pygame.image.load("змейка/man.jpg")
snake_head_img = pygame.transform.scale(snake_head_img, (CELL_SIZE, CELL_SIZE))

# Text input box
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)
        return False

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

# Create input box
input_box = InputBox(WIDTH//2 - 100, HEIGHT//2 - 25, 100, 50)
start_button = classGame.Button(WIDTH//2 - 100, HEIGHT//2 + 50, 100, 50, (0, 200, 0), "Start Game", (255, 255, 255), 5)

running = True
while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_started:
            if input_box.handle_event(event):
                username = input_box.text.strip()
            if event.type == pygame.MOUSEBUTTONUP:
                if start_button.rect.collidepoint(event.pos) and input_box.text.strip():
                    username = input_box.text.strip()
                    user = get_user(username)
                    if user:
                        # Existing user - load their progress
                        nickname, current_level, score = user
                        ui.num = score
                        tick_speed = 13 + (current_level - 1) * 0.5
                    else:
                        # New user - create record
                        if create_user(username):
                            current_level = 1
                            ui.num = 0
                    game_started = True
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pause and save game
                    if username and play_game:
                        update_user_score(username, ui.num, current_level)
                
                if event.key == pygame.K_w and direction != 'DOWN':
                    change_to = 'UP'
                elif event.key == pygame.K_s and direction != 'UP':
                    change_to = 'DOWN'
                elif event.key == pygame.K_d and direction != 'LEFT':
                    change_to = 'RIGHT'
                elif event.key == pygame.K_a and direction != 'RIGHT':
                    change_to = 'LEFT'

            elif event.type == pygame.MOUSEBUTTONUP:
                if not play_game: 
                    pos = event.pos
                    if button_exit.rect.collidepoint(pos):
                        running = False
                    if button_replay.rect.collidepoint(pos):
                        tick_speed = 13
                        level_up = True
                        play_game = True
                        food = False
                        obstacles = []
                        snake_pos = [100, 100]
                        snake_body = [[100, 100], [80, 100], [60, 100]]
                        direction = 'RIGHT'
                        change_to = direction
                        ui = classGame.UI_Count(WIDTH - 100, 20, 80, 40, (50, 50, 50), 36)

    if not game_started:
        screen.fill(BLACK)
        title = classGame.UI_level(0, HEIGHT//4, WIDTH, 60, (255, 255, 255), 60, "Enter your nickname:")
        title.draw(screen)
        input_box.update()
        input_box.draw(screen)
        start_button.draw(screen)
        pygame.display.flip()
        continue

    # Rest of the game logic remains the same as before...
    if play_game:
        # Check for self-collision
        for i in range(1, len(snake_body)):
            if snake_body[0][0] == snake_body[i][0] and snake_body[0][1] == snake_body[i][1]:
                play_game = False
                # Save final score when game ends
                update_user_score(username, ui.num, current_level)
                pygame.mixer.music.load("змейка/mario-smert.mp3")
                pygame.mixer.music.play()

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("змейка/super-mario-saundtrek.mp3")
            pygame.mixer.music.play()

        direction = change_to

        # Create food
        if current_time - start_time >= INTERVAL:
            if not food: 
                food_x = ran.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
                food_y = ran.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
                choose = ran.randint(1, 3)
                if choose == 1:
                    food = classGame.GameObject(food_x, food_y, CELL_SIZE, CELL_SIZE, (255, 255, 255), 1)
                elif choose == 2:
                    food = classGame.GameObject(food_x, food_y, CELL_SIZE, CELL_SIZE, (255, 255, 255), 2)
                elif choose == 3: 
                    food = classGame.GameObject(food_x, food_y, CELL_SIZE, CELL_SIZE, (255, 0, 0), 3)
                    line_time = pygame.Rect(700, 30, 300, 10)
                    special_food = True
                obstacles.append(food)
                food = True
            time_set += 1

        # Check food collision
        player = pygame.Rect(snake_pos[0], snake_pos[1], CELL_SIZE, CELL_SIZE)
        for obstacle in obstacles[:]:
            if player.colliderect(obstacle.rect):
                obj: classGame.GameObject = obstacle
                ui.count_more(obj.get_weight()) 
                obstacles.remove(obstacle)
                snake_body.insert(0, list(snake_pos))
                special_food = False
                line_time = None
                level_up = True
                monetka.play()
                monetka_music = True
                food = False

        # Stop coin sound
        if time_set % 10 == 0:
            monetka_music = False
        if not monetka_music:
            monetka.stop()

        # Special food timer
        if special_food:
            line_time.width -= 5
            if line_time.width <= 0: 
                obstacles.clear()
                special_food = False
                line_time = None
                food = False

        # Level up
        if ui.num % 5 == 0 and ui.num != 0 and level_up: 
            level_up = False
            tick_speed += 0.5
            current_level += 1
            # Auto-save when leveling up
            update_user_score(username, ui.num, current_level)

        # Move snake
        if direction == 'UP':
            snake_pos[1] -= CELL_SIZE 
        elif direction == 'DOWN':
            snake_pos[1] += CELL_SIZE 
        elif direction == 'LEFT':
            snake_pos[0] -= CELL_SIZE 
        elif direction == 'RIGHT':
            snake_pos[0] += CELL_SIZE 

        # Screen boundaries
        if (snake_pos[0] < 0 or snake_pos[0] >= WIDTH or 
            snake_pos[1] < 0 or snake_pos[1] >= HEIGHT):
            play_game = False
            # Save final score when game ends
            update_user_score(username, ui.num, current_level)
            pygame.mixer.music.load("змейка/mario-smert.mp3")
            pygame.mixer.music.play()

        snake_body.insert(0, list(snake_pos))
        snake_body.pop()

    screen.fill(BLACK)

    # Draw game
    if play_game: 
        for i in range(1, len(snake_body)):
            pygame.draw.rect(screen, GREEN, pygame.Rect(snake_body[i][0], snake_body[i][1], CELL_SIZE, CELL_SIZE))
        for obstacle in obstacles: 
            obstacle.draw(screen)    

        # Draw snake head
        screen.blit(snake_head_img, (snake_pos[0], snake_pos[1]))

        if special_food:
            pygame.draw.rect(screen, (255, 255, 255), line_time)
        
        # Draw UI elements
        ui.draw(screen)
        
        # Display level and username
        level_text = classGame.UI_level(20, 20, 200, 40, (255, 255, 255), 36, f"Level: {current_level}")
        user_text = classGame.UI_level(20, 60, 300, 40, (255, 255, 255), 36, f"Player: {username}")
        level_text.draw(screen)
        user_text.draw(screen)
        
        # Draw pause/save hint
        pause_text = classGame.UI_level(WIDTH - 300, HEIGHT - 40, 280, 30, (200, 200, 200), 24, "Press P to save game")
        pause_text.draw(screen)
    else: 
        game_over = classGame.UI_level(0, 0, WIDTH, HEIGHT, (200, 0, 0), 80, "Game Over!")
        button_replay = classGame.Button(580, 450, 150, 60, (0, 0, 0), "Replay", (255, 255, 255), 5)
        button_exit = classGame.Button(780, 450, 150, 60, (0, 0, 0), "Exit", (255, 255, 255), 5)        
        game_over.draw(screen)
        button_exit.draw(screen)
        button_replay.draw(screen)

    pygame.display.flip()
    clock.tick(tick_speed)

pygame.quit()
sys.exit()