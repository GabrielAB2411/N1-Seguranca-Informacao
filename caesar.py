"""
caesar.py
----------
Implementação AUTORAL da Cifra de César, sem uso de bibliotecas prontas de
criptografia (não usa 'cryptography', 'hashlib', 'base64', etc.).

Diferença em relação à Cifra de César "clássica" (que só desloca letras A-Z):
como o socket transporta qualquer tipo de caractere (acentos, números,
pontuação, espaços...), a cifra aqui foi estendida para operar sobre TODOS os
bytes (0 a 255) da mensagem, deslocando cada byte por uma chave (shift).
A lógica é exatamente a mesma da Cifra de César tradicional, só que aplicada
ao alfabeto de 256 símbolos (bytes) em vez do alfabeto de 26 letras.

A chave 'shift' usada aqui é derivada do segredo compartilhado gerado pelo
Diffie-Hellman (ver dh.py), então cada par Alice/Bob usa uma chave diferente
a cada execução.
"""

TAMANHO_ALFABETO = 256  # trabalhamos com todos os valores possíveis de 1 byte


def gerar_shift_a_partir_do_segredo(segredo: int) -> int:
    """
    Converte o segredo compartilhado (número grande, gerado pelo Diffie-Hellman)
    em um deslocamento (shift) utilizável pela Cifra de César, no intervalo
    [1, 255] (0 deixaria a mensagem sem alteração).
    """
    shift = segredo % TAMANHO_ALFABETO
    if shift == 0:
        shift = 1
    return shift


def encriptar(texto: str, shift: int) -> bytes:
    """
    Encripta uma string usando a Cifra de César estendida.
    Cada caractere é convertido em byte e deslocado 'shift' posições,
    com "volta ao início" (mod 256), igual à lógica original da Cifra de César.
    """
    dados = texto.encode("utf-8", errors="ignore")
    cifrado = bytearray()
    for byte in dados:
        novo_byte = (byte + shift) % TAMANHO_ALFABETO
        cifrado.append(novo_byte)
    return bytes(cifrado)


def decriptar(dados_cifrados: bytes, shift: int) -> str:
    """
    Decriptografa os bytes recebidos pela rede, revertendo o deslocamento
    aplicado por encriptar().
    """
    decifrado = bytearray()
    for byte in dados_cifrados:
        original = (byte - shift) % TAMANHO_ALFABETO
        decifrado.append(original)
    return bytes(decifrado).decode("utf-8", errors="ignore")


if __name__ == "__main__":
    # Teste rápido e isolado do módulo 
    mensagem = "Ola, Bob! Teste com acentuação e símbolos: @#% 123"
    chave = 77

    print("Mensagem original :", mensagem)
    c = encriptar(mensagem, chave)
    print("Mensagem cifrada  :", c)
    d = decriptar(c, chave)
    print("Mensagem decifrada:", d)
    print("OK!" if d == mensagem else "ERRO na cifra!")
