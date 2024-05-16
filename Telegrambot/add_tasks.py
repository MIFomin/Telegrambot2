import db_control

db_control.execute(
    """
    CREATE TABLE IF NOT EXISTS Tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        answer TEXT,
        level INTEGER,
        hint1 TEXT,
        hint2 TEXT,
        hint3 TEXT
    );
    """
)

db_control.execute(
    """
    INSERT INTO Tasks (task, answer, level, hint1, hint2, hint3) VALUES ('Задача 1', 'Ответ 1', 1, 'Подсказка 1', 'Подсказка 2', 'Подсказка 3'), ('Задача 2', 'Ответ 2', 2, 'Подсказка 4', 'Подсказка 5', 'Подсказка 6');
    """
)
