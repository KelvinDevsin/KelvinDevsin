import time
import requests
import uiautomator2 as u2
import os
import sys
import customtkinter as ctk
import subprocess
import threading
from email_handler import create_email, get_inbox
import random
from secmail import gerar_email_temporario, esperar_codigo_de_confirmacao
from inboxes import gerar_email, ativar_inbox, aguardar_codigo 
executando = True
lock = threading.Lock()
pause_event = threading.Event()

# Contador para controlar o número de threads ativas
threads_ativas = 0
threads_lock = threading.Lock()

# Função para iniciar o driver usando IP e porta
def iniciar_driver(device_ip, port):
    full_address = f"{device_ip}:{port}"
    print(f"Conectando ao dispositivo em {full_address}...")
    return u2.connect(full_address)


# Função para iniciar o Instagram Lite no emulador
def iniciar_instagram_lite(d):
    try:
        print("Iniciando Instagram Lite...")
        d.app_clear("com.instagram.android")
        d.app_start("com.instagram.android")
    except Exception as e:
        print(f"Erro ao iniciar o Instagram Lite: {e}")
        return False
    return True

def reiniciar_aplicativo(d):
    print("Reiniciando o aplicativo e limpando dados...")
    d.app_clear("com.instagram.android")
    d.app_start("com.instagram.android")

