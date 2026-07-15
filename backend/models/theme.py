from extensions import db

class Theme(db.Model):
    """
    Representa um Tema / Debate (anteriormente Comitê).
    Criado dinamicamente pelos administradores (ex: 'Estreito de Ormuz').
    """
    __tablename__ = 'themes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(300), default='')  # URL da imagem

    def __repr__(self):
        return f"<Theme {self.name}>"
