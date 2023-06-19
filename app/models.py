from datetime import datetime
from run import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False)
    tg_id = db.Column(db.Integer, unique=True)

    def get_projects(self):
        return self.projects.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            'username': self.username
        }


class Project(db.Model):
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
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, name=None, description=None, status=None):
        for key, value in locals().items():
            if key != 'self' and value is not None:
                setattr(self, key, value)
            self.updated_at = datetime.utcnow()
            db.session.commit()

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.strftime('%d.%m.%y %H:%M'),
            'status': self.status
        }
