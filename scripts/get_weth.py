from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def get_weth(account=None):
    """
    Mints WETH by depositing ETH
    """
    #  To deposit eth we need:
    # -- ABI
    # -- WETH Address
    # -- WE NEED THE INTERFACE
    account = account if account else get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": amount})
    # tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Got 0.1 WETH")
    return tx


def main():
    get_weth()
