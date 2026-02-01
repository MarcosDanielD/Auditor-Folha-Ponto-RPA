# 🔍 Auditor de Ponto Inteligente (RPA)

> **Automação de Departamento Pessoal:** De 3 horas de conferência manual para menos de 1 minuto de processamento automatizado.

## 📄 Sobre o Projeto
Este projeto nasceu de uma necessidade real no meu setor de Departamento Pessoal. A conferência manual de espelhos de ponto (cartões ponto) em arquivos PDF extensos (300+ páginas) é uma tarefa repetitiva, exaustiva e propensa a falhas humanas.

Desenvolvi este script em Python para atuar como um **"auditor virtual"**, lendo cada linha do PDF, interpretando regras de negócio e gerando um relatório instantâneo com as divergências.

### O Problema Resolvido
No meu cotidiano, preciso verificar situações críticas, como:
* Funcionários com **mais de 2 horas extras** na jornada (limite legal).
* Faltas sem justificativa ou abono.
* Erros de registro de ponto.

Antes, essa conferência levava de 2 a 3 horas. Com o script, o tempo caiu para **no máximo 1 minuto**, garantindo que nada passe despercebido ("passar algo para trás").

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.x
* **Bibliotecas:** `pdfplumber` (Extração de dados), `re` (RegEx para tratamento de texto).
* **Conceitos:** Manipulação de Arquivos PDF, Lógica de Programação, Tratamento de Exceções, Automação de Processos (RPA).

## 📊 Impacto e Resultados
* 🚀 **Produtividade:** Redução de ~99% no tempo de conferência.
* 🎯 **Precisão:** 100% de assertividade na detecção de falhas configuradas.
* 📈 **Escalabilidade:** O script pode processar múltiplos arquivos de diferentes filiais em sequência.

## ⚙️ Como Executar

### Pré-requisitos
* Python 3 instalado.
* Biblioteca `pdfplumber`.

### Instalação
No terminal, instale a dependência necessária:

```bash
pip install pdfplumber
