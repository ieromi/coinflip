import json
from web3 import Web3

# RPC endpoint and contract details
rpc = 'https://rpc.camp-network-testnet.gelato.digital'
contract_address = Web3.to_checksum_address('')


# Connecting to testnet
def connection():
    """
    Establishes a connection to the Camp testnet via Gelato.

    Returns:
        Web3 object if successful, Exception if failed.
    """
    try:
        w3 = Web3(provider=Web3.HTTPProvider(endpoint_uri=rpc))
        if not w3.is_connected():
            raise Exception("Failed to connect to testnet.")
        return w3
    except Exception as e:
        return e


# Creating account with private key
def create_account(w3, pk):
    """
    Creates an account using a provided private key.

    Args:
        w3 (Web3): Web3 object connected to the testnet.
        pk (str): Private key of the account.

    Returns:
        Account object if successful, Exception if failed.
    """
    try:
        acc = w3.eth.account.from_key(private_key=pk)
        return acc
    except Exception as e:
        return e


# Creating contract
def create_contract(w3):
    """
    Creates a contract instance using the ABI and contract address.

    Args:
        w3 (Web3): Web3 object connected to the testnet.

    Returns:
        Contract object if successful, Exception if failed.
    """
    try:
        with open('camp_nut_approve_abi.json') as abi:
            contract_abi = json.load(abi)
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        return contract
    except Exception as e:
        return e


def send_transaction(sender_pk):
    """
    Sends a transaction to approve a specified amount of tokens.

    Args:
        sender_pk (str): Private key of the sender's account.

    Returns:
        str: Transaction result message.
    """
    try:
        amount_eth = 0

        w3 = connection()
        account = create_account(w3, sender_pk)
        contract = create_contract(w3)

        tx_args = contract.encodeABI('approve',
                                     args=(
                                         Web3.to_checksum_address('0xb496430bf2394c1dd3c3f52edca68faf14b2a0d7'),
                                         115792089237316195423570985008687907853269984665640564039457584007913129639935
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

        # Set transaction parameters
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

        # Sign and send the transaction
        signed_tx = w3.eth.account.sign_transaction(tx_params, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_data = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)

        # Check the transaction status
        if tx_data['status'] == 1:
            return f'Transaction success, tx_hash: 0x{tx_data["transactionHash"].hex()}'
        else:
            raise Exception
    except Exception as e:
        return f"Transaction error: {e}"
