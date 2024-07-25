from datetime import datetime
from run import db


class User(db.Model):
    """
    User model.

    Attributes:
        id (int): Unique user identifier
        username (str): Username
        tg_id (int): Unique Telegram user ID
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False)
    tg_id = db.Column(db.Integer, unique=True)

    def get_projects(self):
        """
        Retrieving all user projects

        :return: List of user projects
        """
        return self.projects.all()

    def save(self):
        """
        Saving the user in the database
        """
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """
        Convert the user object to a dictionary

        :return: Dictionary with user data
        """
        return {
            'username': self.username
        }


class Project(db.Model):
    """
    Project model

    Attributes:
        id (int): Unique identifier for the project
        name (str): Project name
        description (str): Description of the project
        created_at (datetime): The date and time the project was created
        updated_at (datetime): The date and time the project was last updated
        user_id (int): Identifier of the user who owns the project
        user (User): Link to the user model
        status (str): Project status (Running or Stopped)
    """

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='projects', cascade='all,delete')
    status = db.Column(db.Enum('Запущен', 'Остановлен'), default='Остановлен', nullable=False)

    def save(self):
        """
        Saving the project in the database
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Removing a project from the database
        """
        db.session.delete(self)
        db.session.commit()

    def update(self, name=None, description=None, status=None):
        """
        Update project data

        :param name: New project name
        :param description: New description of the project
        :param status: New project status
        """
        for key, value in locals().items():
            if key != 'self' and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """
        Convert a project object to a dictionary

        :return: Dictionary with project data
        """
        return {
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.strftime('%d.%m.%y %H:%M'),
            'status': self.status
        }
