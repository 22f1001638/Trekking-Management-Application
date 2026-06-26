import os


class Config:

    SQLALCHEMY_DATABASE_URI = "sqlite:///trek.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False