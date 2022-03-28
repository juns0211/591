from main.settings import db
import sqlalchemy


class House(db.Model):
    # 清單API提供的欄位
    post_id = db.Column(db.Integer, primary_key=True)
    regionid = db.Column(db.Integer)
    region_name = db.Column(db.Text)
    price = db.Column(db.Text)
    unit = db.Column(db.Text)
    section_name = db.Column(db.Text)
    street_name = db.Column(db.Text)
    address = db.Column(db.Text)
    room_str = db.Column(db.Text)
    closed = db.Column(db.Integer)
    linkman = db.Column(db.Text)
    role_name = db.Column(db.Text)
    layout = db.Column(db.Text)
    floorStr = db.Column(db.Text)
    kind_name = db.Column(db.Text)

    # 內容頁面API提供的欄位
    deposit = db.Column(db.Text)
    imName = db.Column(db.Text)
    mobile = db.Column(db.Text)
    rule = db.Column(db.Text)

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
