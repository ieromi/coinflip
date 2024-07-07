import json
from web3 import Web3


rpc = 'https://rpc.camp-network-testnet.gelato.digital'
contract_address = Web3.to_checksum_address('0x57220dF057fF9DfECa19DAe9D8CcDb36F37fF74E')


# Connecting to testnet
def connection():
    """
    This function connects to the Camp Network Testnet using the provided RPC endpoint.

    Returns:
        Web3: An instance of the Web3 library connected to the testnet.
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
    This function creates an account using the provided private key.

    Args:
        w3 (Web3): An instance of the Web3 library.
        pk (str): The private key of the account.

    Returns:
        Web3.eth.account: An instance of the Web3 account.
    """
    try:
        acc = w3.eth.account.from_key(private_key=pk)
        return acc
    except Exception as e:
        return e


# Creating contract
def create_contract(w3):
    """
    This function creates a contract instance using the provided contract address and ABI.

    Args:
        w3 (Web3): An instance of the Web3 library.

    Returns:
        Web3.eth.contract: An instance of the Web3 contract.
    """
    try:
        with open('camp_nut_approve_abi.json') as abi:
            contract_abi = json.load(abi)
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        return contract
    except Exception as e:
        return e


def get_token_balance(address):
    """
    This function retrieves the token balance of the provided address.

    Args:
        address (str): The address to retrieve the balance for.

    Returns:
        float: The token balance in ether.
    """
    try:
        w3 = connection()
        contract = create_contract(w3)
        balance = contract.functions.balanceOf(address).call()
        return Web3.from_wei(balance, 'ether')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
