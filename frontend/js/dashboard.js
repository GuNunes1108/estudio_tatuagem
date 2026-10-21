if (Auth.exigirLogin()) {
  Auth.mostrarUsuario();
  const usuario = Auth.usuario();
  const atalho = document.getElementById('atalhoCadastro');
  if (atalho && usuario?.tipo !== 'admin') atalho.classList.add('d-none');
  document.getElementById('botaoSair').addEventListener('click', () => Auth.sair());
}
