import ev3dev.ev3 as ev3
import time
from PIL import ImageFont
from math import floor

class Interaction:
    '''
        The Interaction Class provides the possibility to get input from the User via the basic user interface of the lego brick. There is a screen to display content and 5 buttons (left, right, up, down, enter) do select options.

        Besids printing text in an optimal size there is the possibility to get Integer or Boolean values from the user interface.
    '''

    def __init__(self):
        self.screen = ev3.Screen()

    def get_number(self, start, end, default=None):
        '''
            Asks the user to select a number with a picker from a given range intervall [start, end]. Default is the preselected value of the picker.

            Returns an integer value
        '''

        return NumberInput(start, end, self.screen, default).get_number()

    def get_bool(self, message):
        '''
            Asks the user to select a boolean value as the answer to the question/message

            Returns a boolean value
        '''
        return BooleanInput(message, self.screen).get_bool()

    def print(self, *arg):
        '''
            Print lines in an optimal size on the screen.

            Argument:
                arg     lines to be displayed
        '''

        line_length, count_lines = max(map(len, arg)), len(arg)
        '''
            screen is 178x128 pixel
            each character is 3/5*size pixels wide and 5/6*size pixels high
            making size small enough that line_length many characters and count_lines lines fit on the screen
        '''
        size = min(floor(178*5/3/line_length), floor(128/count_lines*6/5))
        courier_new = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Courier_New.ttf', size)

        self.screen.clear()
        for k, line in enumerate(arg):
            # pos is upper left corner of next line
            # each character is courier_new.getsize("x")[1] pixel high
            pos = (0, courier_new.getsize("x")[1]*k)
            self.screen.draw.text(pos, line, font=courier_new)

        self.screen.update()

class NumberInput:
    '''
        The NumberInput class handles user interaction with the aim to get an integer return value
    '''

    def __init__(self, start, end, screen, default=None):
        '''
            Arguments:
                start         lower bound of number to be entered
                end           upper bound of number to be entered
                screen        screen object to be printed on
                default       starting number, if ommited (start+end)//2
        '''
        self.position = 0 # which digit is to be changed
        self.position_count = len(str(end)) # amount of digits
        self.start = start
        self.end = end
        self.current_number = (start + end)//2 if default is None else default # saves current state
        self.result = None # after enter press, result is the input of the user

        # adding functions to be executed on different button presses
        self.btn = ev3.Button()
        self.btn.on_up = self.increase
        self.btn.on_down = self.decrease
        self.btn.on_left = self.left
        self.btn.on_right = self.right
        self.btn.on_enter = self.enter

        self.screen = screen
        # same calculation as above
        size = min(floor(178*5/3/self.position_count), floor(128*6/5))
        self.courier_new = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Courier_New.ttf', size)

    def reset(self):
        ''' reset class to input another number '''
        self.result = None
        self.current_number = (self.start + self.end)//2
        self.position = 0

    def is_finished(self):
        ''' returns whether enter was already pressed '''
        return self.result is not None

    def get_number(self):
        ''' waits while enter isn't pressed yet and returns the result'''
        if not self.is_finished():
            self.refresh()
        while not self.is_finished():
            time.sleep(0.01)    # fixes a double event from the button
            self.btn.process()
        return self.result

    def refresh(self):
        ''' prints current number and marks the digit to be changed '''
        self.screen.clear()
        # formatted_str is current number precedet by numbers such that len(formatted_str) == position_count
        formatted_str = ("{:0" + str(self.position_count) + "}").format(int(self.current_number))

        for pos in range(self.position_count):
            if self.position_count - pos - 1 == self.position:
                # gives the selected position a black background and white font color
                prev_width = self.screen.draw.textsize(formatted_str[:pos], font=self.courier_new)
                next_width = self.screen.draw.textsize(formatted_str[:pos+1], font=self.courier_new)
                self.screen.draw.rectangle((prev_width[0], 0, next_width[0], next_width[1]), fill="black")
                self.screen.draw.text((prev_width[0],0), formatted_str[pos], font=self.courier_new, fill="white")
            else:
                prev_width = self.screen.draw.textsize(formatted_str[:pos], font=self.courier_new)[0]
                self.screen.draw.text((prev_width,0), formatted_str[pos], font=self.courier_new)

        self.screen.update()

    def increase(self, state):
        ''' increases the current_number at the current position by 1 '''
        if self.is_finished(): return
        if state:
            self.current_number += 10**self.position
            self.current_number = min(self.current_number, self.end)
            self.refresh()

    def decrease(self, state):
        ''' decreases the current_number at the current position by 1 '''
        if self.is_finished(): return
        if state:
            self.current_number -= 10**self.position
            self.current_number = max(self.current_number, self.start)
            self.refresh()

    def left(self, state):
        ''' switches position to left '''
        if self.is_finished(): return
        if state:
            self.position = min(self.position+1, self.position_count)
            self.refresh()

    def right(self, state):
        ''' switches position to right '''
        if self.is_finished(): return
        if state:
            self.position = max(self.position-1, 0)
            self.refresh()

    def enter(self, state):
        ''' selects the current_number and submits it '''
        if state:
            self.screen.clear()
            formatted_str = ("{:0" + str(self.position_count) + "}").format(int(self.current_number))
            self.screen.draw.text((0,0), formatted_str, font=self.courier_new) # no black background anymore after submit
            self.screen.update()

            self.result = self.current_number

class BooleanInput:
    '''
        The BooleanInput class handles user interaction with the aim to get a boolean return value
        Works the same way as NumberInput except choosing between "ja" and "nein"
    '''

    def __init__(self, message, screen):
        self.current_value = True
        self.result = None

        self.btn = ev3.Button()
        self.btn.on_left = self.change
        self.btn.on_right = self.change
        self.btn.on_enter = self.enter

        self.screen = screen
        self.message = message
        self.courier_new_bool = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Courier_New.ttf', 40)
        size = min(floor(178*5/3/len(message)), floor(128/2*6/5))
        self.courier_new_text = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Courier_New.ttf', size)

    def reset(self):
        self.result = None
        self.current_value = True

    def is_finished(self):
        return self.result is not None

    def get_bool(self):
        if not self.is_finished():
            self.refresh()
        while not self.is_finished():
            time.sleep(0.01)    # fixes a double event from the button
            self.btn.process()
        return self.result

    def refresh(self):
        self.screen.clear()
        self.screen.draw.text((0,0), self.message, font=self.courier_new_text)
        if self.current_value:
            self.screen.draw.text((0,64), "Ja", font=self.courier_new_bool)
        else:
            self.screen.draw.text((0,64), "Nein", font=self.courier_new_bool)
        self.screen.update()

    def change(self, state):
        if state and not self.is_finished():
            self.current_value = not self.current_value
            self.refresh()

    def enter(self, state):
        if state:
            self.result = self.current_value



if __name__ == '__main__':
    # for debugging only
    interaction = Interaction()
    print(interaction.get_number())