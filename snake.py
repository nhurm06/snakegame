from tkinter import *
from abc import abstractmethod
from collections import namedtuple
import random
from itertools import count
from typing import Protocol, Tuple

BASE_SPEED = 100
SPEED_INCREMENT = 5
BACKGROUND_COLOR = "#000000"
CELL_SIZE =25
MAX_FOOD = 2

class Fruit(Protocol):
    """All Fruit must have reward and spawn"""
    def reward(self, game: "Game") -> int: ...
    def spawn(self) -> int: ...

class Player:
    """Handles a player's snake and controls."""
    #Passing in a player id/Player number is easier, but wanted to see if it can be automated
    playerIdCounter = count().__next__

    def __init__(self, canvas: Canvas, color: str) -> None:
        """Initialize player with a canvas and color."""
        self.canvas = canvas
        self.color = color
        self.playerId = Player.playerIdCounter()

    def change_direction(self, new_direction: str) -> None:
        """Change the player's direction if not reversing."""
        opposite_directions = {"up": "down", "down": "up", "left": "right", "right": "left"}
        if new_direction != opposite_directions.get(self.direction):
            self.direction = new_direction


    def random_coord(self, game: "Game") -> tuple:
        #TODO Only Randomizing X due to needing to account for Snake directions other than down
        x = random.randint(0, (game.width // CELL_SIZE) - 1) * CELL_SIZE
        return x, 0

    def change_score(self, reward: int) -> int:
        self.score = self.score + reward
        return self.score


    def spawn_snake(self, start_x: int, start_y: int, direction: str) -> "Snake":
        return Snake(self.canvas, self.color, start_x, start_y, direction)

    def start_player(self, game: "Game") -> None:
        """Initial Snake and direction"""
        start_x, start_y = self.random_coord(game)

        self.direction = "down" #Hardcoded due to possible issues spawing near a wall
        self.snake = self.spawn_snake(start_x, start_y, self.direction)

        self.score = 0



class Snake:

    def __init__(self, canvas: Canvas, color: str, start_x: int = 0, start_y: int = 0, direction: str = "down") -> None:
        self.canvas = canvas
        self.body_size = 3
        self.color = color
        self.food_consumed = 0
        self.speed = BASE_SPEED
        self.coordinates = [(start_x, start_y) for i in range(self.body_size)]
        self.squares = [self.create_square(x, y) for x, y in self.coordinates]

    def create_square(self, x: int, y: int) -> int:
        return self.canvas.create_rectangle(
            x, y, x + CELL_SIZE, y + CELL_SIZE, fill=self.color, tag="snake"
        )

    def move(self, direction: str) -> tuple:
        x, y = self.coordinates[0]

        if direction == "up":
            y -= CELL_SIZE
        elif direction == "down":
            y += CELL_SIZE
        elif direction == "left":
            x -= CELL_SIZE
        elif direction == "right":
            x += CELL_SIZE

        self.coordinates.insert(0, (x, y))
        self.squares.insert(0, self.create_square(x, y))

        return (x, y)

    def grow(self) -> None:
        """Snake eats, increases size and speed the."""
        self.body_size += 1
        self.food_consumed += 1
        self.speed = self.speed - (self.food_consumed * SPEED_INCREMENT) #counter intuitive. Lower the self.speed the quicker the refesh

    def cleanup(self) -> None:
        """Remove the last segment of the snake when moving forward."""
        if len(self.coordinates) > self.body_size:
            self.canvas.delete(self.squares[-1])
            del self.coordinates[-1]
            del self.squares[-1]



class Food(Fruit):


    spawn_rate = 1 #needed to set up a weighted query

    def __init__(self, canvas: Canvas, color: str, width: int, height: int):
        self.canvas = canvas
        self.color = color
        self.width = width
        self.height = height
        self.coordinates = self.random_coord()
        self.oval_id = self.spawn()

    def random_coord(self) -> tuple:
        """Generate a random coordinate within game boundaries."""
        x = random.randint(0, (self.width // CELL_SIZE) - 1) * CELL_SIZE
        y = random.randint(0, (self.height // CELL_SIZE) - 1) * CELL_SIZE
        return x, y

    def spawn(self):
        x, y = self.coordinates
        return self.canvas.create_oval(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=self.color, tag="food")


    def reward(self, game: "Game"):
        """Reward for eating. Force Subclasses to implement"""
        pass
    @classmethod
    def weighted_query_foods(cls) -> list:
        """Return a list with all foods multiplied by their spawn rate"""
        return [food for food in cls.__subclasses__() for i in range(food.spawn_rate)]


    @staticmethod
    def spawn_food(canvas: Canvas, width: int, height: int) -> "Fruit":
        """Create a food from weighted list of foods"""
        foods = Food.weighted_query_foods()
        return random.choice(foods)(canvas, width, height)


class Apple(Food):
    spawn_rate = 6

    def __init__(self, canvas: Canvas, width: int, height: int):
        super().__init__(canvas, "#FF0000", width, height)  # Red color for Apple

    def reward(self, game: "Game") -> int:
        return 1


class Blueberry(Food):
    spawn_rate = 3

    def __init__(self, canvas: Canvas, width: int, height: int):
        super().__init__(canvas, "#0000FF", width, height)  # Blue color for Blueberry

    def reward(self, game: "Game") -> int:
        return 2


class Cherry(Food):
    spawn_rate = 1

    def __init__(self, canvas: Canvas, width: int, height: int):
        super().__init__(canvas, "#FF00FF", width, height)  # Purple color for Cherry

    def reward(self, game: "Game") -> int:
        """Cherries also spawn apples."""
        self.spawn_apples(game)
        return 3

    def spawn_apples(self, game: "Game") -> None:
        for i in range(3):
            apple = Apple(game.canvas, game.width, game.height)
            game.foods.append(apple)




##add a new class to manage the game rather than functions
class Game:


    def __init__(self):
        self.game_running = False
        self.window = Tk()
        self.window.title("Snake Game")
        self.window.geometry(f"700x700")
        self.window.bind("<Configure>", self.on_resize) #needed to ensure game area is updated
        #Should window be resized when game is active?

        self.canvas = Canvas(self.window, bg=BACKGROUND_COLOR)
        self.canvas.pack(fill=BOTH, expand=True)
        self.foods = []
        self.players = [Player(self.canvas,"#00FF00"),Player(self.canvas,"#FFFF00")]  # Add more players as needed
        self.players = [Player(self.canvas, "#0FFFF0")]

        self.score_frame =LabelFrame(self.window, text="SCORE", font=('consolas',20))
        #TODO Edge case where food is spawned behind score label

        self.score_frame.pack(side=TOP)
        self.score_labels = {}
        for player in self.players:
            player_frame = Frame(self.score_frame)  # Container for each player's score
            player_frame.pack(side=LEFT, padx=10)
            color_canvas = Canvas(player_frame, width=20, height=20, bg=player.color)
            color_canvas.pack(side=LEFT, padx=5)
            label = Label(player_frame, text=f"Player {player.playerId + 1}: 0", font=("consolas", 14))
            label.pack(side=LEFT, padx=10)
            self.score_labels[player.playerId] = label
        self.bind_keys()
        self.window.mainloop()


    def update_score(self, player_id: int , new_score: int) -> None:
        """Update the score label dynamically."""
        self.score_labels[player_id].config(text=f"Player {player_id + 1}: {new_score}")

    def on_resize(self, event):
        """Adjust game width and height if window is changed"""
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()


        self.canvas.delete("start")
        self.canvas.create_text(
            self.width // 2, self.height // 2, font=('consolas', 40),
            text="GAME START", fill="white", tag="start"
        )
        self.canvas.create_text(
            self.width // 2, (self.height // 2) + 50, font=('consolas', 20),
            text="Press SPACE", fill="white", tag="start"
        )

    def game_start(self) -> None:
        self.game_running = False
        self.unbind_menu()
        self.canvas.delete("start")
        self.canvas.delete("gameover")
        self.foods.clear()
        self.manage_food()
        self.game_running = True
        for player in self.players:
            player.start_player(self)
            self.update_score(player.playerId,0)

            self.window.after(BASE_SPEED, self.next_turn, player)

    def bind_keys(self) -> None:
        """Bind movement keys to players."""
        #TODO We could make this on the player
        self.window.bind('<Left>', lambda event: self.players[0].change_direction("left"))
        self.window.bind('<Right>', lambda event: self.players[0].change_direction("right"))
        self.window.bind('<Up>', lambda event: self.players[0].change_direction("up"))
        self.window.bind('<Down>', lambda event: self.players[0].change_direction("down"))
        self.window.bind('<a>', lambda event: self.players[1].change_direction("left"))
        self.window.bind('<d>', lambda event: self.players[1].change_direction("right"))
        self.window.bind('<w>', lambda event: self.players[1].change_direction("up"))
        self.window.bind('<s>', lambda event: self.players[1].change_direction("down"))
        self.window.bind('<space>', lambda event: self.game_start())
    def unbind_menu(self) -> None:
        #TODO there's undoubtedly a better way to do is.
        #temp unbinding of a key during gameplay
        self.window.unbind("<space>")

    def manage_food(self) -> None:
        """Ensure both players have access to food"""
        while len(self.foods) < MAX_FOOD:
            new_food = Food.spawn_food(self.canvas, self.width, self.height)
            self.foods.append(new_food)
    def next_turn(self, player: Player) -> None:
        if not self.game_running: #Don't move if game isn't running
            return

        x, y = player.snake.move(player.direction)

        #TODO Can simplify this.
        #If player collides with other player snake, stop movement, but dont end game
        for p in self.players:
            if player.playerId != p.playerId:

                if (x,y) in p.snake.coordinates:
                    self.canvas.delete(player.snake.squares[0])
                    player.snake.squares.pop(0)
                    player.snake.coordinates.pop(0)

        if self.check_collision(player.snake):
            self.game_over()
            return

        for food in self.foods[:]:
            if (x, y) == (food.coordinates):
                player.snake.grow()
                self.update_score(player.playerId, player.change_score(food.reward(self)))

                self.foods.remove(food)
                self.canvas.delete(food.oval_id)

                self.manage_food()
                break
        player.snake.cleanup()
        self.window.after(player.snake.speed, self.next_turn, player)

    def check_collision(self, snake: Snake) -> bool:
        """Check if the snake collides with the walls or itself."""
        x, y = snake.coordinates[0]

        # Wall collision
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True

        # Self-collision
        for segment in snake.coordinates[1:]:
            if x == segment[0] and y == segment[1]:
                return True

        return False

    def game_over(self) -> None:
        """End the game and display a Game Over message."""
        self.game_running = False
        self.canvas.delete(ALL)
        self.canvas.create_text(
            self.width // 2, self.height // 2, font=('consolas', 40),
            text="GAME OVER", fill="red", tag="gameover"
        )
        self.canvas.create_text(
            self.width // 2, self.height // 2 + 50, font=('consolas', 40),
            text="Space to Retry", fill="white", tag="gameover"
        )
        self.window.bind('<space>', lambda event: self.game_start())


if __name__ == "__main__":
    Game()