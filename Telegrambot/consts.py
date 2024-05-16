from enum import Enum


class Keys(Enum):
    HISTORY = "Посмотреть решенные задачи"
    STATISTICS = "Статистика"
    NEXT_OLYMP = "Ближайшие олимпиады"
    SEARCH = "Поиск задачи"
    RANDOM_TASK = "Случайная задача"
    YES = 'Да'
    NO = 'Нет'


class Reply:
    class Error(Enum):
        UNHANDLED = "Непредвиденная ошибка"
        INVALID_GRADE = "Некорректный номер класса, повторите ввод"
        USER_TASKS_EMPTY = "У вас нет решённых задач"
        SEVERAL_USERS_FOUND = "Найдено более одного пользователя"
        TASK_NOT_FOUND = "Задача не найдена"

    class Success(Enum):
        ASK_GRADE = "Теперь ты, в каком ты классе?"
        SAVE_USER = "Спасибо, мы вас запомнили"
        EXISTS_USER = "Вы уже зарегистрированы"
        ALL_SOLVED = "Поздравляю, вы решили все задачи"
