from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    filiere = db.Column(db.String(100), nullable=False)  # New field
    couleur_peau = db.Column(db.String(50), nullable=False)  # New field
    niveau_etudes = db.Column(db.String(50), nullable=False)  # New field

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        name=data['name'],
        filiere=data['filiere'],  # New field
        couleur_peau=data['couleur_peau'],  # New field
        niveau_etudes=data['niveau_etudes']  # New field
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

# Other routes...

if __name__ == '__main__':
    app.run(debug=True)