from flask import Flask, app
from routes.chat import chat_bp
from routes.memory import memory_bp
from routes.tasks import task_bp
from routes.files import file_bp
from routes.settings import settings_bp
from core.logger import init_logger
from core.db import init_db
from routes.providers import provider_bp
from routes.models import model_bp
from routes.workgroups import workgroup_bp
from routes.realtime import realtime_bp
def create_app():
    app = Flask(__name__,
    template_folder='templates',
    static_folder='static')
    init_logger()
    init_db()
    app.register_blueprint(chat_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(workgroup_bp)
    app.register_blueprint(realtime_bp)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)