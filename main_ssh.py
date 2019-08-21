import asyncssh
import time
import devices
import os
from time import strftime
import asyncio
import paramiko


@asyncio.coroutine
async def save_output(process, request, command_send):
    """

    :param process: process created for the connection.
    :param request: the hostname of the equipment
    :param command_send: the command sended to equipment
    :return:
    """
    date_time = strftime("%d%m%Y", time.localtime())

    if (request[0:3] == 'LDA' or request[0:3] == 'APS'):
        
		directory = '/home/****/Backup/BACKUP_'+date_time+'/'+request[0:6]+'_'+ date_time+'/'
        path = os.path.exists(directory)
		
    elif request[0:3] == '***' or request[0:3] == '***' or request[0:3] == '****':
        
		directory = '/home/***/Backup/BACKUP_'+date_time+'/'+request[0:3]+'OLT_'+ date_time+'/'
        path = os.path.exists(directory)
		
    path = str(directory)
    output_final= ''
    output_data=''
	
    try:
        
		if request[0:3] == 'MyHost' or request[0:3] == 'MyHost' or request[0:3] == 'MyHost':            
			if command_send == 'display ipv6 neighbors' or command_send == 'display current-configuration':                
				while True:                    
					output_data = await process.stdout.readline()                    
					
                    if output_data[32:38] == 'Static':					
                        break
						
                    if output_data[:6] == 'return':					
                        break
						
                    output_final= output_final+ output_data            
			else:
                output_final= await process.stdout.readuntil("#")
                
        else:
            
			if request[6:11] == 'MyHost' or request[6:11] == 'MyHost' or request[6:11] == 'MyHost':
               
			   if command_send == 'display ipv6 neighbors' or command_send == 'display current-configuration' or command_send == 'show running-config verbose full':
                    
					while True:
                        output_data = await process.stdout.readline()                        
                        if output_data[32:38] == 'Static':
                            break
                        if output_data[:6] == 'return':
                            break
                        if output_data[:29] == 'configure slot 13 no shutdown':
                            break
                        output_final= output_final+ output_data
                else:
                    if request[6:11] == 'MyHost' or request[6:11] == 'MyHost:
                        output_final= await process.stdout.readuntil(">")                       
                    else:
                        output_final= await process.stdout.readuntil(request + "#")                       
            else:
                    output_final= await process.stdout.readuntil(request + "#")
                   

        with open(path + request + '_' + date_time + '.txt', 'a+') as f:
            f.write(output_final[:])
            output_final= ''
            return "ok"

    except (OSError, ) as exc:
        return str(exc)

@asyncio.coroutine
async def run_client(request, user, password):
    """

    :param request: Equipamento que será realizado a conexão
    :param user: Login
    :param password: Senha
    :return: Se todas as condições forem aceitas, será retornado OK.
    """
    date_time = strftime("%d%m%Y", time.localtime())
   
    if (request[0:3] == 'LDA' or request[0:3] == 'APS'):
        directory = '/home/***/Backup/BACKUP_'+date_time+'/'+request[0:6]+'_'+ date_time+'/'
        path = os.path.exists(directory)
    if request[0:3] == 'APU' or request[0:3] == 'CAB' or request[0:3] == 'RLA':
        directory = '/home/***/Backup/BACKUP_'+date_time+'/'+request[0:3]+'OLT_'+ date_time+'/'
        path = os.path.exists(directory)

    print(request)
    print (path)
    if path == True:

        if request[:11] =='MyHost'or request[:11] == 'MyHost': ##used paramiko connection because my equipment did not accept asyncssh
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(devices.device(request), port=22, username=user, password=password, look_for_keys='', timeout=200 * 60)
            connection = ssh.invoke_shell()
			
            output=''
            stdout= connection.recv(64).decode(encoding='utf-8')
            outFile = open(directory + request + '_' + date_time+'.txt', "w")
            outFile.write(stdout[:])
          
            commands = devices.commands(request)
			
            for p in commands:
                connection.send(p + '\n')
                time.sleep(2)
                if p == 'Show running-config':
                    time.sleep(10)
                stdout= connection.recv(2500000).decode(encoding='utf-8')
                output_final= output_final+ stdout
               
            
			outFile = open(directory + request + '_' + date_time+'.txt', "a+")
            outFile.write(output[:]+ '\n')
            return 'ok'

        else:

            async with asyncssh.connect(devices.device(request), port=22, username=user, password=password, known_hosts=None, client_keys=None) as conn:
                process = await conn.create_process()
              
				##used to separate citys and equipments
                if request[0:3] == 'MyHost' or request[0:3] == 'MyHost' or request[0:3] == 'MyHost':
                    output_final= ''
                    output_final= await  process.stdout.readuntil(">") ##used because a huawei equipment.
                    outFile = open(directory + request + '_' + date_time+'.txt', "w")
                    commands = devices.commands(request)
                    outFile.write(output+ '\n')

                    for command_send in commands:
                        process.stdin.write(command_send + '\n')
                        await save_output(process, request, command_send)
                    return "ok"
					
                else:
                    if request[6:11] == 'MyHost' or request[6:11] == 'MyHost': ##used because a huawei equipment.
                        output_final= await  process.stdout.readuntil(">")
                        outFile = open(directory + request + '_' + date_time + '.txt', "w")
                    else:                       
                        output_final= await  process.stdout.readuntil("*") ## used to equipment cisco
                        outFile = open(directory + request + '_' + date_time + '.txt', "w")
                    
                    commands = devices.commands(request)
                    outFile.write(output_final+ '\n')

                    for command_send in commands:
                        print (command_send)
                        if command_send == 'show running-config verbose full':
                            process.stdin.write(command_send + '\n')

                            await save_output(process, request, command_send)
                        else:
                            process.stdin.write(command_send + '\n')
                            await save_output(process, request, command_send)
                    return "ok"
    else:
        return "Folder is not created!."













