from flask import Flask
from config.config import Config
from flask import Flask
from config.config import Config
from backend.db.db import db
from backend.service.create_default_service import CreateDefaultService

try:
    import redis
except ImportError:
    redis = None


def _migrate_sqlite_trek_status():
    if db.engine.dialect.name != 'sqlite':
        return

    conn = db.engine.raw_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='trek_table'")
        row = cur.fetchone()
        if not row:
            return

        table_sql = row[0] or ''
        if 'started' in table_sql:
            return

        cur.execute("ALTER TABLE trek_table RENAME TO trek_table_old")
        cur.execute("""
            CREATE TABLE trek_table (
                trek_id INTEGER NOT NULL,
                trek_name VARCHAR NOT NULL,
                price FLOAT NOT NULL,
                location VARCHAR NOT NULL,
                difficulty VARCHAR(8) NOT NULL,
                duration INTEGER NOT NULL,
                available_slots INTEGER NOT NULL,
                assigned_slot VARCHAR,
                assigned_staff_id INTEGER,
                status VARCHAR(8) NOT NULL,
                start_date VARCHAR,
                end_date VARCHAR,
                PRIMARY KEY (trek_id),
                CONSTRAINT difficulty CHECK (difficulty IN ('easy', 'moderate', 'hard')),
                CONSTRAINT status CHECK (status IN ('pending', 'approved', 'open', 'started', 'closed', 'complete'))
            )
        """)
        cur.execute("""
            INSERT INTO trek_table (trek_id, trek_name, price, location, difficulty, duration, available_slots, assigned_slot, assigned_staff_id, status, start_date, end_date)
            SELECT trek_id, trek_name, price, location, difficulty, duration, available_slots, assigned_slot, assigned_staff_id, status, start_date, end_date
            FROM trek_table_old
        """)
        cur.execute("DROP TABLE trek_table_old")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    if redis:
        try:
            app.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            app.redis_client.ping()
        except Exception:
            app.redis_client = None
    else:
        app.redis_client = None

    from backend.route.route import user_bp
    app.register_blueprint(user_bp)

    with app.app_context():
        _migrate_sqlite_trek_status()
        db.create_all()
        CreateDefaultService().create_def_users()


    return app