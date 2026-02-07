from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import User, Team, TeamMember

bp = Blueprint('admin', __name__)

@bp.route('/manage_teams', methods=['GET', 'POST'])
@login_required
def manage_teams():
    if current_user.role != 'Admin':
        flash('Zugriff verweigert.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        # NEW: Get multiple leader IDs from the form
        leader_ids = request.form.getlist('leader_ids') 
        
        if team_name:
            new_team = Team(name=team_name)
            # NEW: Add all selected leaders
            for l_id in leader_ids:
                leader_user = User.query.get(l_id)
                if leader_user:
                    new_team.leaders.append(leader_user)
            
            db.session.add(new_team)
            db.session.commit()
            flash(f'Team "{team_name}" wurde erstellt.', 'success')
        return redirect(url_for('admin.manage_teams'))

    teams = Team.query.all()
    # Find everyone who can be a leader (Admins and leaders)
    potential_leaders = User.query.filter(User.role.in_(['Admin', 'Teamleiter'])).all()
    return render_template('admin/manage_teams.html', teams=teams, potential_leaders=potential_leaders)

@bp.route('/delete_team/<int:id>')
@login_required
def delete_team(id):
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    team = Team.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    flash('Team gelöscht.', 'success')
    return redirect(url_for('admin.manage_teams'))
