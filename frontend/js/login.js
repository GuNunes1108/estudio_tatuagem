document.getElementById('formLogin').addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const aviso = document.getElementById('aviso');
  aviso.textContent = 'Verificando dados...';
  aviso.className = 'alert alert-info';
  try {
    const resposta = await fetch(`${API_URL}/login`, {
      method: 'POST', headers: {
        'Content-Type':'application/json'
      }, body: JSON.stringify({
        email: document.getElementById('email').value.trim(), senha: document.getElementById('senha').value
      })
    });
    const resultado = await resposta.json();
    if (!resposta.ok) throw new Error(resultado.detail || 'Não foi possível entrar.');
    localStorage.setItem('token', resultado.access_token);
    localStorage.setItem('usuario', JSON.stringify(resultado.usuario));
    window.location.href = 'dashboard.html';
  } catch (erro) {
    aviso.textContent = `Erro no login: ${erro.message}`;
    aviso.className = 'alert alert-danger';
  }
});
