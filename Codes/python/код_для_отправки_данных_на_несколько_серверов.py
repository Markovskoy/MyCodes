import paramiko
import getpass

hosts = [
    #"10.12.151.250"
]


username = "markovskoy_vv"
password = getpass.getpass("Введите пароль: ")
command = "echo -e 'проверка добавления' | sudo tee -a /home/markovskoy_vv/test && cat /home/markovskoy_vv/test"


def execute_command_on_server(host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 

    try:
        client.connect(host, port=22, username=username, password=password)


        print("Открытие сессии с правами root...")
        stdin, stdout, stderr = client.exec_command(f"echo {password} | sudo -S -p '' {command}", get_pty=True)
 
        output = stdout.read().decode()  
        error = stderr.read().decode()   

        client.close()

        with open("to_dima.txt", "a", encoding="utf-8") as file:
            if error and "пароль" not in error.lower():
                result = f"Ошибка на сервере {host}: {error}\n"
            else:
                result = f"Результат от сервера {host}:\n{output}\n"
            print(result)
            file.write(result)

    except Exception as e:
        error_msg = f"Ошибка подключения к серверу {host}: {e}\n"
        print(error_msg)
        with open("to_dima.txt", "a", encoding="utf-8") as file:
            file.write(error_msg)


for host in hosts:
    connect_msg = f"Подключение к серверу {host}\n"
    print(connect_msg)
    with open("to_dima.txt", "a", encoding="utf-8") as file:
            file.write(connect_msg)
    execute_command_on_server(host)