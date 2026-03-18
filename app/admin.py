from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Team, TeamMember, Coaching, Workshop, Project
from app.forms import UserForm, UserEditForm
from app.utils import role_required, ROLE_ADMIN, ROLE_BETRIEBSLEITER, ARCHIV_TEAM_NAME

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def index():
    return render_template('admin/index.html')

@bp.route('/users')
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def users():
    all_users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=all_users)

@bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def new_user():
    form = UserForm()
    
    if form.validate_on_submit():
        # Username automatisch generieren
        username = form.generate_username()
        
        # Prüfen, ob Username bereits existiert
        if User.query.filter_by(username=username).first():
            flash(f'Username {username} existiert bereits. Bitte manuell anpassen.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Neuen User anlegen')
        
        user = User(
            username=username,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=form.email.data,
            role=form.role.data,
            project_id=form.project_id.data,
            team_id_if_leader=form.team_id_if_leader.data if form.team_id_if_leader.data != 0 else None
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.full_name} (Login: {user.username}) wurde angelegt!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='Neuen User anlegen')

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    # Alten Username speichern für späteren Vergleich
    old_username = user.username
    
    if form.validate_on_submit():
        user.first_name = form.first_name.data.strip()
        user.last_name = form.last_name.data.strip()
        user.email = form.email.data
        user.role = form.role.data
        user.project_id = form.project_id.data
        user.team_id_if_leader = form.team_id_if_leader.data if form.team_id_if_leader.data != 0 else None
        
        # Neuen Username generieren, wenn sich Vor-/Nachname geändert haben
        new_username = (user.first_name[0] + user.last_name).lower()
        
        # Wenn sich der Username geändert hat, prüfen ob er bereits existiert
        if new_username != old_username:
            if User.query.filter_by(username=new_username).first():
                flash(f'Username {new_username} existiert bereits. Bitte manuell anpassen.', 'danger')
                return render_template('admin/user_form.html', form=form, title='User bearbeiten', user=user)
            user.username = new_username
        
        # Passwort nur ändern, wenn ein neues eingegeben wurde
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash(f'User {user.full_name} wurde aktualisiert!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='User bearbeiten', user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Du kannst dich nicht selbst löschen!', 'danger')
        return redirect(url_for('admin.users'))
    
    # Prüfen, ob der User Coachings hat
    if user.coachings.count() > 0:
        flash(f'User {user.full_name} kann nicht gelöscht werden, da er noch {user.coachings.count()} Coachings hat!', 'danger')
        return redirect(url_for('admin.users'))
    
    # Prüfen, ob der User Workshops hat
    if user.workshops.count() > 0:
        flash(f'User {user.full_name} kann nicht gelöscht werden, da er noch {user.workshops.count()} Workshops hat!', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.full_name} wurde gelöscht!', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/projects')
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def projects():
    all_projects = Project.query.order_by(Project.name).all()
    return render_template('admin/projects.html', projects=all_projects)

@bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def new_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Projektname ist erforderlich!', 'danger')
            return redirect(url_for('admin.projects'))
        
        project = Project(name=name, description=description)
        db.session.add(project)
        db.session.commit()
        
        flash(f'Projekt {name} wurde angelegt!', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/project_form.html', title='Neues Projekt anlegen')

@bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.name = request.form.get('name')
        project.description = request.form.get('description')
        db.session.commit()
        
        flash(f'Projekt {project.name} wurde aktualisiert!', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/project_form.html', title='Projekt bearbeiten', project=project)

@bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Prüfen, ob das Projekt Users hat
    if project.users.count() > 0:
        flash(f'Projekt {project.name} kann nicht gelöscht werden, da es noch {project.users.count()} Users hat!', 'danger')
        return redirect(url_for('admin.projects'))
    
    # Prüfen, ob das Projekt Teams hat
    if project.teams.count() > 0:
        flash(f'Projekt {project.name} kann nicht gelöscht werden, da es noch {project.teams.count()} Teams hat!', 'danger')
        return redirect(url_for('admin.projects'))
    
    db.session.delete(project)
    db.session.commit()
    flash(f'Projekt {project.name} wurde gelöscht!', 'success')
    return redirect(url_for('admin.projects'))

@bp.route('/manage_coachings')
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def manage_coachings():
    page = request.args.get('page', 1, type=int)
    coachings = Coaching.query.order_by(Coaching.coaching_date.desc()).paginate(page=page, per_page=20)
    return render_template('admin/manage_coachings.html', coachings=coachings)

@bp.route('/manage_workshops')
@login_required
@role_required([ROLE_ADMIN, ROLE_BETRIEBSLEITER])
def manage_workshops():
    page = request.args.get('page', 1, type=int)
    workshops = Workshop.query.order_by(Workshop.workshop_date.desc()).paginate(page=page, per_page=20)
    return render_template('admin/manage_workshops.html', workshops=workshops)
