import socket

from caesar import encriptar, decriptar, gerar_shift_a_partir_do_segredo
from dh import gerar_chave_privada, gerar_chave_publica, gerar_segredo_compartilhado

PORT = 65432


def receber_inteiro(arquivo) -> int:
    """Lê um inteiro grande enviado como uma linha de texto (ver nota no SimpleTCPServer.py)."""
    linha = arquivo.readline()
    return int(linha.strip())


def enviar_inteiro(arquivo, valor: int):
    arquivo.write(str(valor) + "\n")
    arquivo.flush()


def main():
    host = input("IP do servidor (Bob) [127.0.0.1]: ").strip() or "127.0.0.1"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, PORT))
        print(f"[Alice] Conectada em {host}:{PORT}")
        arquivo_texto = sock.makefile("rw")  # canal de texto (linhas) para o handshake DH

        # ---------- ETAPA 3: Diffie-Hellman ----------
        print("[Alice] Recebendo parâmetros públicos p e g de Bob...")
        p = receber_inteiro(arquivo_texto)
        g = receber_inteiro(arquivo_texto)

        a_privada = gerar_chave_privada(p)
        a_publica = gerar_chave_publica(a_privada, g, p)
        print("[Alice] Enviando minha chave pública para Bob...")
        enviar_inteiro(arquivo_texto, a_publica)

        print("[Alice] Aguardando chave pública de Bob...")
        chave_publica_bob = receber_inteiro(arquivo_texto)

        segredo = gerar_segredo_compartilhado(chave_publica_bob, a_privada, p)
        shift = gerar_shift_a_partir_do_segredo(segredo)
        print(f"[Alice] Segredo compartilhado calculado! Shift da Cifra de César = {shift}")

        # ---------- ETAPA 2: comunicação cifrada com César ----------
        print("[Alice] Pronta para conversar com Bob. Digite 'sair' para encerrar.\n")
        while True:
            mensagem = input("[Alice] Mensagem para Bob: ")
            sock.sendall(encriptar(mensagem, shift))

            if mensagem.strip().lower() == "sair":
                print("[Alice] Encerrando.")
                break

            resposta = sock.recv(4096)
            if not resposta:
                print("[Alice] Bob encerrou a conexão.")
                break

            print(f"[Alice] Resposta cifrada (bytes crus): {resposta}")
            print(f"[Alice] Resposta decifrada: {decriptar(resposta, shift)}\n")


if __name__ == "__main__":
    main()
