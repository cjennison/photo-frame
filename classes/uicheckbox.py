import pygame

class UICheckbox:
  def __init__(self, rect, text, key, toggle_action):
    self.rect = pygame.Rect(rect)
    self.text = text
    self.key = key
    self.toggle_action = toggle_action

  def draw(self, screen, font, ticked):
    # Draw checkbox border
    pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

    # Fill checkbox if active
    if ticked:
      pygame.draw.rect(screen, (255, 255, 255), self.rect)

    # Draw text label
    label = font.render(self.text, True, (255, 255, 255))
    label_rect = label.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
    screen.blit(label, label_rect)

  def handle_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
      if self.rect.collidepoint(event.pos):
        self.toggle_action(self.key)