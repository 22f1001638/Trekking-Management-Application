from application.dao.trek_dao import DAO
import csv
import pandas as pd

from application.db.db import db
from application.model.TrekModel import UserTable


class CreateDefaultService:
    def __init__(self):
        pass

    def create_def_users(self):
        data=pd.read_csv(r"application\default\default_data.csv")
        values=data.to_dict(orient="records")
        check_table=DAO().get_all()
        id_list = [i.user_id for i in check_table]

        print(id_list)
        for i in values:
            user=UserTable(**i)
            if user.user_id not in id_list :
                DAO().save(user)
        for i in DAO().get_all():
            print(i.to_dict())
