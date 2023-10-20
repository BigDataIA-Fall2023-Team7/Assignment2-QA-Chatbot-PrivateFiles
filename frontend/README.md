# Assignment2-QA-System-Application

Steps to run the fastapi code on localhost

You must have pipenv installed on your computer (If you don't have it, open terminal and run 'pip install pipenv')

Create a .env file in the folder 'fastapi' same as example.env file

Give the name of the python virtual environment in the .env file

Open the terminal at 'fastapi' folder location and run the command 'pipenv shell' to activate virtualenv with your given name

Run the command 'pip install --dev' to download all the dependencies on your virtualenv

Chnage directory to fastapi/src

Run the command 'uvicorn app:app'

This starts the local FastAPI server on port 8000

You can use localhost:8000/docs to see the API documentation

You can also use the Postman collection in fastapi/postman folder to get access to postman collection for api testing