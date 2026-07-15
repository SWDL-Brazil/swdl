from app import create_app
from extensions import db
from models.user import User
from models.delegation import Delegation

app = create_app()

with app.app_context():
    # Remove teste antigo se existir
    u = User.query.filter_by(email='delegado@teste.com').first()
    if u:
        d = Delegation.query.filter_by(user_id=u.id).first()
        if d:
            db.session.delete(d)
        db.session.delete(u)
        db.session.commit()
        print('♻️  Delegado antigo removido.')

    # Cria usuário
    u = User(name='Ana Silva', email='delegado@teste.com', role='delegate')
    u.set_password('teste2025')
    db.session.add(u)
    db.session.flush()

    # Cria delegação com bandeira
    d = Delegation(
        user_id        = u.id,
        country        = 'Brasil',
        country_flag   = '🇧🇷',
        flag_url       = 'https://flagcdn.com/w320/br.png',
        committee      = 'cs',
        pair_name      = 'Bruno Costa',
        flag_animation = True,
    )
    db.session.add(d)
    db.session.commit()
    print('✅ Delegado criado!')
    print('   Login: delegado@teste.com')
    print('   Senha: teste2025')