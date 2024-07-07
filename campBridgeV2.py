import json
from web3 import Web3

# RPC endpoint and contract details
rpc = ''
contract_address = Web3.to_checksum_address('0x5c3Ec2182Be9FbeA0da50d517362a069e13FB50E')
min_gas_limit = 200000
extra_data = '0x7375706572627269646765'


# Connecting to testnet
def connection():
    """
    Establishes a connection to the Sepolia testnet via Infura.

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


# Creating Sepolia -> Camp testnet bridge contract
def create_contract(w3):
    """
    Creates a contract instance using the ABI and contract address.

    Args:
        w3 (Web3): Web3 object connected to the testnet.

    Returns:
        Contract object if successful, Exception if failed.
    """
    try:
        with open('camp_bridge_v2_abi.json') as abi:
            contract_abi = json.load(abi)
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        return contract
    except Exception as e:
        return e


def send_transaction(receiver_address, sender_pk, amount_eth):
    """
    Sends a transaction to bridge ETH from Sepolia to Camp testnet.

    Args:
        receiver_address (str): Address of the receiver.
        sender_pk (str): Private key of the sender's account.
        amount_eth (float): Amount of ETH to bridge.

    Returns:
        str: Transaction result message.
    """
    try:
        w3 = connection()
        account = create_account(w3, sender_pk)
        contract = create_contract(w3)

        to_address = receiver_address

        # Encode the transaction arguments
        tx_args = contract.encodeABI('bridgeETHTo',
                                     args=(
                                         to_address,
                                         min_gas_limit,
                                         extra_data
                                     ))

        # Estimate gas for the transaction
        gas_estimate = w3.eth.estimate_gas({
            'from': account.address,
            'to': contract.address,
            'value': w3.to_wei(amount_eth, 'ether'),
            'data': tx_args
        })
        print(f'Gas estimate: {gas_estimate}')

        # Retrieve fee history and calculate gas fees
        fee_history = w3.eth.fee_history(1, 'latest', [10])
        base_fee = fee_history['baseFeePerGas'][-1]
        max_priority_fee_per_gas = max_fee_per_gas = base_fee + 1000000
        print(f'max_priority_fee_per_gas: {max_priority_fee_per_gas}')

        # Set transaction parameters
        tx_params = {
            'chainId': w3.eth.chain_id,
            'gas': 200000,
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
            return f'Transaction success, tx_hash: {tx_data["transactionHash"].hex()}'
        else:
            raise Exception
    except Exception as e:
        return f"Transaction error: {e}"
