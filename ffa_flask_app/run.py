from app import create_app  # Import the package directly

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
