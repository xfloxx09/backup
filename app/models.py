from flask_login import UserMixin
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(50), nullable=False, default='Mitarbeiter')
    team_id_if_leader = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, default=1)
    
    # Beziehungen
    teams_led = db.relationship('Team', backref='leader', foreign_keys='Team.team_leader_id')
    project = db.relationship('Project')
    
    @property
    def full_name(self):
        """Gibt den vollen Namen zurück (für Anzeige)"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Beziehungen
    teams = db.relationship('Team', backref='project', lazy='dynamic')
    users = db.relationship('User', backref='project', lazy='dynamic')
    coachings = db.relationship('Coaching', backref='project', lazy='dynamic')
    workshops = db.relationship('Workshop', backref='project', lazy='dynamic')
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_leader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Beziehungen
    members = db.relationship('TeamMember', backref='team', lazy='dynamic')
    leaders = db.relationship('User', backref='team_led', foreign_keys=[team_leader_id])
    
    def __repr__(self):
        return f'<Team {self.name}>'

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    original_team_id = db.Column(db.Integer, nullable=True)
    original_project_id = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<TeamMember {self.name}>'

class Coaching(db.Model):
    __tablename__ = 'coachings'
    
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coaching_date = db.Column(db.DateTime, default=datetime.utcnow)
    coaching_style = db.Column(db.String(50))
    tcap_id = db.Column(db.String(100), nullable=True)
    
    # Leitfaden-Felder
    leitfaden_begruessung = db.Column(db.String(10), default='k.A.')
    leitfaden_legitimation = db.Column(db.String(10), default='k.A.')
    leitfaden_pka = db.Column(db.String(10), default='k.A.')
    leitfaden_kek = db.Column(db.String(10), default='k.A.')
    leitfaden_angebot = db.Column(db.String(10), default='k.A.')
    leitfaden_zusammenfassung = db.Column(db.String(10), default='k.A.')
    leitfaden_kzb = db.Column(db.String(10), default='k.A.')
    
    performance_mark = db.Column(db.Integer)
    time_spent = db.Column(db.Integer)
    project_leader_notes = db.Column(db.Text, nullable=True)
    coaching_subject = db.Column(db.String(100))
    coach_notes = db.Column(db.Text, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    
    # Beziehungen
    team_member_coached = db.relationship('TeamMember', backref='coachings', foreign_keys=[team_member_id])
    coach = db.relationship('User', backref='coachings', foreign_keys=[coach_id])
    team = db.relationship('Team', foreign_keys=[team_id])
    
    @property
    def overall_score(self):
        if self.performance_mark is not None:
            return round(self.performance_mark * 10, 1)
        return 0
    
    @property
    def leitfaden_fields_list(self):
        fields = [
            ('Begrüßung', self.leitfaden_begruessung),
            ('Legitimation', self.leitfaden_legitimation),
            ('PKA', self.leitfaden_pka),
            ('KEK', self.leitfaden_kek),
            ('Angebot', self.leitfaden_angebot),
            ('Zusammenfassung', self.leitfaden_zusammenfassung),
            ('KZB', self.leitfaden_kzb),
        ]
        return fields

class Workshop(db.Model):
    __tablename__ = 'workshops'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workshop_date = db.Column(db.DateTime, default=datetime.utcnow)
    overall_rating = db.Column(db.Integer)
    time_spent = db.Column(db.Integer)
    notes = db.Column(db.Text, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Beziehungen
    coach = db.relationship('User', backref='workshops')
    participants = db.relationship('TeamMember', secondary='workshop_participants', backref='workshops')

# Assoziationstabelle für Workshop-Teilnehmer
workshop_participants = db.Table('workshop_participants',
    db.Column('workshop_id', db.Integer, db.ForeignKey('workshops.id'), primary_key=True),
    db.Column('team_member_id', db.Integer, db.ForeignKey('team_members.id'), primary_key=True),
    db.Column('individual_rating', db.Integer),
    db.Column('original_team_id', db.Integer)
)
