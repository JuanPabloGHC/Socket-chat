# Examen Redes

Carlos A. Cancino Escobar

Juan Pablo Gomez Haro Cabrera

## Data Structure

```python
users = {
    username : {
        "conn": conn,
        "friends": {
            username: {
                "messages": ["messages..."],
                "isBlocked": True | False,
                "notifications": int
            }
        },
        "groups": {
            name: {
                "friends": [],
                "messages": [],
                "notifications": int
            }
        },
        "online": True | False
    }
}
```

## Commands

`LOGIN|<username>`: Login

`SHOWF`: Show friends

`SHOWU`: Show unfriends

`SHOWG`: Show groups

`ADD|<username>`: Adds friend

`DELETF|<username>`: Delete a friend

`HIST|<username>`: Show message history

`SEND|<username>|<message>`: Send a message to a user

`BROADCAST|<username>*|<message>`: Send a message to many users

`GROUP|CREATE|<name>|<username>*`: Create a group with many users

`GROUP|ADD|<name>|<username>`: Add a friend to a group

`GROUP|SHOWU|<name>`: Show friends that are not members of the group

`GROUP|SHOWF|<name>`: Show friends that are in the group

`GROUP|SEND|<name>|<message>`: Send a message to a group

`GROUP|HIST|<name>`: Show message history of a group

`GROUP|DELETC|<name>`: Delete message history of a group

`GROUP|EXIT|<name>`: Exit from a group

`DELETEC|<username>`: Delete message history

`BLOCK|<username>`: Block or Unlock a user

`QUIT`: Logout