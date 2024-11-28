from peewee import CharField, Model, Proxy

db_proxy = Proxy()


# Models
class BaseModel(Model):
    class Meta:
        database = db_proxy


class WebSite(BaseModel):
    hostname = CharField(unique=True)
    base_url = CharField(unique=True)
