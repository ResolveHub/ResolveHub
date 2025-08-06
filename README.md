ResolveHub - Project Setup and Running Instructions
________________


Step 1: Setup Backend (Django Server)
1. Open a terminal and navigate to the project folder:
cd ResolveHub

2. Create a virtual environment:
python -m venv .venv

3. Activate the virtual environment:

   * On Windows:
.venv\Scripts\activate

   * On Mac/Linux:
source .venv/bin/activate

      4. Install dependencies:
pip install -r requirements.txt

      5. Run the backend server:
python manage.py runserver

⚠ Important:
 Keep this terminal open. The backend server must be running when you start the frontend.
For admin functionality sign up as ‘….@admin.ac.in’ and then after log in you can view admin functionality and can manage the authorities. 




________________


Step 2: Setup Frontend (Python UI)
         1. Open a new terminal window

         2. Navigate to the frontend directory:


cd frontend


            3. Run the frontend:
python components/widgets/login.py


For Running Test
            1. Navigate to cd ResolveHub 
            2.  Run command 
pip install -r requirements-test.txt
pytest
