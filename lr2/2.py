import re



def is_valid_name(name):
    if not name or name[0].islower():
        return False
    if not re.match("^[A-Za-zа-яёА-ЯЁ]+$", name):
        return False
    return True


def main():
    error_file = 'error.txt'
    try:
        while True:
            name = input("Пожалуйста, введите ваше имя: ").strip()
            if is_valid_name(name):
                print(f"Привет, {name}!")
            else:
                with open(error_file, 'a') as ef:
                    ef.write(f"Ошибка: недопустимое имя '{name}'\n")
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
