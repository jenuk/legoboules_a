import ev3dev.ev3 as ev3
import time
import sys
import model_dicts
from interaction import Interaction

class Controller:
    '''
        The Controller Class is the central class of this lego boules project. It coordinates the input parameters and controls the output of the robot. The robot uses two motors for output:
         -- trigger:    opens and closes the gate of the cage holding the ball (motor A)
         -- lift:       pulls the cage up on the ramp and let's it down again  (motor B)
    '''

    RAMP_ROTATION_LENGTH = 1300         # length of ramp in degree of rotation of lift motor (use only 95% of that)
    TRIGGER_ROTATION_DEGREES = 95       # rotation needed to open trigger
    LIFT_SPEED_UP = 300                 # speed of lift motor pulling up
    LIFT_SPEED_DOWN = 450               # speed of lift motor pushing down
    TRIGGER_SPEED = 450                 # speed of trigger motor
    LIFT_DOWN_OFFSET_PERCENTAGE = 0.975 # offset fixes bug letting the cage not as far down as pulling it up

    def __init__(self, dist_dict):
        '''
            Initializes a new Controller with a distance dictinary

            Argument:
                dist_dict   dictionary which matches distances in cm with degrees
        '''

        self.dist_dict = dist_dict
        self.start, self.end = min(dist_dict), max(dist_dict)   # sets the range interval that can be reached
        self.interaction = Interaction()

        self.trigger = ev3.LargeMotor("outA")
        self.lift = ev3.LargeMotor("outB")

    def dist_to_rot(self, dist):
        '''
            Converts distances to degrees

            Argument:
                dist    distance in cm or in percent [0,1)
        '''

        if 0 <= dist < 1:
            ''' distance is already given in percent '''
            percentage = dist
        else:
            ''' distance needs to be converted into percent '''
            dist = min(max(int(dist), self.start), self.end)    # avoids distances outside of the range interval
            percentage = (self.dist_dict[dist]/100)

        return Controller.RAMP_ROTATION_LENGTH * percentage

    def roll(self, dist):
        '''
            Rolls the ball to a given distance

            Argument:
                dist    distance in cm or in procent [0,1)
        '''

        lift_rotation_degrees = self.dist_to_rot(dist)

        self.lift.run_to_rel_pos(position_sp=lift_rotation_degrees, speed_sp=Controller.LIFT_SPEED_UP, stop_action="brake")
        self.lift.wait_while("running")

        self.open_trigger_gate()

        self.lift.run_to_rel_pos(position_sp=-lift_rotation_degrees*Controller.LIFT_DOWN_OFFSET_PERCENTAGE, speed_sp=Controller.LIFT_SPEED_DOWN, stop_action="brake")
        self.lift.wait_while("running")

    def open_trigger_gate(self):
        ''' Opens the gate of the cage to let the ball roll down '''
        self.trigger.run_to_rel_pos(position_sp=Controller.TRIGGER_ROTATION_DEGREES, speed_sp=Controller.TRIGGER_SPEED, stop_action="brake")
        time.sleep(2)
        self.trigger.run_to_rel_pos(position_sp=-Controller.TRIGGER_ROTATION_DEGREES, speed_sp=Controller.TRIGGER_SPEED, stop_action="brake")
        time.sleep(2)

    def main(self):
        '''
            Runs the program in a loop. At the beginning it prints the instuction once and then repeatedly asks for a distance, rolls the ball for this distance and asks for the next round.
        '''
        play_again = True
        self.interaction.print("Bitte gib", "eine Weite", "in cm an")
        time.sleep(4)
        while play_again:
            time.sleep(1)
            dist = self.interaction.get_number(self.start, self.end)
            self.roll(dist)
            play_again = self.interaction.get_bool("Nochmal?")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # for debugging only: first command line argument is the model type, default is cubic splines
        if sys.argv[1] == "pol_lin":
            dist_dict = model_dicts.pol_lin
        elif sys.argv[1] == "pol_cubic":
            dist_dict = model_dicts.pol_cubic
        elif sys.argv[1] == "spline_lin":
            dist_dict = model_dicts.spline_lin
        else:
            dist_dict = model_dicts.spline_cubic
    else:
        dist_dict = model_dicts.spline_cubic

    controller = Controller(dist_dict)

    if len(sys.argv) > 2:
        # for debugging only: second command line argument is a distance either in cm or in percent [0,1)
        dist = max(0, min(float(sys.argv[2]), 1))
        controller.roll(dist)
    else:
        # without command line arguments the program runs in normal mode
        controller.main()