from controller import Controller
from interaction import Interaction

'''
    to create a series of measurements for 0%, 5%, ..., 95%
    to make a new model
'''

interaction = Interaction()
controller = Controller([0])

controller.open_trigger_gate() # alternative to controller.roll(0)
for p in range(5, 100, 5):
    # displays next number and waits for confirmation
    # xx% -> 0.xx
    p = interaction.get_number(1, 95, default=p)/100
    controller.roll(p)