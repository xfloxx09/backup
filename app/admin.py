from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import User, Team, TeamMember
from app.forms import TeamForm
from app.utils import ARCHIV_TEAM_NAME

bp = Blueprint('admin', __name__)

@bp.route('/panel')
@login_required
def panel():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    teams = Team.query.all()
    users = User.query.all()
    team_members = TeamMember.query.all()
    archived_team = Team.query.filter_by(name=ARCHIV_TEAM_NAME).first()
    archived_members = archived_team.members.all() if archived_team else []
    return render_template('admin/admin_panel.html', teams=teams, users=users, team_members=team_members, archived_members=archived_members, title="Admin Panel")

@bp.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    form = TeamForm()
    if form.validate_on_submit():
        new_team = Team(name=form.name.data)
        # Add multiple leaders
        for l_id in form.team_leader_ids.data:
            u = User.query.get(l_id)
            if u: new_team.leaders.append(u)
        db.session.add(new_team)
        db.session.commit()
        flash('Team erstellt.', 'success')
        return redirect(url_for('admin.panel'))
    return render_template('admin/create_team.html', form=form, title="Team erstellen")

@bp.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    team = Team.query.get_or_404(team_id)
    form = TeamForm(original_name=team.name)
    if form.validate_on_submit():
        team.name = form.name.data
        # Update multiple leaders
        team.leaders = [] # Clear existing
        for l_id in form.team_leader_ids.data:
            u = User.query.get(l_id)
            if u: team.leaders.append(u)
        db.session.commit()
        flash('Team aktualisiert.', 'success')
        return redirect(url_for('admin.panel'))
    elif request.method == 'GET':
        form.name.data = team.name
        form.team_leader_ids.data = [l.id for l in team.leaders]
    return render_template('admin/edit_team.html', form=form, team=team, title="Team bearbeiten")
