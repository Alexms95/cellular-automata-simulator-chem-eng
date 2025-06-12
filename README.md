# Cellular Automata Simulator

This project is a simulator for cellular automata, allowing users to create, configure, and run simulations with custom parameters.

## Prerequisites

- **Python**: Version 3.12.6.
- **Node.js**: Version 20 or higher.
- **npm**: Comes with Node.js.
- **PostgreSQL**: Version 12 or higher.

## Instructions to Run the Application

### 1. Clone the Repository

```sh
git clone https://github.com/Alexms95/tcc-eng-quimica.git
cd tcc-eng-quimica
```

---

### 2. Set Up the API

1. **Navigate to the API directory**:

    ```sh
    cd api
    ```

2. **Create and activate a Python virtual environment**:

    - On Windows:

      ```sh
      python -m venv .venv
      .venv\Scripts\activate
      ```

    - On Linux/MacOS:

      ```sh
      python -m venv .venv
      source .venv/bin/activate
      ```

3. **Install dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Configure environment variables**:

    Copy `.env.example` to `.env` and update the values as needed:

    ```sh
    cp .env.example .env
    ```

5. **Run database migrations**:

    Ensure PostgreSQL is running and properly configured (in the .env file), then execute:

    ```sh
    alembic upgrade head
    ```

6. **Run the API**:

    ```sh
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

---

### 3. Set Up the Frontend

1. **Navigate to the UI directory**:

    ```sh
    cd ../ui
    ```

2. **Install dependencies**:

    ```sh
    npm install
    ```

3. **Run the development server**:

    ```sh
    npm run dev
    ```

4. **Access the application**:

    Open your browser and navigate to `http://localhost:5173`.

---

### 4. Testing

- **API Tests**:
  Run the tests in the `api` directory:

  ```sh
  pytest tests.py
  ```

- **Frontend Linting**:
  Run ESLint in the `ui` directory:

  ```sh
  npm run lint
  ```

---

### 5. Additional Notes

- Ensure your environment variables are properly configured if required.
- For issues, visit the [Issues](https://github.com/Alexms95/tcc-eng-quimica/issues) section on GitHub.

---

## Project Structure

- **API**: Backend service built with FastAPI.
- **UI**: Frontend application built with React, TypeScript, and Vite.
- **Database**: Uses PostgreSQL with Alembic for migrations.

Enjoy exploring and simulating cellular automata!
