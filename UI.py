import json
from functools import partial
from tkinter import colorchooser
from tkinter.filedialog import askopenfilename
from typing import Optional

from Evolving_Organisms import *
import Evolving_Organisms
import charts
from charts import *
from classes import *

# Initialising window size and
pygame.init()
screen = pygame.display.set_mode((1920,1080))
charts.screen = screen
clock = pygame.time.Clock()
running = True
isPaused = False # If true running of sim is suspended
settingsMenu = False # Weather the settings menu is up
# Initialising a world object
world = World((10,10),98,10)
organisms_count = 300

#Initialise Fonts
button_font = pygame.font.SysFont(pygame.font.get_default_font(), 30)

def save_colours(): #Saves colours to a json file
    json_col = json.dumps(colours, indent=4)
    with open("colours.json","w") as file:
        file.write(json_col)


# Creating a colour Dictionary
colours = {"Background" : "#e8cc76",
           "Foreground" : "#f8efd3",
           "Positive" : "#00ff00",
           "Negative" : "#ff0000",
           "Config" : "#0000ff",
           "btnText" : "#ffffff",
           "settings":"#888888",
           "menu_background":"#888888"}

#Loading Settings
try:
    with open("colours.json","r") as f:
        colours = json.loads(f.read())
finally:
    save_colours()
charts.colours = colours

# Creating a Rectangle to act as the foreground
foreground = pygame.Rect(world.get_corner(),
                         (world.get_size() * world.get_scale_factor() + 20,
                          world.get_size() * world.get_scale_factor() + 20))

#Initialising organism register
#gene = Genome(("001001" + ("000000" * 7))+
#                (("000000" * 1) + "001001" + ("000000" * 6))+
#                (("000000" * 2) + "001001" + ("000000" * 5))+
#                (("000000" * 3) + "001001" + ("000000" * 4))+
#                (("000000" * 4) + "001001" + ("000000" * 3))+
#                (("000000" * 5) + "001001" + ("000000" * 2))+
#                (("000000" * 6) + "001001" + ("000000" * 1))+
#                (("000000" * 7) + "001001")
#              + ("000" * 154) + "0FF000001",3)
#gene = Genome("000" * 169 + "050" + "000000",3)
#organisms : list[Organism] = [Organism(gene,world)]
#organisms[0].set_position((50,50))
#NN = gen_nn(gene,2,[16,10],lambda x :x)
#organisms[0].NN = NN
organisms : list[Organism] = Evolving_Organisms.world_organisms

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
foods : list[Tuple[float,float]] = [(100,75)]
Evolving_Organisms.world_foods = foods
#print(Evolving_Organisms.world_foods)
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
            print(buttons[button])
            buttons[button][0]()

# Defining Settings Objects
menu_background = pygame.Rect((screen.get_size()[0]/2 - 250,screen.get_size()[1]/2 - 350),(500,700))
colour_offset = 0
colours_shown = 8


#Secondary button collection
setting_buttons : dict[Tuple[Tuple[int,int],Tuple[int,int]],Tuple[Callable[None,None],str,Optional[str]]] = {
    ((menu_background.left + 10,menu_background.top + 10),(160,40)):(change_button_font,"Config","font"),
    ((menu_background.left + 10,menu_background.top + 60),(160,40)):(save_colours,"Config","Save"),
    ((world.get_corner()[0],foreground.bottom + 10),(40,40)) : (toggle_setting,"settings",None),
}
colour_button_pos = [((menu_background.left + 10,menu_background.top + 110 + 50 * n),(160,40)) for n in range(colours_shown)]

def set_buttons(buttons,elements,keys):
    to_add = zip(keys,elements)
    for i in to_add:
        buttons[i[0]] = i[1]

set_buttons(setting_buttons,[(partial(change_colour,list(colours.keys())[i]),"Config",list(colours.keys())[i]) for i in range(colours_shown)],colour_button_pos)

#Setting variables
iters_per_gen = 100
itercount = 0
isFirstGenAndIter = True
eat_act_data = []
kill_act_data = []
move_act_data = []
survivals_data = []
avg_eat_data = []
avg_kill_data = []
avg_move_data = []
gen_data = []


eat_act_count = 0
kill_act_count = 0
move_act_count = 0
survivals_count = 0

