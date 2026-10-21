if (!Auth.exigirLogin()) throw new Error('Login necessário');
Auth.mostrarUsuario();
document.getElementById('botaoSair').addEventListener('click',()=>Auth.sair());
let idEdicao=null;
const form=document.getElementById('formTatuador');
async function carregarOpcoes() {
  const [rs,re]=await Promise.all([Auth.fetch(`${API_URL}/senioridade`),Auth.fetch(`${API_URL}/estilos`)]);
  const s=await rs.json(), e=await re.json();
  if(!rs.ok||!re.ok)throw new Error('Falha ao carregar senioridades ou estilos.');
  document.getElementById('idsenioridade').innerHTML=s.map(x=>`<option value="${x.idsenioridade}">${x.nome}</option>`).join('');
  document.getElementById('opcoesEstilos').innerHTML=e.map(x=>`<label class="form-check me-3"><input class="form-check-input" type="checkbox" value="${x.idestilo}"> <span class="form-check-label">${x.descricao}</span></label>`).join('');
}
async function carregar() {
  const r=await Auth.fetch(`${API_URL}/tatuadores`);
  const d=await r.json();
  if(!r.ok)throw new Error(d.detail);
  const corpo=document.getElementById('lista');
  corpo.replaceChildren();
  d.forEach(x=> {
    const tr=document.createElement('tr');
    [x.idtatuador,x.nometatuador,x.cpf,x.senioridade,x.estilos||'-'].forEach(v=> {
      const td=document.createElement('td');
      td.textContent=v;
      tr.appendChild(td);
    });
    const td=document.createElement('td');
    td.innerHTML=`<button class="btn btn-sm btn-outline-primary" data-edit="${x.idtatuador}">Editar</button> <button class="btn btn-sm btn-outline-danger" data-del="${x.idtatuador}">Excluir</button>`;
    tr.appendChild(td);
    corpo.appendChild(tr);
  });
}
function dadosForm() {
  return {
    nometatuador:form.nometatuador.value.trim(), cpf:form.cpf.value.trim(), email:form.email.value.trim()||null, telefone:form.telefone.value.trim()||null, datacontratacao:form.datacontratacao.value||null, idsenioridade:Number(form.idsenioridade.value)
  };
}
form.addEventListener('submit',async e=> {
  e.preventDefault();
  try {
    const r=await Auth.fetch(`${API_URL}/tatuadores${idEdicao?'/'+idEdicao:''}`, {
      method:idEdicao?'PUT':'POST',headers: {
        'Content-Type':'application/json'
      },body:JSON.stringify(dadosForm())
    });
    const j=await r.json();
    if(!r.ok)throw new Error(j.detail);
    const id=idEdicao||j.idtatuador;
    const estilos=[...document.querySelectorAll('#opcoesEstilos input:checked')].map(x=>Number(x.value));
    const re=await Auth.fetch(`${API_URL}/tatuadores/${id}/estilos`, {
      method:'PUT',headers: {
        'Content-Type':'application/json'
      },body:JSON.stringify({
        estilos
      })
    });
    const je=await re.json();
    if(!re.ok)throw new Error(je.detail);
    idEdicao=null;
    form.reset();
    await carregar();
  } catch(err) {
    alert(`Erro ao salvar tatuador: ${err.message}`);
  }
});
document.getElementById('lista').addEventListener('click',async e=> {
  try {
    if(e.target.dataset.edit) {
      const id=e.target.dataset.edit;
      const [r,re]=await Promise.all([Auth.fetch(`${API_URL}/tatuadores/${id}`),Auth.fetch(`${API_URL}/tatuadores/${id}/estilos`)]);
      const j=await r.json(),ids=await re.json();
      if(!r.ok)throw new Error(j.detail);
      idEdicao=j.idtatuador;
      ['nometatuador','cpf','email','telefone','datacontratacao','idsenioridade'].forEach(k=>form[k].value=j[k]||'');
      document.querySelectorAll('#opcoesEstilos input').forEach(x=>x.checked=ids.includes(Number(x.value)));
      window.scrollTo({
        top:0,behavior:'smooth'
      });
    }
    if(e.target.dataset.del&&confirm('Excluir este tatuador?')) {
      const r=await Auth.fetch(`${API_URL}/tatuadores/${e.target.dataset.del}`, {
        method:'DELETE'
      });
      const j=await r.json();
      if(!r.ok)throw new Error(j.detail);
      await carregar();
    }
  } catch(err) {
    alert(`Erro ao processar tatuador: ${err.message}`);
  }
});
document.getElementById('botaoCancelar').addEventListener('click',()=> {
  idEdicao=null;
  form.reset();
  document.querySelectorAll('#opcoesEstilos input').forEach(x=>x.checked=false);
});
(async()=> {
  try {
    await carregarOpcoes();
    await carregar();
  } catch(e) {
    alert(`Erro ao iniciar tatuadores: ${e.message}`);
  }
})();
