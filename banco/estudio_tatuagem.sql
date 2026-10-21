-- ============================================================
-- estudio_tatuagem.sql — estrutura completa do banco de dados
-- Descrição: tabelas e dados demonstrativos para o sistema.
-- Como usar: importar pelo phpMyAdmin com o MySQL do XAMPP ativo.
-- ============================================================
CREATE DATABASE IF NOT EXISTS estudio_tatuagem
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE estudio_tatuagem;

CREATE TABLE IF NOT EXISTS senioridade (
    idsenioridade INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estilo (
    idestilo INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tatuador (
    idtatuador INT AUTO_INCREMENT PRIMARY KEY,
    nometatuador VARCHAR(100) NOT NULL,
    cpf CHAR(11) NOT NULL UNIQUE,
    email VARCHAR(100) NULL,
    telefone VARCHAR(20) NULL,
    datacontratacao DATE NULL,
    idsenioridade INT NOT NULL,
    CONSTRAINT fk_tatuador_senioridade FOREIGN KEY (idsenioridade)
      REFERENCES senioridade(idsenioridade) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cliente (
    idcliente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf CHAR(11) NOT NULL UNIQUE,
    telefone VARCHAR(20) NULL,
    datacadastro DATE NULL,
    cidade VARCHAR(100) NULL,
    uf CHAR(2) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tatuador_estilo (
    idtatuador INT NOT NULL,
    idestilo INT NOT NULL,
    dataestilo DATE NULL,
    PRIMARY KEY (idtatuador, idestilo),
    CONSTRAINT fk_te_tatuador FOREIGN KEY (idtatuador)
      REFERENCES tatuador(idtatuador) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_te_estilo FOREIGN KEY (idestilo)
      REFERENCES estilo(idestilo) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS agendamento (
    idagendamento INT AUTO_INCREMENT PRIMARY KEY,
    idcliente INT NOT NULL,
    idtatuador INT NOT NULL,
    dataagendamento DATE NOT NULL,
    horaagendamento TIME NOT NULL,
    descricaotatuagem TEXT NULL,
    desenhoaprovado VARCHAR(255) NULL,
    valortatuagem DECIMAL(10,2) NULL,
    status ENUM('pendente','confirmado','concluido','cancelado') NOT NULL DEFAULT 'pendente',
    CONSTRAINT fk_ag_cliente FOREIGN KEY (idcliente)
      REFERENCES cliente(idcliente) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_ag_tatuador FOREIGN KEY (idtatuador)
      REFERENCES tatuador(idtatuador) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuario (
    idusuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('admin','funcionario','cliente') NOT NULL DEFAULT 'funcionario',
    idcliente INT NULL,
    CONSTRAINT fk_usuario_cliente FOREIGN KEY (idcliente)
      REFERENCES cliente(idcliente) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- Dados de exemplo: INSERT IGNORE permite executar o script mais de uma vez.
INSERT IGNORE INTO senioridade (idsenioridade, nome) VALUES
 (1, 'Júnior'), (2, 'Pleno'), (3, 'Sênior');
INSERT IGNORE INTO estilo (idestilo, descricao) VALUES
 (1, 'Blackwork'), (2, 'Aquarela'), (3, 'Realismo'), (4, 'Old School');
INSERT IGNORE INTO tatuador (idtatuador, nometatuador, cpf, email, telefone, datacontratacao, idsenioridade) VALUES
 (1, 'Lucas Mendes', '11111111111', 'lucas@estudio.com', '11999990001', '2020-03-01', 3),
 (2, 'Carla Souza', '22222222222', 'carla@estudio.com', '11999990002', '2022-06-15', 2),
 (3, 'Pedro Lima', '33333333333', 'pedro@estudio.com', '11999990003', '2024-01-10', 1);
INSERT IGNORE INTO cliente (idcliente, nome, cpf, telefone, datacadastro, cidade, uf) VALUES
 (1, 'Ana Silva', '44444444444', '11988880001', '2024-01-15', 'São Paulo', 'SP'),
 (2, 'Bruno Costa', '55555555555', '31988880002', '2024-03-22', 'Belo Horizonte', 'MG');
INSERT IGNORE INTO tatuador_estilo (idtatuador, idestilo, dataestilo) VALUES
 (1, 1, '2020-03-01'), (1, 3, '2021-05-10'), (2, 2, '2022-06-15'), (3, 4, '2024-01-10');
INSERT IGNORE INTO agendamento (idagendamento, idcliente, idtatuador, dataagendamento, horaagendamento, descricaotatuagem, valortatuagem, status) VALUES
 (1, 1, 1, '2026-11-10', '14:00:00', 'Mandala no braço', 350.00, 'pendente'),
 (2, 2, 2, '2026-11-11', '10:00:00', 'Rosa aquarela no ombro', 200.00, 'pendente');
