import os
from app import create_app

# import os
# from app import create_app

# # Debugging - print all environment variables
# print("ENV VARIABLES TEST")
# for key, value in os.environ.items():
#     print(f"{key}: {value}")

# # Ensure FLASK_CONFIG is set
# config_name = os.getenv('FLASK_CONFIG')
# if not config_name:
#     raise ValueError("FLASK_CONFIG is not set!")

# app = create_app(config_name)

# if __name__ == '__main__':
#     port = int(os.environ["PORT"])  # Render requires this
#     app.run(host='0.0.0.0', port=port)


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    port = int(os.environ.get('PORT',5432))


    app.run(host='0.0.0.0', port=port, load_dotenv=True)




