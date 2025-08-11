from flask import Flask
from extensions import db, jwt

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    jwt.init_app(app)

    from models import user
    from models.user import User

    from blueprints.main.routes import main_bp
    from blueprints.admin.routes import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from models.user import AdminUser
        db.create_all()

        if not AdminUser.query.filter_by(username='admin').first():
            admin_user = AdminUser(username='admin')
            import string, secrets
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            admin_user.set_password(password)
            print(f'Your password has been set as \"{password}\"')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")

    app.run(debug=True)
