// A página de cadastro é restrita a administradores.
if (Auth.exigirAdmin()) {
  Auth.mostrarUsuario();

  const form = document.getElementById('formCadastro');
  const seletorTipo = document.getElementById('tipo');
  const campoIdCliente = document.getElementById('campoIdCliente');
  const inputIdCliente = document.getElementById('idcliente');
  const aviso = document.getElementById('aviso');

  function atualizarCampoCliente() {
    const clienteSelecionado = seletorTipo.value === 'cliente';
    campoIdCliente.classList.toggle('d-none', !clienteSelecionado);
    inputIdCliente.required = clienteSelecionado;
  }

  seletorTipo.addEventListener('change', atualizarCampoCliente);
  atualizarCampoCliente();

  const botao = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    aviso.className = 'alert alert-info';
    aviso.textContent = 'Cadastrando usuário...';
    botao.disabled = true;

    const tipo = seletorTipo.value;
    const dados = {
      nome: document.getElementById('nome').value.trim(),
      email: document.getElementById('email').value.trim().toLowerCase(),
      senha: document.getElementById('senha').value,
      tipo
    };

    if (tipo === 'cliente') {
      const idcliente = Number(inputIdCliente.value);
      if (!Number.isInteger(idcliente) || idcliente <= 0) {
        aviso.className = 'alert alert-danger';
        aviso.textContent = 'Informe um ID de cliente válido (maior que zero).';
        botao.disabled = false;
        return;
      }
      dados.idcliente = idcliente;
    }

    try {
      const resposta = await Auth.fetch(`${API_URL}/usuarios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
      });

      const resultado = await resposta.json();
      if (!resposta.ok) {
        const detalhe = resultado.detail;
        throw new Error(typeof detalhe === 'string' ? detalhe : 'Confira os campos informados.');
      }

      aviso.className = 'alert alert-success';
      aviso.textContent = resultado.mensagem || 'Usuário cadastrado com sucesso.';
      form.reset();
      atualizarCampoCliente();
    } catch (erro) {
      aviso.className = 'alert alert-danger';
      aviso.textContent = erro instanceof TypeError
        ? 'Não foi possível conectar à API. Confira se o backend está rodando.'
        : `Erro ao cadastrar usuário: ${erro.message}`;
    } finally {
      botao.disabled = false;
    }
  });

  const botaoSair = document.getElementById('botaoSair');
  if (botaoSair) botaoSair.addEventListener('click', () => Auth.sair());
}
