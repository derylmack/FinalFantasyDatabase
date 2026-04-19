class Config:
    # You can add general Flask settings later
    SECRET_KEY ='Final Fantasy'   # needed for sessions/forms

    #SQLAlchemy database URI goes here
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://@Mystery/FFXIVDatabase?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Good practice to disable this