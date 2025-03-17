from functools import partial
from typing import Tuple, List, Callable, Optional
import pygame
import pygame_chart
from pygame import SurfaceType

figures : List[Tuple[str,pygame_chart.pygame_chart.Figure,List[int],List[int]]]= [] #Collecting figures and their Data
max_figures = 6
screen : SurfaceType
in_add_menu = False
#colours = {}
def remove_graph():
    if len(figures) != 0:
        figures.remove(figures[-1])
def add_menu():
    global in_add_menu
    gen_buttons()
    in_add_menu = True

#Local buttons collection
add_remove_buttons : dict[Tuple[Tuple[int,int],Tuple[int,int]],Tuple[Callable[[],None],str,Optional[str]]] = {
    ((1590,10),(40,40)) : (add_menu,"Positive","+"),
    ((1630,10),(40,40)) : (remove_graph,"Negative","-")
}



datas : dict[str,Tuple[List[int],List[int]]] = {}
menu_background = pygame.Rect((1920/2 - 250,1080/2 - 350),(500,700))
data_buttons : dict[Tuple[Tuple[int,int],Tuple[int,int]],Tuple[Callable[[],None],str,Optional[str]]] = {}


def add_figure(name:str,data_x:List[int],data_y:List[int]) -> None: # Adds an entry to the dictionary with references to
    print(name)
    global in_add_menu
    fig : pygame_chart.pygame_chart.Figure
    if len(figures) == 0:
        fig = pygame_chart.Figure(screen,1030,10,600,200)
    elif len(figures) < max_figures:
        prev_y = figures[-1][1].y
        fig = pygame_chart.Figure(screen,1030,prev_y + 210,600,200)
    else:
        return
    figures.append((name,fig,data_x,data_y))
    in_add_menu = False

def draw_graph(graph : Tuple[str,pygame_chart.pygame_chart.Figure,List[int],List[int]]) -> None: # Takes a graph from the
    graph[1].line(graph[0],graph[-2],graph[-1])
    graph[1].draw()

def render_graphs() -> None:
    for figure in figures:
        draw_graph(figure)

def fix_data(x : List[int],y : List[int]) -> Tuple[List[int],List[int]]:#Adjust Shape of graph to ensure straight lines
    new_x = []
    new_y = []
    for i in range(len(x)):
        new_x.append(x[i])
        new_y.append(y[i])

        if i != len(x) - 1:
            new_x.append(x[i + 1])
            new_y.append(y[i])
    return new_x,new_y

#Adds data to the data log
def commit_data(name:str,x:List[int],y:List[int]):
    datas[name] = fix_data(x,y)

commit_data("Test" ,[0,1,2,3,4],[0,1,1,0,5])
commit_data("Test2" ,[0,1,2,3,4],[0,1,5,3,5])

def gen_buttons():
    x = menu_background.left + 10
    y = menu_background.top + 10
    gen_add_fig = lambda a : add_figure(a,datas[a][0],datas[a][1])
    for key in datas.keys():
        data_buttons[((x,y),(160,40))] = (partial(gen_add_fig,key),"Config",key)
        print(datas[key][1])
        y += 50
    print(data_buttons)

def update_button_pos():
    add_x, add_y = list(add_remove_buttons.keys())[0][0]
    sub_x, sub_y = list(add_remove_buttons.keys())[1][0]
    add_remove_buttons[((add_x, 10 + len(figures) * 210), (40, 40))] = add_remove_buttons.pop(((add_x, add_y), (40, 40)))
    add_remove_buttons[((sub_x, 10 + len(figures) * 210), (40, 40))] = add_remove_buttons.pop(((sub_x, sub_y), (40, 40)))