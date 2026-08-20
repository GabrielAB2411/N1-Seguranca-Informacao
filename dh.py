"""
dh.py
------
Implementação AUTORAL do algoritmo de troca de chaves Diffie-Hellman.

Resumo do protocolo:
1) Existe um número primo grande 'p' e uma raiz primitiva 'g', combinados
   publicamente entre Alice e Bob (aqui: o Servidor/Bob envia p e g ao
   Cliente/Alice assim que a conexão é estabelecida).
2) Cada lado escolhe um número privado secreto (a para Alice, b para Bob),
   que NUNCA é enviado pela rede.
3) Cada lado calcula sua chave pública:
       A = g^a mod p      (Alice)
       B = g^b mod p      (Bob)
   e troca esses valores públicos pela rede (podem ser vistos no Wireshark,
   sem problema algum, essa é a ideia do algoritmo).
4) Cada lado calcula o segredo compartilhado:
       Alice: S = B^a mod p
       Bob:   S = A^b mod p
   Matematicamente os dois chegam ao MESMO valor de S, sem que ele nunca
   tenha trafegado pela rede.
5) Esse segredo S é usado para gerar o shift da Cifra de César (caesar.py).

Sobre o número primo 'p': para o Diffie-Hellman ser seguro, p precisa ser
um número muito grande (centenas de dígitos). Testar a primalidade de um
número desse tamanho por divisão (como em testes_primos.py) é inviável na
prática (levaria anos). Por isso, para números grandes usamos aqui o
Teste de Primalidade de Miller-Rabin, implementado também de forma autoral
(sem biblioteca pronta de criptografia), que é o algoritmo usado por
padrão nas ferramentas reais de geração de chaves.
Para números pequenos, use testes_primos.py (primo_fast/primo_slow), como
pedido no enunciado.
"""
import random

# Primo de 256 bits (grupo MODP conhecido/RFC 5114-like, usado apenas para
# fins didáticos) e raiz primitiva g = 2. Poderiam ser gerados dinamicamente,
# mas usar um primo fixo e já conhecido evita ter que gerar primos gigantes
# em tempo real a cada execução (o que seria lento em Python puro).
P_PADRAO = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD"
    "129024E088A67CC74020BBEA63B139B22514A08798E3404"
    "DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C"
    "245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406"
    "B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE"
    "45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD"
    "24CF5F83655D23DCA3AD961C62F356208552BB9ED529077"
    "096966D670C354E4ABC9804F1746C08CA237327FFFFFFFF"
    "FFFFFFFF",
    16,
)
G_PADRAO = 2


def eh_primo_miller_rabin(n: int, k: int = 20) -> bool:
    """
    Teste de primalidade probabilístico de Miller-Rabin (implementação
    autoral). Usado apenas para validar/checar o número primo grande do
    Diffie-Hellman, já que testar por divisão (testes_primos.py) não é
    viável para números desse tamanho.
    """
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % p == 0:
            return n == p

    # escreve n-1 como d * 2^r
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def gerar_chave_privada(p: int = P_PADRAO) -> int:
    """Gera o número secreto de um dos lados (nunca deve ser enviado pela rede)."""
    return random.randrange(2, p - 2)


def gerar_chave_publica(privada: int, g: int = G_PADRAO, p: int = P_PADRAO) -> int:
    """Calcula g^privada mod p — este valor PODE ser enviado pela rede."""
    return pow(g, privada, p)


def gerar_segredo_compartilhado(chave_publica_recebida: int, minha_privada: int, p: int = P_PADRAO) -> int:
    """Calcula o segredo final: (chave pública do outro)^(minha privada) mod p."""
    return pow(chave_publica_recebida, minha_privada, p)


if __name__ == "__main__":
    # Teste isolado do módulo, simulando Alice e Bob no mesmo processo.
    print("Validando o primo padrão com Miller-Rabin:", eh_primo_miller_rabin(P_PADRAO))

    a_priv = gerar_chave_privada()
    b_priv = gerar_chave_privada()

    a_pub = gerar_chave_publica(a_priv)
    b_pub = gerar_chave_publica(b_priv)

    segredo_alice = gerar_segredo_compartilhado(b_pub, a_priv)
    segredo_bob = gerar_segredo_compartilhado(a_pub, b_priv)

    print("Segredo (Alice):", segredo_alice)
    print("Segredo (Bob)  :", segredo_bob)
    print("Bateram?", segredo_alice == segredo_bob)
