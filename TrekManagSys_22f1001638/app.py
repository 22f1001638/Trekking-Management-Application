from backend import create_app
from flask_cors import CORS
from backend.service.login_service import JWTManager
# from application.scheduler import start_scheduler, shutdown_scheduler
import atexit

app = create_app()

CORS(app)
jwt = JWTManager(app)
# start_scheduler(app)
# atexit.register(shutdown_scheduler)

if __name__ == "__main__":
    app.run(debug=True)