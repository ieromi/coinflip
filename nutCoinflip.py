import json
from web3 import Web3

rpc = 'https://rpc.camp-network-testnet.gelato.digital'
contract_address = Web3.to_checksum_address('0xb496430bF2394C1dd3c3f52EdCA68Faf14b2A0d7')

"""
Connecting to testnet
"""


def connection():
    try:
        w3 = Web3(provider=Web3.HTTPProvider(endpoint_uri=rpc))
        if not w3.is_connected():
            raise Exception("Failed to connect to testnet.")
        return w3
    except Exception as e:
        return e


"""
Creating account with private key
"""


def create_account(w3, pk):
    try:
        acc = w3.eth.account.from_key(private_key=pk)
        return acc
    except Exception as e:
        return e


"""
Creating contract
"""


def create_contract(w3):
    try:
        with open('camp_nut_toss_abi.json') as abi:
            contract_abi = json.load(abi)
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        return contract
    except Exception as e:
        return e


"""
Send transaction
"""


def send_transaction(sender_pk, side: int, amount: int):
    try:
        amount_eth = 0

        w3 = connection()

        account = create_account(w3, sender_pk)

        contract = create_contract(w3)

        tx_args = contract.encodeABI('placeBet',
                                     args=(
                                         side,
                                         w3.to_wei(amount, 'ether')
                                     ))

        # Estimate gas for the transaction
        gas_estimate = w3.eth.estimate_gas({
            'from': account.address,
            'to': contract.address,
            'value': w3.to_wei(amount_eth, 'ether'),
            'data': tx_args
        })

        # Retrieve fee history and calculate gas fees
        fee_history = w3.eth.fee_history(1, 'latest', [10])
        base_fee = fee_history['baseFeePerGas'][-1]
        max_priority_fee_per_gas = max_fee_per_gas = base_fee + 1000000

        tx_params = {
            'chainId': w3.eth.chain_id,
            'gas': gas_estimate,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'from': account.address,
            'to': contract.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'data': tx_args,
            'value': w3.to_wei(amount_eth, 'ether')
        }

        signed_tx = w3.eth.account.sign_transaction(tx_params, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_data = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)

        if tx_data['status'] == 1:
            return f"Transaction success, tx_hash: 0x{tx_data['transactionHash'].hex()}"
        else:
            raise Exception
    except Exception as e:
        return f"Transaction error: {e}"
