from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager 
from datetime import datetime, timezone

# ASSOCIATION TABLE for Multiple Team Leaders
team_leaders = db.Table('team_leaders',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', name='fk_team_leaders_user_id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id', name='fk_team_leaders_team_id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=False, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='Teammitglied')
    
    # NEW: Relationship for multiple teams this user leads
    led_teams = db.relationship('Team', secondary=team_leaders, backref=db.backref('leaders', lazy='dynamic'), lazy='dynamic')
    
    coachings_done = db.relationship('Coaching', foreign_keys='Coaching.coach_id', backref='coach', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    members = db.relationship('TeamMember', backref='team', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Team {self.name}>'

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', name='fk_teammember_team_id'), nullable=False)
    coachings_received = db.relationship('Coaching', backref='team_member_coached', lazy='dynamic', cascade="all, delete-orphan")

class Coaching(db.Model):
    __tablename__ = 'coachings'
    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id', name='fk_coaching_team_member_id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_coaching_coach_id'), nullable=False)
    coaching_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    coaching_style = db.Column(db.String(50), nullable=True)
    tcap_id = db.Column(db.String(50), nullable=True)
    coaching_subject = db.Column(db.String(50), nullable=True) 
    coach_notes = db.Column(db.Text, nullable=True)
    leitfaden_begruessung = db.Column(db.String(10), default="k.A.")
    leitfaden_legitimation = db.Column(db.String(10), default="k.A.")
    leitfaden_pka = db.Column(db.String(10), default="k.A.")
    leitfaden_kek = db.Column(db.String(10), default="k.A.")
    leitfaden_angebot = db.Column(db.String(10), default="k.A.")
    leitfaden_zusammenfassung = db.Column(db.String(10), default="k.A.")
    leitfaden_kzb = db.Column(db.String(10), default="k.A.")
    performance_mark = db.Column(db.Integer)
    time_spent = db.Column(db.Integer)
    project_leader_notes = db.Column(db.Text)
