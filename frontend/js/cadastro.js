if (Auth.exigirAdmin()) Auth.mostrarUsuario();
const seletorTipo = document.getElementById('tipo');
const campoIdCliente = document.getElementById('campoIdCliente');
seletorTipo.addEventListener('change', () => {
  campoIdCliente.classList.toggle('d-none', seletorTipo.value !== 'cliente');
});
document.getElementById('formCadastro').addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const aviso = document.getElementById('aviso');
  const dados = {
    nome: document.getElementById('nome').value.trim(), email: document.getElementById('email').value.trim(), senha: document.getElementById('senha').value, tipo: document.getElementById('tipo').value, idcliente: document.getElementById('tipo').value === 'cliente' ? Number(document.getElementById('idcliente').value) : null
  };
  try {
    const resposta = await Auth.fetch(`${API_URL}/usuarios`, {
      method:'POST', headers: {
        'Content-Type':'application/json'
      }, body:JSON.stringify(dados)
    });
    const resultado = await resposta.json();
    if (!resposta.ok) throw new Error(resultado.detail || 'Falha ao cadastrar usuário.');
    aviso.className='alert alert-success';
    aviso.textContent='Usuário cadastrado com sucesso.';
    evento.target.reset();
  } catch (erro) {
    aviso.className='alert alert-danger';
    aviso.textContent=`Erro ao cadastrar usuário: ${erro.message}`;
  }
});
