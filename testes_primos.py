import time


def primo_fast(N: int) -> bool:
    """Verifica primalidade parando assim que encontra um divisor (mais rápido)."""
    if N < 2:
        return False
    i = 2
    while i < N:
        R = N % i
        if R == 0:
            return False
        i += 1
    return True


def primo_slow(N: int) -> bool:
    """Verifica primalidade contando TODOS os divisores até N-1 (mais lento, didático)."""
    if N < 2:
        return False
    cont = 0
    i = 2
    while i < N:
        R = N % i
        if R == 0:
            cont += 1
        i += 1
    return cont == 0


def testar_com_tempo(funcao, N: int, nome: str):
    """Executa a função de teste de primo medindo o tempo de execução."""
    inicio = time.time()
    resultado = funcao(N)
    fim = time.time()
    tempo = fim - inicio
    status = "é primo" if resultado else "não é primo"
    print(f"[{nome}] {N} {status}. Tempo de execução: {tempo:.6f} segundos")
    return resultado, tempo


if __name__ == "__main__":
    # Reprodução do comportamento original dos scripts primo_fast.py / primo_slow.py,
    # agora comparando os dois de uma vez só para o mesmo N.
    N = int(input("Digite N para testar (ex: 104729): "))

    print("\n--- Comparando desempenho ---")
    testar_com_tempo(primo_fast, N, "FAST")
    testar_com_tempo(primo_slow, N, "SLOW")
