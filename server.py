import socket
import threading

users = {}

def connectClient(conn):
    global users

    connected = True
    username = ""
    friendsList = []

    while connected:
        msg = conn.recv(1024)
        if msg:
            msg = msg.decode()
            msgL = msg.split('|')

            print(msgL)

            # LOGIN-------------------------------------
            if msgL[0] == "LOGIN":
                if msgL[1] not in users:
                    users[msgL[1]] = {
                        'conn': conn, 
                        'friends': {},
                        'groups': {},
                        'online': True
                    }

                    username = msgL[1]

                    conn.send("1".encode())

                elif msgL[1] in users and users[msgL[1]]['online'] == False:
                    users[msgL[1]]['conn'] = conn
                    users[msgL[1]]['online'] = True
                    username = msgL[1]

                    for friend in users[msgL[1]]['friends'].keys():
                        friendsList.append(friend)

                    conn.send("1".encode())

                else:
                    conn.send("0".encode())
            
            # SHOW FRIENDS-----------------------------
            elif msgL[0] == "SHOWF":
                showF = "\n\tFRIENDS"

                if len(users[username]['friends'].keys()) != len(friendsList):
                    friendsList.clear()

                    for friend in users[username]['friends'].keys():
                        friendsList.append(friend)

                for friend in friendsList:
                    notifications = (" " if users[username]['friends'][friend]['notifications'] == 0 else ("(" + str(users[username]['friends'][friend]['notifications']) + ")" ))
                    isOnline = ("(online)" if users[friend]["online"] == True else "(outline)")
                    showF += "\n-> " + friend + " " + isOnline + " " + notifications 

                conn.send(showF.encode())

            # SHOW UNFRIENDS--------------------------
            elif msgL[0] == "SHOWU":
                showU = "\n\tUSERS"

                if len(users[username]['friends'].keys()) != len(friendsList):
                    friendsList.clear()

                    for friend in users[username]['friends'].keys():
                        friendsList.append(friend)

                for unfriend in users.keys():
                    if unfriend not in friendsList and unfriend != username:
                        showU += "\n-> " + unfriend

                conn.send(showU.encode())

            # SHOW GROUPS------------------------------
            elif msgL[0] == "SHOWG":
                showG = "\n\tGROUPS"

                for group in users[username]['groups'].keys():
                    notifications = (" " if users[username]['groups'][group]['notifications'] == 0 else ( "(" + str(users[username]['groups'][group]['notifications']) + ")" ))
                    showG += "\n->" + group + " " + notifications
                
                conn.send(showG.encode())

            # ADD FRIEND-------------------------------
            elif msgL[0] == "ADD":
                if msgL[1] != "@":
                    if msgL[1] in users.keys():
                        users[username]['friends'][msgL[1]] = {'messages': [], 'isBlocked': False, 'notifications': 0}
                        
                        users[msgL[1]]['friends'][username] = {'messages': [], 'isBlocked': False, 'notifications': 0}

                        friendsList.append(msgL[1])
            
            # DELETE FRIEND---------------------------
            elif msgL[0] == "DELETEF":
                if msgL[1] != "@":
                    if msgL[1] in users[username]['friends'].keys():
                        del(users[username]['friends'][msgL[1]])
                        
                        del(users[msgL[1]]['friends'][username])
            
            # HISTORY---------------------------------
            elif msgL[0] == "HIST":
                if msgL[1] in users[username]['friends'].keys():

                    users[username]['friends'][msgL[1]]['notifications'] = 0

                    history = "\n\t" + msgL[1]
                    
                    for message in users[username]['friends'][msgL[1]]['messages']:
                        history += "\n" + message
                    
                    history += ("|BLOCKED" if users[username]['friends'][msgL[1]]['isBlocked'] else "|UNLOCKED")
                
                else:
                    history = "\n\tNOT FOUND"
                
                conn.send(history.encode())
            
            # MESSAGE----------------------------------
            elif msgL[0] == "SEND":

                if msgL[1] in users[username]['friends'].keys():
                    
                    # Message log
                    users[username]['friends'][msgL[1]]['messages'].append(username + ": " + msgL[2])
                    
                    # Are you blocked?
                    if users[msgL[1]]['friends'][username]['isBlocked'] == False:
                        
                        # Message log and notification
                        users[msgL[1]]['friends'][username]['messages'].append(username + ": " + msgL[2])
                        users[msgL[1]]['friends'][username]['notifications'] += 1
            
            # BROADCAST--------------------------------
            elif msgL[0] == "BROADCAST":
                # Check each user
                for i in range(1, len(msgL)-1):
                    
                    if msgL[i] in users[username]['friends'].keys():
                        
                        # Message log
                        users[username]['friends'][msgL[i]]['messages'].append(username + ": " + msgL[len(msgL)-1])
                        
                        # Are you blocked?
                        if users[msgL[i]]['friends'][username]['isBlocked'] == False:
                            
                            # Message log and notification
                            users[msgL[i]]['friends'][username]['messages'].append(username + ": " + msgL[len(msgL)-1])
                            users[msgL[i]]['friends'][username]['notifications'] += 1

            # GROUP-----------------------------
            elif msgL[0] == "GROUP":
                # Create
                if msgL[1] == "CREATE":
                    if msgL[2] != "@":
                        # For each user
                        for i in range(3, len(msgL)):

                            # Is your friend?
                            if msgL[i] in users[username]['friends'].keys():
                                groupList = msgL[3:].copy()
                                
                                groupList[groupList.index(msgL[i])] = username
                                
                                users[msgL[i]]['groups'][msgL[2]] = {'friends': groupList, 'messages': [], 'notifications': 0}

                        users[username]['groups'][msgL[2]] = {'friends': msgL[3:].copy(), 'messages': [], 'notifications': 0}
                
                # Adds Friend to a group
                elif msgL[1] == "ADD":
                    if msgL[3] != "@":

                        if msgL[2] in users[username]['groups'].keys():
                            # Add a new user to the group
                            users[msgL[3]]['groups'][msgL[2]] = {'friends': [], 'messages': [], 'notifications': 0}

                            for member in users[username]['groups'][msgL[2]]['friends']:
                                # Update each member
                                users[member]['groups'][msgL[2]]['friends'].append(msgL[3])

                                users[member]['groups'][msgL[2]]['messages'].append(msgL[3] + " joined")
                                # Update the new member
                                users[msgL[3]]['groups'][msgL[2]]['friends'].append(member)
                            users[msgL[3]]['groups'][msgL[2]]['friends'].append(username)
                            
                            # Update the current user
                            users[username]['groups'][msgL[2]]['friends'].append(msgL[3])

                            users[username]['groups'][msgL[2]]['messages'].append(msgL[3] + " joined")

                # Show friends that are not members of the group
                elif msgL[1] == "SHOWU":
                    friends = "\n\tFRIENDS"
                    
                    if msgL[2] in users[username]['groups'].keys():

                        result= [friend for friend in friendsList if friend not in users[username]['groups'][msgL[2]]['friends']]
                        
                        for r in result:
                            friends += "\n->" + r
                        
                        conn.send(friends.encode())

                # Show
                elif msgL[1] == "SHOWF":
                    showM = "\n\tMEMBERS"

                    showM += f"\n{username} (you)"

                    if msgL[2] in users[username]['groups'].keys():
                        for member in users[username]['groups'][msgL[2]]['friends']:
                            showM += "\n" + member
                    
                    conn.send(showM.encode())
                    
                # Message
                elif msgL[1] == "SEND":
                    if msgL[2] in users[username]['groups'].keys():
                        users[username]['groups'][msgL[2]]['messages'].append(username + ": " + msgL[3])

                        # Update each member
                        for member in users[username]['groups'][msgL[2]]['friends']:

                            users[member]['groups'][msgL[2]]['messages'].append(username + ": " + msgL[3])

                            users[member]['groups'][msgL[2]]['notifications'] += 1
                
                # History
                elif msgL[1] == "HIST":
                    if msgL[2] in users[username]['groups'].keys():
                        users[username]['groups'][msgL[2]]['notifications'] = 0

                        history = "\n\t" + msgL[2]

                        for message in users[username]['groups'][msgL[2]]['messages']:
                            history += "\n" + message
                        
                    else:
                        history = "\n\tNOT FOUND"

                    conn.send(history.encode())

                # Delete Chat
                elif msgL[1] == "DELETEC":
                    
                    if msgL[2] in users[username]['groups'].keys():

                        users[username]['groups'][msgL[2]]['messages'].clear()

                # Exit
                elif msgL[1] == "EXIT":
                    if msgL[2] in users[username]['groups'].keys():

                        # Update each member
                        for member in users[username]['groups'][msgL[2]]['friends']:

                            users[member]['groups'][msgL[2]]['friends'].remove(username)

                            users[member]['groups'][msgL[2]]['messages'].append(username + " left")
                        
                        del(users[username]['groups'][msgL[2]])

            # DELETE CHAT------------------------------
            elif msgL[0] == "DELETEC":

                if msgL[1] in users[username]['friends'].keys():

                    users[username]['friends'][msgL[1]]['messages'].clear()

            # BLOCK USER-------------------------------
            elif msgL[0] == "BLOCK":

                if msgL[1] in users[username]['friends'].keys():
                    
                    users[username]['friends'][msgL[1]]['isBlocked'] = False if users[username]['friends'][msgL[1]]['isBlocked'] else True

            # QUIT-------------------------------------
            elif msgL[0] == "QUIT":
                users[username]['online'] = False
                connected = False
                conn.close()
    
    print("\nOUTLINE: " + username)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 1234

    try:
        server.bind((host, port))
    except:
        print("\nERROR AL CREAR EL SERVIDOR")
    
    threadList = []
    server.listen()
    activo = True

    try:
        print("\nSERVER ACTIVE")
        while activo:
            conn, add = server.accept()

            thread = threading.Thread(target=connectClient, args=[conn])
            threadList.append(thread)
            thread.start()
    
    except:
        print("\nALGO SALIO MAL")

    finally:
        for t in threadList:
            t.join()
        server.close()



if __name__ == '__main__':
    main()