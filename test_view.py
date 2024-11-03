import pytest
import json
from flask import jsonify
from app import app_instance
from models import db, Employee
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    app_instance.config['TESTING'] = True
    app_instance.config[
        'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app_instance.app_context():
        db.create_all()  # Create database tables
        yield app_instance.test_client()
        db.drop_all()  # Clean up after tests


@pytest.fixture
def jwt_token(client):
    return create_access_token(identity='testuser')

@pytest.fixture
def setup_employees(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}
    employees = [
        Employee(name='John Doe', email='john.doe@example.com', department='Engineering', role='Developer'),
        Employee(name='Jane Smith', email='jane.smith@example.com', department='Engineering', role='Developer'),
        Employee(name='Alice Johnson', email='alice.johnson@example.com', department='HR', role='Manager'),
        Employee(name='Bob Brown', email='bob.brown@example.com', department='HR', role='Manager'),
    ]
    db.session.bulk_save_objects(employees)
    db.session.commit()
    return employees

def test_login_success(client):
    # Set the username and password in the app's config for testing
    app_instance.config['USERNAME'] = 'testuser'
    app_instance.config['PASSWORD'] = 'testpass'

    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_login_invalid_username(client):
    app_instance.config['USERNAME'] = 'testuser'
    app_instance.config['PASSWORD'] = 'testpass'

    response = client.post('/login', json={
        'username': 'wronguser',
        'password': 'testpass'
    })

    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid username or password'

def test_login_invalid_password(client):
    app_instance.config['USERNAME'] = 'testuser'
    app_instance.config['PASSWORD'] = 'testpass'

    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpass'
    })

    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid username or password'

def test_login_missing_username(client):
    response = client.post('/login', json={
        'password': 'testpass'
    })

    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid username or password'

def test_login_missing_password(client):
    response = client.post('/login', json={
        'username': 'testuser'
    })

    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Invalid username or password'



def test_create_employee_success(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}
    response = client.post('/api/employees',
                           headers=headers,
                           json={
                               'name': 'John Doe',
                               'email': 'john.doe@example.com',
                               'department': 'Engineering',
                               'role': 'Developer'
                           })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Employee created successfully!'


