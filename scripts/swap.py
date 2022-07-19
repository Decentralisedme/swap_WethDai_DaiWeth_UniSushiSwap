import brownie
from brownie import accounts, interface, config, network, chain
from scripts.helpful_scripts import get_account, approve_erc20
from scripts.chainlink_asset_pr import get_asset_price
from scripts.get_weth import get_weth
from scripts.chainlink_mapping import price_feed_mapping
from web3 import Web3
import time

amount_eth_to_swap = input("In ETH >> Amount of Weth To Dai: ")
amount_to_swap = Web3.toWei(amount_eth_to_swap, "ether")


def main():
    account = get_account()
    weth_address = config["networks"][network.show_active()]["weth_token"]
    dai_address = config["networks"][network.show_active()]["aave_dai_token"]
    sushiswapv2_router02 = config["networks"][network.show_active()][
        "sushiswapv2_router02"
    ]
    # balance_weth = float(interface.IERC20(weth_address).balanceOf(account.address))
    # # balance_weth = balance_weth / (1 * 10 ** 18)
    # balance_dai = float(interface.IERC20(dai_address).balanceOf(account.address))
    # # balance_dai = balance_dai / (1 * 10 ** 18)
    print(
        f"The starting balance of DAI in {account.address} is now {interface.IERC20(dai_address).balanceOf(account.address)/ (1 * 10 ** 18)}"
    )
    print(
        f"The starting balance of WETH in {account.address} is now {interface.IERC20(weth_address).balanceOf(account.address)/ (1 * 10 ** 18)}"
    )

    if network.show_active() in ["mainnet-fork-dev"]:
        get_weth(account=account)

    print(
        f"After I got Weth, Balance of DAI in {account.address} is now {interface.IERC20(dai_address).balanceOf(account.address)/ (1 * 10 ** 18)}"
    )
    print(
        f"After I got Weth, balance of WETH in {account.address} is now {interface.IERC20(weth_address).balanceOf(account.address)/ (1 * 10 ** 18)}"
    )
    #  SWAP in SUSHI
    #  A--- Approve
    print(f"SWAP starting with amount to swap: {amount_to_swap}")
    tx_approve = approve_erc20(
        amount_to_swap, sushiswapv2_router02, weth_address, account
    )
    tx_approve.wait(1)
    print(f"Weth Approved amount {amount_to_swap} ")

    #  B--- Swap
    price_feed_address = price_feed_mapping[network.show_active()][
        (dai_address, weth_address)
    ]
    txn_swp = swap(
        weth_address,
        dai_address,
        amount_to_swap,
        account,
        price_feed_address,
        sushiswapv2_router02,
        reverse_feed=False,
    )
    txn_swp.wait(1)
    # time.sleep(200)
    balance_weth = float(interface.IERC20(weth_address).balanceOf(account.address))
    # balance_weth = balance_weth / (1 * 10 ** 18)
    balance_dai = float(interface.IERC20(dai_address).balanceOf(account.address))
    # balance_dai = balance_dai / (1 * 10 ** 18)
    print(f"AFTER Swap WETH Balance is: {balance_weth/ (1 * 10 ** 18)}")
    print(f"AFTER Swap DAI Balance is: {balance_dai/ (1 * 10 ** 18)}")

    #  RE_SWAP DAI / WETH
    #  C--- Approve DAI
    print(f"SWAP starting with amount to swap: {balance_dai}")
    tx_approve = approve_erc20(balance_dai, sushiswapv2_router02, dai_address, account)
    tx_approve.wait(1)
    print(f"Weth Approved amount {balance_dai} ")

    amount_dai_to_swap = float(input("Percetage in decimal (ie: 0.1) >> % DAI balance to convert in WETH: "))

    amount_to_swap2 = balance_dai * amount_dai_to_swap
    print("RE-SWAP From DAI >> To ETH ")
    txn_swp2 = swap(
        dai_address,
        weth_address,
        amount_to_swap2,
        account,
        price_feed_address,
        sushiswapv2_router02,
        reverse_feed=True,
    )
    txn_swp2.wait(1)
    # time.sleep(100)
    balance_weth = float(interface.IERC20(weth_address).balanceOf(account.address))
    # balance_weth = balance_weth / (1 * 10 ** 18)
    balance_dai = float(interface.IERC20(dai_address).balanceOf(account.address))
    # balance_dai = balance_dai / (1 * 10 ** 18)
    print(f"AFTER RE-Swap WETH Balance is: {balance_weth/ (1 * 10 ** 18)}")
    print(f"AFTER RE-Swap DAI Balance is: {balance_dai/ (1 * 10 ** 18)}")


def swap(
    address_from_token,
    address_to_token,
    amount,
    account,
    price_feed_address,
    swap_router_address,
    reverse_feed=False,
):
    path = [address_from_token, address_to_token]
    #  When you call a pool you need price from Oracle >> use chianlink_asset_pr
    from_to_price = get_asset_price(address_price_feed=price_feed_address)
    if reverse_feed:
        from_to_price = 1 / from_to_price
    # amountOutMin = int((from_to_price * 0.5) * 10 ** 18)
    # 98 is 2% slippage
    # I get a little weird with units here
    # from_to_price isn't in wei, but amount is
    # Min amount we want back is to avoid other doing FrontRun on our swap: so we give min amnt
    amountOutMin = int(0.04 * 10 ** 18)
    if reverse_feed:
        amountOutMin = int(1 / (0.04 * 10 ** 18))
    timestamp = chain[brownie.web3.eth.get_block_number()]["timestamp"] + 120
    routerv2 = interface.IUniswapV2Router02(swap_router_address)
    swap_tx = routerv2.swapExactTokensForTokens(
        amount, amountOutMin, path, account.address, timestamp, {"from": account}
    )
    if network.show_active() in ["mainnet-fork-dev"]:
        swap_tx.wait(1)
    else:
        time.sleep(120)
    return swap_tx
