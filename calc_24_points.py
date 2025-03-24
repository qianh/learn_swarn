import argparse
import copy
import os
import re

from itertools import permutations, product


def get_input() -> list:
    parser = argparse.ArgumentParser(description="Calculate 24 points")
    parser.add_argument('numbers', nargs=4, type=int)
    args = parser.parse_args()
    return args.numbers


def insert_parentheses(expression: str, pos_array: list) -> list:
    expr_list = []
    
    # print(f"{expression}--{pos_array}")
    
    char_list = list(expression)
    pos = 0
    char_list.insert(pos, '(')
    pos = pos_array[1][0]+pos_array[1][1] + 1
    char_list.insert(pos, ')')
    pos = pos_array[1][1]+pos_array[2][0]
    char_list.insert(pos, '(')
    char_list.append(')')
    expr = "".join(char_list)
    expr_list.append(expr)

    char_list = list(expression)
    pos = pos_array[1][0]
    char_list.insert(pos, '(')
    pos = pos_array[2][0] + pos_array[2][1] + 1
    char_list.insert(pos, ')')
    expr = "".join(char_list)
    expr_list.append(expr)

    char_list = list(expression)
    pos = 0
    char_list.insert(pos, '(')
    pos = pos_array[2][0] + pos_array[2][1] + 1
    char_list.insert(pos, ')')
    expr = "".join(char_list)
    expr_list.append(expr)

    char_list = list(expression)
    pos = pos_array[1][0]
    char_list.insert(pos, '(')
    char_list.append(')')
    expr = "".join(char_list)
    expr_list.append(expr)

    char_list = list(expression)
    pos = 0
    char_list.insert(pos, '(')
    pos += 1
    char_list.insert(pos, '(')
    pos = pos_array[1][0] + pos_array[1][1] + 2
    char_list.insert(pos, ')')
    pos = pos_array[2][0] + pos_array[2][1] + 3
    char_list.insert(pos, ')')
    expr = "".join(char_list)
    expr_list.append(expr)

    char_list = list(expression)
    pos = 0
    char_list.insert(pos, '(')
    pos = pos_array[1][0] + 1
    char_list.insert(pos, '(')
    pos = pos_array[2][0] + pos_array[2][1] + 2
    char_list.insert(pos, ')')
    pos += 1
    char_list.insert(pos, ')')
    expr = "".join(char_list)
    expr_list.append(expr)

    char_list = list(expression)
    pos = pos_array[1][0]
    char_list.insert(pos, '(')
    pos += 1
    char_list.insert(pos, '(')
    pos = pos_array[2][0] + pos_array[2][1] + 2
    char_list.insert(pos, ')')
    char_list.append(')')
    expr = "".join(char_list)
    expr_list.append(expr)

    char_list = list(expression)
    pos = pos_array[1][0]
    char_list.insert(pos, '(')
    pos = pos_array[2][0] + 1
    char_list.insert(pos, '(')
    char_list.append(')')
    char_list.append(')')
    expr = "".join(char_list)
    expr_list.append(expr)

    return expr_list


def generate_expressions(nums, ops):
    expr_list = []
    if len(nums) != 4 or len(ops) != 3:
        return []

    pos_array = [[],[],[],[]]
    
    pos = 0
    expr = f""
    for i in range(4):
        num = nums[i]
        num_len = len(str(num))
        
        if i == 0:
            op = ops[i]
            expr = f"{num} {op}"
            pos_array[0].append(0)
            pos_array[0].append(num_len)
            pos += num_len + 2
        elif i < 3:
            op = ops[i]
            expr = f"{expr} {num} {op}"
            pos_array[i].append(pos+1)
            pos_array[i].append(num_len)
            pos += num_len + 3
        else:
            op = ""
            expr = f"{expr} {num}"
            pos_array[i].append(pos+1)
            pos_array[i].append(num_len)
            pos += num_len + 1
     
    expr_list.append(expr)
    expr_list.extend(insert_parentheses(expr, pos_array))
    return expr_list


def calc_24_points(numbers):
    operations = ['+', '-', '*', '/']
    expressions = set()
    for perm in permutations(numbers):
        for ops in product(operations, repeat=3):
            for expr in generate_expressions(perm, ops):
                try:
                    expr_result = float(eval(expr.replace(' ', '')))
                    if abs(24 - expr_result) < 0.0001:
                        expressions.add(expr)
                except ZeroDivisionError as e:
                    continue
    
    return expressions


def get_new_expressions(expression, start_idx, end_idx):
    dup_expression = None

    if start_idx > -1 and end_idx > start_idx:
        char_list = list(expression)
        char_list[start_idx] = ''
        char_list[end_idx] = ''
        new_expression = "".join(char_list)

        try:
            expr_result1 = float(eval(expression.replace(' ', '')))
            expr_result2 = float(eval(new_expression.replace(' ', '')))
            if abs(expr_result1 - expr_result2) < 0.0001:
                dup_expression = new_expression
        except ZeroDivisionError as e:
            dup_expression = None

    return dup_expression


