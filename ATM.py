class ATM:
    def __init__(self):
        self.logged_in = False
        self.current_user = None
        self.accounts = {
            1234: {'name': 'John', 'surname': 'Doe', 'gender': 'Mr', 'balance': 1000},
            5678: {'name': 'Jane', 'surname': 'Smith', 'gender': 'Ms', 'balance': 500},
            # Add more dummy accounts as needed
        }

    def login(self, pin):
        if pin in self.accounts:
            self.logged_in = True
            self.current_user = self.accounts[pin]
            return f"Welcome {self.current_user['gender']} {self.current_user['surname']}!"
        else:
            return "Invalid PIN. Please try again."

    def logout(self):
        self.logged_in = False
        self.current_user = None

    def check_balance(self):
        if self.logged_in:
            return f"Your balance is: ${self.current_user['balance']}"
        else:
            return "Please login first."

    def deposit(self, amount):
        if self.logged_in:
            self.current_user['balance'] += amount
            return f"Deposited ${amount}. Current balance is ${self.current_user['balance']}"
        else:
            return "Please login first."

    def withdraw(self, amount):
        if self.logged_in:
            if self.current_user['balance'] >= amount:
                self.current_user['balance'] -= amount
                return f"Withdrew ${amount}. Current balance is ${self.current_user['balance']}"
            else:
                return "Insufficient funds."
        else:
            return "Please login first."

def main():
    atm = ATM()

    while True:
        if not atm.logged_in:
            print("\n==== Welcome to the ATM ====")
            pin = input("Please enter your PIN: ")
            message = atm.login(int(pin))
            print(message)
            if not atm.logged_in:
                continue  # Go back to the beginning of the loop if login failed

        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Logout")

        try:
            choice = int(input("Enter your choice (1-4): "))
        except ValueError:
            print("Invalid input. Please enter a number (1-4).")
            continue

        if choice == 1:
            print(atm.check_balance())

        elif choice == 2:
            amount = float(input("Enter deposit amount: $"))
            print(atm.deposit(amount))

        elif choice == 3:
            amount = float(input("Enter withdrawal amount: $"))
            print(atm.withdraw(amount))

        elif choice == 4:
            atm.logout()
            print("Logged out. Thank you for using the ATM. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
