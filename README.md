# Expense Profiler
This app is supposed to analize and report the data extracted from user expense/income.  
The idea for this application is taken from two other apps, which they have been consolidated in one app and enhanced with new features.

- Here are the references to other two apps used in this project:  
<https://github.com/AdamJedrychowski/Recipt-Scanner.git>  
<https://github.com/ajo01/SaveSavvy.git>


### Installation Help

If you are installing on a ubuntu system take a note on following steps.  


- To avoid issues with virtualenv uninstall and reinstall it first.  

```
sudo pip uninstall virtualenv
sudo -H pip install virtualenv
```

- after creating and activating virtualenv continue with required packages.  

```bash
virtualenv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Database

If you chose postgres as RDS, the following is a reviw of set up database.  

- login to database

```bash
sudo -i -u postgres
psql -h localhost -U your_database_user -W
# Or simply type:
psql
```

- sql commands

```sql
create database your_database_name;
create user your_database_user with password 'your_password';
ALTER ROLE  your_database_user SET client_encoding TO 'utf8';
ALTER ROLE your_database_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_database_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE mywikis TO your_database_user;
\q
```

- Set up the database in settings.py  

```python
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_NAME'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': os.environ['POSTGRES_PORT']
    }
}
```

- Create new file named .env based on the file .env-sample in project root directory.  

```
EMAIL_HOST_USER=user@gmail.com
EMAIL_HOST_PASSWORD=password_for_send_grid_email
POSTGRES_NAME=expenseprofiler
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=your_password_for_postgres-database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```
