# Task-forge
    Blueprint project for managing tasks for a company. It's easy-to-go, and easy-to-use.
    If you're interested to work in company you can join this site via *Sign-up*, watch preview of tasks and how you can work with them, and some info about site on main page.
    If any manager hired you, and you're a *worker*(developer or anyone), you don't have to worry about anything, you can simply jump to your tasks, create some if you want, chose whatever you want to do with tasks and mark them as finished ;)
    What comes on to a manager? Well, you can create Projects, create Teams, Manage Projects and finish them, also you can watch any related data about finished tasks and anything, like who was working on task, date of task assignment, other features are still beta, but I'll finish em in a while.


## Check it out!

-> [Task-Forge](https://task-forge.onrender.com/)


# Features

-Colored tasks

-Minimalized dark color design(*for anyone who loves Earth*)

-User Authentication: sign up and login where users can create accounts and login to access various features.

-Task Management: Users can create and manage their tasks, assign them to different team members, set deadlines, and mark them as completed.

-Team Collaboration: ProjectManagers can create and join teams to collaborate on different tasks.

-Integration with Other Tools: You can integrate with other tools that users commonly use, such as calendars, project management tools, or messaging platforms.

# how to start

assuming, you already have python installed from python.org (version >= 3)
if you're using cmd/powershell/git:
```
git clone git@github.com:NEkropo1/py-taxi-service-search-and-tests.git
cd task-manager
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver # starts Django server
```
### after successful creation you should login via: yourlocalhost/admin and create position="ProjectManager" and add it to your account

P.S. I left very simple design to unregistered users, so be sure to provide your desired stiles on templates/forge/unregistered/welcome.html

### That's all, mostly!
