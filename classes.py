import numpy as np
import pygame
from typing import Callable, Tuple


def to_int(sig_hex_str : str) -> int:
    unsig_num = int(sig_hex_str[1:],16)
    if sig_hex_str[0] == 1:
        return -unsig_num
    return unsig_num

class Genome:
    def __init__(self,gene : str,length : int):
        self._gene = gene
        self._length = length

    def get_gene(self) -> str:
        return self._gene

    def get_length(self) -> int:
        return self._length

world_display_size : int = 1000

class World:
    def __init__(self,corner : tuple[int,int],size : int,scale_factor : int):
        if size * scale_factor > world_display_size:
            raise RuntimeError("Required world display bigger than allocated")
        else:
            self._corner = corner
            self._size = size
            self._scale_factor = scale_factor

    def get_corner(self) -> tuple[int,int]:
        return self._corner

    def get_size(self) -> int:
        return self._size

    def get_scale_factor(self) -> int:
        return self._scale_factor


class IAction:
    pass

class Move(IAction):
    def __init__(self,angle:float):
        self._angle = angle % (2 * np.pi)

    def get_angle(self) -> float:
        return self._angle

    def set_angle(self,angle:float):
        self._angle = angle % (2 * np.pi)

class Eat(IAction):
    def __init__(self,pos : tuple[float,float]):
        self.food_loc = pos


def square_distance(pos1 : tuple[float,float],pos2 : tuple[float,float]) -> float:
    return ((pos1[0] - pos2[0]) ** 2) + ((pos1[1] - pos2[1]) ** 2)

def dir_order(pos1 : tuple[float,float],pos2 : tuple[float,float]) -> int:
    angle = np.arctan2(pos2[1] - pos1[1],pos2[0] - pos1[0])
    if angle < 0:
        angle = angle + 2 * np.pi
    return int(((8 * angle) % (2 * np.pi)) / (2 * np.pi))

class Organism:
    def __init__(self,gene : Genome,world : World):
        # Setting the initial state of the organism
        self._pos : tuple[float,float] = (0,0)
        self.gene = gene
        self._food : int = 0
        self._world = world
        self.LastAction : IAction = IAction()
        # Setting the default neural network to the identity function
        self.NN : Callable[[list[float]],list[float]] = lambda x : x

        # Getting colours for each channel
        r = int(to_int(self.gene.get_gene()[len(self.gene.get_gene())-9:len(self.gene.get_gene())-6])/2 + 128)
        g = int(to_int(self.gene.get_gene()[len(self.gene.get_gene())-3:])/2 + 128)
        b = int(to_int(self.gene.get_gene()[len(self.gene.get_gene())-6:len(self.gene.get_gene())-3])/2 + 128)
        self.colour: Tuple[int,int,int] = (r,g,b)
        #Initialisaing a sprite object
        self.sprite= pygame.Rect(((0,0),(20,20)))




    def set_position(self,pos : tuple[float,float]):
        pos_as_arr = [pos[0],pos[1]]
        clipped_arr = np.clip(pos_as_arr,0,((self._world.get_size() * self._world.get_scale_factor()) - 1) / self._world.get_scale_factor())
        self._pos = (clipped_arr[0],clipped_arr[1])


    def get_position(self) -> tuple[float,float]:
        return self._pos

    def change_food(self,delta:int):
        if delta >= 0:
            self._food += delta

    def get_food(self) -> int:
        return self._food

    def gen_action(self,visibility_scaling:float,organisms : 'list[Organism]',foods : list[tuple[float,float]]):
        visibility = to_int(self.gene.get_gene()[len(self.gene.get_gene())-9:len(self.gene.get_gene())-6])
        closest_dist_sq_in_dir = [np.inf for _ in range(8)]
        closest_in_dir : list[Organism | int]= [0 for _ in range(8)]
        food_locations = [(-1.,-1.) for _ in range(8)]
        for organism in organisms:
            if organism != self:
                distance = square_distance(self.get_position(),organism.get_position())
                if distance<= (visibility * visibility_scaling) ** 2:
                    direction = dir_order(self.get_position(),organism.get_position())
                    if distance < closest_dist_sq_in_dir[direction]:
                        closest_in_dir[direction] = organism
                        closest_dist_sq_in_dir[direction] = distance
        for food in foods:
            distance = square_distance(self.get_position(),food)
            if distance<= (visibility * visibility_scaling) ** 2:
                direction = dir_order(self.get_position(),food)
                if distance < closest_dist_sq_in_dir[direction]:
                    closest_in_dir[direction] = 1
                    closest_dist_sq_in_dir[direction] = distance
                    food_locations[direction] = food

        nn_vec = []
        for i in range(8):
            if closest_in_dir[i] == 0:
                nn_vec.append(0)
                nn_vec.append(0)
            elif closest_in_dir[i] == 1:
                nn_vec.append(0)
                nn_vec.append(100-np.sqrt(closest_dist_sq_in_dir[i]))
            else:
                nn_vec.append(100-np.sqrt(closest_dist_sq_in_dir[i]))
                nn_vec.append(0)
        out = self.NN(nn_vec)
        if max(out) in out[:8]:
            self.LastAction = Move(out.index(max(out))/8 * 2 * np.pi)
        elif max(out) == out[8]:
            min_dist = np.inf
            min_index = -1
            for i in range(8):
                if type(closest_in_dir[i]) == type(Organism):
                    if closest_dist_sq_in_dir[i] < min_dist and closest_dist_sq_in_dir[i] < closest_dist_sq_in_dir[i] < ((visibility * visibility_scaling) ** 2)/25:
                        min_dist = closest_dist_sq_in_dir[i]
                        min_index = i
            if min_index != -1:
                self.LastAction = Kill(closest_in_dir[min_index])
            else:
                self.LastAction = IAction()
        elif max(out) == out[9]:
            min_dist = np.inf

            min_index = -1
            for i in range(8):
                if type(closest_in_dir[i]) == int:
                    if closest_in_dir[i] == 1:
                        if closest_dist_sq_in_dir[i]  < min_dist and closest_dist_sq_in_dir[i] < ((visibility * visibility_scaling) ** 2)/25:
                            min_dist = closest_dist_sq_in_dir[i]
                            min_index = i
            if min_index != -1:
                self.LastAction = Eat(food_locations[min_index])
            else:
                self.LastAction = IAction()



class Kill(IAction):
    def __init__(self,organism : Organism):
        self.killed_organism = organism



