if (!Auth.exigirLogin()) throw new Error('Login necessário');
Auth.mostrarUsuario();
document.getElementById('botaoSair').addEventListener('click',()=>Auth.sair());
let idEdicao=null;
const form=document.getElementById('formItem');
async function carregar() {
  const r=await Auth.fetch(`${API_URL}/estilos`);
  const d=await r.json();
  if(!r.ok)throw new Error(d.detail);
  const corpo=document.getElementById('lista');
  corpo.replaceChildren();
  d.forEach(x=> {
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${x.idestilo}</td><td></td><td><button class="btn btn-sm btn-outline-primary" data-edit="${x.idestilo}">Editar</button> <button class="btn btn-sm btn-outline-danger" data-del="${x.idestilo}">Excluir</button></td>`;
    tr.children[1].textContent=x.descricao;
    corpo.appendChild(tr);
  });
}
form.addEventListener('submit',async e=> {
  e.preventDefault();
  try {
    const r=await Auth.fetch(`${API_URL}/estilos${idEdicao?'/'+idEdicao:''}`, {
      method:idEdicao?'PUT':'POST',headers: {
        'Content-Type':'application/json'
      },body:JSON.stringify({
        descricao:form.descricao.value.trim()
      })
    });
    const j=await r.json();
    if(!r.ok)throw new Error(j.detail);
    idEdicao=null;
    form.reset();
    await carregar();
  } catch(err) {
    alert(`Erro ao salvar estilo: ${err.message}`);
  }
});
document.getElementById('lista').addEventListener('click',async e=> {
  try {
    if(e.target.dataset.edit) {
      const r=await Auth.fetch(`${API_URL}/estilos/${e.target.dataset.edit}`);
      const j=await r.json();
      if(!r.ok)throw new Error(j.detail);
      idEdicao=j.idestilo;
      form.descricao.value=j.descricao;
    }
    if(e.target.dataset.del&&confirm('Excluir este estilo?')) {
      const r=await Auth.fetch(`${API_URL}/estilos/${e.target.dataset.del}`, {
        method:'DELETE'
      });
      const j=await r.json();
      if(!r.ok)throw new Error(j.detail);
      await carregar();
    }
  } catch(err) {
    alert(`Erro ao processar estilo: ${err.message}`);
  }
});
document.getElementById('botaoCancelar').addEventListener('click',()=> {
  idEdicao=null;
  form.reset();
});
carregar().catch(e=>alert(`Erro ao carregar estilos: ${e.message}`));