# Função para criar a conta no Instagram Lite
def criar_conta_instagram_lite(d, device_id):
    while True:  # Loop para tentar até ter sucesso
        global threads_ativas
        try:
            with threads_lock:
                threads_ativas += 1  # Incrementa contador ao iniciar thread
            print("Iniciando processo de criação de conta...")
            # Criar nova conta
            d.xpath('//android.view.View[@content-desc="Criar nova conta"]').click()
            print("Aceitando permissões de contatos.")
            time.sleep(1)

            try:
                d.xpath('//android.view.View[@content-desc="Começar"]').click(timeout=5)
            except:
                pass
            
            
            # Apertar em "Avançar" apos adicionar o email
            d.xpath('//android.view.View[@content-desc="Cadastrar-se com o email"]').click()
            print("Apertou 'Cadastrar-se com o email'.")

            # Criar e adicionar o email temporário (1secmail)
            email_copied = gerar_email_temporario()
                        # Gerar e adicionar o email temporário usando inboxes
            #email_copied = gerar_email()
            #ativar_inbox(email_copied)  # Ativar a inbox para o email gerado
            print(f"E-mail temporário gerado: {email_copied}")
            time.sleep(1)
            # Inserir o email
            d.xpath('//android.widget.EditText').set_text(email_copied)
            print("Email inserido.")
            time.sleep(1)

            # Apertar em "Avançar" apos adicionar o email
            d.xpath('//android.view.View[@content-desc="Avançar"]').click()
            print("Apertou 'Avançar'.")


            # Aguardar código de verificação no email (1secmail)
            codigo = esperar_codigo_de_confirmacao(email_copied)
            #codigo = aguardar_codigo(email_copied)
            if codigo:
                print(f"Código recebido: {codigo}")

                # Inserir o código de verificação
                d.xpath('//android.widget.EditText').set_text(codigo)
                print("Código inserido.")

                # Apertar em "Avançar" após inserir o código
                d.xpath('//android.view.View[@content-desc="Avançar"]').click()
                print("Apertou 'Avançar'.")
                time.sleep(5)

                # Criar senha
                senha = "Kelvin2002"
                d.xpath('//android.widget.EditText').set_text(senha)
                print(f"Senha '{senha}' inserida.")
                time.sleep(2)

                # Apertar em "Avançar" após criar a senha
                d.xpath('//android.view.View[@content-desc="Avançar"]').click()
                print("Apertou 'Avançar' após senha.")
                time.sleep(1)
                try:
                    # Apertar em "Agora não" após criar a senha
                    d.xpath('//android.widget.Button[@resource-id="android:id/button2"]').click(timeout=10)
                    print("Apertou 'criar nova conta' após senha.")
                    time.sleep(1) 
                except:
                    pass

                # Apertar em "Agora não" após criar a senha
                d.xpath('//android.view.View[@content-desc="Agora não"]').click()
                print("Apertou 'Agora não' após senha.")
                time.sleep(1)

                # Deslizar para selecionar a data de nascimento
                for _ in range(4):
                    d.swipe(382, 372, 384, 923, duration=0)
                time.sleep(2)
                
                # Apertar em "Avançar" final após a data de nascimento
                d.xpath('//android.widget.EditText[@resource-id="android:id/numberpicker_input" and @text="2001"]').click()
                print("Ano 2000 adicionado")

                # Apertar em "Avançar" final
                d.xpath('//android.widget.Button[@resource-id="android:id/button1"]').click()
                print("Apertou 'DEFINIR'.")
                time.sleep(1.5)
                
                # Apertar em "Avançar" final
                d.xpath('//android.view.View[@content-desc="Avançar"]').click()
                print("Apertou 'Avançar'.")
                time.sleep(1.5)
                # Apertar em "Avançar" final
                d.xpath('//android.view.View[@content-desc="Avançar"]').click()
                print("Apertou 'Avançar'.")
                time.sleep(1.5)

                # Apertar em "Avançar" final
                d.xpath('//android.view.View[@content-desc="Avançar"]').click()
                print("Apertou 'Avançar'.")

                time.sleep(2)
                # *** Sincronizar o clique no botão final ***
                with lock:
                    try:
                       d.xpath('//android.view.View[@content-desc="Concordo"]').click()
                       print("Apertou 'CONCORDO'.")
                    except:
                           print('Não foi possivel apertar em avnaçar')
                    time.sleep(5)

                try:
                    d.xpath('//android.widget.TextView[@text="Tente novamente mais tarde"]').click(timeout=5)
                    # Quando o processo terminar, decrementa o contador de threads ativas
                    with threads_lock:
                        threads_ativas -= 1
                        if threads_ativas == 0:  # Se for a última thread
                            # Sincronizar para ativar o modo avião
                            print("Todas as threads finalizaram. Ativando modo avião.")
                            subprocess.run(["adb", "-s", device_id, "shell", "cmd", "connectivity", "airplane-mode", "enable"], check=True)
                            time.sleep(4)
                            print("Desativando modo avião...")
                            subprocess.run(["adb", "-s", device_id, "shell", "cmd", "connectivity", "airplane-mode", "disable"], check=True)
                            time.sleep(4)
                            print("Modo avião alternado após todas as instâncias.")

                    reiniciar_aplicativo(d)
                    continue  # Reinicia o loop para tentar criar outra conta
                except u2.XPathElementNotFoundError:
                    pass  # Segue com a criação da conta caso não encontre o elemento

                time.sleep(14)  # Espera 14 segundos para sincronizar com outras threads
                
                try:
                    d.xpath('//android.view.View[@text="Fazer uma apelação"]').click(timeout=5)
                    print("tomou SMS...")
                    subprocess.run(["adb", "-s", '104301f50507', "shell", "cmd", "connectivity", "airplane-mode", "enable"], check=True)
                    time.sleep(4)
                    print("Desativando modo avião...")
                    subprocess.run(["adb", "-s", '104301f50507', "shell", "cmd", "connectivity", "airplane-mode", "disable"], check=True)
                    time.sleep(4)

                    reiniciar_aplicativo(d)
                    continue  # Reinicia o loop para tentar criar outra conta
                except u2.XPathElementNotFoundError:
                    pass 



                try:
                    # Tenta clicar no primeiro xpath
                    d.xpath('//android.view.View[@content-desc="Adicionar foto"]').click(timeout=5)
                    print("Apertou adicionar foto (xpath 1)")               
                except:
                    print("Falha ao apertar adicionar foto")  
                time.sleep(1)        
                # Escolher na galeria
                d.xpath('//android.view.View[@content-desc="Escolher na Galeria"]').click()
                print("Escolher na galeria")             
                time.sleep(1) 
                # aceitar permissão
                d.xpath('//android.widget.Button[@resource-id="com.android.packageinstaller:id/permission_allow_button"]').click()
                print("aceitar permissão")               
            
                time.sleep(1) 
                # Apertar em recente
                d.xpath('//android.widget.TextView[@resource-id="android:id/title" and @text="Recentes"]').click()
                print("Apertou EM RECENTE")          
                time.sleep(2)

                # Apertar na foto
                d.xpath('(//android.widget.ImageView[@resource-id="com.android.documentsui:id/icon_thumb"])[2]').click()
                print("Apertou na foto")          
                time.sleep(5)
                try:
                # Avançar
                 d.xpath('//android.view.View[@content-desc="Concluir"]').click()
                 print("Apertou em salvar")    
                 time.sleep(5)
                 with open("contas.txt", "a") as file:
                    file.write(f"{email_copied}\n")
                    file.write("Kelvin2002!?\n")     
                except:
                    print("botão não encontrado > salvar") 
                
            # Se não houver erro, sair do loop

            break

        except (u2.UiObjectNotFoundError, u2.XPathElementNotFoundError) as e:
            print(f"Erro ao criar conta: {e}. Reiniciando aplicativo...")
            reiniciar_aplicativo(d)
            time.sleep(5)  # Aguardar um pouco antes de tentar novamente

