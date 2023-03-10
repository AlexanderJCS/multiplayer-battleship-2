import threading
import pygame
import socket

from networking import RecvMessage
from gui_text import Text

if not pygame.get_init():
    pygame.init()

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.SysFont("Calibri", 25)


class InputBox:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, (255, 255, 255))
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            self.active = not self.active if self.rect.collidepoint(event.pos) else False

            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        if self.active and event.type == pygame.KEYDOWN and event.key != pygame.K_RETURN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            else:
                self.text += event.unicode

            # Re-render the won_text.
            self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.text


class IPConnectionScreen:
    def __init__(self, surface, width, player_offset, client_socket, default_info_text="Press enter to connect"):
        self.surface = surface
        self.client_socket = client_socket

        self.width = width
        self.player_offset = player_offset

        # Text
        self.ip_text = Text("Server IP:", (255, 255, 255),
                            (self.width // 2, self.player_offset))

        self.port_text = Text("Server Port:", (255, 255, 255),
                              (self.width // 2, self.player_offset + 180))

        self.info_text = Text(default_info_text, (255, 255, 255),
                              (self.width // 2, self.player_offset + 300))

        # Input boxes
        self.ip_input = InputBox(self.width // 2 - 100, self.player_offset + 20, 200, 40)
        self.port_input = InputBox(self.width // 2 - 100, self.player_offset + 200, 200, 40, "9850")

        self.start_message = ""
        self.connected = False

    def get_start_message(self):
        start_message = RecvMessage(self.client_socket)
        start_message.recv_blocking()
        self.start_message = start_message.message

    def draw(self):
        self.surface.fill((0, 0, 0))

        self.ip_text.draw(self.surface)
        self.port_text.draw(self.surface)
        self.info_text.draw(self.surface)

        self.ip_input.draw(self.surface)
        self.port_input.draw(self.surface)
        pygame.display.update()

    """
    Runs the GUI for the IP connection screen.

    Returns: if the connection succeeded
    """

    def run(self):
        clock = pygame.time.Clock()

        while not self.start_message:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN and not self.connected and event.key == pygame.K_RETURN:
                    self.connected = self.connect()

                    if self.connected is False:  # if the connection failed
                        return False  # the connection failed

                    self.client_socket.settimeout(1000)

                    t = threading.Thread(target=self.get_start_message)
                    t.start()

                self.ip_input.handle_event(event)
                self.port_input.handle_event(event)

            self.draw()
            clock.tick(60)

        return True  # the connection succeeded

    def connect(self):  # returns: if the client successfully connected
        # sourcery skip: extract-duplicate-method
        self.info_text.change_text("Connecting...")
        self.draw()

        try:
            self.client_socket.connect((self.ip_input.get_text(), int(self.port_input.get_text())))

        except (TypeError, socket.error, ConnectionRefusedError, TimeoutError, ValueError):
            self.info_text.change_text("Failed")
            self.draw()
            return False

        self.info_text.change_text("Connected")
        self.draw()
        return True