def test_create_employee_duplicate_name(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Create the first employee
    client.post('/api/employees',
                headers=headers,
                json={
                    'name': 'Jane Doe',
                    'email': 'jane.doe@example.com',
                    'department': 'Engineering',
                    'role': 'Developer'
                })

    # Attempt to create a duplicate employee
    response = client.post('/api/employees',
                           headers=headers,
                           json={
                               'name': 'Jane Doe',  # Duplicate name
                               'email': 'jane.doe2@example.com',
                               'department': 'Engineering',
                               'role': 'Developer'
                           })

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == "Employee should have a unique name and email."


def test_create_employee_duplicate_email(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Create the first employee
    client.post('/api/employees',
                headers=headers,
                json={
                    'name': 'Alice Smith',
                    'email': 'alice.smith@example.com',
                    'department': 'HR',
                    'role': 'Manager'
                })

    # Attempt to create a duplicate employee
    response = client.post('/api/employees',
                           headers=headers,
                           json={
                               'name': 'Bob Brown',
                               'email': 'alice.smith@example.com',  # Duplicate email
                               'department': 'HR',
                               'role': 'Manager'
                           })

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == "Employee should have a unique name and email."


def test_create_employee_missing_fields(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    response = client.post('/api/employees',
                           headers=headers,
                           json={
                               'name': 'Charlie Brown'
                               # Missing email
                           })

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data


## get all list of employees test cases

def test_get_all_employees(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}
    response = client.get('/api/employees', headers=headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 4
    assert len(data['employees']) == 4

def test_get_employees_by_department(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}
    response = client.get('/api/employees?department=Engineering', headers=headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 2
    assert len(data['employees']) == 2
    assert all(emp['department'] == 'Engineering' for emp in data['employees'])

def test_get_employees_by_role(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}
    response = client.get('/api/employees?role=Manager', headers=headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 2
    assert len(data['employees']) == 2
    assert all(emp['role'] == 'Manager' for emp in data['employees'])

def test_get_employees_with_pagination(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}
    response = client.get('/api/employees?page=1', headers=headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 4
    assert data['current_page'] == 1
    assert len(data['employees']) == 4  # Assuming per_page is set to 10

    response = client.get('/api/employees?page=2', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['current_page'] == 2
    assert len(data['employees']) == 0  # No more employees to return

def test_get_employees_with_no_results(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}
    response = client.get('/api/employees?department=NonExistent', headers=headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 0
    assert len(data['employees']) == 0

## get specific employee by Id test cases

def test_get_employee_success(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Get the first employee's ID currently making it hardcoded since the limited records are inserting
    employee_id = 1
    response = client.get(f'/api/employees/{employee_id}', headers=headers)

    assert response.status_code == 200
    data = json.loads(response.data)

    assert data['name'] == 'John Doe'
    assert data['email'] == 'john.doe@example.com'
    assert data['department'] == 'Engineering'
    assert data['role'] == 'Developer'


def test_get_employee_not_found(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Attempt to get an employee that does not exist
    response = client.get('/api/employees/999', headers=headers)  # Assuming 999 is an invalid ID

    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data


## update the employee endpoint test cases

def test_update_employee_success(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Get the first employee's ID currently making it hardcoded since the limited records are inserting
    employee_id = 1
    update_data = {
        'name': 'John Updated',
        'email': 'john.updated@example.com',
        'department': 'Engineering',
        'role': 'Senior Developer'
    }

    response = client.put(f'/api/employees/{employee_id}', headers=headers, json=update_data)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Employee updated successfully!'

    # Verify the employee's data was updated
    updated_employee = Employee.query.get(employee_id)
    assert updated_employee.name == 'John Updated'
    assert updated_employee.email == 'john.updated@example.com'
    assert updated_employee.role == 'Senior Developer'


def test_update_employee_not_found(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    update_data = {
        'name': 'Non Existent',
        'email': 'non.existent@example.com'
    }

    # Attempt to update an employee that does not exist
    response = client.put('/api/employees/999', headers=headers, json=update_data)  # Assuming 999 is an invalid ID

    assert response.status_code == 404  # Should return 404 for not found


def test_update_employee_duplicate_email(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Get the first employee's ID currently making it hardcoded since the limited records are inserting
    employee_id = 1
    update_data = {
        'name': 'John Doe',
        'email': 'jane.smith@example.com',  # This email already exists
        'department': 'Engineering',
        'role': 'Developer'
    }

    response = client.put(f'/api/employees/{employee_id}', headers=headers, json=update_data)

    assert response.status_code == 400  # Should return 400 for duplicate email
    data = json.loads(response.data)
    assert data['message'] == 'Error: An employee with this email already exists.'


def test_update_employee_with_invalid_data(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Get the first employee's ID currently making it hardcoded since the limited records are inserting
    employee_id = 1
    update_data = {
        'name': 'John Doe',
        # Missing email field
    }

    response = client.put(f'/api/employees/{employee_id}', headers=headers, json=update_data)

    assert response.status_code == 500  # Should return 500 for an error
    data = json.loads(response.data)
    assert 'message' in data  # Ensure some error message is returned

## delete the employee endpoint test cases


def test_delete_employee_success(client, jwt_token, setup_employees):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    response = client.delete(f'/api/employees/2', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Employee deleted successfully!'
    assert len(setup_employees) == 4
    # Verify the employee has been deleted
    deleted_employee = Employee.query.get(2)
    assert deleted_employee is None


def test_delete_employee_not_found(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Attempt to delete an employee that does not exist
    response = client.delete('/api/employees/999', headers=headers)  # Assuming 999 is an invalid ID

    assert response.status_code == 404  # Should return 404 for not found
    data = json.loads(response.data)
    assert data['message'] == 'Employee Id not found.'  # Ensure the correct message is returned


def test_delete_employee_with_error(client, jwt_token):
    headers = {'Authorization': f'Bearer {jwt_token}'}

    # Attempt to delete the first employee, but simulate an error during deletion
    employee_id = 33
    response = client.delete(f'/api/employees/{employee_id}', headers=headers)

    # Check for rollback and error message
    assert response.status_code == 404  # Should return 400 for an error
    data = json.loads(response.data)
    assert data['message'] == 'Employee Id not found.'  # Ensure the correct error message is returned

