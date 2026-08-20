# N1 – Cifra de César + Diffie-Hellman sobre Socket TCP

Trabalho da disciplina de Criptografia Simétrica. Implementação de comunicação
cliente/servidor via **socket TCP**, com troca de chaves por **Diffie-Hellman**
e criptografia do fluxo de mensagens por uma **Cifra de César autoral**
(implementada do zero, sem bibliotecas prontas de criptografia).

Personagens da comunicação:
- **Alice** → `SimpleTCPClient.py`
- **Bob** → `SimpleTCPServer.py`

## Estrutura dos arquivos

| Arquivo               | Descrição |
|------------------------|-----------|
| `SimpleTCPServer.py`   | Servidor TCP (Bob). Faz o handshake Diffie-Hellman e recebe/decifra mensagens de Alice. |
| `SimpleTCPClient.py`   | Cliente TCP (Alice). Faz o handshake Diffie-Hellman e envia mensagens cifradas para Bob. |
| `dh.py`                 | Implementação autoral do Diffie-Hellman (chave privada, chave pública, segredo compartilhado) + teste de primalidade Miller-Rabin para o primo grande utilizado. |
| `caesar.py`             | Implementação autoral da Cifra de César (estendida para os 256 valores de byte, não só A-Z), usada para cifrar/decifrar o fluxo de mensagens. |
| `testes_primos.py`      | Adaptação dos scripts `primo fast` e `primo slow` do enunciado, em formato de função reutilizável, para testar/comparar a primalidade de números menores. |

## Como as 3 etapas do enunciado foram atendidas

### Etapa 1 – Testar client/server em máquinas distintas + Wireshark
Os dois scripts (`SimpleTCPServer.py` e `SimpleTCPClient.py`) usam `socket`
puro do Python, então já funcionam em máquinas diferentes na mesma rede —
basta rodar o servidor em uma máquina e apontar o IP dela no cliente.
**Esta etapa fica por sua conta** (rodar nas duas máquinas + gravar a captura
no Wireshark). Roteiro sugerido abaixo em "Como testar".

### Etapa 2 – Cifra de César autoral
Implementada em `caesar.py`, sem usar nenhuma biblioteca de criptografia
(`cryptography`, `hashlib`, etc.) — é a lógica clássica de "somar um
deslocamento e voltar ao início do alfabeto quando passa do limite",
só que aplicada aos 256 valores possíveis de um byte (para suportar
acentos, números, símbolos, não só letras A-Z).

### Etapa 3 – Diffie-Hellman
Implementado em `dh.py`. Servidor e cliente combinam publicamente um primo
`p` e uma raiz `g`, cada lado gera sua chave privada (nunca trafega pela
rede), calcula e envia sua chave pública, e os dois lados chegam ao mesmo
**segredo compartilhado**. Esse segredo vira o `shift` usado na Cifra de
César da Etapa 2.

### Sobre os testes de números primos (`primo fast` / `primo slow`)
O enunciado pede para "implementar o algoritmo para testar os números
primos necessários para o Diffie-Hellman", com base nos exemplos
`primo fast` e `primo slow`. Isso foi feito em `testes_primos.py`
(mesma lógica dos dois scripts, só organizada em funções), útil para
testar/comparar desempenho em números pequenos/médios.

Só que, para o Diffie-Hellman ser seguro de verdade, o número primo `p`
precisa ter centenas de dígitos — testar isso por divisão (como no
`primo fast`/`primo slow`) levaria tempo inviável (dias/anos). Por isso,
para o primo realmente usado na troca de chaves (`dh.py`), foi implementado
também, do zero, o **Teste de Primalidade de Miller-Rabin**
(`eh_primo_miller_rabin`), que é o algoritmo real usado nesses casos.
Rode `python3 dh.py` para ver a validação sendo feita.

## Como testar

### 1) Instalação
Requer apenas Python 3 (nenhuma dependência externa/pip — tudo é biblioteca
padrão: `socket`, `random`, `time`).

### 2) Rodando em uma única máquina (teste rápido)
```bash
# terminal 1
python3 SimpleTCPServer.py

# terminal 2
python3 SimpleTCPClient.py
# quando pedir o IP do servidor, digite: 127.0.0.1
```

### 3) Rodando em duas máquinas distintas (o que o enunciado pede)
```bash
# Máquina do Bob (servidor)
python3 SimpleTCPServer.py

# Máquina da Alice (cliente) — precisa saber o IP da máquina do Bob na rede
python3 SimpleTCPClient.py
# digite o IP da máquina do Bob quando solicitado, ex: 192.168.0.15
```
> Se a conexão não abrir, verifique se o firewall da máquina do Bob está
> liberando a porta `65432/TCP`.

### 4) Capturando com Wireshark
1. Abra o Wireshark **na máquina do Bob (servidor)** antes de iniciar o
   `SimpleTCPServer.py`.
2. Use o filtro: `tcp.port == 65432`
3. Inicie o servidor, depois o cliente, e troque algumas mensagens.
4. No Wireshark, observe:
   - O handshake do DH: os pacotes com `p`, `g` e as chaves públicas
     (`A` e `B`) — são valores grandes, mas **em texto legível**, pois
     esses valores realmente podem trafegar em aberto (essa é a ideia do
     Diffie-Hellman: só as chaves *privadas* nunca aparecem na rede).
   - As mensagens trocadas depois disso: os bytes aparecem
     **cifrados/ilegíveis** (é o resultado da Cifra de César aplicada),
     comprovando que a criptografia está funcionando fim a fim.

### 5) Testando o módulo de primos isoladamente
```bash
python3 testes_primos.py
# digite um N, ex: 104729
# compara o tempo do primo_fast x primo_slow para o mesmo número
```