# Função para executar o processo principal em uma porta específica
# Função para executar o processo principal em uma porta específica
def executar_processo(device_ip, port, device_id):
    d = iniciar_driver(device_ip, port)
    if iniciar_instagram_lite(d):
        criar_conta_instagram_lite(d, device_id)

# Interface gráfica com customtkinter
def iniciar_interface():
    def iniciar_processo():
        global executando
        portas = entry_portas.get().split(",")  # Divide a entrada de múltiplas portas
        label_status.configure(text="Processo em execução...", text_color="blue")
        executando = True  # Seta a flag como True para iniciar o processo

        # Função interna que será executada na thread
        def thread_process(porta):
            global executando
            device_id = "emulator-" + porta.strip()  # Exemplo de como associar o device_id com a porta
            while executando:  # Loop para tentar criar contas enquanto 'executando' for True
                try:
                    executar_processo("127.0.0.1", int(porta), device_id)
                    label_status.configure(text=f"Finalizado na porta {porta}. Reiniciando ", text_color="green")

                except Exception as e:
                    print(f"Erro durante o processo na porta {porta}: {e}.")
                    label_status.configure(text=f"Erro: {e}. ", text_color="red")

                 

            if not executando:
                label_status.configure(text="Processo interrompido.", text_color="red")

        # Cria uma thread para cada porta
        for porta in portas:
            processo_thread = threading.Thread(target=thread_process, args=(porta,))
            processo_thread.daemon = True  # Configura a thread como "daemon"
            processo_thread.start()  # Iniciar a thread

    def reiniciar():
        label_status.configure(text="")
        botao_reiniciar.pack_forget()

    # Função para parar o processo
    def parar():
        global executando
        executando = False  # Define a flag como False para interromper o processo
        pause_event.set()  # Libera qualquer pausa pendente
        label_status.configure(text="Processo interrompido pelo usuário.", text_color="red")

    # Função chamada quando o "X" é clicado
    def fechar_janela():
        parar()  # Interrompe o processo em execução
        janela.destroy()  # Fecha a janela da interface gráfica
        sys.exit()  # Finaliza o programa no terminal e interrompe todas as threads

    # Configurações da janela
    ctk.set_appearance_mode("dark")
    janela = ctk.CTk()
    janela.title("Gerador de Conta Instagram Lite")
    janela.geometry("400x300")

    # Capturar o evento de fechamento (clicar no "X")
    janela.protocol("WM_DELETE_WINDOW", fechar_janela)

    # Label e entrada para as portas
    label_portas = ctk.CTkLabel(janela, text="Portas dos dispositivos (separadas por vírgula):")
    label_portas.pack(pady=10)
    entry_portas = ctk.CTkEntry(janela)
    entry_portas.pack(pady=10)

    # Botão para iniciar o processo
    botao_iniciar = ctk.CTkButton(janela, text="Iniciar", command=iniciar_processo)
    botao_iniciar.pack(pady=10)

    # Botão para parar o processo
    botao_parar = ctk.CTkButton(janela, text="Parar", command=parar)
    botao_parar.pack(pady=10)

    # Label de status
    label_status = ctk.CTkLabel(janela, text="")
    label_status.pack(pady=10)

    # Botão reiniciar
    botao_reiniciar = ctk.CTkButton(janela, text="Reiniciar", command=reiniciar)

    janela.mainloop()

if __name__ == "__main__":
    iniciar_interface()
