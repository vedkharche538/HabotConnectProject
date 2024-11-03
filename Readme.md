## HabotConnect project

**Prerequisites**

To ensure a smooth setup experience, we recommend following these steps:

**1. Environment Setup:**

- **Dependency Installation:** We'll utilize a virtual environment to manage project dependencies effectively. Begin by creating one using the command `python3 -m venv venv`.
- **Virtual Environment Activation:**  Activate the virtual environment using either of the following methods, depending on your operating system:
    - **Linux:** `source venv/bin/activate`
    - **Windows:** `venv\Scripts\activate`

**2. Dependency Installation:**

Once the virtual environment is active, proceed to install all project dependencies listed in the `requirements.txt` file using the command:

```bash
pip install -r requirements.txt
```

**Running the Project**

**1. Project Execution:**

After activating the virtual environment, launch the application using the command:

```bash
python3 app.py
```

This will start the server, and you can access it through the following URL:

```
http://127.0.0.1:5000
```

**2. Token Generation:**

Since the application utilizes token-based authentication, you'll need to create a token before interacting with the API endpoints. You can achieve this by sending a POST request to the `/login` endpoint. The request body should include the username and password credentials. Currently, these credentials are kept static for security reasons. However, you can refer to the `app.py` file for reference and construct the request accordingly.

Once the response is received, you'll obtain an access token that can be used to call other protected API endpoints.

**3. Available API Endpoints:**

The application offers a comprehensive set of API endpoints designed to manage employee data:

- **`/api/employees` (POST):** Create a new employee record.
- **`/api/employees` (GET):** Retrieve a list of all employees. You can further filter results by department, role, or page number, providing greater flexibility in your queries.
- **`/api/employees/[id]` (GET):** Fetch detailed information for a specific employee based on their unique identifier.
- **`/api/employees/[id]` (PUT):** Modify existing employee data.
- **`/api/employees/[id]` (DELETE):** Delete an employee record.

These endpoints encompass all validation and handling scenarios as outlined in the project requirements.

## API Documentation
#### Base URL `http://localhost:5000`

Authentication
- Endpoint: /login
- Method: POST
- Description: Authenticates a user and returns a JWT token.
- Request Body:
```json
{
    "username": "string",
    "password": "string"
}

```

Response:
200 OK: Returns the JWT token.
```json
{
    "access_token": "string"
}
```

401 Unauthorized: Invalid username or password.
```json
{
    "message": "Invalid username or password"
}
```

### Employee Endpoints
1. Get All Employees
- Endpoint: /api/employees
- Method: GET
- Description: Retrieves a list of all employees.
- Headers:
    Authorization: Bearer token (JWT)

- Response:
200 OK: Returns an array of employee objects.
```json
{
  "total": 2,
  "pages": 1,
  "current_page": 1,
  "employees": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@example.com",
      "department": "Engineering",
      "role": "Developer",
      "joining_date": "current date"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane.smith@example.com",
      "department": "Engineering",
      "role": "Developer",
      "joining_date": "current date"
    }
  ]
}
```

2. Create a New Employee
- Endpoint: /api/employees
- Method: POST
- Description: Creates a new employee.
- Headers:
     Authorization: Bearer token (JWT)

- Request Body:
```json
{
    "name": "string",
    "email": "string",
    "department": "string",
    "role": "string"
}
```

Response:
201 Created: Successfully Created Employee.
```json
{"message": "Employee created successfully!"}

```
400 Bad Request: Employee should have a unique name and email.
```json
{
    "message": "Employee should have a unique name and email."
}
```

3. Get Employee by ID
- Endpoint: /api/employees/<id>
- Method: GET
- Description: Retrieves a specific employee by ID.
- Headers:
   Authorization: Bearer token (JWT)

- Response:
200 OK: Returns the employee object.
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "department": "Engineering",
    "role": "Developer",
    "joining_date": "joining date"
}
```

404 Not Found: Employee does not exist.
```json
{
    "message": "Employee does not exist."
}
```

4. Update Employee
- Endpoint: /api/employees/<id>
- Method: PUT
- Description: Updates an existing employee's details.
- Headers:
    Authorization: Bearer token (JWT)

- Request Body:
```json
{
    "name": "string",
    "email": "string",
    "department": "string",
    "role": "string"
}
```

Response:
200 OK: Returns the success message on updating
```json
{"message": "Employee updated successfully!"}
```
404 Not Found: Employee does not exist.
```json
{
    "message": "Employee does not exist."
}
```

400 Bad Request: Invalid employee properties.
```json
{"message": "Error: An employee with this email already exists."}
```

5. Delete Employee
- Endpoint: /api/employees/<id>
- Method: DELETE
- Description: Deletes an employee by ID.
- Headers:
    Authorization: Bearer token (JWT)

- Response:
200 OK: Returns the deleted employee object.
404 Not Found: Employee does not exist.
```json
{
    "message": "Employee does not exist."
}
```


