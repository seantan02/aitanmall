import asyncio
import websockets
import ssl
from helper import json_tools
from collections import defaultdict
import json
import requests
from classes.space import Space
from classes.room import Room
from classes.member import Member
from helper import general

merchant_api_key_to_space = json_tools.read_json("/var/www/aitanmall.com/socket/api_keys/key_to_merchant.json")
MESSAGE_LIMIT = 20 #per second

existing_space_names = []
existing_spaces = []
existing_client_sids = []
client_message_count = defaultdict(int)

async def handle_websocket(websocket, path):
    await websocket.send(json.dumps({"event_type":"verification", "message": "Please send API key"}))

    # Now wait for the client to send the API key
    response = await websocket.recv()

    # Parse the JSON response
    data = json.loads(response)

    # Extract the API key
    api_key = data.get('api_key')  # replace 'api_key' with the actual key used in your JSON object
    space_extension = data.get('room_id', "")
    room_id = data.get('room_id', "000000")
    member_name = data.get('room_id', "socket")
    
    # Do something with the API key...
    print(f"Received API key: {api_key}")
    print(f"Room ID: {room_id}")
    
    if api_key not in merchant_api_key_to_space:
        print("Invalid token")
        await websocket.send(json.dumps({"message": "Token invalid"}))
        await websocket.close()
        return
    print("Token valid")

    #generate unique SID for client
    member_sid_not_unique = True
    while member_sid_not_unique:
        member_sid = general.generate_random_string(9)
        if member_sid not in existing_client_sids:
            existing_client_sids.append(member_sid)
            member_sid_not_unique = False
    #create a websocket member
    member = Member(websocket, member_name, member_sid)
    print(f"Member created: {member}")

    merchant_space_name = merchant_api_key_to_space[api_key]

    if merchant_space_name not in existing_space_names:
        space = Space(merchant_space_name+space_extension)
        print(f"Space created: {space}")
        room = Room(room_id)
        print(f"Room created: {room}")
        room.add_member(member)
        print(f"Member added to room:{room}")
        space.create_room(room)
        print(f"Room created in space:{space}")
        existing_spaces.append(space)
        existing_space_names.append(merchant_space_name)
        print(f"Current space and space names: {existing_spaces} ; {existing_space_names}")
    else:
        print(f"Space name found! :{merchant_space_name}")
        space = existing_spaces[existing_space_names.index(merchant_space_name)]
        print(f"Spce selected {space}")
        room = space.get_room(room_id)
        print(f"Room selected from space: {room}")
        if not isinstance(room, Room):
            print(f"Room is {room} so we assign room id to : {room_id}")
            room = Room(room_id)
            print(f"Room created: {room}")
            space.create_room(room)
            print(f"Room created in space:{space}")
        room.add_member(member)
        print(f"Member added to room: {room}. Current members in room: {room.get_members}")

    print(f"Space: {space} created. Rooms inside are {space.get_environment()}")
    print(f"Spaces are now: {existing_spaces}")
    #This function handles incoming WebSocket connections
    try:
        client_websocket = member.get_websocket()
        await client_websocket.send(json.dumps({
        "event_type":"connected",
        "message": "Connection established. Ready to go."
        }))
        print("Connection message sent!")
        print("Waiting for message")
        global client_message
        while True:
            client_message = await client_websocket.recv()

            print("Checking limit. Start of while.")
            if client_message_count[api_key] >= MESSAGE_LIMIT:
                print("Rate limit exceeded.")
                await client_websocket.send('message_limit_exceeded')
                await client_websocket.close()

            data = json.loads(client_message)
            data_message = data.get("message")
            data_name = data.get("name", None)
            data_to_name = data.get("to_name", None)
            data_webhook = data.get("webhook_address", None)
            data_broadcast = data.get("broadcast")
            data_room_id = data.get("room_id", "000000")
            
            print(f"Message received {data_message}, room id: {data_room_id}")
            #if broadcast == True we send message to everyone
            #if get room_id, else room_id = 0
            if data_broadcast == True:
                await broadcast_message(member, space, "message", data_name, room, data_message)
            else:
                await send_message_to_room(space, data_room_id, "message", data_name, member, room, data_message)

            client_message_count[api_key] += 1
            #if client set a  webhook address, we send a wbhook data to the address
            if data_webhook != None:
                print(f"Sending webhook and from_name is {data_name}")
                await post_webhook("message", data_name, data_to_name, room, member, data_webhook, data_message)


    except websockets.exceptions.ConnectionClosedOK as e:
        print("Connection closed properly")
        print(str(e))
    except websockets.exceptions.ConnectionClosedError as e:
        print("Connection lost with client")
        print(str(e))
    except Exception as e:
        print(e)
    finally:
        room = space.get_room(room_id)
        member_removed = room.remove_member(member)
        if isinstance(room, Room):
            if room.get_members_count() == 0:
                space.remove_room(room)
                room = None
                if space.get_object_count ==0:
                    index_space = existing_spaces.index(space)
                    existing_spaces.pop(index_space)
                    space = None
        #broadcast message to everyone in the space name
        await broadcast_message(member, space, "member_left", data_name, room, f"{member_removed.get_name()} from room: {room.get_room_number()} has left")

        asyncio.create_task(reset_message_count(api_key))

