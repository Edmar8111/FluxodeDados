from flask import Blueprint, request, url_for, render_template
from flaskJWT import token_generate

#simula a geração de token pro usuario // sera uma variavel self para verificação dos acessos e contabilizando o tempo de ativo
#token_user=token_generate.gerar_token({'nome':'NOME_USER','email':'user@test'})

bp=Blueprint('minhas_rotas', __name__)


@bp.errorhandler(404)
def page_not_found(e):
    return 'Error', 404

@bp.route('/', methods=['GET'])
def init_page():
    #metodo para verificação e validação do timer
    #print(token_generate.verificar_token(token_user))
    
    if request.method=='GET':
        return render_template('base.html')
    else:
        return page_not_found('')
@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        pass
    else:
        return render_template('html/login_page.html')

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        pass
    else:
        return render_template('html/login_page.html', key_register=1)