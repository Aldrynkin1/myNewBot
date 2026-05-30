import random
from libc.stdlib cimport abs

cdef class User:
    cdef public str name
    cdef public int answer

    def __init__(self, str name, int answer):
        self.name = name
        self.answer = answer


cdef double count_res(int a, int b, char symbol):
    if symbol == b'+':
        return a + b
    elif symbol == b'-':
        return a - b
    elif symbol == b'*':
        return a * b
    else:
        return (<double>a / b) if b != 0 else 0.0

cdef int winner(double correct_res, User u1, User u2):
    cdef double answer1 = abs(correct_res - u1.answer)
    cdef double answer2 = abs(correct_res - u2.answer)

    if answer1 < answer2:
        return u1.tg_id
    elif answer1 > answer2:
        return u2.tg_id
    else:
        return 0

def count_game(int user1_name, int user1_ans, int user2_name, int user2_ans):
    cdef int first_num = random.randint(1, 10000)
    cdef int second_num = random.randint(1, 10000)
    cdef list symbols = [b'+', b'-', b'/', b'*']
    cdef char chosen_symbol = random.choice(symbols)

    cdef double correct_res = count_res(first_num, second_num, chosen_symbol)

    cdef User u1 = User(name=user1_name, answer=user1_ans)
    cdef User u2 = User(name=user2_name, answer=user2_ans)

    cdef winner_id = winner(correct_res, u1, u2)

    return {
        "Пример: ": f'{first_num} {chosen_symbol.decode()} {second_num}',
        "Правильный ответ: ": correct_res,
        "Победитель: ": winner_id,
    }