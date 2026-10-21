const Auth = {
  token() {
    return localStorage.getItem('token');
  },
  usuario() {
    try {
      return JSON.parse(localStorage.getItem('usuario') || 'null');
    } catch {
      return null;
    }
  },
  sair() {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    window.location.href = 'login.html';
  },
  exigirLogin() {
    if (!this.token()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },
  exigirAdmin() {
    if (!this.exigirLogin()) return false;
    if (this.usuario()?.tipo !== 'admin') {
      alert('Apenas administradores podem cadastrar usuários.');
      window.location.href = 'dashboard.html';
      return false;
    }
    return true;
  },
  async fetch(url, opcoes = {
  }) {
    const headers = {
      ...(opcoes.headers || {
      })
    };
    if (this.token()) headers.Authorization = `Bearer ${this.token()}`;
    const resposta = await fetch(url, {
      ...opcoes, headers
    });
    if (resposta.status === 401) {
      this.sair();
      throw new Error('Sua sessão expirou. Entre novamente.');
    }
    return resposta;
  },
  mostrarUsuario() {
    const el = document.getElementById('usuarioAtual');
    if (el) {
      const u = this.usuario();
      el.textContent = u ? `${u.nome} (${u.tipo})` : '';
    }
  }
};
