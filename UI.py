from typing import Optional
from functools import partial
import pygame

from Evolving_Organisms import translate_organism, process_action
from classes import *
import Evolving_Organisms

from tkinter.filedialog import askopenfilename
from tkinter import colorchooser

# Initialising window size and
pygame.init()
screen = pygame.display.set_mode((1920,1080))
clock = pygame.time.Clock()
running = True
isPaused = False # If true running of sim is suspended
settingsMenu = False # Weather the settings menu is up
# Initialising a world object
world = World((10,10),100,10)

#Initialise Fonts
button_font = pygame.font.SysFont(pygame.font.get_default_font(), 30)

# Creating a colour Dictionary
colours = {"Background" : "#e8cc76",
           "Foreground" : "#f8efd3",
           "Positive" : "#00ff00",
           "Negative" : "#ff0000",
           "Config" : "#0000ff",
           "btnText" : "#ffffff",
           "settings":"#888888",
           "menu_background":"#888888"}
# Creating a Rectangle to act as the foreground
foreground = pygame.Rect(world.get_corner(),
                         (world.get_size() * world.get_scale_factor(),
                          world.get_size() * world.get_scale_factor()))

#Initialising organism register
organisms : list[Organism] = [Organism(Genome("0001FF001",3),world)]
organisms[0].set_position((50,50))
organisms[0].LastAction = Move(-np.pi/4)


#Functions mapped to the click of a button
def pause():
    global isPaused
    isPaused = True
def unpause():
    global isPaused
    isPaused = False

#Functions for Presets configurations
def config1():
    Evolving_Organisms.weight_scaling = 0
    Evolving_Organisms.speed_scaling = 1
    Evolving_Organisms.mutation_rate = 0.05
def config2():
    Evolving_Organisms.weight_scaling = 0
    Evolving_Organisms.speed_scaling = 0.5
    Evolving_Organisms.mutation_rate = 0.05
def config3():
    Evolving_Organisms.weight_scaling = 0
    Evolving_Organisms.speed_scaling = 1
    Evolving_Organisms.mutation_rate = 0.1
def config4():
    Evolving_Organisms.weight_scaling = 3
    Evolving_Organisms.speed_scaling = 1
    Evolving_Organisms.mutation_rate = 0.05

def toggle_setting():
    global settingsMenu
    settingsMenu = not settingsMenu
    print(settingsMenu)

def change_colour(colour_class = "Background"):
    colour = colorchooser.askcolor()
    if colour[1] is not None:
        colours[colour_class] = colour[1]
    else:
        while colour[1] is None:
            colour = colorchooser.askcolor()
    colours[colour_class] = colour[1]

def change_button_font():
    global button_font
    path = askopenfilename()
    while not ("ttf" in path or "otf" in path):
        path = askopenfilename()
    button_font = pygame.font.Font(path,30)




#Initialising Food Register
foods : list[Tuple[float,float]] = [(25,25,),
                                    (75,75),
                                    (25,75)]
# Collections of locations of buttons and their associated data
global_buttons : dict[Tuple[Tuple[int,int],Tuple[int,int]],Tuple[Callable[None,None],str,Optional[str]]] = {
    ((int(world.get_size() * world.get_scale_factor() / 2)  ,foreground.bottom + 10),(40,40)) : (pause,"Negative",None),
    ((int(world.get_size() * world.get_scale_factor() / 2) - 40,foreground.bottom + 10),(40,40)) : (unpause,"Positive",None),
    ((int(world.get_size() * world.get_scale_factor() / 2) - 130,foreground.bottom + 10),(80,40)) : (config2,"Config","Config 2"),
    ((int(world.get_size() * world.get_scale_factor() / 2) - 220,foreground.bottom + 10),(80,40)) : (config1,"Config","Config 1"),
    ((int(world.get_size() * world.get_scale_factor() / 2) + 50,foreground.bottom + 10),(80,40)) : (config3,"Config","Config 3"),
    ((int(world.get_size() * world.get_scale_factor() / 2) + 140,foreground.bottom + 10),(80,40)) : (config4,"Config","Config 4"),
    ((world.get_corner()[0],foreground.bottom + 10),(40,40)) : (toggle_setting,"settings",None),
}




#Function to redner world entities
def render_entities():
    for organism in organisms:
        #Transfrom world position to screen space
        organism.sprite.topleft = (float(world.get_corner()[0] + float(world.get_scale_factor()) * organism.get_position()[0]),
                                   float(world.get_corner()[1] + float(world.get_scale_factor()) * organism.get_position()[1]))

        pygame.draw.rect(screen,organism.colour,organism.sprite)

    for food in foods:
        #Transfrom world position to screen space
        screen_pos = (float(world.get_corner()[0] + float(world.get_scale_factor()) * food[0]),
                                   float(world.get_corner()[1] + float(world.get_scale_factor()) * food[1]))

        pygame.draw.circle(screen,"green",screen_pos,10)

def draw_buttons(buttons):
    for button in buttons.keys():
        pygame.draw.rect(screen,colours[buttons[button][1]],pygame.Rect(button[0],button[1]))
        if buttons[button][2] is not None:
            img = button_font.render(buttons[button][2], True, colours["btnText"])
            screen.blit(img,button[0])

# Fetches and executes the Function associated with the button
def exec_button(pos : Tuple[int,int],buttons):
    for button in buttons.keys():
        if pygame.Rect(button[0],button[1]).collidepoint(pos):
            buttons[button][0]()

# Defining Settings Objects
menu_background = pygame.Rect((screen.get_size()[0]/2 - 250,screen.get_size()[1]/2 - 350),(500,700))
colour_offset = 0
colours_shown = 5
setting_buttons : dict[Tuple[Tuple[int,int],Tuple[int,int]],Tuple[Callable[None,None],str,Optional[str]]] = {
    ((menu_background.left + 10,menu_background.top + 10),(40,40)):(change_button_font,"Config","font")
}
colour_button_pos = [((menu_background.left + 10,menu_background.top + 60 + 50 * n),(160,40)) for n in range(5)]

def set_buttons(buttons,elements,keys):
    to_add = zip(keys,elements)
    for i in to_add:
        buttons[i[0]] = i[1]

set_buttons(setting_buttons,[(partial(change_colour,list(colours.keys())[i]),"Config",list(colours.keys())[i]) for i in range(colours_shown)],colour_button_pos)

while running:
    # Checking if game running is over
    # and if so exit the game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if not settingsMenu:
                exec_button(mouse_pos,global_buttons)
            else:
                exec_button(mouse_pos,setting_buttons)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if settingsMenu:
                    colour_offset += 1
                    set_buttons(setting_buttons,
                                [(partial(change_colour, list(colours.keys())[colour_offset + i]), "Config", list(colours.keys())[colour_offset + i])
                                 for i in range(colours_shown)], colour_button_pos)


    screen.fill(colours["Background"])# Draw a color to the Screen
    pygame.draw.rect(screen,colours["Foreground"],foreground)# Drawing rect

    draw_buttons(global_buttons)
    render_entities()

    if not isPaused:
        for _organism in organisms:
            translate_organism(_organism)
            process_action(_organism)

    if settingsMenu:
        pygame.draw.rect(screen,colours["menu_background"],menu_background)
        draw_buttons(setting_buttons)


    pygame.display.flip()# Update the frame
    clock.tick(60)# Set frame rate to 60

pygame.quit()
