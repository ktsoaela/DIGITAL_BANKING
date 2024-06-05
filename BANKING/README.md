# ATM Application

This project is a simple ATM (Automated Teller Machine) application implemented using Django and Django REST Framework. It allows users to perform basic banking operations like depositing money, withdrawing money, and checking account balances through a RESTful API.

## Features

- **User Account Management**

  - Create and manage user accounts.
  - Change PIN for user accounts.

- **Banking Operations**

  - Deposit money into an account.
  - Withdraw money from an account.
  - Check account balance.

- **Transaction History**

  - View transaction history.
  - Generate mini statements and detailed statements.

- **Additional Features**
  - Bill payments.
  - Mobile recharge services.
  - Prepaid electricity reload.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ktsoaela/DIGITAL_BANKING.git
   ```

2. Navigate into the project directory:

   ```bash
   cd atm
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. Access the application at [http://localhost:8000/](http://localhost:8000/).

## Usage

- **API Endpoints**:

  - Deposit money: `/api/deposit/`
  - Withdraw money: `/api/withdraw/`
  - Account balance: `/api/balance/`
  - User account management: `/api/accounts/`

- **Web Interface**:
  - Access the deposit page: [http://localhost:8000/deposit/](http://localhost:8000/deposit/)
  - Access the withdraw page: [http://localhost:8000/withdraw/](http://localhost:8000/withdraw/)

## Testing

Run tests using the following command:

```bash
python manage.py test atm
```

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the GPLv3 license: - see the [LICENSE](LICENSE) file for details.
