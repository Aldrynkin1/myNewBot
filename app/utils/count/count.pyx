import random
from libc.math cimport fabs

cdef class User:
    cdef public long long tg_id
    cdef public double answer

    def __init__(self, long long tg_id, answer):
        self.tg_id = tg_id
        self.answer = float(answer)


cdef double count_res(int a, int b, char symbol):
    if symbol == b'+'[0]:
        return a + b
    elif symbol == b'-'[0]:
        return a - b
    elif symbol == b'*'[0]:
        return a * b
    else:
        return (<double>a / b) if b != 0 else 0.0

cdef long long winner(double correct_res, User u1, User u2):
    cdef double answer1 = fabs(correct_res - u1.answer)
    cdef double answer2 = fabs(correct_res - u2.answer)

    if answer1 < answer2:
        return u1.tg_id
    elif answer1 > answer2:
        return u2.tg_id
    else:
        return 0


def generate_question():
    cdef int first_num = random.randint(1, 10000)
    cdef int second_num = random.randint(1, 10000)
    symbols = [b'+', b'-', b'/', b'*']
    cdef bytes chosen_symbol = random.choice(symbols)

    cdef double correct_res = count_res(first_num, second_num, chosen_symbol[0])

    return {
        "Пример: ": f'{first_num} {chosen_symbol.decode()} {second_num}',
        "Правильный ответ: ": correct_res,
    }

def check_winner(double correct_res, long long user1_tg_id, double user1_ans, long long user2_tg_id, double user2_ans):
    cdef User u1 = User(tg_id=user1_tg_id, answer=user1_ans)
    cdef User u2 = User(tg_id=user2_tg_id, answer=user2_ans)

    cdef winner_id = winner(correct_res, u1, u2)

    return {
        "Победитель: ": winner_id
    }