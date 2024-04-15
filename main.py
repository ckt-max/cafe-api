from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
secret_api_key = "klsfld"
app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def random_cafe():
    cafe = random.choice(db.session.execute(db.select(Cafe)).scalars().all())
    dictionary = cafe.__dict__
    del dictionary['_sa_instance_state']
    return jsonify(dictionary)

@app.route("/all", methods=['GET'])
def all():
    cafe_list = db.session.execute(db.select(Cafe)).scalars().all()
    main_dict={}
    i=0
    for cafe in cafe_list:
        dictionary = cafe.__dict__
        del dictionary['_sa_instance_state']
        main_dict[i]=dictionary
        i+=1
    return jsonify(main_dict)

# searching cafe by location
@app.route('/search', methods=['GET'])
def search():
    query_loc = request.args.get("loc")
    cafe_list = db.session.execute(db.select(Cafe).where(Cafe.location==query_loc)).scalars().all()
    if len(cafe_list) == 0:
        return {
            "error": {
                "Not Found": "Sorry, we don't have a cafe at that location."
            }
        }
    else:
        i=0
        main_dict = {}
        for cafe in cafe_list:
            dictionary = cafe.__dict__
            del dictionary['_sa_instance_state']
            main_dict[i] = dictionary
            i += 1
        return jsonify(main_dict),404
# HTTP POST - Create Record
@app.route('/add',methods=['GET','POST'])
def add():
    new_cafe = Cafe(
                    name=request.args.get('name'),
                    map_url=request.args.get('map_url'),
                    img_url=request.args.get('img_url'),
                    location=request.args.get('location'),
                    has_sockets= bool(request.args.get('has_sockets')) ,
                    has_toilet=bool(request.args.get('has_toilet')) ,
                    has_wifi= bool( request.args.get('has_wifi')),
                    can_take_calls=bool(request.args.get('can_take_calls')) ,
                    seats=request.args.get('seats'),
                    coffee_price=request.args.get('coffee_price'))

    db.session.add(new_cafe)
    db.session.commit()
    return jsonify({
        'response':{
            'Success': 'Successfully added the new cafe.'
        }
    })
# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods = ['GET','PATCH'])
def update_price(cafe_id):
    cafe_row = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if cafe_row == None:
        return {
            "error": "Sorry a cafe with that id was not found on the database"
        },200
    else:

        new_coffee_price =  request.args.get('new_coffee_price')
        cafe_row.price = new_coffee_price
        db.session.commit()
        return{
            "Success": "Successfully updated the price."
        },404



# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['GET','DELETE'])
def delete(cafe_id):

    if request.args.get('api-key')==secret_api_key:
        cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe == None:
            return {
                'error':{
                    "Not Found":'Sorry a cafe with that id was not found in the database'
                }
            },403

        else:
            db.session.delete(cafe)
            db.session.commit()
            return {
                'Success': "Cafe deleted successfully"
            }
    else:
        return {
            'error': "Sorry, that's not allowed. Make sure you have the correct api_key"
        }


if __name__ == '__main__':
    app.run(debug=True)
