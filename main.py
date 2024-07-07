from campBridgeV2 import send_transaction as bridge
from checks import get_faucet_tx as faucet_check
from checks import get_bridge_tx as bridge_check
from nutClaim import get_faucet as claim_token
from nutApprove import send_transaction as approve_flips
from nutCoinflip import send_transaction as flip_token
from nutBalanceCheck import get_token_balance
from time import sleep
from datetime import datetime as dt
from datetime import timedelta
import logging
from random import randint
from threading import Thread

# Setting up logging configuration
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

# Console handler for logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler_format = '%(asctime)s | %(levelname)s [%(threadName)s]: %(message)s'
console_handler.setFormatter(logging.Formatter(console_handler_format))
logger.addHandler(console_handler)

# File handler for debug logs
dfile_handler = logging.FileHandler('./logs/debug.log')
dfile_handler.setLevel(logging.DEBUG)
dfile_handler_format = '%(asctime)s | %(levelname)s [%(threadName)s]: %(message)s'
dfile_handler.setFormatter(logging.Formatter(dfile_handler_format))
logger.addHandler(dfile_handler)

# File handler for info logs
file_handler = logging.FileHandler('./logs/info.log')
file_handler.setLevel(logging.INFO)
file_handler_format = '%(asctime)s | %(levelname)s [%(threadName)s]: %(message)s'
file_handler.setFormatter(logging.Formatter(file_handler_format))
logger.addHandler(file_handler)


def start_thread(addr, pk, i, proxy):
    """
    Function to start a thread for processing token claims and flips.

    Args:
        addr (str): Wallet address.
        pk (str): Private key for the wallet.
        i (int): Index of the wallet.
        proxy (str): Proxy address

    Returns:
        None
    """
    token_claims_counter = 0
    flip_approve = 0

    try:
        max_token_claims = randint(1, 5)  # Maximum number of token claims
        while token_claims_counter < max_token_claims:
            time_to_sleep = 0
            delta = timedelta(days=1)

            claim_result = claim_token(addr, proxy)
            token_claims_counter += 1
            logger.info(f'W{i} address: {addr}\n'
                        f'Token claim #{token_claims_counter}\n'
                        f'{claim_result}')

            if not flip_approve:
                time_between_firstclaim_and_approve = randint(30, 60)  # Time between the first claim and approval
                sleep(time_between_firstclaim_and_approve)
                approve_result = approve_flips(pk)
                logger.info(f'W{i} address: {addr}\n'
                            f'Approve result: {approve_result}')
                flip_approve += 1

            last_token_claim_timing = dt.now()
            time_between_claim_and_firstflip = randint(120, 180)  # Time between the first claim and the first flip
            sleep(time_between_claim_and_firstflip)

            while True:
                flip_side = randint(0, 1)
                balance = int(get_token_balance(addr))

                if (last_token_claim_timing - dt.now()) > delta:
                    break

                if balance == 0:
                    logger.info(f'W{i} address: {addr}\n'
                                f'Token balance is empty. Sleeping till next claim.')
                    time_to_sleep = (last_token_claim_timing + delta) - (
                            dt.now() + (timedelta(minutes=randint(1, 120))))
                    break
                elif balance > 50:
                    flip_amount = randint(1, 50)  # Amount of tokens to flip
                    flip_result = flip_token(pk, flip_side, flip_amount)
                else:
                    flip_amount = randint(1, balance)  # Amount of tokens to flip
                    flip_result = flip_token(pk, flip_side, flip_amount)

                logger.info(f'W{i} address: {addr}\n'
                            f'Flip result: {flip_result}')

                time_between_flips = randint(3_600, 14_400)  # Time between flips
                sleep(time_between_flips)

            sleep(time_to_sleep.total_seconds())

    except Exception as e:
        logger.info(f'Inside thread error: {e}')


def main():
    """
    Main function to read wallet data, initiate transactions, and start threads.


    Returns:
        None
    """
    threads_counter = 0
    threads = []
    logger.info(f'Started application.\n\n\n')

    with open('addrlist_shuffled') as file:
        for i, line in enumerate(file):

            address, privkey, proxy = line.strip().split(';')
            logger.info(f'W{i} address: {address}\n'
                        f'Started with new wallet.')

            try:
                if not faucet_check(address):
                    logger.error(f'W{i} address: {address}\n'
                                 f'No faucet txs found. Raised error.')
                    raise ValueError

                amount_to_bridge_in_eth = float(
                    randint(1, 5) * 10 ** (-4)) + (randint(1, 99_999) * 10**(-9))  # Amount to bridge in ETH
                logger.info(f'W{i} address: {address}\n'
                            f'Bridge: {bridge(address, privkey, amount_to_bridge_in_eth)}')

                after_bridge_interval = randint(120, 180)  # Delay after starting with a new wallet
                sleep(after_bridge_interval)

                if not bridge_check(address):
                    logger.error(f'W{i} address: {address}\n'
                                 f'No bridge txs found. Raised error.')
                    raise ValueError

                before_thread_interval = randint(0, 0)  # Delay before starting the thread
                sleep(before_thread_interval)

                thread_name = f"Thread-{threads_counter}"
                logger.info(f'W{i} address: {address}\n'
                            f'Starting {thread_name}')
                thread = Thread(target=start_thread, args=(address, privkey, i, proxy), name=thread_name)
                threads.append(thread)
                thread.start()
                threads_counter += 1

            except Exception as exc:
                logger.error(f'W{i} address: {address}\n'
                             f'Failed to start with wallet\n'
                             f'Exception: {exc}')

    for thread in threads:
        thread.join()
    logger.info(f'\nFinished application.\n')


if __name__ == '__main__':
    print(float(
        randint(1, 5) * 10 ** (-4)) + (randint(1, 99_999) * 10**(-9)))
