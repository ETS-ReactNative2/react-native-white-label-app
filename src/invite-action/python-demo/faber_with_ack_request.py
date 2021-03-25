import asyncio
import json
from time import sleep
import requests

from vcx.api.connection import Connection
from vcx.api.utils import vcx_agent_provision, vcx_messages_download
from vcx.api.vcx_init import vcx_init_with_config
from vcx.state import State

# 'agency_url': URL of the agency
# 'agency_did':  public DID of the agency
# 'agency_verkey': public verkey of the agency
# 'wallet_name': name for newly created encrypted wallet
# 'wallet_key': encryption key for encoding wallet
# 'payment_method': method that will be used for payments
provisionConfig = {
    'agency_url': 'https://eas-team1.pdev.evernym.com',
    'agency_did': 'CV65RFpeCtPu82hNF9i61G',
    'agency_verkey': '7G3LhXFKXKTMv7XGx1Qc9wqkMbwcU2iLBHL8x1JXWWC2',
    'wallet_name': 'faber_wallet',
    'wallet_key': '123',
    'payment_method': 'null',
    'enterprise_seed': '000000000000000000000000Trustee1',
    'protocol_type': '1.0',
}


async def main():
    await init()

    connection_to_alice = await connect()

    print("Send invite for action with requesting Ack on Accept")
    
    url = "https://ecosystem.corpone.org/IDPal/uuid/applications?_profile=test"

    payload="{\r\n  \"c1_token\": \"A7D2ED82-765E-53E1-EA0E-246B8A0D632C\",\r\n  \"profile_id\": \"131\"\r\n}"
    headers = {
        'Authorization': 'Key=Z50i1buy6SaWv4OxsY4EeEseC19mZ_aFjKifazXOvTlDeRAQCjjnMakIF36HXOduQ15kYf9NCYhtt0_OhE_qzg',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': 'AWSALB=mG3O5lGya7C3cmPeYTLkH4Jxg0H8JFIFPoP8DmTsXbBfTxDl4GntRzhh2w6KV9DKii8Z0biQBUvR3rvm0OLNHAlHkX6rFNoV8pGvzHnl0le8RdHB67DXZCrGDFXl'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    idPalUUID = json.loads(response.text)['uuid'];

    # For testing expired tokens
    expired_id_pal_token = '06de533c'
    invite_action_data = {
        "invite_action_meta_data": {
            "id_pal_token": idPalUUID,
            "invite_action_title": "Hi, Jonny",
            "invite_action_detail": "Example Credit Union would like you to complete some identity verification steps. These will include scanning a drivers\' license and a facial scan",
            "accept_text": "Verify my identity",
            "deny_text": "Decline",
        }
    }

    stringified_invite_action = json.dumps(invite_action_data, separators=(',', ':'))

    invite = await connection_to_alice.send_invite_action({'goal_code': stringified_invite_action, 'ack_on': ['ACCEPT']})
    print("Invitation for the action was sent")
    invite = json.loads(invite)

    sleep(10)

    print("Waiting for received an acknowledgment for the invitation")
    # get connection DID
    pw_did = await connection_to_alice.get_my_pw_did()

    while True:
        print("Download messages for connection and find either ack or problem-report message")
        message_type, message = await download_message(pw_did, ['ack', 'problem-report'])
        if message and message_type == "ack" and invite["@id"] == json.loads(message)["~thread"]["thid"]:
            print("Ack message is received")
            print(message)
            break
        elif message and message_type == "problem-report" and invite["@id"] == json.loads(message)["~thread"]["thid"]:
            print("Invitation was rejected")
            print(message)
            break

        sleep(10)

    print("Finished")


async def init():
    print("Provision an agent and wallet, get back configuration details")
    config = await vcx_agent_provision(json.dumps(provisionConfig))
    config = json.loads(config)
    # Set some additional configuration options specific to alice
    config['institution_name'] = 'Faber'
    config['institution_logo_url'] = 'http://robohash.org/1'
    config['genesis_path'] = 'docker.txn'

    config = json.dumps(config)

    print("Initialize libvcx with new configuration")
    await vcx_init_with_config(config)


async def connect():
    print("#5 Create a connection to alice and print out the invite details")
    connection_to_alice = await Connection.create('alice')
    await connection_to_alice.connect('{"use_public_did": true}')
    await connection_to_alice.update_state()
    details = await connection_to_alice.invite_details(False)
    print("**invite details**")
    print(json.dumps(details))
    print("******************")

    print("#6 Poll agency and wait for alice to accept the invitation (start alice.py now)")
    connection_state = await connection_to_alice.get_state()
    while connection_state != State.Accepted:
        sleep(2)
        await connection_to_alice.update_state()
        connection_state = await connection_to_alice.get_state()

    print("Connection is established")
    return connection_to_alice


async def download_message(pw_did: str, msg_types: [str]):
    messages = await vcx_messages_download("MS-103", None, pw_did)
    messages = json.loads(messages.decode())[0]['msgs']
    message = [message for message in messages if json.loads(message["decryptedPayload"])["@type"]["name"] in msg_types]
    if len(message) > 0:
        decryptedPayload = message[0]["decryptedPayload"]
        return json.loads(decryptedPayload)["@type"]["name"], json.loads(decryptedPayload)["@msg"]
    else:
        return None, None

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    sleep(1)
