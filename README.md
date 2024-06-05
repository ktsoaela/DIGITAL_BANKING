# ATM Application

This project is a simple ATM (Automated Teller Machine) application implemented using Django and Django REST Framework for the backend, and React for the frontend. It allows users to perform basic banking operations like depositing money, withdrawing money, and checking account balances through a RESTful API.

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
   cd DIGITAL_BANKING
   ```

3. Set up environment variables:

   - **Django Backend**: Create a `.env` file in the `BANKING` directory with the following content:

     ```
     SECRET_KEY='your_secret_key_here'
     DEBUG=True
     DB_ENGINE='django.db.backends.postgresql'
     DB_NAME='atm_database'
     DB_USER='postgres'
     DB_PASSWORD='postgres'
     DB_HOST='db'
     DB_PORT='5432'
     ```

   - **React Frontend**: Create a `.env` file in the `atm-frontend` directory with the following content:
     ```
     REACT_APP_API_URL=http://localhost:8000/api
     ```

4. Install dependencies:

   - **Django Backend**:

     ```bash
     cd BANKING
     pip install -r requirements.txt
     ```

   - **React Frontend**:
     ```bash
     cd atm-frontend
     npm install
     ```

5. Apply database migrations for Django backend:

   ```bash
   python manage.py migrate
   ```

6. Start the development server:

   - **Django Backend**:

     ```bash
     python manage.py runserver
     ```

   - **React Frontend**:
     ```bash
     npm start
     ```

7. Access the application at:
   - Django Backend: [http://localhost:8000/](http://localhost:8000/)
   - React Frontend: [http://localhost:3000/](http://localhost:3000/)

## Usage

- **API Endpoints** (Django Backend):

  - Deposit money: `/api/deposit/`
  - Withdraw money: `/api/withdraw/`
  - Account balance: `/api/balance/`
  - User account management: `/api/accounts/`

- **Web Interface** (React Frontend):
  - Access the deposit page: [http://localhost:3000/deposit/](http://localhost:3000/deposit/)
  - Access the withdraw page: [http://localhost:3000/withdraw/](http://localhost:3000/withdraw/)

## Testing

Run tests for the Django backend using the following command:

```bash
python manage.py test atm
```

<!-- ## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request. -->

## License

This project is licensed under the GPLv3 license: - see the [LICENSE](LICENSE) file for details.

---

To run your Docker Compose setup, follow these steps:

1. **Ensure Docker is Installed**: Make sure Docker and Docker Compose are installed on your machine. You can check if Docker is installed by running `docker --version` and `docker-compose --version`.

2. **Navigate to Your Project Directory**: Open a terminal and navigate to the directory containing your `docker-compose.yml` file. This file defines the services you want to run.

3. **Run Docker Compose**: Use the following command to build and start the services defined in your `docker-compose.yml` file:

   ```sh
   docker-compose up --build
   ```

   - The `--build` flag ensures that Docker Compose rebuilds the images if there have been changes since the last build.
   - If you want to run the containers in detached mode (in the background), add the `-d` flag:

     ```sh
     docker-compose up --build -d
     ```

### Additional Useful Commands:

- **Stop and Remove Containers**: To stop and remove the containers, networks, and volumes created by `docker-compose up`, use:

  ```sh
  docker-compose down
  ```

- **View Logs**: To view the logs for all services:

  ```sh
  docker-compose logs -f
  ```

- **Execute a Command in a Running Container**: To open a shell inside one of the running containers (e.g., `web` service):

  ```sh
  docker-compose exec web bash
  ```

Make sure your `Dockerfile` for each service (e.g., `./BANKING`, `./atm-frontend`, `./nginx`) is correctly set up to build the Docker images.
