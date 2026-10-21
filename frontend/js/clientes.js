if (!Auth.exigirLogin()) throw new Error('Login necessário');
Auth.mostrarUsuario();
document.getElementById('botaoSair').addEventListener('click', () => Auth.sair());
let idEmEdicao = null;
const form = document.getElementById('formCliente');
const campos = ['nome','cpf','telefone','cidade','uf'];
async function carregarClientes() {
  const r = await Auth.fetch(`${API_URL}/clientes`);
  const dados = await r.json();
  if (!r.ok) throw new Error(dados.detail || 'Falha ao listar clientes.');
  const corpo = document.getElementById('listaClientes');
  corpo.replaceChildren();
  dados.forEach(c => {
    const tr = document.createElement('tr');
    [c.idcliente,c.nome,c.cpf,c.telefone || '-',c.cidade || '-',c.uf || '-'].forEach(v => {
      const td=document.createElement('td');
      td.textContent=v;
      tr.appendChild(td);
    });
    const td=document.createElement('td');
    td.innerHTML=`<button class="btn btn-sm btn-outline-primary me-1" data-editar="${c.idcliente}">Editar</button><button class="btn btn-sm btn-outline-danger" data-excluir="${c.idcliente}">Excluir</button>`;
    tr.appendChild(td);
    corpo.appendChild(tr);
  });
}
function novoCliente() {
  idEmEdicao=null;
  form.reset();
  document.getElementById('tituloForm').textContent='Novo cliente';
}
form.addEventListener('submit', async e => {
  e.preventDefault();
  const dados= {
    nome:form.nome.value.trim(), cpf:form.cpf.value.trim(), telefone:form.telefone.value.trim()||null, datacadastro:new Date().toISOString().slice(0,10), cidade:form.cidade.value.trim()||null, uf:form.uf.value.trim().toUpperCase()||null
  };
  try {
    const r=await Auth.fetch(`${API_URL}/clientes${idEmEdicao?'/'+idEmEdicao:''}`, {
      method:idEmEdicao?'PUT':'POST',headers: {
        'Content-Type':'application/json'
      },body:JSON.stringify(dados)
    });
    const j=await r.json();
    if(!r.ok)throw new Error(j.detail||'Falha ao salvar.');
    novoCliente();
    await carregarClientes();
  } catch(err) {
    alert(`Erro ao salvar cliente: ${err.message}`);
  }
});
document.getElementById('listaClientes').addEventListener('click', async e => {
  const editar=e.target.dataset.editar, excluir=e.target.dataset.excluir;
  try {
    if(editar) {
      const r=await Auth.fetch(`${API_URL}/clientes/${editar}`);
      const c=await r.json();
      if(!r.ok)throw new Error(c.detail);
      idEmEdicao=c.idcliente;
      campos.forEach(k=>form[k].value=c[k]||'');
      document.getElementById('tituloForm').textContent='Editar cliente';
      window.scrollTo({
        top:0,behavior:'smooth'
      });
    }
    if(excluir && confirm('Tem certeza de que deseja excluir este cliente?')) {
      const r=await Auth.fetch(`${API_URL}/clientes/${excluir}`, {
        method:'DELETE'
      });
      const j=await r.json();
      if(!r.ok)throw new Error(j.detail);
      await carregarClientes();
    }
  } catch(err) {
    alert(`Erro ao processar cliente: ${err.message}`);
  }
});
document.getElementById('botaoNovo').addEventListener('click',novoCliente);
carregarClientes().catch(err=>alert(`Erro ao carregar clientes: ${err.message}`));
