import socket
import time

def menu():
    print("\n\n1. See Friends")
    print("2. Add Friend")
    print("3. Enter Conversation")
    print("4. Delete Friend")
    print("5. Broadcast List")
    print("6. See Groups")
    print("7. Create Group")
    print("8. Enter Conversation Group")
    print("0. Exit")

def menu_conversation(isBlocked = False, isGroup = False):
    option4 = "4. Unlock User"
    if isBlocked == False:
        print("\n\n1. Send Message")
        print("2. Refresh Conversation")

        option4 = "4. Block User"

    print("3. Delete Conversation")
    if isGroup:
        print("4. Show Members")
        print("5. Add member")
        print("6. Exit Group")
    else:
        print(option4)
    print("0. Exit")

def show_friends(client: socket.socket):
    command = "SHOWF"

    client.send(command.encode())
    
    friends = client.recv(1024)

    if friends:
        print(friends.decode())

def show_groups(client: socket.socket):
    command = "SHOWG"

    client.send(command.encode())

    groups = client.recv(1024)

    if groups:
        print(groups.decode())

def show_members(client: socket.socket, name: str):
    command = f"GROUP|SHOWF|{name}"

    client.send(command.encode())

    members = client.recv(1024)

    if members:
        print(members.decode())

def get_conversation(client: socket.socket, username: str) -> bool:
    isBlocked = False

    command = f"HIST|{username}"

    client.send(command.encode())

    conversation = client.recv(2048)

    if conversation:
        conversationL = conversation.decode().split("|")
        print(conversationL[0])

        try:
            if conversationL[1] == "BLOCKED":

                isBlocked = True
                print("\t" + conversationL[1])
        except:
            pass

    return isBlocked

def get_group_conversation(client: socket.socket, name: str):
    command = f"GROUP|HIST|{name}"

    client.send(command.encode())

    conversation = client.recv(2048)

    if conversation:
        print(conversation.decode())

def enter_username():
    username = ""

    while not username:
        username = input("Enter a name: ")
    
    return username

def login(client: socket.socket):
    username = enter_username()
    
    command = f"LOGIN|{username}"

    client.send(command.encode())

    message = ""

    try:
        print("Connecting...")
        message = client.recv(1024)

        if message: 
            message = message.decode()

            if message == "1":
                return True
    
    except socket.error as e:
            print(f"An error ocurred: {e}")
    
    return False
    

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = socket.gethostname()
    # host = '172.18.18.107'
    port = 1234
    
    command = ""
    
    try:
        client.connect((host, port))

        if(login(client)):

            op = -1

            while op != "0":
                
                menu()
                op = input("Select an Option: ")
                
                # See friends---------------------
                if op == "1":
                    show_friends(client)
                
                # Add | Delete friend-------------
                elif op == "2":
                    command = "SHOWU"

                    client.send(command.encode())
                    
                    time.sleep(1)

                    users = client.recv(2048)

                    if users:
                        print(users.decode())

                    username = enter_username()
                        
                    command = f"ADD|{username}"

                    client.send(command.encode())

                # Enter Coversation---------------
                elif op == "3":
                    show_friends(client)

                    username = enter_username()

                    isBlocked = get_conversation(client, username)

                    sub_op = " "

                    while sub_op != "0":
                        time.sleep(0.5)
                        
                        menu_conversation(isBlocked)
                        sub_op = input("Select an Option: ")
                        # Send Message
                        if sub_op == "1" and isBlocked == False:
                            message = ""

                            while not message:
                                message = input("Enter A Message: ")

                            command = f"SEND|{username}|{message}"

                            client.send(command.encode())
                        # Refresh Chat
                        elif sub_op == "2" and isBlocked == False:
                            isBlocked = get_conversation(client, username)
                        # Delete Chat
                        elif sub_op == "3":
                            command = f"DELETEC|{username}"

                            client.send(command.encode())
                        # Block User
                        elif sub_op == "4":
                            command = f"BLOCK|{username}"

                            client.send(command.encode())
                            
                            isBlocked = get_conversation(client, username)

                # Delete Friend-------------------
                elif op == "4":
                    show_friends(client)

                    username = enter_username()

                    command = f"DELETEF|{username}"

                    client.send(command.encode())

                # Broadcast List------------------
                elif op == "5":
                    show_friends(client)

                    print("@ to finish")

                    username = ""
                    
                    command = "BROADCAST"

                    while username != "@":
                        username = enter_username()

                        if username != "@":
                            command += f"|{username}"
                    
                    message = ""

                    while not message:
                        message = input("Enter A Message: ")
                    
                    command += f"|{message}"

                    client.send(command.encode())

                # See Group-----------------------
                elif op == "6":
                    show_groups(client)

                # Create Group--------------------
                elif op == "7":
                    command = "GROUP|CREATE"

                    name = ""
                    
                    while not name:
                        name = input("Name of the group: ")
                    
                    command += f"|{name}"

                    show_friends(client)

                    print("@ to finish")

                    username = ""

                    while username != "@":
                        username = enter_username()

                        if username != "@":
                            command += f"|{username}"
                    
                    client.send(command.encode())

                # Enter Conversation Group--------
                elif op == "8":
                    show_groups(client)

                    name = enter_username()

                    get_group_conversation(client, name)

                    sub_op = " "

                    while sub_op != "0":
                        time.sleep(0.5)

                        menu_conversation(False, True)
                        sub_op = input("Select an Option: ")

                        # Send Message
                        if sub_op == "1":
                            message = ""

                            while not message:
                                message = input("Enter A Message: ")
                            
                            command = f"GROUP|SEND|{name}|{message}"

                            client.send(command.encode())
                        
                        # Refresh Chat
                        elif sub_op == "2":
                            get_group_conversation(client, name)

                        # Delete Chat
                        elif sub_op == "3":
                            command = f"GROUP|DELETEC|{name}"

                            client.send(command.encode())

                        # Show Members
                        elif sub_op == "4":
                            show_members(client, name)

                        # Add Member
                        elif sub_op == "5":
                            command = f"GROUP|SHOWU|{name}"

                            client.send(command.encode())

                            time.sleep(1)

                            users = client.recv(1024)

                            if users:
                                print(users.decode())

                            username = enter_username()

                            command = f"GROUP|ADD|{name}|{username}"

                            client.send(command.encode())

                        # Exit Group
                        elif sub_op == "6":
                            command = f"GROUP|EXIT|{name}"

                            client.send(command.encode())

                            sub_op = "0"

                # Exit----------------------------
                elif op == "0":
                    msj = "QUIT"
                    client.send(msj.encode())
    
    except socket.error as e:
        print(f"An error ocurred: {e}")

    except KeyboardInterrupt:
        print('Closing server')
    
    finally:
        client.close()


if __name__ == '__main__':
    main()