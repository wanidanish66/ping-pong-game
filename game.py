import pygame
import sys
import socket
import threading
import pickle
import webbrowser
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 7
        self.score = 0
    
    def move(self, dy):
        self.rect.y += dy * self.speed
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
        self.dx = 5
        self.dy = 5
    
    def reset(self):
        self.rect.center = (WIDTH//2, HEIGHT//2)
        self.dx = -self.dx
        self.dy = 5 if pygame.time.get_ticks() % 2 == 0 else -5

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ping Pong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.player = Paddle(20, HEIGHT//2 - PADDLE_HEIGHT//2)
        self.opponent = Paddle(WIDTH - 20 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2)
        self.ball = Ball()
        
        self.running = True
        self.is_host = False
        self.connected = False
        self.sock = None
        self.opponent_addr = None
        self.network_thread = None

    def host_game(self):
        self.is_host = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 5555))
        print("Hosting on port 5555 - share your IP with opponent")
        
        self.network_thread = threading.Thread(target=self.network_listen, daemon=True)
        self.network_thread.start()

    def join_game(self, host_ip):
        self.is_host = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.opponent_addr = (host_ip, 5555)
        self.sock.sendto(b"connect", self.opponent_addr)
        
        self.network_thread = threading.Thread(target=self.network_listen, daemon=True)
        self.network_thread.start()

    def network_listen(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                
                if not self.connected:
                    if data == b"connect" and self.is_host:
                        self.opponent_addr = addr
                        self.sock.sendto(b"connected", addr)
                        self.connected = True
                    elif data == b"connected" and not self.is_host:
                        self.connected = True
                    continue
                
                if self.is_host:
                    try:
                        self.opponent.rect.y = pickle.loads(data)
                    except:
                        pass
                else:
                    try:
                        game_state = pickle.loads(data)
                        self.ball.rect.x = game_state['ball_x']
                        self.ball.rect.y = game_state['ball_y']
                        self.player.score = game_state['player_score']
                        self.opponent.score = game_state['opponent_score']
                    except:
                        pass
            except:
                time.sleep(0.1)

    def send_data(self):
        if not self.connected: return
        
        try:
            if self.is_host:
                game_state = {
                    'ball_x': self.ball.rect.x,
                    'ball_y': self.ball.rect.y,
                    'player_score': self.player.score,
                    'opponent_score': self.opponent.score
                }
                self.sock.sendto(pickle.dumps(game_state), self.opponent_addr)
            else:
                self.sock.sendto(pickle.dumps(self.player.rect.y), self.opponent_addr)
        except:
            pass

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: self.player.move(-1)
        if keys[pygame.K_DOWN]: self.player.move(1)
        
        if self.is_host and self.connected:
            self.ball.rect.x += self.ball.dx
            self.ball.rect.y += self.ball.dy
            
            if self.ball.rect.top <= 0 or self.ball.rect.bottom >= HEIGHT:
                self.ball.dy *= -1
            
            if self.ball.rect.colliderect(self.player.rect):
                self.ball.dx = abs(self.ball.dx)
                relative_intersect = (self.player.rect.centery - self.ball.rect.centery) / (PADDLE_HEIGHT/2)
                self.ball.dy = -relative_intersect * 7
            
            if self.ball.rect.colliderect(self.opponent.rect):
                self.ball.dx = -abs(self.ball.dx)
                relative_intersect = (self.opponent.rect.centery - self.ball.rect.centery) / (PADDLE_HEIGHT/2)
                self.ball.dy = -relative_intersect * 7
            
            if self.ball.rect.left <= 0:
                self.opponent.score += 1
                self.ball.reset()
            if self.ball.rect.right >= WIDTH:
                self.player.score += 1
                self.ball.reset()
        
        if self.connected:
            self.send_data()

    def render(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, self.player.rect)
        pygame.draw.rect(self.screen, WHITE, self.opponent.rect)
        pygame.draw.ellipse(self.screen, WHITE, self.ball.rect)
        pygame.draw.aaline(self.screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
        
        player_score = self.font.render(str(self.player.score), True, WHITE)
        opponent_score = self.font.render(str(self.opponent.score), True, WHITE)
        self.screen.blit(player_score, (WIDTH//4, 20))
        self.screen.blit(opponent_score, (3*WIDTH//4, 20))
        
        if not self.connected:
            status = self.font.render("Press H to host or J to join", True, WHITE)
            self.screen.blit(status, (WIDTH//2 - 150, HEIGHT//2))
        else:
            status = self.font.render("Connected!", True, (0, 255, 0))
            self.screen.blit(status, (WIDTH//2 - 50, 10))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_h and not self.connected:
                        self.host_game()
                    elif event.key == pygame.K_j and not self.connected:
                        host_ip = input("Enter host IP: ")
                        self.join_game(host_ip)
            
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        if self.sock:
            self.sock.close()
        pygame.quit()
        sys.exit()

def start_web_server():
    PORT = 8000
    Handler = SimpleHTTPRequestHandler
    httpd = TCPServer(("", PORT), Handler)
    print(f"Serving at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    print("Starting web server...")
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    game = Game()
    game.run()