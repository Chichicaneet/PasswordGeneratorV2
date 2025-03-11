import secrets
import string
from PySide6.QtWidgets import QMessageBox

def generate_password(length_input, numbers_check, letters_check, symbols_check, numbers_count_input, letters_count_input, symbols_count_input, language, parent):
    """
    Генерирует пароль на основе введенных параметров.
    """
    try:
        length = int(length_input.text())
        if length <= 0:
            raise ValueError("Длина пароля должна быть больше 0.")
    except ValueError:
        QMessageBox.critical(parent, "Ошибка", "Введите корректную длину пароля (целое число больше 0)." if language == "ru" else "Please enter a valid password length (integer greater than 0).")
        return ""

    use_numbers = numbers_check.isChecked()
    use_letters = letters_check.isChecked()
    use_symbols = symbols_check.isChecked()

    if not (use_numbers or use_letters or use_symbols):
        QMessageBox.critical(parent, "Ошибка", "Выберите хотя бы один тип символов." if language == "ru" else "Please select at least one type of symbols.")
        return ""

    # Получаем количество цифр, букв и символов из полей ввода
    numbers_count = numbers_count_input.text()
    letters_count = letters_count_input.text()
    symbols_count = symbols_count_input.text()

    # Если поля пустые, количество будет задано автоматически
    numbers_count = int(numbers_count) if numbers_count else None
    letters_count = int(letters_count) if letters_count else None
    symbols_count = int(symbols_count) if symbols_count else None

    # Генерация пароля
    password = generate_password_with_counts(length, use_numbers, use_letters, use_symbols, numbers_count, letters_count, symbols_count, parent)
    return password

def generate_password_with_counts(length, use_numbers, use_letters, use_symbols, numbers_count=None, letters_count=None, symbols_count=None, parent=None):
    """
    Генерирует пароль с учетом заданного количества цифр, букв и символов.
    """
    characters = []
    
    # Определяем количество каждого типа символов
    specified_counts = {
        "numbers": numbers_count if numbers_count is not None else 0,
        "letters": letters_count if letters_count is not None else 0,
        "symbols": symbols_count if symbols_count is not None else 0
    }
    
    used_types = {
        "numbers": use_numbers,
        "letters": use_letters,
        "symbols": use_symbols
    }
    
    # Вычисляем количество явно заданных символов
    total_specified = sum(specified_counts.values())
    
    # Проверяем, не превышает ли сумма длину пароля
    if total_specified > length:
        QMessageBox.critical(parent, "Ошибка", "Сумма заданных количеств символов превышает длину пароля.")
        return ""
    
    # Определяем оставшееся количество символов, которые нужно распределить
    remaining_length = length - total_specified
    
    # Собираем категории, где количество не задано
    unspecified_types = [t for t, v in used_types.items() if v and specified_counts[t] == 0]
    
    # Если есть нераспределенные символы, равномерно распределяем их между активными категориями
    if unspecified_types and remaining_length > 0:
        add_per_type = remaining_length // len(unspecified_types)
        extra = remaining_length % len(unspecified_types)  # Оставшиеся символы, если не делится ровно

        for i, t in enumerate(unspecified_types):
            specified_counts[t] = add_per_type + (1 if i < extra else 0)  # Распределяем остатки
    
    # Наполняем список символов
    if used_types["numbers"]:
        characters.extend(secrets.choice(string.digits) for _ in range(specified_counts["numbers"]))
    if used_types["letters"]:
        characters.extend(secrets.choice(string.ascii_letters) for _ in range(specified_counts["letters"]))
    if used_types["symbols"]:
        characters.extend(secrets.choice(string.punctuation) for _ in range(specified_counts["symbols"]))

    # Перемешиваем символы для случайного порядка
    secrets.SystemRandom().shuffle(characters)
    
    return ''.join(characters)