def remove_parentheses(expression: str) -> str:
    expr_len = len(expression)
    start_idx = -1
    end_idx = -1

    for i in range(expr_len):
        if expression[i] == '(':
            start_idx = i
        
        if expression[i] == ')':
            if end_idx == -1:
                end_idx = i
            elif end_idx < start_idx:
                end_idx = i
                break

    new_expression = get_new_expressions(expression, start_idx, end_idx)
    if new_expression is not None:
        return new_expression

    start_idx = -1
    end_idx = -1
    for i in range(expr_len):
        if expression[i] == '(':
            start_idx = i
        
        if expression[i] == ')':
            if end_idx == -1:
                end_idx = i
                break

    new_expression = get_new_expressions(expression, start_idx, end_idx)
    if new_expression is not None:
        return new_expression
    
    return copy.copy(expression)


def simplify_expression(expression):
    if '(' not in expression:
        return expression
    
    expr = copy.copy(expression)
    while True:
        new_expr = remove_parentheses(expr)
        if new_expr == expr:
            break
        else:
            expr = new_expr
    
    return new_expr


def count_chars(string, char):
    pattern = rf"\{char}"
    matches = re.findall(pattern, string)
    return len(matches)


def count_numbers(string):
    pattern = r'\d+'
    matches = re.findall(pattern, string)
    return len(matches)


def get_sub_expr(expression):
    start_idx = expression.find('(') + 1
    end_idx = expression.find(')')

    sub_expr = expression[start_idx:end_idx]
    return sub_expr


def create_dup_expr_list(list_size: int) -> list:
    dup_expr_list = []
    for i in range(list_size):
        dup_expr_list.append([False, ""])
    return dup_expr_list


def print_dup_expressions(dup_expr_list, call_tag):
    list_size = len(dup_expr_list)
    
    if dup_expr_list[0][0] and dup_expr_list[1][0]:
        dup_expressions = f"'{dup_expr_list[0][1]}', '{dup_expr_list[1][1]}'"
        for i in range(list_size-2):
            flag = dup_expr_list[2+i][0]
            expr = dup_expr_list[2+i][1]
            if flag:
                dup_expressions = f"{dup_expressions}, '{expr}'"
            else:
                break
                
        print(f"{call_tag} find dup expressions: {dup_expressions}")


def find_dup_expressions(expressions: list, numbers: list) -> None:
    dup_expr_list = []

    list_size = 20
        
    for i in range(len(numbers)):
        num1 = numbers[i]
        other_numbers = copy.copy(numbers)
        del other_numbers[i]
        for num2 in other_numbers:
            dup_expr_list = create_dup_expr_list(list_size)
            for expr in expressions:
                divide_num = count_chars(expr, '/')
                if divide_num == 0:
                    if f"{num1} * {num2}" in expr:
                        dup_expr_list[0] = [True, expr]
                    if f"{num2} * {num1}" in expr:
                        dup_expr_list[1] = [True, expr]
                        
            print_dup_expressions(dup_expr_list, "case 1") 

        dup_expr_list = create_dup_expr_list(list_size)
        for expr in expressions:
            multiply_num = count_chars(expr, '*')
            divide_num = count_chars(expr, '/')
            parentheses_num = count_chars(expr, '(')

            if multiply_num == 1 and parentheses_num == 1 and divide_num == 0:
                sub_expr = get_sub_expr(expr)
                sub_expr_numbers = count_numbers(sub_expr)
                if sub_expr_numbers == 2:
                    continue
                
                if f"{num1} * ({sub_expr})" in expr or f"({sub_expr}) * {num1}" in expr:
                    for i in range(list_size):
                        if not dup_expr_list[i][0]:
                            dup_expr_list[i] = [True, expr]
                            break                        

        print_dup_expressions(dup_expr_list, "case 2") 

    dup_expr_list = create_dup_expr_list(list_size)

    for expr in expressions:
        multiply_num = count_chars(expr, '*')
        divide_num = count_chars(expr, '/')

        if multiply_num == 0 and divide_num == 0:
            for i in range(list_size):
                if not dup_expr_list[i][0]:
                    dup_expr_list[i] = [True, expr]
                    break                        

    print_dup_expressions(dup_expr_list, "case 3") 


def calc_all_expressions(numbers):
    expressions = calc_24_points(numbers)
    # print(f"{expressions}")
    # print(len(expressions))    
    simplified_expressions = [simplify_expression(expr) for expr in expressions]
    simplified_expressions = list(set(simplified_expressions))
    # print(f"{simplified_expressions}")
    # print(len(simplified_expressions))

    return simplified_expressions


def main():
    numbers = list(get_input())
    
    simplified_expressions = calc_all_expressions(numbers)    
    find_dup_expressions(simplified_expressions, numbers)



if __name__ == "__main__":
    main()
