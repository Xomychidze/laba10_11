import pygame
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Шрифт


class GameObject:
    def __init__(self, x, y, width, height, color, weight):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.weight : int = weight

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
    
    def get_weight(self):
        return self.weight
        
# Класс овтечающий за UI 
class UI: 
    def __init__(self, x, y, width, height, color, size):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_color = (255,255,255)
        if(size == None): 
            size = 36
        self.font = pygame.font.Font(None, size)
        
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.count, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
class Button:
    def __init__(self, x, y, width, height, color, text, text_color, rounded):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)
        self.rounded = rounded

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect,30, self.rounded)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)    

class UI_level(UI):
    def __init__(self, x, y, width, height, color,size, text):
        super().__init__(x, y, width, height, color, size) 
        self.text = text
        self.text_color = (255,255,255)
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    

class UI_Count(UI): 
    def __init__(self, x, y, width, height, color,size):
        super().__init__(x, y, width, height, color, size)
        self.count = "0"
        self.num = 0
        
    def count_more(self, weight):
        self.num += weight
        self.count = f"{self.num}"
        
class InputBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = WHITE
        self.color_active = GRAY
        self.color = self.color_inactive
        self.text = ''  # Текст, который вводит пользователь
        self.input_value = None  # Сюда сохранится введённый текст
        self.input_received = False  # Флаг, что данные введены
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(self.text, True, WHITE)
        self.border_color = WHITE
        self.border_width = 2

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.input_value = self.text  # Сохраняем введённый текст
                self.input_received = True    # Меняем флаг на True
                self.text = ''  # Очищаем поле (опционально)
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, WHITE)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        inner_rect = pygame.Rect(
            self.rect.x + self.border_width,
            self.rect.y + self.border_width,
            self.rect.width - 2 * self.border_width,
            self.rect.height - 2 * self.border_width
        )
        pygame.draw.rect(screen, BLACK, inner_rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))