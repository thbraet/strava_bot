import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    port = int(os.environ.get('PORT',5432))
    app.run(host='0.0.0.0', port=port, load_dotenv=True)




