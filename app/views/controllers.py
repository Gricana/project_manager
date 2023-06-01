from flask import Blueprint, jsonify, request
from app.models import User, Project
from . import api


@api.route('/users', methods=['POST'])
def create_user():
    username = request.json.get('username')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    user = User(username=username)
    user.save()

    return jsonify({'token': user.token}), 201


@api.route('users/<username>/projects', methods=['GET'])
def get_user_projects(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    projects = user.get_projects()
    project_list = [project.to_dict() for project in projects]
    return jsonify({'projects': project_list}), 200


@api.route('users/<username>/projects/<name>/status', methods=['PUT'])
def update_project_status(username, name):
    user_project = Project.query.join(User)\
        .filter(User.username == username, Project.name == name)\
        .first()

    if not user_project:
        return jsonify({'error': 'A project with this name was not found'}), 404

    data = request.get_json()
    user_project.update(status=data['status'])
    return jsonify({'project': user_project.to_dict()})
