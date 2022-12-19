

class Text:
    def __init__(self, message, font, color, pos):
        self.font = font
        self.color = color
        self.pos = pos

        self.message = message
        self.text = self.font.render(message, True, self.color)
        self.rect = self.text.get_rect()
        self.rect.center = self.pos

    def draw(self, surface):
        surface.blit(self.text, self.rect)

    def change_text(self, new_text):
        self.message = new_text
        self.text = self.font.render(self.message, True, self.color)
        self.rect = self.text.get_rect()
        self.rect.center = self.pos

    def change_color(self, new_color):
        self.color = new_color
        self.text = self.font.render(self.message, True, self.color)
