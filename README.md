# tcc-eng-quimica

## Instructions to Run the Code

1. **Clone the Repository:**

    ```sh
    git clone https://github.com/yourusername/tcc-eng-quimica.git
    cd tcc-eng-quimica
    ```

2. **Install API Dependencies:**

    Ensure you have [Python](https://www.python.org/downloads/) installed (version 3.12.6).

    2.1. **Create a python virtual environment and activate it**

    ```sh
    cd api

    python -m venv .venv
    ```

    On Windows, execute:

    ```sh
    .venv\Scripts\activate
    ```

    On Linux/MacOS, execute:

    ```sh
    source .venv/bin/activate
    ```

    2.2. **Install the dependencies**

    ```sh
    pip install -r requirements.txt
    ```

3. **Run the Code:**
    Execute the main script:

    ```sh
    uvicorn main:app --host: 0.0.0.0 --port 8000
    ```

4. **Configuration:**
    If there are any configuration files, ensure they are properly set up before running the code.

5. **Testing:**
    To run tests, use:

    ```sh
    pytest
    ```

6. **Additional Notes:**
    - Ensure your environment variables are set up as required.
    - Refer to the `config` directory for any additional configuration files.

For any issues, please refer to the [Issues](https://github.com/Alexms95/tcc-eng-quimica/issues) section on GitHub
