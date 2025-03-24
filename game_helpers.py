import json
import random
import os


from calc_24_points import calc_all_expressions


# helper functions here

cached_expressions = {}

def get_cached_expressions(point_list: list):
    global cached_expressions
    
    point_list.sort()
    key = json.dumps(point_list)
    
    if key in cached_expressions:
        return cached_expressions[key]
    
    expressions = calc_all_expressions(point_list)
    cached_expressions[key] = expressions
    return expressions


def get_random_suit() -> list:
    suit_list = ['Clubs', 'Hearts', 'Spades', 'Diamonds']
    random.shuffle(suit_list)
    return suit_list


def get_rank_str(point):
    if point == 1:
        rank = "A"
    elif point == 11:
        rank = "J"
    elif point == 12:
        rank = "Q"
    elif point == 13:
        rank = "K"
    else:
        rank = str(point)
    return rank


def get_recent_point_list(context):
    for item in context:
        if item.role == "user" and '"point_list":' in item.content:
            card_list = item.content
    point_list = json.loads(card_list)["point_list"]
    return point_list


def get_random_card_list(number_list):
    suit_list = get_random_suit()
    
    cards_list = []
    for i in range(4):
        
        point = number_list[i]
        rank = get_rank_str(point)
            
        cards_list.append({"suit": suit_list[i], "rank": rank, "point": point})

    return cards_list
