if (!Auth.exigirLogin()) throw new Error('Login necessário');
Auth.mostrarUsuario();
document.getElementById('botaoSair').addEventListener('click',()=>Auth.sair());
let idEdicao=null;
const form=document.getElementById('formAgendamento');
async function carregarOpcoes() {
  const [rc,rt]=await Promise.all([Auth.fetch(`${API_URL}/clientes`),Auth.fetch(`${API_URL}/tatuadores`)]);
  const c=await rc.json(), t=await rt.json();
  if(!rc.ok||!rt.ok)throw new Error('Cadastre clientes e tatuadores antes dos agendamentos.');
  document.getElementById('idcliente').innerHTML=c.map(x=>`<option value="${x.idcliente}">${x.nome}</option>`).join('');
  document.getElementById('idtatuador').innerHTML=t.map(x=>`<option value="${x.idtatuador}">${x.nometatuador}</option>`).join('');
}
async function carregar() {
  const r=await Auth.fetch(`${API_URL}/agendamentos`);
  const d=await r.json();
  if(!r.ok)throw new Error(d.detail);
  const corpo=document.getElementById('lista');
  corpo.replaceChildren();
  d.forEach(x=> {
    const tr=document.createElement('tr');
    [x.idagendamento,x.cliente,x.tatuador,x.dataagendamento,x.horaagendamento,x.status, x.valortatuagem??'-'].forEach(v=> {
      const td=document.createElement('td');
      td.textContent=v;
      tr.appendChild(td);
    });
    const imagem=document.createElement('td');
    if(x.desenhoaprovado) {
      const a=document.createElement('a');
      a.href=`${API_URL}${x.desenhoaprovado}`;
      a.target='_blank';
      a.rel='noopener';
      a.textContent='Ver desenho';
      imagem.appendChild(a);
    } else imagem.textContent='—';
    tr.appendChild(imagem);
    const acoes=document.createElement('td');
    acoes.innerHTML=`<button class="btn btn-sm btn-outline-primary" data-edit="${x.idagendamento}">Editar</button> <button class="btn btn-sm btn-outline-danger" data-del="${x.idagendamento}">Excluir</button>`;
    tr.appendChild(acoes);
    corpo.appendChild(tr);
  });
}
function dados() {
  return {
    idcliente:Number(form.idcliente.value), idtatuador:Number(form.idtatuador.value), dataagendamento:form.dataagendamento.value, horaagendamento:form.horaagendamento.value, descricaotatuagem:form.descricaotatuagem.value.trim()||null, valortatuagem:form.valortatuagem.value?Number(form.valortatuagem.value):null, status:form.status.value||'pendente'
  };
}
form.addEventListener('submit',async e=> {
  e.preventDefault();
  try {
    const r=await Auth.fetch(`${API_URL}/agendamentos${idEdicao?'/'+idEdicao:''}`, {
      method:idEdicao?'PUT':'POST',headers: {
        'Content-Type':'application/json'
      },body:JSON.stringify(dados())
    });
    const j=await r.json();
    if(!r.ok)throw new Error(j.detail);
    const id=idEdicao||j.idagendamento;
    const arquivo=form.desenho.files[0];
    if(arquivo) {
      const fd=new FormData();
      fd.append('arquivo',arquivo);
      const ri=await Auth.fetch(`${API_URL}/agendamentos/${id}/desenho`, {
        method:'POST',body:fd
      });
      const ji=await ri.json();
      if(!ri.ok)throw new Error(ji.detail);
    }
    idEdicao=null;
    form.reset();
    document.getElementById('statusBox').classList.add('d-none');
    await carregar();
  } catch(err) {
    alert(`Erro ao salvar agendamento: ${err.message}`);
  }
});
document.getElementById('lista').addEventListener('click',async e=> {
  try {
    if(e.target.dataset.edit) {
      const r=await Auth.fetch(`${API_URL}/agendamentos/${e.target.dataset.edit}`);
      const j=await r.json();
      if(!r.ok)throw new Error(j.detail);
      idEdicao=j.idagendamento;
      ['idcliente','idtatuador','dataagendamento','horaagendamento','descricaotatuagem','valortatuagem','status'].forEach(k=>form[k].value=j[k]??'');
      document.getElementById('statusBox').classList.remove('d-none');
      window.scrollTo({
        top:0,behavior:'smooth'
      });
    }
    if(e.target.dataset.del&&confirm('Excluir este agendamento?')) {
      const r=await Auth.fetch(`${API_URL}/agendamentos/${e.target.dataset.del}`, {
        method:'DELETE'
      });
      const j=await r.json();
      if(!r.ok)throw new Error(j.detail);
      await carregar();
    }
  } catch(err) {
    alert(`Erro ao processar agendamento: ${err.message}`);
  }
});
document.getElementById('botaoCancelar').addEventListener('click',()=> {
  idEdicao=null;
  form.reset();
  document.getElementById('statusBox').classList.add('d-none');
});
(async()=> {
  try {
    await carregarOpcoes();
    await carregar();
  } catch(e) {
    alert(`Erro ao iniciar agendamentos: ${e.message}`);
  }
})();
