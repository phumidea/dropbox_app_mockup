import json
import boto3
from datetime import datetime, timedelta

BUCKET_NAME = "phum2021" # Bucket name keep user data
s3 = boto3.client('s3') # Connect with S3
dynamodb = boto3.resource('dynamodb') # Connect with DynamoDB
table = dynamodb.Table('myDropboxUsers') # Connect table

def lambda_handler(event, context):

    command = str(event["queryStringParameters"]["command"]) # Classify what request want from command parameter
    
    #############################################################################################
    if command == "newuser": # Create new user
    
        username = str(event["queryStringParameters"]["username"]) # Get username from request
        password = str(event["queryStringParameters"]["password"]) # Get password from request
        
        try:
            response = table.get_item(Key={'username': username})["Item"]
            return {
                'statusCode': 200,
                'body': json.dumps("This username alredy existing.")
            }
        except:
            response = table.put_item(Item = {'username':username,'password':password})
            return {
                'statusCode': 200,
                'body': json.dumps("Create newuser finish.")
            }
            
   #############################################################################################
    elif command == "login": # Login to the application
        
        username = str(event["queryStringParameters"]["username"]) # Get username from request
        password = str(event["queryStringParameters"]["password"]) # Get password from request
        
        try:
            response = table.get_item(Key={'username': username})["Item"]
            if (response["username"] == username) and (response["password"] == password):
                return {
                    'statusCode': 200,
                    'body': json.dumps("Login successfull")
                }
            else:
                return {
                'statusCode': 200,
                'body': json.dumps("Wrong password! Please try again")
                }
        except:
            return {
            'statusCode': 200,
            'body': json.dumps("No username in database.")
            }
            
    #############################################################################################
    elif command == "put": # Upload file to S3
        fileName = str(event["queryStringParameters"]["fileName"]) # Get filename from request
        content = str(event["queryStringParameters"]["content"]) # Get file content from request
        path = "/tmp/" + fileName # Prepare path to save new file
        with open(path, 'w+') as file: # Write content in new file
            file.write(content)
        s3.upload_file(path, BUCKET_NAME, fileName) # Upload file to S3
        return {
            'statusCode': 200,
            'body': json.dumps("Put finish")
        }
    
    #############################################################################################
    elif command == "view": # List all file in bucket
        username = str(event["queryStringParameters"]["username"])
        all_file = [] # Create empty list for containing object information
        for obj in s3.list_objects(Bucket=BUCKET_NAME)["Contents"]: # Check loop for each object in bucket
            key = str(obj["Key"])
            key_list = key.split("+")
            if username in key_list[1:]:
                file = dict()
                file["Key"] = key_list[0]
                file["LastModified"] = (obj["LastModified"] + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                file["Size"] = obj["Size"]
                all_file.append(file)
        return {
            'statusCode': 200,
            'body': json.dumps(all_file)
        }
        
    #############################################################################################
    elif command == "get": # Download file from S3
        fileName = str(event["queryStringParameters"]["fileName"]) # get file name from request
        username = str(event["queryStringParameters"]["username"])
        for obj in s3.list_objects(Bucket=BUCKET_NAME)["Contents"]: # check each object
            key_str = str(obj["Key"])
            key_list = key_str.split("+")

            if (key_list[0] == fileName) and (username in key_list[1:]): # Match obj with file name
                path = "/tmp/"+key_str # create tmp path
                s3.download_file(BUCKET_NAME, key_str, path) # dwonload file from s3
                file = open(path,"r") # open and read content inside
                content = file.read()
                return {
                    'statusCode': 200,
                    'body': content
                }
        return {
            'statusCode': 200,
            'body': json.dumps("Type wrong filename")            
        }
      
    ############################################################################################# 
    elif command == "share":
        fileName = str(event["queryStringParameters"]["fileName"]) # get file name from request
        username = str(event["queryStringParameters"]["username"])
        share_user = str(event["queryStringParameters"]["share_user"])
        for obj in s3.list_objects(Bucket=BUCKET_NAME)["Contents"]:
            key = str(obj["Key"])
            key_list = key.split("+")
            if (key_list[0] == fileName) and (key_list[1] == username):
                copy_source = {"Bucket":BUCKET_NAME, "Key":key}
                s3.copy(copy_source,BUCKET_NAME,key+"+"+share_user)
                s3.delete_object(Bucket=BUCKET_NAME, Key=key)
                return {
                    'statusCode': 200,
                    'body': "Finish"
                }
    #############################################################################################
    else:
        return {
                'statusCode': 500,
                'body': json.dumps("AWS Service broken")
            }
