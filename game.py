import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")
clock = pygame.time.Clock()

# Game objects
player_paddle = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent_paddle = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Game variables
player_score = 0
opponent_score = 0  # Fixed: Changed from 'opponent_score' to 'opponent_score'
ball_speed_x = 7 * random.choice((1, -1))
ball_speed_y = 7 * random.choice((1, -1))
player_speed = 0
opponent_speed = 7
game_font = pygame.font.Font(None, 36)

def ball_restart():
    global ball_speed_x, ball_speed_y
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed_x *= random.choice((1, -1))
    ball_speed_y *= random.choice((1, -1))

def ball_animation():
    global ball_speed_x, ball_speed_y, player_score, opponent_score  # Fixed variable name
    
    # Move the ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y
    
    # Ball collision with top and bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1
    
    # Ball collision with paddles
    if ball.colliderect(player_paddle) or ball.colliderect(opponent_paddle):
        ball_speed_x *= -1
    
    # Score points
    if ball.left <= 0:
        opponent_score += 1
        ball_restart()
    if ball.right >= WIDTH:
        player_score += 1
        ball_restart()

def player_animation():
    player_paddle.y += player_speed
    
    # Keep paddle on screen
    if player_paddle.top <= 0:
        player_paddle.top = 0
    if player_paddle.bottom >= HEIGHT:
        player_paddle.bottom = HEIGHT

def opponent_ai():
    # Simple AI to follow the ball
    if opponent_paddle.centery < ball.centery:
        opponent_paddle.y += opponent_speed
    if opponent_paddle.centery > ball.centery:
        opponent_paddle.y -= opponent_speed
    
    # Keep paddle on screen
    if opponent_paddle.top <= 0:
        opponent_paddle.top = 0
    if opponent_paddle.bottom >= HEIGHT:
        opponent_paddle.bottom = HEIGHT

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Player paddle control
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player_speed = 7
            if event.key == pygame.K_UP:
                player_speed = -7
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                player_speed = 0
    
    # Game logic
    ball_animation()
    player_animation()
    opponent_ai()
    
    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, opponent_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    
    # Display scores
    player_text = game_font.render(f"{player_score}", False, WHITE)
    opponent_text = game_font.render(f"{opponent_score}", False, WHITE)  # Fixed variable name
    screen.blit(player_text, (WIDTH // 4, 20))
    screen.blit(opponent_text, (3 * WIDTH // 4, 20))
    
    # Update the display
    pygame.display.flip()
    clock.tick(FPS)