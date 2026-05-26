<div align="center">

# 🔄 GeradorNatural

### Transpilador Natural/Adabas → Pseudocódigo em Português

**Converte código-fonte Natural (Software AG) em pseudocódigo algorítmico legível,  
estilo Portugol/VisuAlg, pronto para documentação e revisão de lógica.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/Licença-MIT-green)
![Testes](https://img.shields.io/badge/Testes-33%20passando-brightgreen)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

</div>

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Exemplo Completo](#-exemplo-completo)
- [Instruções Suportadas](#-instruções-natural-suportadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Executar os Testes](#-executar-os-testes)
- [Contribuindo](#-contribuindo)

---

## 🎯 Visão Geral

O **GeradorNatural** lê arquivos `.txt` contendo código-fonte **Natural/Adabas** (Software AG)
e gera automaticamente um arquivo `.algo` com o **pseudocódigo algorítmico em português**,
preservando a lógica original, comentários e estrutura de blocos.

**O que é transformado:**

| Código Natural                  | Pseudocódigo gerado                |
|---------------------------------|------------------------------------|
| `IF #SAL > 3000`                | `SE #SAL > 3000 ENTÃO`             |
| `MOVE 5000 TO #SAL`             | `#SAL ← 5000`                      |
| `COMPUTE #X = #A * #B`         | `#X ← #A * #B`                     |
| `ADD 1 TO #CONT`               | `#CONT ← #CONT + 1`                |
| `FIND EMP WITH NAME = 'SILVA'` | `BUSCAR em EMP WHERE NAME = 'SILVA'`|
| `READ EMP BY NAME`             | `LER EMP BY NAME`                  |
| `PERFORM CALCULAR-IMPOSTO`     | `EXECUTAR CALCULAR-IMPOSTO`        |
| `WRITE 'Resultado: ' #X`       | `ESCREVER 'Resultado: ' #X`        |
| `* comentário`                 | `// comentário`                    |
| `DEFINE SUBROUTINE CALC`       | Seção separada ao final            |

---

## 🔧 Pré-requisitos

- **Python 3.11 ou superior**
- Nenhuma biblioteca externa de runtime (apenas `pytest` para testes)

Verifique sua versão do Python:

```bash
python --version
```

---

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/robertohbr1/GeradorNatural.git
cd GeradorNatural
```

### 2. (Opcional) Crie e ative um ambiente virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências de desenvolvimento

```bash
pip install -r requirements.txt
```

> ⚠️ O transpilador em si **não tem dependências de runtime**. O `requirements.txt`
> instala apenas o `pytest` para rodar os testes.

---

## 🚀 Uso

### Sintaxe básica

```bash
python main.py <arquivo_entrada.txt> [OPÇÕES]
```

### Opções disponíveis

| Opção                    | Descrição                                               | Padrão                    |
|--------------------------|---------------------------------------------------------|---------------------------|
| `<arquivo_entrada.txt>`  | Arquivo `.txt` com código-fonte Natural **(obrigatório)**| —                         |
| `--output`, `-o`         | Caminho do arquivo de saída                             | mesmo nome, extensão `.algo` |
| `--encoding`, `-e`       | Codificação do arquivo de entrada                       | `cp1252` (padrão mainframe)|

### Exemplos de uso

```bash
# Uso mais simples: gera programa.algo no mesmo diretório
python main.py programa.txt

# Especificar arquivo de saída
python main.py programa.txt --output documentacao/algoritmo.algo

# Arquivo com codificação UTF-8
python main.py programa.txt --encoding utf-8

# Arquivo com codificação Latin-1
python main.py programa.txt --encoding latin-1

# Forma abreviada das opções
python main.py programa.txt -o saida.algo -e cp1252
```

### Erros comuns

| Mensagem de erro                          | Causa e solução                                         |
|-------------------------------------------|---------------------------------------------------------|
| `Erro: arquivo não encontrado: x.txt`    | Verifique o caminho do arquivo de entrada              |
| `Erro de codificação...`                  | Tente `--encoding utf-8` ou `--encoding latin-1`       |
| `Erro de parse: Linha N: ...`             | Verifique a estrutura do bloco indicado na linha N     |

---

## 📄 Exemplo Completo

### Arquivo de entrada: `folha.txt`

```natural
* Cálculo de folha de pagamento
DEFINE DATA LOCAL
  1 #SALARIO_BASE (N10.2)
  1 #PERCENTUAL   (N5.4)
  1 #DESCONTO     (N10.2)
  1 #LIQUIDO      (N10.2)
END-DEFINE
*
MOVE 8500.00 TO #SALARIO_BASE
*
IF #SALARIO_BASE > 5000
  COMPUTE #PERCENTUAL = 0.275
ELSE
  COMPUTE #PERCENTUAL = 0.150
END-IF
*
PERFORM CALCULAR-DESCONTO
COMPUTE #LIQUIDO = #SALARIO_BASE - #DESCONTO
WRITE 'Salario Base:  ' #SALARIO_BASE
WRITE 'Desconto:      ' #DESCONTO
WRITE 'Salario Liq.:  ' #LIQUIDO
END
*
DEFINE SUBROUTINE CALCULAR-DESCONTO
  MULTIPLY #SALARIO_BASE BY #PERCENTUAL
  MOVE #PERCENTUAL TO #DESCONTO
END-SUBROUTINE
```

### Comando

```bash
python main.py folha.txt
```

### Arquivo gerado: `folha.algo`

```
// Cálculo de folha de pagamento
VARIÁVEIS LOCAIS:
  1 #SALARIO_BASE (N10.2)
  1 #PERCENTUAL   (N5.4)
  1 #DESCONTO     (N10.2)
  1 #LIQUIDO      (N10.2)

#SALARIO_BASE ← 8500.00

SE #SALARIO_BASE > 5000 ENTÃO
  #PERCENTUAL ← 0.275
SENÃO
  #PERCENTUAL ← 0.150
FIM-SE

EXECUTAR CALCULAR-DESCONTO
#LIQUIDO ← #SALARIO_BASE - #DESCONTO
ESCREVER 'Salario Base:  ' #SALARIO_BASE
ESCREVER 'Desconto:      ' #DESCONTO
ESCREVER 'Salario Liq.:  ' #LIQUIDO
FIM

────────────────────────────────────────────────────────────
SUBROTINAS
────────────────────────────────────────────────────────────

SUBROTINA CALCULAR-DESCONTO
  #SALARIO_BASE ← #SALARIO_BASE * #PERCENTUAL
  #DESCONTO ← #PERCENTUAL
FIM-SUBROTINA
```

---

## 📘 Instruções Natural Suportadas

### Controle de Fluxo

| Instrução Natural            | Pseudocódigo              |
|------------------------------|---------------------------|
| `IF cond`                    | `SE cond ENTÃO`           |
| `ELSE`                       | `SENÃO`                   |
| `END-IF`                     | `FIM-SE`                  |
| `FOR #I = 1 TO N`            | `PARA #I = 1 TO N FAÇA`   |
| `END-FOR`                    | `FIM-PARA`                |
| `REPEAT`                     | `REPETIR`                 |
| `END-REPEAT`                 | `FIM-REPETIR`             |
| `ESCAPE TOP`                 | `SAIR DO TOPO DO LAÇO`    |
| `ESCAPE BOTTOM`              | `SAIR DO FUNDO DO LAÇO`   |
| `STOP`                       | `PARAR`                   |
| `TERMINATE`                  | `ENCERRAR`                |
| `END`                        | `FIM`                     |

### Acesso ao Banco de Dados (Adabas)

| Instrução Natural            | Pseudocódigo                    |
|------------------------------|---------------------------------|
| `FIND view WITH crit`        | `BUSCAR em view WHERE crit`     |
| `END-FIND`                   | `FIM-BUSCA`                     |
| `READ view BY field`         | `LER view BY field`             |
| `END-READ`                   | `FIM-LEITURA`                   |
| `HISTOGRAM view FOR field`   | `HISTOGRAMA view FOR field`     |
| `END-HISTOGRAM`              | `FIM-HISTOGRAMA`                |
| `STORE view`                 | `ARMAZENAR view`                |
| `UPDATE`                     | `ATUALIZAR`                     |
| `DELETE`                     | `EXCLUIR`                       |
| `GET view`                   | `OBTER view`                    |
| `END-TRANSACTION`            | `FIM-TRANSAÇÃO`                 |
| `BACKOUT TRANSACTION`        | `DESFAZER TRANSAÇÃO`            |

### Atribuição e Aritmética

| Instrução Natural            | Pseudocódigo                    |
|------------------------------|---------------------------------|
| `MOVE A TO B`                | `B ← A`                         |
| `COMPUTE X = expr`           | `X ← expr`                      |
| `ADD val TO var`             | `var ← var + val`               |
| `SUBTRACT val FROM var`      | `var ← var - val`               |
| `MULTIPLY var BY val`        | `var ← var * val`               |
| `DIVIDE val INTO var`        | `var ← var / val`               |
| `DIVIDE val INTO var GIVING r`| `r ← var / val`                |
| `RESET var`                  | `ZERAR var`                     |

### Entrada e Saída

| Instrução Natural            | Pseudocódigo                    |
|------------------------------|---------------------------------|
| `WRITE texto`                | `ESCREVER texto`                |
| `DISPLAY campos`             | `EXIBIR campos`                 |
| `PRINT texto`                | `IMPRIMIR texto`                |
| `INPUT var`                  | `LER var`                       |

### Subrotinas e Chamadas

| Instrução Natural            | Pseudocódigo                    |
|------------------------------|---------------------------------|
| `PERFORM nome`               | `EXECUTAR nome`                 |
| `CALL 'PROG' USING var`      | `CHAMAR 'PROG' USING var`       |
| `FETCH 'PROG'`               | `CARREGAR PROGRAMA 'PROG'`      |
| `DEFINE SUBROUTINE nome`     | Seção separada ao final         |

### Declaração de Dados

| Instrução Natural            | Pseudocódigo                    |
|------------------------------|---------------------------------|
| `DEFINE DATA LOCAL`          | `VARIÁVEIS LOCAIS:`             |
| `DEFINE DATA GLOBAL`         | `VARIÁVEIS GLOBAIS:`            |
| `DEFINE DATA PARAMETER`      | `PARÂMETROS:`                   |
| `END-DEFINE`                 | *(fecha o bloco)*               |

### Comentários

| Instrução Natural            | Pseudocódigo                    |
|------------------------------|---------------------------------|
| `* texto`                    | `// texto`                      |
| `/* texto inline`            | *(removido da linha)*           |
| Linhas não reconhecidas      | `/* linha original */`          |

---

## 🗂 Estrutura do Projeto

```
GeradorNatural/
│
├── nat2algo/                  # Pacote principal do transpilador
│   ├── __init__.py
│   ├── mappings.py            # Tabela de mapeamento Natural → português
│   ├── lexer.py               # Tokenização linha a linha
│   ├── parser.py              # Construção da AST (árvore de instruções)
│   └── emitter.py             # Geração do pseudocódigo a partir da AST
│
├── tests/                     # Suíte de testes automatizados
│   ├── __init__.py
│   ├── test_lexer.py          # Testes de tokenização
│   ├── test_parser.py         # Testes de estrutura de blocos
│   ├── test_emitter.py        # Testes de saída final (incluindo golden files)
│   └── fixtures/              # Programas Natural de exemplo
│       ├── sample_basic.txt       # IF/ELSE, MOVE, COMPUTE, WRITE
│       ├── sample_find.txt        # READ loop, ADD, DISPLAY
│       └── sample_subroutine.txt  # PERFORM, DEFINE SUBROUTINE
│
├── main.py                    # Ponto de entrada da CLI
├── requirements.txt           # Dependências (apenas pytest)
└── README.md                  # Esta documentação
```

### Arquitetura interna

```
arquivo .txt
     │
     ▼
 lexer.py          → lista de Token(line_no, keyword, args, raw)
     │
     ▼
 parser.py         → Program(body=[ASTNode...], subroutines=[ASTNode...])
     │
     ▼
 emitter.py        → string de pseudocódigo em português
     │
     ▼
 arquivo .algo
```

---

## 🧪 Executar os Testes

```bash
# Rodar todos os testes com detalhes
python -m pytest tests/ -v

# Rodar apenas um módulo de testes
python -m pytest tests/test_emitter.py -v

# Ver cobertura resumida
python -m pytest tests/ --tb=short
```

**Resultado esperado:** `33 passed`

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para adicionar suporte a novas instruções Natural:

1. Abra o arquivo [`nat2algo/mappings.py`](nat2algo/mappings.py)
2. Adicione a instrução no dicionário correto (`CONDITIONAL`, `LOOP`, `DB_ACCESS`, etc.)
3. Se a instrução abre um bloco, adicione sua keyword em `BLOCK_OPENERS` e seu fechador em `_closer_for()` no [`parser.py`](nat2algo/parser.py)
4. Escreva um teste em [`tests/test_emitter.py`](tests/test_emitter.py)
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

<div align="center">
Desenvolvido por <a href="https://github.com/robertohbr1">Roberto Brum</a>
</div>
