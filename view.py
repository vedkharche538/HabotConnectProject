import sqlalchemy.exc
from app import app_instance
from models import Employee, db
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask import request, jsonify, Response
from werkzeug.exceptions import NotFound
from typing import Dict, Any, Optional

jwt = JWTManager(app_instance)

# Create the database and tables
with app_instance.app_context():
    db.create_all()

@app_instance.route('/login', methods=['POST'])
def login() -> tuple[Response, int]:
    username: str = request.json.get('username')
    password: str = request.json.get('password')

    if username != app_instance.config['USERNAME'] or password != app_instance.config['PASSWORD']:
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token: str = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app_instance.route('/api/employees', methods=['POST'])
@jwt_required()
def create_employee() -> tuple[Response, int]:
    data: Dict[str, Any] = request.get_json()

    try:
        new_employee = Employee(
            name=data['name'],
            email=data['email'],
            department=data.get('department'),
            role=data.get('role')
        )
        db.session.add(new_employee)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return jsonify({'message': "Employee should have a unique name and email."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

    return jsonify({'message': 'Employee created successfully!'}), 201

@app_instance.route('/api/employees', methods=['GET'])
@jwt_required()
def get_employees() -> tuple[Response, int]:
    department: Optional[str] = request.args.get('department')
    role: Optional[str] = request.args.get('role')
    page: int = request.args.get('page', 1, type=int)
    per_page: int = 10
    query = Employee.query
    if department:
        query = query.filter(Employee.department == department)

    if role:
        query = query.filter(Employee.role == role)
    employees = query.paginate(page=page, per_page=per_page, error_out=False)
    response = {
        'total': employees.total,
        'pages': employees.pages,
        'current_page': employees.page,
        'employees': [{
            'id': emp.id,
            'name': emp.name,
            'email': emp.email,
            'department': emp.department,
            'role': emp.role,
            'joining_date': emp.date_joined.isoformat()
        } for emp in employees.items]
    }
    return jsonify(response), 200

@app_instance.route('/api/employees/<int:id>', methods=['GET'])
@jwt_required()
def get_employee(id: int) -> tuple[Response, int]:
    try:
        employee: Employee = Employee.query.get_or_404(id)
    except NotFound:
        return jsonify({'message': 'Employee not found'}), 404
    return jsonify({
        'id': employee.id,
        'name': employee.name,
        'email': employee.email,
        'department': employee.department,
        'role': employee.role,
        'joining_date': employee.date_joined.isoformat()
    }), 200

@app_instance.route('/api/employees/<int:id>', methods=['PUT'])
@jwt_required()
def update_employee(id: int) -> tuple[Response, int]:
    data: Dict[str, Any] = request.get_json()

    try:
        employee: Employee = Employee.query.get_or_404(id)
        employee.name = data['name']
        employee.email = data['email']
        employee.department = data.get('department')
        employee.role = data.get('role')
        db.session.commit()
    except NotFound:
        db.session.rollback()
        return jsonify({'message': 'Employee not found'}), 404
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error: An employee with this email already exists.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred.', 'error': str(e)}), 500

    return jsonify({'message': 'Employee updated successfully!'}), 200

@app_instance.route('/api/employees/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_employee(id: int) -> tuple[Response, int]:
    try:
        employee: Employee = Employee.query.get_or_404(id)
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'message': 'Employee deleted successfully!'}), 200
    except NotFound:
        return jsonify({'message': 'Employee Id not found.'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred'}), 400