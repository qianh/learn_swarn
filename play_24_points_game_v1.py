import json
import random

from swarm import Swarm, Agent
from typing import List

from game_helpers import get_random_card_list, get_cached_expressions


client = Swarm()


instruction_template_dict = {
    "GameDealer": """
        Generate 4 random natural numbers between 1 and 13, include 1 and 13. Just return 4 numbers in an array, don't include other content. The returned array should not be repeated with the following arrays:
        {old_arrays}
        """,
    "MathProdigy": """You are a helpful agent. """,
    "GameJudger": """You are a helpful agent. """,
    "GamePlayer": """You are a helpful agent. """,
}


user_prompt_template_dict = {
    "GameDealer": """generate an array""",
    "MathProdigy": """
        What's the 24 points expression of {last_cards_posted} ? 
        If the result is 'expression not found', just return 'expression not found'. 
        If the result is an arithmetic expression, just return the expression itself and do not add anything else.
        """,
    "GameJudger": """
        Cards posted is '{last_cards_posted}', what's the check result of {expression} ? Just return the check result itself such as 'Correct' or 'Wrong', and do not add anything else such as 'The check result is ...'. 
    """,
    "GamePlayer": """
        What's the human reply of {last_cards_posted} ? Just return the human reply itself and do not add anything else, such as 'The human reply ...'. If the input is an arithmetic expression, return it as is.
    """,
}


def get_instruction(context_variables):
    global instruction_template_dict

    agent_name = context_variables["agent_name"]
    instruction_template = instruction_template_dict[agent_name]
    instruction = instruction_template

    if agent_name == "GameDealer":
        last_cards_posted = context_variables["old_arrays"]
        instruction = instruction_template.format(old_arrays=last_cards_posted)
   
    return instruction


def get_user_prompt(context_variables):
    global user_prompt_template_dict

    agent_name = context_variables["agent_name"]
    user_prompt_template = user_prompt_template_dict[agent_name]
    user_prompt = user_prompt_template

    if agent_name == "MathProdigy":
        last_cards_posted = context_variables["last_cards_posted"]
        user_prompt = user_prompt_template.format(last_cards_posted=last_cards_posted)

    elif agent_name == "GameJudger":
        expression = context_variables["expression"]
        last_cards_posted = context_variables["last_cards_posted"]
        user_prompt = user_prompt_template.format(expression=expression,last_cards_posted=last_cards_posted)

    elif agent_name == "GamePlayer":
        last_cards_posted = context_variables["last_cards_posted"]
        user_prompt = user_prompt_template.format(last_cards_posted=last_cards_posted)

    return user_prompt


def get_24_points_expression_func(last_cards_posted: str) -> str:
    """Resolve the expression of 24 points game, return an arithmetic expression.

    Keyword arguments:
      last_cards_posted: an array of 4 integers between 1 to 13.
    """

    point_list = json.loads(last_cards_posted)  
    if len(point_list) == 0:
        return "expression not found"

    expressions = get_cached_expressions(point_list)
    
    result = "expression not found"
    if len(expressions) > 0:
        random_idx = random.randint(0, len(expressions)-1)
        expression = f"'{expressions[random_idx]}'".replace("'", "")
        print(f"The resolved 24 points expression is '{expression}'")
        return expression
    
    return "expression not found"


def check_24_points_expression_func(expression: str, last_cards_posted: str) -> str:
    """Check if the result of an arithmetic expression is equal 24, return 'Correct' or 'Wrong'.

    Keyword arguments:
      expression: an arithmetic expression
      last_cards_posted: an array of 4 integers between 1 to 13.
    """

    result = eval(expression.replace("'", ""))
    if abs(result - 24) < 0.001:
        return "Correct"

    return "Wrong"


