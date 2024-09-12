from classes import *
import numpy as np
import random

world_organisms : list[Organism] = []
world_foods : list[tuple[float,float]] = []
speed_scaling : float = 1
weight_scaling : float = 0
mutation_rate : float = 0.05

def gen_genome(gene_length:int,val_range:int) -> Genome:
    genome = ""
    for i in range(gene_length):
        weight = random.randint(-val_range,val_range)
        if weight < 0:
            genome += "1" + hex(weight)[3:].zfill(len(hex(val_range)[2:]))
        else:
            genome += "0" + hex(weight)[2:].zfill(len(hex(val_range)[2:]))
    return Genome(genome,len(hex(val_range)[2:]) + 1)

def to_int(sig_hex_str : str) -> int:
    unsig_num = int(sig_hex_str[1:],16)
    if sig_hex_str[0] == "1":
        return -unsig_num
    return unsig_num

def gen_nn(gene : Genome, layer_count : int, layer_sizes : list[int], activation : Callable[[float],float]) -> Callable[
    [list[float]],list[float]]:
    if layer_count == 0 or layer_sizes == []:
        raise RuntimeError("Dimensions too low")
    weights_str = []
    for i in range(int(len(gene.get_gene())/gene.get_length())):
        weight = ""
        for j in range(gene.get_length()):
            weight += gene.get_gene()[i * 3 + j]
        weights_str.append(weight)

    weights = list(map(to_int,weights_str))
    matrices = []
    biases = []

    curr_weight = 0
    for i in range(layer_count - 1):
        matrices.append(np.reshape(weights[curr_weight:layer_sizes[i] * layer_sizes[i+1] + curr_weight],(layer_sizes[i+1],layer_sizes[i])))
        curr_weight = layer_sizes[i] * layer_sizes[i+1] + curr_weight
        biases.append(weights[curr_weight:layer_sizes[i+1] + curr_weight])
        curr_weight = layer_sizes[i+1] + curr_weight

    def nn(vec : list[float]) -> list[float]:
        for transform in range(len(matrices)):
            vec = list(map(activation,matrices[transform] @ vec + biases[transform]))
        return vec

    return nn

def gen_positions(world:World):
    positions = set()
    for organism in world_organisms:
        pos = (random.random() * world.get_size(),random.random() * world.get_size())
        attempts = 0
        while pos in positions:
            if attempts > 10:
                return
            pos = (random.random() * world.get_size(), random.random() * world.get_size())
            attempts += 1

        organism.set_position(pos)
        positions.add(pos)

def gen_food(food_count:int,world:World):
    positions = set()
    for i in range(food_count):
        pos = (random.random() * world.get_size(),random.random() * world.get_size())
        attempts = 0
        while pos in positions:
            if attempts > 10:
                return
            pos = (random.random() * world.get_size(), random.random() * world.get_size())
            attempts += 1
        world_foods.append(pos)

def translate_organism(organism:Organism):
    speed = to_int(organism.gene.get_gene()[len(organism.gene.get_gene())-3:])
    if isinstance(organism.LastAction,Move):
        x = speed * speed_scaling * np.cos(organism.LastAction.get_angle())
        y = speed * speed_scaling * np.sin(organism.LastAction.get_angle())
        organism.set_position((organism.get_position()[0] + x,organism.get_position()[1] + y))

def process_action(organism:Organism):
    if isinstance(organism.LastAction,Eat):
        world_foods.remove(organism.LastAction.food_loc)
        organism.change_food(1)
    if isinstance(organism.LastAction,Kill):
        if to_int(organism.gene.get_gene()[len(organism.gene.get_gene())-6:len(organism.gene.get_gene())-3]) > to_int(organism.LastAction.killed_organism.gene.get_gene()[len(organism.LastAction.killed_organism.gene.get_gene())-6:len(organism.LastAction.killed_organism.gene.get_gene())-3]):
            world_organisms.remove(organism.LastAction.killed_organism)
            organism.change_food(2)

def fitness(organisms:list[Organism],threshold:int) -> dict[Organism,int]:
    breedables : dict[Organism,int] = {}
    for organism in organisms:
        if organism.get_food() > threshold + to_int(organism.gene.get_gene()[len(organism.gene.get_gene())-6:len(organism.gene.get_gene())-3]) * weight_scaling:
            breedables[organism] = organism.get_food()
    return breedables

def sample(organisms:dict[Organism,int]) -> Organism:
    max_val = sum(organisms.values())
    sample_num = random.randrange(max_val)
    count = 0
    for organism,food in organisms.items():
        if sample_num < count + food:
            return organism
        else :
            count += food

def cross(organism1:Organism,organism2:Organism,world:World) -> Organism:
    gene1 = organism1.gene
    gene2 = organism2.gene

    weights_str1 = []
    for i in range(int(len(gene1.get_gene()) / gene1.get_length())):
        weight = ""
        for j in range(gene1.get_length()):
            weight += gene1.get_gene()[i + j]
        weights_str1.append(weight)

    weights1 = list(map(to_int, weights_str1))

    weights_str2 = []
    for i in range(int(len(gene2.get_gene()) / gene2.get_length())):
        weight = ""
        for j in range(gene2.get_length()):
            weight += gene2.get_gene()[i + j]
        weights_str1.append(weight)

    weights2 = list(map(to_int, weights_str2))

    new_weights = []
    for i in range(len(weights1)):
        to_add = (weights1[i] + weights2[i]) / 2
        if random.random() < mutation_rate:
            if random.random() < 0.5:
                to_add -= 10
            else:
                to_add += 10
        new_weights.append(to_add)

    new_weights = np.clip(new_weights,-(16 ** gene1.get_length()),16 ** gene1.get_length())

    genome = ""
    for weight in new_weights:
        if weight < 0:
            genome += "1" + hex(weight)[2:].zfill(gene1.get_length() - 1)
        else:
            genome += "0" + hex(weight)[2:].zfill(gene1.get_length() - 1)

    return Organism(Genome(genome,gene1.get_length()),world)

test_world = World((0,0),100,10)
test_organism1 = Organism(Genome("0ff000",3),test_world)
test_organism2 = Organism(Genome("0ff000",3),test_world)

test_breedables = {test_organism1 : 10,test_organism2 : 5}



input()