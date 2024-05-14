# Simple ATM Simulation

This is a basic ATM simulation program implemented in Python. It allows users to log in with a PIN and perform operations such as checking balance, depositing funds, and withdrawing funds.

## Features

- **Login System**: Users must enter a valid PIN to access their account.
- **Operations**:
  - Check Balance: View the current account balance.
  - Deposit: Add funds to the account.
  - Withdraw: Withdraw funds from the account (if sufficient balance).
  - Logout: Exit the ATM system.

## Getting Started

1. **Prerequisites**:

   - Python 3 installed on your system.

2. **Setup**:

   - Download or clone the `ATM.py` script.

3. **Running the Program**:

   - Open a terminal or command prompt.
   - Navigate to the directory containing `ATM.py`.
   - Run the program using the following command:
     ```
     python3 ATM.py
     ```

4. **Using the ATM**:
   - Upon running the program, you will be prompted to enter a PIN.
   - Use one of the following dummy PINs for testing:
     - `1234` (John Doe)
     - `5678` (Jane Smith)
   - Once logged in, you can choose from the available options:
     - Enter `1` to check balance.
     - Enter `2` to deposit funds.
     - Enter `3` to withdraw funds.
     - Enter `4` to logout and exit.

## Sample Usage

```
==== Welcome to the ATM ====
Please enter your PIN: 1234
Welcome Mr Doe!
1. Check Balance
2. Deposit
3. Withdraw
4. Logout
Enter your choice (1-4): 1
Your balance is: $1000

1. Check Balance
2. Deposit
3. Withdraw
4. Logout
Enter your choice (1-4): 2
Enter deposit amount: $500
Deposited $500. Current balance is $1500

1. Check Balance
2. Deposit
3. Withdraw
4. Logout
Enter your choice (1-4): 3
Enter withdrawal amount: $300
Withdrew $300. Current balance is $1200

1. Check Balance
2. Deposit
3. Withdraw
4. Logout
Enter your choice (1-4): 4
Logged out. Thank you for using the ATM. Goodbye!
```

## Notes

- This is a simplified simulation for educational purposes.
- Dummy account details (names, balances) are provided within the program.
- Feel free to extend or modify the code for additional features or improvements.

---
