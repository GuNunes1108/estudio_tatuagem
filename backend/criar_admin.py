# ============================================================
# criar_admin.py — criação segura do primeiro administrador
# Descrição: cria um usuário admin sem expor senha no código.
# Como rodar: python criar_admin.py (com o ambiente virtual ativo).
# ============================================================
import getpass
import bcrypt
from database import obter_conexao

# Solicita os dados, gera o hash da senha e salva a conta administradora.
def criar_administrador():
    nome = input("Nome do administrador: ").strip()
    email = input("E-mail do administrador: ").strip().lower()
    senha = getpass.getpass("Senha (mínimo 10 caracteres): ")
    confirmar = getpass.getpass("Repita a senha: ")
    if not nome or not email or "@" not in email:
        print("Informe um nome e um e-mail válido.")
        return
    if len(senha) < 10:
        print("A senha precisa ter pelo menos 10 caracteres.")
        return
    if senha != confirmar:
        print("As senhas não são iguais.")
        return
    # bcrypt transforma a senha em hash; a senha original não é gravada.
    hash_senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conexao = None
    cursor = None
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO usuario (nome, email, senha, tipo) VALUES (%s, %s, %s, 'admin')", (nome, email, hash_senha))
        conexao.commit()
        print("Administrador criado com sucesso. Guarde a senha em local seguro.")
    except Exception as erro:
        if conexao:
            conexao.rollback()
        print(f"Não foi possível criar o administrador: {erro}")
    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()

if __name__ == "__main__":
    criar_administrador()
