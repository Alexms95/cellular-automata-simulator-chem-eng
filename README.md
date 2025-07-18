# Cellular Automata Simulator

This project is a simulator for cellular automata, allowing users to create, configure, and run simulations with custom parameters.

## Instructions to Run the Application

You can run the application by using Docker (recommended for just running and testing) or manually (recommended for studying the code).

## 1. From Docker containers

Download and Install [Docker](https://docs.docker.com/get-started/get-docker/) or [Rancher Desktop](https://rancherdesktop.io/).

Download the `compose.yml` file from the repository root and run the following command from your OS's terminal in the same directory:

```sh
docker compose up -d
```

That's it! The application will be available at `http://localhost:9000` for the UI and `http://localhost:8000` for the API.

## 2. By cloning and running the code

## Prerequisites

- **Python**: Version 3.12.6.
- **Node.js**: Version 20 or higher.
- **npm**: Comes with Node.js.
- **PostgreSQL**: Version 12 or higher.


### 1. Clone the Repository

```sh
git clone https://github.com/Alexms95/cellular-automata-simulator-chem-eng.git
cd cellular-automata-simulator-chem-eng
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
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
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
  pytest -v
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
