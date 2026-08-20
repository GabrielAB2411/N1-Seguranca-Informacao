import socket

from caesar import encriptar, decriptar, gerar_shift_a_partir_do_segredo
from dh import (
    P_PADRAO,
    G_PADRAO,
    gerar_chave_privada,
    gerar_chave_publica,
    gerar_segredo_compartilhado,
)

HOST = "0.0.0.0"   # aceita conexões de qualquer interface de rede
PORT = 65432        # porta usada pelo servidor (pode trocar se estiver ocupada)


def receber_inteiro(arquivo) -> int:
    """
    Recebe um inteiro grande enviado como texto terminado por '\\n'.
    Usa socket.makefile() (arquivo em modo texto ligado ao socket) para
    garantir que cada leitura respeite exatamente uma linha, mesmo que o
    TCP junte várias mensagens pequenas no mesmo pacote de rede.
    """
    linha = arquivo.readline()
    return int(linha.strip())


def enviar_inteiro(arquivo, valor: int):
    arquivo.write(str(valor) + "\n")
    arquivo.flush()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen(1)
        print(f"[Bob] Servidor ouvindo em {HOST}:{PORT} ... aguardando Alice.")

        conn, endereco = servidor.accept()
        with conn:
            print(f"[Bob] Conectado por {endereco}")
            arquivo_texto = conn.makefile("rw")  # canal de texto (linhas) para o handshake DH

            # ---------- ETAPA 3: Diffie-Hellman ----------
            print("[Bob] Enviando parâmetros públicos p e g para Alice...")
            enviar_inteiro(arquivo_texto, P_PADRAO)
            enviar_inteiro(arquivo_texto, G_PADRAO)

            print("[Bob] Aguardando chave pública de Alice...")
            chave_publica_alice = receber_inteiro(arquivo_texto)

            b_privada = gerar_chave_privada(P_PADRAO)
            b_publica = gerar_chave_publica(b_privada, G_PADRAO, P_PADRAO)
            print("[Bob] Enviando minha chave pública para Alice...")
            enviar_inteiro(arquivo_texto, b_publica)

            segredo = gerar_segredo_compartilhado(chave_publica_alice, b_privada, P_PADRAO)
            shift = gerar_shift_a_partir_do_segredo(segredo)
            print(f"[Bob] Segredo compartilhado calculado! Shift da Cifra de César = {shift}")

            # ---------- ETAPA 2: comunicação cifrada com César ----------
            print("[Bob] Pronto para receber mensagens cifradas de Alice. (Ctrl+C para sair)\n")
            while True:
                dados = conn.recv(4096)
                if not dados:
                    print("[Bob] Alice encerrou a conexão.")
                    break

                mensagem = decriptar(dados, shift)
                print(f"[Bob] Recebido (cifrado, bytes crus): {dados}")
                print(f"[Bob] Decifrado: {mensagem}")

                if mensagem.strip().lower() == "sair":
                    print("[Bob] Encerrando a pedido de Alice.")
                    break

                resposta = f"Bob recebeu: {mensagem}"
                conn.sendall(encriptar(resposta, shift))


if __name__ == "__main__":
    main()
