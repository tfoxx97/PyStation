from PyStation import create_app

app = create_app()

#allows us to execute program using >>>python run.py
if __name__ == '__main__':
    app.run(debug=True)