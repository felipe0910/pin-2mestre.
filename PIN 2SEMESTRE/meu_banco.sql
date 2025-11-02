-- Cria o banco (se ainda não existir)
CREATE DATABASE IF NOT EXISTS meu_banco;

-- Seleciona o banco
USE meu_banco;

-- Criação das tabelas
CREATE TABLE IF NOT EXISTS alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50),
    sobrenome VARCHAR(50),
    data_nascimento DATE,
    ra VARCHAR(20) UNIQUE,
    email VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ra VARCHAR(20) UNIQUE,
    senha VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS notas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_aluno INT,
    np1 FLOAT,
    np2 FLOAT,
    pin FLOAT,
    media FLOAT,
    situacao VARCHAR(20),
    FOREIGN KEY (id_aluno) REFERENCES alunos(id)
);
