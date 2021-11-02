import csv

from ape_safe import ApeSafe
from scripts.one_inch import one_inch
from brownie import web3, interface, AggregationRouterV3

routers = {
    "UNISWAP_V2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    "SUSHISWAP": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
    "BALv2": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
}

safe_address = "0x3bCF3Db69897125Aa61496Fc8a8B55A5e3f245d5"
play_address = "0x33e18a092a93ff21aD04746c7Da12e35D34DC7C4"


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(f"{question} [y/n]: ")).lower().strip()
        if reply[:1] == "y":
            return True
        if reply[:1] == "n":
            return False


def get_tokens(tokens_file):
    with open(tokens_file, "r") as f:
        csv_reader = csv.DictReader(f, fieldnames=["symbol", "address"])

        tokens = {}
        for r in csv_reader:
            if csv_reader.line_num == 1:
                continue

            tokens[r["symbol"]] = web3.toChecksumAddress(r["address"])

    return tokens


def get_swaps(swaps_file):
    with open(swaps_file, "r") as f:
        csv_reader = csv.DictReader(f, fieldnames=["token_in", "token_out", "qty"])

        swaps = []
        for r in csv_reader:
            if csv_reader.line_num == 1:
                continue

            swaps.append(r)

    return swaps


def approval_tx(tokens, swaps):
    if yes_or_no("Generate approval tx?"):
        safe = ApeSafe(safe_address)

        for swap in swaps:
            interface.ERC20(tokens[swap["token_in"]])
            token_contract = safe.contract(tokens[swap["token_in"]])
            token_contract.approve(one_inch.ONE_INCH_ROUTER_ADDRESS, int(swap["qty"]))

        safe_tx = safe.multisend_from_receipts()
        safe.preview(safe_tx)

        print(safe_tx)

        for swap in swaps:
            symbol = swap["token_in"]
            token_contract = safe.contract(tokens[symbol])
            print(
                f"Allowance to 1Inch router for {symbol}: {token_contract.allowance(safe_address, one_inch.ONE_INCH_ROUTER_ADDRESS)}"
            )

        print("To:", safe_tx.to, "Calldata:", safe_tx.data.hex())

        if yes_or_no("Post this tx"):
            safe.post_transaction(safe_tx)
            input(
                "Press Enter when tx is mined.. approvals are needed for 1Inch swaps to be performed.."
            )


def swaps_tx(tokens, swaps):
    if yes_or_no("Generate swaps tx?"):
        safe = ApeSafe(safe_address)

        router = AggregationRouterV3.at(
            one_inch.ONE_INCH_ROUTER_ADDRESS, owner=safe.account
        )

        weth = interface.ERC20(tokens['WETH'])

        balance_before = weth.balanceOf(safe.account.address)

        for swap in swaps:
            address_in = tokens[swap["token_in"]]
            address_out = tokens[swap["token_out"]]

            (_, calldata) = one_inch.get_swap_data(address_in, address_out, swap["qty"], safe_address)
            (method, args) = router.decode_input(calldata)

            object = router.get_method_object(calldata)

            symbol_in = swap["token_in"]
            symbol_out = swap["token_out"]

            print(f'Args for {symbol_in} <-> {symbol_out}:', method, args)

            object.transact(*args)

        balance_after = weth.balanceOf(safe.account.address)

        print('WETH gained:', (balance_after - balance_before))

        safe_tx = safe.multisend_from_receipts()
        safe.preview(safe_tx)

        print("To:", safe_tx.to, "Calldata:", safe_tx.data.hex())


def main():
    tokens = get_tokens("resources/tokens.csv")
    swaps = get_swaps("resources/swaps.csv")

    approval_tx(tokens, swaps)
    swaps_tx(tokens, swaps)