async def broadcast_message(current_member, selected_space, event_type, client_name, current_room, client_message):
    for each_room in selected_space.get_environment():
        print(f"{each_room} selected")
        for each_member in each_room.get_members():
            member_websocket = each_member.get_websocket()
            if  each_member.get_sid() == current_member.get_sid():
                #client message to send
                message_to_send = json.dumps({
                    "event_type":event_type,
                    "from_name": client_name,
                    "from_room_id": current_room.get_room_number(),
                    "room_id": each_room.get_room_number(),
                    "client_sid":current_member.get_sid(),
                    "from_others": False,
                    "message": client_message
                })
            else:
                #client message to send
                message_to_send = json.dumps({
                    "event_type":event_type,
                    "from_name": client_name,
                    "from_room_id": current_room.get_room_number(),
                    "room_id": each_room.get_room_number(),
                    "client_sid":current_member.get_sid(),
                    "from_others": True,
                    "message": client_message
                })
            await member_websocket.send(message_to_send)
            print(f"{client_message} was sent to {each_member}")

async def send_message_to_room(selected_space, target_room_id, event_type, client_name, client_member, client_room, client_message):
    to_room = selected_space.get_room(target_room_id)
    for each_member in to_room.get_members():
        if isinstance(each_member, Member) and not None:
            if  each_member.get_sid() == client_member.get_sid():
                #client message to send
                message_to_send = json.dumps({
                    "event_type":event_type,
                    "from_name": client_name,
                    "from_room_id": client_room.get_room_number(),
                    "to_room_id": target_room_id,
                    "client_sid":each_member.get_sid(),
                    "from_others": False,
                    "message": client_message
                })
            else:
                #client message to send
                message_to_send = json.dumps({
                    "event_type":event_type,
                    "from_name": client_name,
                    "from_room_id": client_room.get_room_number(),
                    "to_room_id": target_room_id,
                    "client_sid":each_member.get_sid(),
                        "from_others": True,
                        "message": client_message
                    })
                member_websocket = each_member.get_websocket()
                await member_websocket.send(message_to_send)
                print(f"{client_message} was sent to {each_member}")
        else:
            member_websocket = client_member.get_websocket()
            await member_websocket.send("Room ID does not exist.")
            print(f"Room: {target_room_id} doesnt not exist. Message did not deliver.")

async def post_webhook(event_type, client_name, receiver_name, current_room, current_member, webhook_address, client_message):
    print(f"Webhook address not None so preparing to send webhook")
    print(f"Webhook from_name {client_name}")
    webhook_data = { 
        "event_type":event_type,
        "from_name": client_name,
        "to_name": receiver_name,
        "from_room_id": current_room.get_room_number(),
        "broadcast":True,
        "client_sid":current_member.get_sid(),
        "message": client_message
    }
    webhook_post = requests.post(webhook_address, json=webhook_data)
    print(f"Webhook data posted to {webhook_address}")
    webhook_response = webhook_post.status_code
    if webhook_response == 201:
        webhook_status = "sent"
    elif webhook_response == 200:
        webhook_status = "received"
    else:
        webhook_status = "failed"

    print(f"Webhook reponse: {webhook_post}")
    print(f"Webhook postage status code: {webhook_response}")
    webhook_response_notification = json.dumps({
        "event_type":"webhook_update",
        "webhook_address":webhook_address,
        "status": webhook_status
    })
    await current_member.get_websocket().send(webhook_response_notification)
    print(f"Webhook update sent to {current_member.get_websocket()}")

async def reset_message_count(api_key):
    await asyncio.sleep(10)
    client_message_count[api_key] = 0

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = "/etc/letsencrypt/live/aitanmall.com/fullchain.pem"
private_key = "/etc/letsencrypt/live/aitanmall.com/privkey.pem"
ssl_context.load_cert_chain(localhost_pem, private_key)

# Define the host and port for your WebSocket server
host = 'aitanmall.com'
port = 59001

# Start the WebSocket server
start_server = websockets.serve(handle_websocket, host, port, ssl=ssl_context)

# Run the server indefinitely
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
