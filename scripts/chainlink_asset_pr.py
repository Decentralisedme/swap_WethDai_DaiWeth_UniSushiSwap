from brownie import interface, network, config
from web3 import Web3


def get_asset_price(address_price_feed=None):
    # which address
    address_price_feed = (
        address_price_feed
        if address_price_feed
        else config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    dai_eth_price_feed = interface.AggregatorV3Interface(address_price_feed)
    dai_eth_latest_price = Web3.fromWei(
        dai_eth_price_feed.latestRoundData()[1], "ether"
    )
    eth_dai_latest_price = float(1 / dai_eth_latest_price)
    print(f"Latest Price >>>  DAI/ETH: {dai_eth_latest_price}")
    print(f"Latest Price >>>  ETH/DAI: {eth_dai_latest_price}")
    return float(dai_eth_latest_price)