def get_human_reply_func(last_cards_posted: str) -> str:
    """Get a human reply for an an array formated as string. The replay should be 'deal', 'help', 'exit' or an an arithmetic expression.

    Keyword arguments:
      last_cards_posted: an array of 4 integers between 1 to 13.
    """

    PROMPT_TEMPLATE: str = """
    Cards the dealer just posted: {content}
    Please give an expression for the four operations that results in 24.
    Type 'help' if you feel it's difficult.
    Type 'deal' if you want the dealer to deal cards again.
    Type 'exit' if you want to exit this game, type 'exit'.
    """

    point_list = json.loads(last_cards_posted)
    card_list = get_random_card_list(point_list)
    cards_content = f"{{'card_list': {card_list}, 'point_list': {point_list}}}"

    prompt = PROMPT_TEMPLATE.format(content=cards_content)
    human_reply = input(prompt)

    return {"human_reply": f"{human_reply}"}


agent_bill = Agent(
    name="GameDealer",
    instructions=get_instruction,
    model="qwen-max-latest",
    functions=[],
)


agent_gauss = Agent(
    name="MathProdigy",
    instructions=get_instruction,
    model="qwen-max-latest",
    functions=[get_24_points_expression_func],
)


agent_peter = Agent(
    name="GameJudger",
    instructions=get_instruction,
    model="qwen-max-latest",
    functions=[check_24_points_expression_func],
)


agent_david = Agent(
    name="GamePlayer",
    instructions=get_instruction,
    model="qwen-max-latest",
    functions=[get_human_reply_func],
)


def deal_cards(old_arrays: List[int]) -> str:
    global client, agent_bill

    print(f"used old_arrays is :{old_arrays}")
    context_var_dict = {
        "agent_name":"GameDealer", 
        "old_arrays": f"{old_arrays}"
    }
    response = client.run(
        agent=agent_bill,
        messages=[{"role": "user", "content": get_user_prompt(context_var_dict)}],
        context_variables=context_var_dict
    )

    cards_posted = response.messages[-1]["content"]
    print(cards_posted)
    return cards_posted


def machine_give_expression(last_cards_posted: str) -> str:
    global client, agent_gauss

    context_var_dict = {
        "agent_name":"MathProdigy", 
        "last_cards_posted": f"{last_cards_posted}"
    }
    response = client.run(
        agent=agent_gauss,
        messages=[{"role": "user", "content": get_user_prompt(context_var_dict)}],
        context_variables=context_var_dict
    )

    expression = response.messages[-1]["content"]
    print(expression)
    return expression


def check_expression(expression: str, last_cards_posted: str) -> str:
    global client, agent_peter

    context_var_dict = {
        "agent_name":"GameJudger", 
        "expression": f"{expression}",
        "last_cards_posted": f"{last_cards_posted}"
    }
    response = client.run(
        agent=agent_peter,
        messages=[{"role": "user", "content": get_user_prompt(context_var_dict)}],
        context_variables=context_var_dict
    )

    check_result = response.messages[-1]["content"]
    print(check_result)
    return check_result


def get_human_reply(last_cards_posted: str) -> str:
    global client, agent_david

    context_var_dict = {
        "agent_name":"GamePlayer", 
        "last_cards_posted": f"{last_cards_posted}"
    }
    response = client.run(
        agent=agent_david,
        messages=[{"role": "user", "content": get_user_prompt(context_var_dict)}],
        context_variables=context_var_dict
    )

    human_reply = response.messages[-1]["content"]
    print(human_reply)
    return human_reply


def main_func():
    
    old_arrays = []
    last_cards_posted = deal_cards(old_arrays)

    while True:
        human_reply = get_human_reply(last_cards_posted)

        if human_reply == "deal":
            old_arrays.append(json.loads(last_cards_posted))
            last_cards_posted = deal_cards(old_arrays)
            continue
        elif human_reply == "help":
            expression = machine_give_expression(last_cards_posted)
        elif human_reply == "exit":
            print("Bye bye, have a good day!")
            break
        else:
            expression = human_reply
        
        if expression != "expression not found":
            check_result = check_expression(expression, last_cards_posted)
        else:
            check_result = "Correct"
                        
        if check_result == "Correct":
            old_arrays.append(json.loads(last_cards_posted))
            last_cards_posted = deal_cards(old_arrays)


if __name__ == "__main__":
    main_func()

