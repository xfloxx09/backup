from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError
from app.models import User, Team, Project

class UserForm(FlaskForm):
    first_name = StringField('Vorname', validators=[DataRequired()])
    last_name = StringField('Nachname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Rolle', choices=[
        ('Admin', 'Admin'),
        ('Betriebsleiter', 'Betriebsleiter'),
        ('Projektleiter', 'Projektleiter'),
        ('Abteilungsleiter', 'Abteilungsleiter'),
        ('QM', 'QM'),
        ('Teamleiter', 'Teamleiter'),
        ('SalesCoach', 'SalesCoach'),
        ('Trainer', 'Trainer')
    ], validators=[DataRequired()])
    project_id = SelectField('Projekt', coerce=int, validators=[DataRequired()])
    team_id_if_leader = SelectField('Team (falls Teamleiter)', coerce=int, validators=[Optional()])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=6)])
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.project_id.choices = [(p.id, p.name) for p in Project.query.order_by('name').all()]
        self.team_id_if_leader.choices = [(0, 'Kein Team')] + [(t.id, t.name) for t in Team.query.order_by('name').all()]
    
    def validate_first_name(self, field):
        if not field.data.strip():
            raise ValidationError('Vorname darf nicht leer sein')
    
    def validate_last_name(self, field):
        if not field.data.strip():
            raise ValidationError('Nachname darf nicht leer sein')
    
    def generate_username(self):
        first = self.first_name.data.strip()
        last = self.last_name.data.strip()
        return (first[0] + last).lower()

class UserEditForm(FlaskForm):
    first_name = StringField('Vorname', validators=[DataRequired()])
    last_name = StringField('Nachname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Rolle', choices=[
        ('Admin', 'Admin'),
        ('Betriebsleiter', 'Betriebsleiter'),
        ('Projektleiter', 'Projektleiter'),
        ('Abteilungsleiter', 'Abteilungsleiter'),
        ('QM', 'QM'),
        ('Teamleiter', 'Teamleiter'),
        ('SalesCoach', 'SalesCoach'),
        ('Trainer', 'Trainer')
    ], validators=[DataRequired()])
    project_id = SelectField('Projekt', coerce=int, validators=[DataRequired()])
    team_id_if_leader = SelectField('Team (falls Teamleiter)', coerce=int, validators=[Optional()])
    password = PasswordField('Neues Passwort (nur ändern wenn gewünscht)', validators=[Optional(), Length(min=6)])
    
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.project_id.choices = [(p.id, p.name) for p in Project.query.order_by('name').all()]
        self.team_id_if_leader.choices = [(0, 'Kein Team')] + [(t.id, t.name) for t in Team.query.order_by('name').all()]

class CoachingForm(FlaskForm):
    team_member_id = SelectField('Teammitglied', coerce=int, validators=[DataRequired()])
    coaching_style = SelectField('Coaching-Stil', choices=[
        ('', 'Bitte wählen'),
        ('TCAP', 'TCAP'),
        ('Side-by-Side', 'Side-by-Side')
    ], validators=[DataRequired()])
    tcap_id = StringField('T-CAP ID', validators=[Optional()])
    coaching_subject = SelectField('Thema', choices=[
        ('Allgemein', 'Allgemein'),
        ('Qualität', 'Qualität'),
        ('Sales', 'Sales')
    ], validators=[DataRequired()])
    coach_notes = TextAreaField('Notizen des Coaches', validators=[Optional()])
    
    # Leitfaden-Felder
    leitfaden_begruessung = SelectField('Begrüßung', 
        choices=[('Ja', 'Ja'), ('Nein', 'Nein'), ('k.A.', 'k.A.')], default='k.A.')
    leitfaden_legitimation = SelectField('Legitimation', 
        choices=[('Ja', 'Ja'), ('Nein', 'Nein'), ('k.A.', 'k.A.')], default='k.A.')
    leitfaden_pka = SelectField('PKA', 
        choices=[('Ja', 'Ja'), ('Nein', 'Nein'), ('k.A.', 'k.A.')], default='k.A.')
    leitfaden_kek = SelectField('KEK', 
        choices=[('Ja', 'Ja'), ('Nein', 'Nein'), ('k.A.', 'k.A.')], default='k.A.')
    leitfaden_angebot = SelectField('Angebot', 
        choices=[('Ja', 'Ja'), ('Nein', 'Nein'), ('k.A.', 'k.A.')], default='k.A.')
    leitfaden_zusammenfassung = SelectField('Zusammenfassung', 
        choices=[('Ja', 'Ja'), ('Nein', 'Nein'), ('k.A.', 'k.A.')], default='k.A.')
    leitfaden_kzb = SelectField('KZB', 
        choices=[('Ja', 'Ja'), ('Nein', 'Nein'), ('k.A.', 'k.A.')], default='k.A.')
    
    performance_mark = IntegerField('Performance Note (0-10)', validators=[DataRequired()])
    time_spent = IntegerField('Zeitaufwand (Minuten)', validators=[DataRequired()])
    submit = SubmitField('Speichern')
    
    def __init__(self, *args, **kwargs):
        super(CoachingForm, self).__init__(*args, **kwargs)
    
    def update_team_member_choices(self, exclude_archiv=True, project_id=None):
        from app.models import TeamMember, Team
        query = TeamMember.query.join(Team)
        if exclude_archiv:
            from app.utils import ARCHIV_TEAM_NAME
            query = query.filter(Team.name != ARCHIV_TEAM_NAME)
        if project_id:
            query = query.filter(Team.project_id == project_id)
        members = query.order_by(TeamMember.name).all()
        self.team_member_id.choices = [(m.id, f"{m.name} ({m.team.name})") for m in members]

class WorkshopForm(FlaskForm):
    title = StringField('Titel', validators=[DataRequired()])
    team_member_ids = SelectField('Teilnehmer', coerce=int, validators=[DataRequired()])
    overall_rating = IntegerField('Gesamtbewertung (0-10)', validators=[DataRequired()])
    time_spent = IntegerField('Zeitaufwand (Minuten)', validators=[DataRequired()])
    notes = TextAreaField('Notizen', validators=[Optional()])
    submit = SubmitField('Speichern')
    
    def __init__(self, *args, **kwargs):
        super(WorkshopForm, self).__init__(*args, **kwargs)
    
    def update_participant_choices(self, project_id=None):
        from app.models import TeamMember, Team
        query = TeamMember.query.join(Team)
        if project_id:
            query = query.filter(Team.project_id == project_id)
        members = query.order_by(Team.name, TeamMember.name).all()
        self.team_member_ids.choices = [(m.id, f"{m.name} ({m.team.name})") for m in members]

class ProjectLeaderNoteForm(FlaskForm):
    notes = TextAreaField('Notiz', validators=[Optional()])
    submit = SubmitField('Notiz speichern')

class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Altes Passwort', validators=[DataRequired()])
    new_password = PasswordField('Neues Passwort', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Passwort bestätigen', validators=[DataRequired()])
    submit = SubmitField('Passwort ändern')
    
    def validate_confirm_password(self, field):
        if field.data != self.new_password.data:
            raise ValidationError('Passwörter stimmen nicht überein')
