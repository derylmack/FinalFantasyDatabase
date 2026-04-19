"""
Database models for the FFXIV tracker application.
This file defines the SQLAlchemy models for the FFXIVDatabase
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


db = SQLAlchemy()

"""
 Define the Server models 
"""
class Server(db.Model):
    __tablename__ = 'Servers'     # exact table name in database
    Server_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Server_Name = db.Column(db.String(50), nullable=False, unique=True)
    characters = relationship('Character', back_populates='server')

    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<Server {self.Server_Name}>"

class Character(db.Model):
    __tablename__: str = 'Character'   # exact table name in database
    Character_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Character_Name = db.Column(db.String(50), nullable=False, unique=True)
    Server_ID = db.Column(db.Integer, db.ForeignKey('Servers.Server_ID'), nullable=False)
    Playable = db.Column(db.Boolean, nullable=False)
    server = db.relationship('Server', back_populates='characters')
    storage_locations = db.relationship('StorageLocations', back_populates='character')
    characters_job_levels = db.relationship('CharactersJobLevels', back_populates='job_level_character')
    characters_job = db.relationship('Jobs', back_populates='job_character')

    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<Character {self.Character_Name} on Server ID {self.Server_ID}>"
    
class Jobs(db.Model):
    __tablename__: str = 'Jobs'   # exact table name in database
    Job_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Job_Longname  = db.Column(db.String(50), nullable=False, unique=True)
    Job_Shortname = db.Column(db.String(50), nullable=False, unique=True)
    Starting_Level = db.Column(db.Integer, nullable=False)
    Limited_Job = db.Column(db.Boolean, nullable=False)
    Job_Type = db.Column(db.String(50), nullable=False)
    job_character = db.relationship('Character', back_populates='characters_job')
    job_level = db.relationship('CharactersJobLevels', back_populates='level_job')


    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<Job {self.Job_Name} >"
    
class CharactersJobLevels(db.Model):
    __tablename__: str = 'CharactersJobLevels'   # exact table name in database
    Character_ID = db.Column(db.Integer, db.ForeignKey('Character.Character_ID'), primary_key=True, nullable=False)
    Job_ID = db.Column(db.Integer, db.ForeignKey('Jobs.Job_ID'), primary_key=True, nullable=False)
    Job_Level = db.Column(db.Integer, nullable=True)
    job_level_character = db.relationship('Character', back_populates='character_job_levels')
    level_job = db.relationship('Jobs', back_populates='job_level')

    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<CharactersJobLevel Character ID {self.Character_ID} Job ID {self.Job_ID} Level {self.Job_Level}>"

class StorageLocations(db.Model):
    __tablename__: str = 'StorageLocations'   # exact table name in database
    Storage_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Character_ID = db.Column(db.Integer, db.ForeignKey('Character.Character_ID'), nullable=False)
    Storage_Location = db.Column(db.String(50), nullable=False)
    character = db.relationship('Character', back_populates='storage_locations')
    item_locations = db.relationship('ItemLocations', back_populates='storage')

    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<StorageLocation {self.StorageLocations} >" 

class Items(db.Model): 
    __tablename__: str = 'Items'   # exact table name in database
    Item_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Item_Name = db.Column(db.String(100), nullable=False, unique=True)
    Item_Type = db.Column(db.String(50), nullable=True)
    Item_Obtained_From = db.Column(db.String(50), nullable=True)
    item_locations = db.relationship('ItemLocations', back_populates='item')

    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<Item {self.Item_Name} >"
    
class ItemLocations(db.Model):
    __tablename__: str = 'ItemLocations'   # exact table name in database
    Item_ID = db.Column(db.Integer, db.ForeignKey(Items.Item_ID), primary_key=True)
    Storage_ID = db.Column(db.Integer, db.ForeignKey(StorageLocations.Storage_ID), primary_key=True)
    Quantity = db.Column(db.Integer, nullable=True)
    Quantity_HQ = db.Column(db.Integer, nullable=True)
    storage = db.relationship('StorageLocations', back_populates='item_locations')
    item = db.relationship('Items', back_populates='item_locations')

    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<ItemLocation Storage ID {self.Storage_ID} Item ID {self.Item_ID} Quantity {self.Quantity}>"

class Recipies(db.Model):
    __tablename__: str = 'Recipies'   # exact table name in database
    Recipie_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Recipie_Name = db.Column(db.String(100), nullable=False, unique=True)
    Job_ID = db.Column(db.Integer, db.ForeignKey(Jobs.Job_ID), nullable=False)
    Level_Required = db.Column(db.Integer, nullable=True)

    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<Recipie {self.Recipie_Name} >"   
    
class Ingredients(db.Model):
    __tablename__: str = 'Ingredients'   # exact table name in database
    Recipie_ID = db.Column(db.Integer, db.ForeignKey(Recipies.Recipie_ID), primary_key=True)
    Item_ID = db.Column(db.Integer, db.ForeignKey(Items.Item_ID), primary_key=True)
    Quantity = db.Column(db.Integer, nullable=False)

    # Optional: String representation for easier debugging
    def __repr__(self):
        return f"<Ingredient Recipie ID {self.Recipie_ID} Item ID {self.Item_ID} Quantity Required {self.Quantity_Required}>"