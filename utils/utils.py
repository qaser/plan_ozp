def word_conjugate(number: int, words: list) -> str:
    last_digit = number % 10
    last_two_digit = number % 100  # для проверки 11...14
    if last_digit == 1 and last_two_digit != 11:
        return f'{words[0]}'  # заявка
    if 1 < last_digit < 5 and last_two_digit not in range(11, 15):
        return f'{words[1]}'  # заявки
    return f'{words[2]}'  # заявок
