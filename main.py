import os
import pickle
import time
from decimal import Decimal, ROUND_DOWN
from getpass import getpass
import platform
from pathlib import Path

class User:
    def __init__(self, name, tax, hourly_wage, password):
        self.name = name
        self.tax = tax / 100  # Convert percentage to decimal
        self.hourly_wage = hourly_wage
        self.password = password
        self.monthly_pay = {}

    def add_monthly_pay(self, month, pay):
        self.monthly_pay[month] = pay

def get_settings_file_path():
    documents_dir = Path.home() / "Documents"
    settings_dir = documents_dir / "Pay Calculator Settings"
    os.makedirs(settings_dir, exist_ok=True)
    settings_file = settings_dir / "settings.pkl"
    return str(settings_file)

def save_users(users):
    settings_file = get_settings_file_path()
    with open(settings_file, 'wb') as f:
        pickle.dump(users, f)

def load_users():
    settings_file = get_settings_file_path()
    if os.path.exists(settings_file):
        with open(settings_file, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def delete_user(users, username):
    if username in users:
        print("\nDeleting settings...")
        time.sleep(1)
        del users[username]
        save_users(users)
        print("Settings deleted.")

def expected_pay(user, hours_worked):
    return user.hourly_wage * hours_worked * (1 - user.tax)

def compare_pay(user, actual_pay, hours_worked):
    expected = expected_pay(user, hours_worked)
    difference = Decimal(actual_pay - expected).quantize(Decimal('.01'), rounding=ROUND_DOWN)  
    press_enter()
    clear_screen()
    print("Difference Breakdown:")
    print(f"\nExpected pay: {user.hourly_wage} * {hours_worked} hours * (1 - {user.tax})")
    print(f"Expected pay: {user.hourly_wage} * {hours_worked} hours * {1 - user.tax}")
    print(f"Expected pay: {user.hourly_wage * hours_worked * (1 - user.tax)}")
    print(f"\nActual pay: {actual_pay}")
    print(f"\nDifference: {expected} - {actual_pay}")
    print(f"Difference: {difference}")
    press_enter()

def adjust_settings(user):
    print("\nEnter the new values. Leave blank to keep the current value.")
    while True:
        try:
            tax = input(f"\nCurrent tax rate is {user.tax * 100}%. Enter new tax rate (as a percentage): ")
            if not tax:
                break
            tax = float(tax) / 100
            if tax < 0:
                raise ValueError("Tax rate cannot be negative.")
            user.tax = tax
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    while True:
        try:
            hourly_wage = input(f"\nCurrent hourly wage is {user.hourly_wage}. Enter new hourly wage: ")
            if not hourly_wage:
                break
            hourly_wage = float(hourly_wage)
            if hourly_wage < 0:
                raise ValueError("Hourly wage cannot be negative.")
            user.hourly_wage = hourly_wage
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    return user

def settings_area(users, username):
    user = users.get(username)
    if user:
        clear_screen()
        print(f"\nName: {user.name}")
        print(f"Tax: {user.tax * 100}%") 
        print(f"Hourly Wage: {user.hourly_wage}")
        print(f"Monthly pays: {user.monthly_pay}")
        action = input(
            "\nType DELETE to remove settings or ADJUST to adjust settings or ENTER to continue: ").strip().lower()
        if action == 'delete':
            confirm = input("\nAre you sure you want to delete your settings? (yes/no): ")
            if confirm.lower() == 'yes':
                delete_user(users, username)
                user = None
        elif action == 'adjust':
            user = adjust_settings(user)
    else:
        print("No settings found.")
    return user

def actual_pay_area(users, username):
    user = users.get(username)
    if user:
        clear_screen()
        while True:
            try:
                actual_pay = float(input("\nEnter your actual pay: "))
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        month = input("\nEnter the month (in format 'YYYY-MM'): ")

        while True:
            try:
                hours_worked = int(input("Enter your hours worked (for the month): "))
                if hours_worked < 0:
                    raise ValueError("Hours worked cannot be negative.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

        user.add_monthly_pay(month, actual_pay)
        compare_pay(user, actual_pay, hours_worked)
        save_users(users)

def login(users):
            while True:
                clear_screen()
                print("\n1. Login")
                print("2. Register")
                print("3. Exit")
                option = input("\nSelect an option (1-3): ")
                if option == '1':
                    username = input("\nEnter your username: ")
                    password = getpass("Enter your password: ")
                    if username in users and users[username].password == password:
                        return username
                    else:
                        print("Invalid username or password.")
                elif option == '2':
                    while True:
                        username = input("\nEnter a new username: ")
                        if username in users:
                            print("Username already taken.")
                        else:
                            break

                    password = getpass("Enter a new password: ")
                    name = input("Enter your name: ")

                    while True:
                        try:
                            tax = float(input("Enter your tax rate (as a percentage): "))
                            break
                        except ValueError:
                            print("Invalid input. Please enter a valid number.")

                    while True:
                        try:
                            hourly_wage = float(input("Enter your hourly wage: "))
                            break
                        except ValueError:
                            print("Invalid input. Please enter a valid number.")

                    user = User(name, tax, hourly_wage, password)
                    users[username] = user
                    save_users(users)
                    return username
                elif option == '3':
                    return None
                else:
                    print("Invalid option. Please enter a number between 1 and 3.")


def clear_screen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
    print("\033[1m")  # Bold style
    print("------------------------------")
    print("\033[91mPAY CALCULATOR\033[0m")  # Red color
    print("\033[1m------------------------------\033[0m")  # Reset styles
    print(
        "\n\033[2mDisclaimer: This script is for educational purposes only. The calculations provided are approximate and may not reflect actual pay amounts. Your payslip may differ from the results obtained using this script.\033[0m")
    print("------------------------------\n")

def main():
    users = load_users()
    while True:
        username = login(users)
        if username is None:
            break
        while True:
            clear_screen()
            print("\n\033[1m1. Enter Actual Pay and Calculate Difference\033[0m")  # Bold style
            print("\033[1m2. Go to Settings\033[0m")  # Bold style
            print("\033[1m3. Logout\033[0m")  # Bold style
            option = input("\nSelect an option (1-3): ")
            if option == '1':
                actual_pay_area(users, username)
            elif option == '2':
                settings_area(users, username)
            elif option == '3':
                break
            else:
                print("Invalid option. Please enter a number between 1 and 3.")
            transition_effect()

def transition_effect():
    if platform.system() == 'Windows':
        time.sleep(0.5)
    else:
        os.system('sleep 0.5')

def press_enter():
    input("\nPress Enter to continue...")
    clear_screen()

if __name__ == "__main__":
    main()
