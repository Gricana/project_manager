from flask import Blueprint, jsonify, request
from deploy.container.manager import DjangoManager
from app.deploy.container.exceptions import SecurityIssueError
from models import *

# Create a blueprint for the API
api = Blueprint('api', __name__)


@api.route('/<int:id>/projects', methods=['GET'])
def get_user_projects(id):
    """
    Retrieving user projects by his Telegram ID

    :param id: Telegram user ID
    :return: JSON with user projects or error message
    """
    user = User.query.filter_by(tg_id=id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    projects = user.get_projects()
    project_list = [project.to_dict() for project in projects]
    return jsonify({'projects': project_list}), 200


@api.route('/projects/start', methods=['PUT'])
def start_project():
    """
    Launch of the project

    :return: JSON with a message about starting the project or an error message
    """
    return handle_project_action(DjangoManager.start, 'Запущен')


@api.route('/projects/restart', methods=['PUT'])
def restart_project():
    """
    Restarting the project

    :return: JSON with a message about restarting the project or an error message
    """
    return handle_project_action(DjangoManager.restart, 'Остановлен')


@api.route('/projects/stop', methods=['PUT'])
def stop_project():
    """
    Stopping the project

    :return: JSON with a message about stopping the project or an error message
    """
    data = request.get_json()
    project = Project.query.join(User).filter(User.tg_id == data.get('id'),
                                              Project.name == data.get('name'),
                                              Project.status == 'Запущен').first()
    if not project:
        return jsonify({'error': 'Проект с указанным именем не существует или он уже остановлен'}), 400

    DjangoManager.stop()
    project.update(status='Остановлен')
    return jsonify({'message': 'Проект успешно остановлен!'}), 200


@api.route('/projects', methods=['DELETE'])
def delete_project():
    """
    Deleting a project

    :return: JSON with a message about project deletion or an error message
    """
    data = request.get_json()
    project = Project.query.join(User).filter(User.tg_id == data.get('id'), Project.name == data.get('name'),
                                              Project.status != 'Остановлен').first()
    if not project:
        return jsonify({'error': 'Проект с указанным именем не существует или находится в статусе "Запущен"'}), 400

    project.delete()
    return jsonify({'message': 'Проект успешно удалён'}), 204


@api.route('/projects', methods=['POST'])
def create_project():
    """
    Creating a new project

    :return: JSON with information about the created project or an error message
    """
    data = request.get_json()
    user = User.query.filter_by(tg_id=data.get('id')).first()
    if not user:
        user = User(username=data.get('username'), tg_id=data.get('id'))
        user.save()

    project = Project.query.filter_by(user=user, name=data.get('name')).first()
    if project:
        return jsonify({'error': f'Проект с именем {project.name} уже существует'}), 400

    new_project = Project(name=data.get('name'), description=data.get('description'), user=user)
    new_project.save()

    return jsonify({'message': new_project.to_dict()}), 201


def handle_project_action(action, status):
    """
    Processing actions on the project (start, restart, stop)

    :param action: Action function (start, restart, stop)
    :param status: Expected project status after action
    :return: JSON with a message about the result of the action or an error message
    """
    data = request.get_json()
    project = Project.query.join(User).filter(User.tg_id == data.get('id'),
                                              Project.name == data.get('name'), Project.status != status).first()
    if not project:
        return jsonify({'error': f"Проект с именем {data.get('name')} не существует или уже {status}"}), 400

    try:
        project_data = {
            'config': data.get('config'),
            'ext': data.get('ext'),
            'id': data.get('id'),
            'name': data.get('name'),
            'repo_url': data.get('repo_url')
        }
        run_status = action(**project_data)
        if run_status:
            project.update(status=status)
            return jsonify({'message': 'Проект успешно запущен!',
                            'link': f'Ссылка: http://{project.name}.ewdbot.com'}), 200
        else:
            return jsonify({'error': 'Настройки проекта не позволяют запустить проект'}), 400

    except (KeyError, ValueError, FileNotFoundError, json.JSONDecodeError, SecurityIssueError) as e:
        return jsonify({'error': str(e)}), 400
