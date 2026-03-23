from app import create_app, db
from sqlalchemy import inspect, text
from app.models import Project, User, Team, Workshop, Coaching, TeamMember

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    conn = db.engine.connect()

    # 1. Prüfen und Hinzufügen von coachings.team_id
    columns_coachings = [col['name'] for col in inspector.get_columns('coachings')]
    if 'team_id' not in columns_coachings:
        print("⚠️ Spalte 'team_id' in coachings fehlt – wird hinzugefügt...")
        conn.execute(text('ALTER TABLE coachings ADD COLUMN team_id INTEGER REFERENCES teams(id)'))
        conn.commit()
        print("✅ Spalte 'team_id' in coachings hinzugefügt.")
    else:
        print("✅ Spalte 'team_id' in coachings existiert bereits.")

    # 2. Für bestehende Coachings die team_id nachtragen (falls NULL)
    conn.execute(text('''
        UPDATE coachings
        SET team_id = team_members.team_id
        FROM team_members
        WHERE coachings.team_member_id = team_members.id
        AND coachings.team_id IS NULL
    '''))
    conn.commit()
    print("ℹ️ Bestehende Coachings mit team_id aktualisiert.")

    # 3. Prüfen und Hinzufügen von workshop_participants.original_team_id
    if 'workshop_participants' in inspector.get_table_names():
        columns_wp = [col['name'] for col in inspector.get_columns('workshop_participants')]
        if 'original_team_id' not in columns_wp:
            print("⚠️ Spalte 'original_team_id' in workshop_participants fehlt – wird hinzugefügt...")
            conn.execute(text('ALTER TABLE workshop_participants ADD COLUMN original_team_id INTEGER REFERENCES teams(id)'))
            conn.commit()
            print("✅ Spalte 'original_team_id' in workshop_participants hinzugefügt.")
        else:
            print("✅ Spalte 'original_team_id' in workshop_participants existiert bereits.")

        conn.execute(text('''
            UPDATE workshop_participants
            SET original_team_id = team_members.team_id
            FROM team_members
            WHERE workshop_participants.team_member_id = team_members.id
            AND workshop_participants.original_team_id IS NULL
        '''))
        conn.commit()
        print("ℹ️ Bestehende Workshop-Teilnehmer mit original_team_id aktualisiert.")
    else:
        print("✅ Tabelle 'workshop_participants' existiert noch nicht, später automatisch.")

    # ========== NEU: user_projects Tabelle für Abteilungsleiter ==========
    # 4. Prüfen, ob die Tabelle user_projects existiert
    if 'user_projects' not in inspector.get_table_names():
        print("⚠️ Tabelle 'user_projects' fehlt – wird erstellt...")
        conn.execute(text('''
            CREATE TABLE user_projects (
                user_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, project_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        '''))
        conn.commit()
        print("✅ Tabelle 'user_projects' erstellt.")

        # 5. Für alle bestehenden Abteilungsleiter die Zuordnung zum aktuellen Projekt eintragen
        res = conn.execute(text("SELECT id, project_id FROM users WHERE role = 'Abteilungsleiter' AND project_id IS NOT NULL"))
        rows = res.fetchall()
        for user_id, project_id in rows:
            conn.execute(
                text("INSERT INTO user_projects (user_id, project_id) VALUES (:user_id, :project_id)"),
                {"user_id": user_id, "project_id": project_id}
            )
        conn.commit()
        print(f"ℹ️ {len(rows)} Abteilungsleiter-Zuordnungen in user_projects eingetragen.")
    else:
        print("✅ Tabelle 'user_projects' existiert bereits.")

    # 6. Optional: Bei vorhandener Tabelle trotzdem noch fehlende Zuordnungen nachholen
    #    (z.B. wenn manuelle Zuordnung nachträglich geändert wurde)
    res = conn.execute(text("""
        SELECT u.id, u.project_id
        FROM users u
        WHERE u.role = 'Abteilungsleiter'
          AND u.project_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM user_projects up WHERE up.user_id = u.id AND up.project_id = u.project_id)
    """))
    rows = res.fetchall()
    for user_id, project_id in rows:
        conn.execute(
            text("INSERT INTO user_projects (user_id, project_id) VALUES (:user_id, :project_id)"),
            {"user_id": user_id, "project_id": project_id}
        )
    conn.commit()
    if rows:
        print(f"ℹ️ {len(rows)} zusätzliche Abteilungsleiter-Zuordnungen in user_projects nachgetragen.")
    # ========== Ende NEU ==========

    print("✅ Migration für historische Team-Zuordnung und Abteilungsleiter-Projekte abgeschlossen.")

if __name__ == "__main__":
    app.run()
