from waitress import serve
from SalesExpense.wsgi import application

if __name__ == '__main__':
    serve(application, port='8080')
