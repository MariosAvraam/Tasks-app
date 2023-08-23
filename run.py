from app import app, db

if __name__ == '__main__':
    # Create all database tables (if they don't exist) before running the app
    with app.app_context():
        db.create_all()
    # Run the Flask application with debugging enabled
    app.run(debug=True)