while running:
    # Checking if game running is over
    # and if so exit the game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if settingsMenu:
                exec_button(mouse_pos,setting_buttons)
            elif charts.in_add_menu:
                exec_button(mouse_pos,data_buttons)
            else:
                exec_button(mouse_pos,global_buttons)
                exec_button(mouse_pos, add_remove_buttons)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if settingsMenu:
                    colour_offset += 1
                    set_buttons(setting_buttons,
                                [(partial(change_colour, list(colours.keys())[(colour_offset + i) % len(colours)]), "Config", list(colours.keys())[(colour_offset + i) % len(colours)])
                                 for i in range(colours_shown)], colour_button_pos)
            elif event.key == pygame.K_UP:
                if settingsMenu:
                    colour_offset -= 1
                    set_buttons(setting_buttons,
                                [(partial(change_colour, list(colours.keys())[(colour_offset + i) % len(colours)]), "Config", list(colours.keys())[(colour_offset + i) % len(colours)])
                                 for i in range(colours_shown)], colour_button_pos)


    screen.fill(colours["Background"])# Draw a color to the Screen
    pygame.draw.rect(screen,colours["Foreground"],foreground)# Drawing rect

    if itercount == 0:
        if isFirstGenAndIter:
            for i in range(organisms_count):
                gene = gen_genome(173,256)
                NN = gen_nn(gene,2,[16,10],lambda x: np.abs(x))
                new_org = Organism(gene,world)
                new_org.NN = NN
                organisms.append(new_org)
            isFirstGenAndIter = False
            gen_data.append(1)
        else:
            fit_organisms = fitness(organisms, 1)
            print(fit_organisms)
            survivals_count = len(fit_organisms)
            organisms.clear()
            foods.clear()
            for i in range(organisms_count):
                mother = sample(fit_organisms)
                father = sample(fit_organisms)
                child = cross(mother,father,world)
                child.NN = gen_nn(child.gene,2,[16,10],lambda x: np.abs(x))
                organisms.append(child)
            #Data collection
            eat_act_data.append(eat_act_count)
            kill_act_data.append(kill_act_count)
            move_act_data.append(move_act_count)
            survivals_data.append(survivals_count)
            avg_eat_data.append(int(eat_act_count/iters_per_gen))
            avg_kill_data.append(int(kill_act_count/iters_per_gen))
            avg_move_data.append(int(move_act_count/iters_per_gen))
            commit_data("Eats",eat_act_data,gen_data)
            commit_data("Kills",kill_act_data,gen_data)
            commit_data("Moves",move_act_data,gen_data)
            commit_data("Survivals",survivals_data,gen_data)
            commit_data("Avg Eats",avg_eat_data,gen_data)
            commit_data("Avg Kills",avg_kill_data,gen_data)
            commit_data("Avg Moves",avg_move_data,gen_data)

        gen_positions(world)
        gen_food(50,world)
        gen_data.append(gen_data[-1] + 1)
        eat_act_count = 0
        kill_act_count = 0
        move_act_count = 0
        survivals_count = 0




    #Drawing everything
    draw_buttons(global_buttons)
    draw_buttons(add_remove_buttons)
    render_entities()
    render_graphs()
    if not isPaused:
        for _organism in organisms:
            _organism.gen_action(visibility_scale,organisms, foods)
            if isinstance(_organism.LastAction,Move):
                move_act_count += 1
            elif isinstance(_organism.LastAction,Kill):
                kill_act_count += 1
            elif isinstance(_organism.LastAction,Kill):
                eat_act_count += 1
            translate_organism(_organism)
            process_action(_organism)
        itercount = (itercount + 1) % iters_per_gen

    if settingsMenu:
        pygame.draw.rect(screen,colours["menu_background"],menu_background)
        draw_buttons(setting_buttons)
    if charts.in_add_menu:
        pygame.draw.rect(screen, colours["menu_background"], menu_background)
        draw_buttons(charts.data_buttons)

    #organisms[0].gen_action(visibility_scale,organisms, foods)
    #print(organisms[0].LastAction)
    #process_action(organisms[0])
    ##translate_organism(organisms[0])
    #charts.correct_all_data()

    charts.update_button_pos()
    pygame.display.flip()# Update the frame
    clock.tick(60)# Set frame rate to 60
pygame.quit()
