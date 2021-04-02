
################################### Mydropbox 6030462921 Phum Lertritmahachai ####################################

import requests
import json

##################### This is url for connect aws lambda ####################
URL = "https://qaplszm1tb.execute-api.ap-southeast-1.amazonaws.com/default/myDropbox" # This is url for connect aws

#################### This function is called when start or when run previous command finish. ####################
def init_state():
    print("==========================================")
    print("Please input command")
    print("1) newuser => create a new user with specified username and password.")
    print("2) login => login to the application.")
    print("3) logout => logout from the application.")
    print("4) put => upload one file at a time.")
    print("5) view => look at files that users have uploaded themselves.")
    print("6) get => download one file at a time.")
    print("7) share => share a file with another user.")
    print("8) quit => stop using the myDropbox application.")
    print("==========================================")
    
#################### This function is create user and store information in dynamodb ####################
def newuser(username, password):
    payload = {"username" : username, "password":password, "command": "newuser"}
    r = requests.post(URL, params = payload)
    print(r.text)

#################### This function is login and check user from dynamodb ####################
def login(is_Login, username, password):
    if is_Login:
        print("You are already login, please logout first.")
        return [is_Login, ""]
    else:
        payload = {"username" : username, "password":password, "command": "login"}
        r = requests.post(URL, params = payload)
        print(r.text)
        if r.text == '"Login successfull"':
            is_Login = True
        return [is_Login, username]

#################### This function is logout from console ####################
def logout(is_Login):
    if is_Login:
        is_Login = False
        print("You are already Logout")
    else:
        print("You can't logout while you didn't login.")
    return is_Login

#################### This function is upload file from local to s3 ####################
def put(is_Login, user_login, fileName):
    if not is_Login:
        print("You must login before use put.")
    else:
        f = open(fileName,"r") # Open and Read content inside file
        content = f.read()
        payload = {"fileName" : fileName + "+" + str(user_login), "content":content, "command": "put"} # Add data to use in lambda
        r = requests.post(URL, params = payload) # Send request for put file to Lambda
        print(r.text) # print respond from lambda 

#################### This function is show all file in bucket ####################
def view(is_Login, user_login):
    if not is_Login:
        print("You must login before use view.")
    else:
        payload = {"username":user_login,"command": "view"}
        r = requests.get(URL, params = payload) # Send request for view object in bucket
        all_file = eval(r.text) # Change from string to list
        for f in all_file: # List all file
            print(f)

#################### This function is download file to local ####################
def get(is_Login, user_login, fileName):
    if not is_Login:
        print("You must login before use get.")
    else:
        payload = {"fileName":fileName, "username":str(user_login) ,"command": "get"}
        r = requests.get(URL, params = payload) # Send request to lambda
        content = r.text # Read content in download file
        print(r.text)
        with open("./downloads/" + fileName, 'w') as f: # Write new file
            f.write(content)
        print("Get finish")

#################### This function is share file with user ####################
def share(is_Login, user_login, fileName, share_user):
    if not is_Login:
        print("You must login before use share.")
    else:
        payload = {"fileName":fileName, "username": user_login, "share_user":share_user , "command": "share"}
        r = requests.get(URL, params = payload)
        print("Finish")

#################### This function is init dropbox ####################
def main():
    is_Login = False
    user_login = ""
    print("Welcome to myDropbox Application")
    while(True):
        init_state()
        request = input("add you command here => ").split()
        command = request[0]
        ########## new user ##########
        if command == "newuser":
            username = request[1]
            password = request[2]
            check_password = request[3]
            if password != check_password:
                print("You type wrong password. Please check your password again")
            else:
                newuser(username,password)

        ########## login ##########
        elif command == "login":
            username = request[1]
            password = request[2]
            result = login(is_Login, username, password)
            is_Login = result[0]
            user_login = result[1]
        
        ########## logout ##########
        elif command == "logout": 
            is_Login = logout(is_Login)
            user_login = ""
        
        ########## put ##########
        elif command == "put":
            fileName = request[1]
            put(is_Login, user_login, fileName)

        ########## view ##########
        elif command == "view": view(is_Login, user_login)

        ########## get ##########
        elif command == "get":
            fileName = request[1]
            get(is_Login, user_login, fileName)
        
        ######### share ##########
        elif command == "share":
            fileName = request[1]
            share_user = request[2] 
            share(is_Login, user_login, fileName, share_user)

        ########## quit ##########
        elif command == "quit": break
        else:
            print("You enter wrong command, please try again")

main()