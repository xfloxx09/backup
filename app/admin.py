from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import User, Team

bp = Blueprint('admin', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def admin_home():
    if current_user.role != 'Admin':
        flash('Zugriff verweigert.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Create Team Logic
        if 'add_team' in request.form:
            name = request.form.get('team_name')
            # Changed to getlist for multiple leaders
            leader_ids = request.form.getlist('leader_ids')
            if name:
                new_team = Team(name=name)
                for l_id in leader_ids:
                    l_user = User.query.get(l_id)
                    if l_user:
                        new_team.leaders.append(l_user)
                db.session.add(new_team)
                db.session.commit()
                flash(f'Team "{name}" erstellt.', 'success')
        
        # Delete Team Logic
        elif 'delete_team' in request.form:
            team_id = request.form.get('team_id')
            team = Team.query.get(team_id)
            if team:
                db.session.delete(team)
                db.session.commit()
                flash('Team gelöscht.', 'success')

    teams = Team.query.all()
    # Updated to find all potential leaders
    potential_leaders = User.query.filter(User.role.in_(['Admin', 'Teamleiter'])).all()
    return render_template('admin.html', teams=teams, potential_leaders=potential_leaders)

@bp.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    users = User.query.all()
    return render_template('admin_manage_users.html', users=users)
