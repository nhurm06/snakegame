from tkinter import *
import random

SPEED = 100
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BACKGROUND_COLOR = "#000000"
HEIGHT = 700
WIDTH = 700
CELL_SIZE =50


class Snake(object):

    def __init__(self, canvas):
        self.body_size = 3
        self.coordinates = []
        self.squares = []

        #change range to factor in body size rather than hard coding
        for i in range(0, self.body_size):
            self.coordinates.append([0, 0])

        for x, y in self.coordinates:
            square = canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)


class Food(object):

    def __init__(self, canvas):

        x = random.randint(0, (WIDTH / CELL_SIZE)-1) * CELL_SIZE
        y = random.randint(0, (HEIGHT / CELL_SIZE) - 1) * CELL_SIZE

        self.coordinates = [x, y]

        canvas.create_oval(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=FOOD_COLOR, tag="food")

##add a new class to manage the game rather than functions
class Game(object):
    '''
    Snake Game logic
    '''

    def __init__(self):
        '''
        initalize the window and game
        Returns:

        '''
        self.window = Tk()
        self.window.title("Snake game")
        self.window.resizable(False, False)

        #set score and directior to be members of the class rather than global. New game new score/direction
        self.score = 0
        self.direction = 'down'

        self.label = Label(self.window, text="Score:{}".format(self.score), font=('consolas', 40))
        self.label.pack()

        self.canvas = Canvas(self.window, bg=BACKGROUND_COLOR, height=HEIGHT, width=WIDTH)
        self.canvas.pack()

        self.window.update()

        #TODO window setup could be moved to a new function
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.window.bind('<Left>', lambda event: self.change_direction('left'))
        self.window.bind('<Right>', lambda event: self.change_direction('right'))
        self.window.bind('<Up>', lambda event: self.change_direction('up'))
        self.window.bind('<Down>', lambda event: self.change_direction('down'))

        self.snake = Snake(self.canvas)
        self.food = Food(self.canvas)

        self.next_turn()

        self.window.mainloop()

    def next_turn(self):

        x, y = self.snake.coordinates[0]

        if self.direction == "up":
            y -= 50
        elif self.direction == "down":
            y += 50
        elif self.direction == "left":
            x -= 50
        elif self.direction == "right":
            x += 50

        self.snake.coordinates.insert(0, (x, y))

        square = self.canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=SNAKE_COLOR)

        self.snake.squares.insert(0, square)

        if x == self.food.coordinates[0] and y == self.food.coordinates[1]:

            self.score += 1

            self.label.config(text="Score:{}".format(self.score))

            self.canvas.delete("food")

            self.food = Food(self.canvas)

        else:

            del self.snake.coordinates[-1]

            self.canvas.delete(self.snake.squares[-1])

            del self.snake.squares[-1]

        if self.check_collisions():
            self.game_over()

        else:
            self.window.after(SPEED, self.next_turn)


    def change_direction(self,new_direction):
        #changing complicated direction change. Snake cannot turn 180
        if new_direction == 'left':
            if self.direction != 'right':
                self.direction = new_direction
        elif new_direction == 'right':
            if self.direction != 'left':
                self.direction = new_direction
        elif new_direction == 'up':
            if self.direction != 'down':
                self.direction = new_direction
        elif new_direction == 'down':
            if self.direction != 'up':
                self.direction = new_direction


    def check_collisions(self):

        x, y = self.snake.coordinates[0]
        #make window size a constant
        if x < 0 or x >= HEIGHT:
            return True
        elif y < 0 or y >= WIDTH:
            return True

        for body_part in self.snake.coordinates[1:]:
            if x == body_part[0] and y == body_part[1]:
                return True

        return False


    def game_over(self):

        self.canvas.delete(ALL)
        self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2,
                           font=('consolas',70), text="GAME OVER", fill="red", tag="gameover")


if __name__ == "__main__":
    Game()