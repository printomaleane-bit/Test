from flask import Flask, render_template
from business_api import business_bp

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.register_blueprint(business_bp)

    @app.route("/business_dashboard")
    def business_dashboard():
        return render_template("business_dashboard.html")

    @app.route("/")
    def index():
        return render_template("business_dashboard.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
