from brownie import web3
import requests

ONE_INCH_ROUTER_ADDRESS = "0x11111112542D85B3EF69AE05771c2dCCff4fAa26"

base_url = "https://api.1inch.exchange/v3.0/1/"
url_quote = base_url + "quote"
url_swap = base_url + "swap"
url_approve = base_url + "approve/calldata"

def get_quote(token_input, token_output, amount_in):
    request_data = {
        'fromTokenAddress': token_input, 
        'toTokenAddress': token_output, 
        'amount': amount_in
    }

    response = requests.get(url_quote, request_data).json()
    
    return response['toTokenAmount']

def get_swap_data(token_input, token_output, amount_in, address_out, slippage=5.0):
    request_data = {
        'fromTokenAddress': token_input, 
        'toTokenAddress': token_output, 
        'amount': amount_in,
        'fromAddress': address_out,
        'slippage': slippage
    }

    response = requests.get(url_swap, request_data).json()

    return (response['tx']['to'], response['tx']['data'])

def get_approve_data(token_input, amount_in):
    request_data = {
        'tokenAddress': token_input, 
        'amount': amount_in,
    }

    response = requests.get(url_approve, request_data).json()

    return (web3.toChecksumAddress(response['to']), response['data'])