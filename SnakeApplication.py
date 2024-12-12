import time
import curses
import argparse
import rti.connextdds as dds
from collections import deque
from utils import ShapeTypeExtended


class SnakeApplication:
    def __init__(self, snake_id, domain_id=0, is_bot=False):
        self.running = True
        self.dds_width = 230
        self.dds_height = 265

        # Initialize curses for input handling
        if not is_bot:
            self.screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.screen.keypad(True)
            self.screen.nodelay(True)

        # Initialize DDS components
        # TODO: Implement DDS initialization

        
        # Initialize snake attributes
        self.snake_id = snake_id
        self.is_bot = is_bot

        # Initialize snake with DDS coordinates
        self.snake = deque([(30, 40), (30, 35), (30, 30)])  # DDS coordinates
        self.direction = (0, 5)  # DDS coordinate movement
        self.food_position = None

    def handle_input(self):
        # TODO: Implement user input handling for controlling the snake
        pass

    def calculate_bot_direction(self):
        # TODO: Implement bot logic to calculate the next move
        pass

    def update_snake(self):
        head_x, head_y = self.snake[0]
        dy, dx = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Handle wrapping in DDS coordinates
        new_head = (new_head[0] % self.dds_width, new_head[1] % self.dds_height)

        self.snake.appendleft(new_head)
        self.snake.pop()

        # Publish snake position to DDS
        self.snake_writer.write(
            ShapeTypeExtended(
                color=self.snake_id, x=new_head[0], y=new_head[1], shapesize=10
            )
        )

    def check_food_updates(self):
        for sample in self.food_reader.read():
            if sample.info.valid:
                self.food_position = sample.data

    def run(self):
        while self.running:
            if self.is_bot:
                self.direction = self.calculate_bot_direction()
            else:
                self.handle_input()
            self.update_snake()
            self.check_food_updates()  # Check for food updates more frequently
            time.sleep(0.1)

    def __del__(self):
        if not self.is_bot:
            # Cleanup curses
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()


def parse_args():
    parser = argparse.ArgumentParser(description="Snake Game")
    parser.add_argument(
        "--snake-id", required=True, help="Unique identifier for the snake"
    )
    parser.add_argument("--domain-id", type=int, default=0, help="DDS Domain ID")
    parser.add_argument("--is-bot", action="store_true", help="Run as a bot")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        app = SnakeApplication(
            args.snake_id, domain_id=args.domain_id, is_bot=args.is_bot
        )
        app.run()
    except KeyboardInterrupt:
        print(f"\nSnake {args.snake_id} has stopped.")
    finally:
        if not args.is_bot:
            curses.endwin()  # Ensure proper cleanup


if __name__ == "__main__":
    main()
