if (!Auth.exigirLogin()) throw new Error('Login necessário');
Auth.mostrarUsuario();
document.getElementById('botaoSair').addEventListener('click',()=>Auth.sair());
let idEdicao=null;
const form=document.getElementById('formItem');
async function carregar() {
  const r=await Auth.fetch(`${API_URL}/senioridade`);
  const d=await r.json();
  if(!r.ok)throw new Error(d.detail);
  const corpo=document.getElementById('lista');
  corpo.replaceChildren();
  d.forEach(x=> {
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${x.idsenioridade}</td><td></td><td><button class="btn btn-sm btn-outline-primary" data-edit="${x.idsenioridade}">Editar</button> <button class="btn btn-sm btn-outline-danger" data-del="${x.idsenioridade}">Excluir</button></td>`;
    tr.children[1].textContent=x.nome;
    corpo.appendChild(tr);
  });
}
form.addEventListener('submit',async e=> {
  e.preventDefault();
  try {
    const r=await Auth.fetch(`${API_URL}/senioridade${idEdicao?'/'+idEdicao:''}`, {
      method:idEdicao?'PUT':'POST',headers: {
        'Content-Type':'application/json'
      },body:JSON.stringify({
        nome:form.nome.value.trim()
      })
    });
    const j=await r.json();
    if(!r.ok)throw new Error(j.detail);
    idEdicao=null;
    form.reset();
    await carregar();
  } catch(err) {
    alert(`Erro ao salvar senioridade: ${err.message}`);
  }
});
document.getElementById('lista').addEventListener('click',async e=> {
  try {
    if(e.target.dataset.edit) {
      const r=await Auth.fetch(`${API_URL}/senioridade/${e.target.dataset.edit}`);
      const j=await r.json();
      if(!r.ok)throw new Error(j.detail);
      idEdicao=j.idsenioridade;
      form.nome.value=j.nome;
    }
    if(e.target.dataset.del&&confirm('Excluir esta senioridade?')) {
      const r=await Auth.fetch(`${API_URL}/senioridade/${e.target.dataset.del}`, {
        method:'DELETE'
      });
      const j=await r.json();
      if(!r.ok)throw new Error(j.detail);
      await carregar();
    }
  } catch(err) {
    alert(`Erro ao processar senioridade: ${err.message}`);
  }
});
document.getElementById('botaoCancelar').addEventListener('click',()=> {
  idEdicao=null;
  form.reset();
});
carregar().catch(e=>alert(`Erro ao carregar senioridades: ${e.message}`));
