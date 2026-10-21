const formLogin = document.getElementById('formLogin');

formLogin.addEventListener('submit', async (evento) => {
  evento.preventDefault();

  const aviso = document.getElementById('aviso');
  const botao = formLogin.querySelector('button[type="submit"]');
  const email = document.getElementById('email').value.trim().toLowerCase();
  const senha = document.getElementById('senha').value;

  aviso.className = 'alert alert-info';
  aviso.textContent = 'Verificando seus dados...';
  botao.disabled = true;

  try {
    const resposta = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, senha })
    });

    let resultado;
    try {
      resultado = await resposta.json();
    } catch {
      throw new Error('A API respondeu em um formato inesperado.');
    }

    if (!resposta.ok) {
      const detalhe = resultado.detail;
      throw new Error(typeof detalhe === 'string' ? detalhe : 'Confira o e-mail e a senha.');
    }

    if (!resultado.access_token || !resultado.usuario) {
      throw new Error('A API não retornou os dados de acesso esperados.');
    }

    localStorage.setItem('token', resultado.access_token);
    localStorage.setItem('usuario', JSON.stringify(resultado.usuario));
    window.location.href = 'dashboard.html';
  } catch (erro) {
    aviso.className = 'alert alert-danger';
    aviso.textContent = erro instanceof TypeError
      ? 'Não foi possível conectar à API. Confira se o backend está rodando em http://localhost:8000.'
      : `Erro no login: ${erro.message}`;
  } finally {
    botao.disabled = false;
  }
});
