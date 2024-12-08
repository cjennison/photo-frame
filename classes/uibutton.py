import pygame

class UIButton:
  def __init__(self, rect, text, action):
    self.rect = pygame.Rect(rect)
    self.text = text
    self.action = action

  def draw(self, screen, font):
    pygame.draw.rect(screen, (0, 0, 0), self.rect)  # Black background for button
    label = font.render(self.text, True, (255, 255, 255))
    label_rect = label.get_rect(center=self.rect.center)
    screen.blit(label, label_rect)

  def handle_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
      if self.rect.collidepoint(event.pos):
        self.action()