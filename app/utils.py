import logging

import requests
from requests.exceptions import Timeout, ConnectionError

from app.fields import counter_fields
from app.settings import MONIKER, RPC_API_PORT


def get_prometheus_info(name, url):
    try:
        response = requests.get(url=url)
        return response.text
    except (Timeout, ConnectionError):
        logging.error(f"[{name}] Timeout connection")
        return None


def get_count_validators_status(validators_response: dict) -> dict:
    counter = \
        {
            'BOND_STATUS_UNSPECIFIED': 0,
            'BOND_STATUS_UNBONDED': 0,
            'BOND_STATUS_UNBONDING': 0,
            'BOND_STATUS_BONDED': 0,
            'JAILED': 0,
            'TOTAL': 0,
        }

    for validator in validators_response['validators']:
        counter[validator['status']] += 1

        if validator['jailed']:
            counter['JAILED'] += 1

    counter['TOTAL'] = len(validators_response['validators'])
    return counter


def format_count_network_status(counter: dict) -> str:
    count_network_status = str()

    for field in counter_fields:
        count_network_status += f"# HELP {field['name']} {field['description']}\n" \
                                f"# TYPE {field['name']} {field['type']}\n" \
                                f"{field['name']} {counter[field['counter_key']]}\n"

    return count_network_status


def get_top_number_validator(validators_response: dict, moniker: str) -> int:
    sorted_validators = sorted(validators_response['validators'], key=lambda d: float(d['tokens']), reverse=True)

    counter = 1
    for validator in sorted_validators:
        if moniker == validator['description']['moniker']:
            return counter

        if validator['status'] == "BOND_STATUS_BONDED":
            counter += 1


def get_my_validator(validators_response: dict):
    for validator in validators_response['validators']:
        if MONIKER == validator['description']['moniker']:
            top_number = get_top_number_validator(validators_response, MONIKER)
            validator['top_number'] = top_number
            return validator


def get_additional_info_about_my_validator(my_validator: dict) -> str:
    additional_info = '{' + \
                      f'operator_address="{my_validator.get("operator_address", "None")}",' \
                      f'jailed="{"JAILED" if my_validator.get("jailed", False) else "ACTIVE"}",' \
                      f'status="{my_validator.get("status", "None")}",' \
                      f'moniker="{MONIKER}"' \
                      '}'

    return additional_info


def get_info_about_my_validator(my_validator: dict) -> str:
    my_validator_additional_info = get_additional_info_about_my_validator(my_validator)

    my_validator_info = f"# HELP top_number Node number in the general top by tokens.\n" \
                        f"# TYPE top_number gauge\n" \
                        f"top_number {my_validator_additional_info} {my_validator.get('top_number', -1)}\n" \
                        f"# HELP tokens Count tokens in your node\n" \
                        f"# TYPE tokens gauge\n" \
                        f"tokens{my_validator_additional_info} {my_validator.get('tokens', -1)}\n" \
                        f"# HELP delegator_shares Delegator shares tokens\n" \
                        f"# TYPE delegator_shares gauge\n" \
                        f"delegator_shares{my_validator_additional_info} {my_validator.get('delegator_shares', -1)}\n" \
                        f"# HELP unbonding_height Block height when your node is unbounding in last time\n" \
                        f"# TYPE unbonding_height gauge\n" \
                        f"unbonding_height{my_validator_additional_info} {my_validator.get('unbonding_height', -1)}\n" \
                        f"# HELP rate Rate commission\n" \
                        f"# TYPE rate gauge\n" \
                        f"rate{my_validator_additional_info} {my_validator.get('commission', dict()).get('commission_rates', dict()).get('rate', -1)}\n" \
                        f"# HELP max_rate Maximum rate commission\n" \
                        f"# TYPE max_rate gauge\n" \
                        f"max_rate{my_validator_additional_info} {my_validator.get('commission', dict()).get('commission_rates', dict()).get('max_rate', -1)}\n" \
                        f"# HELP max_change_rate Maximum change rate commission\n" \
                        f"# TYPE max_change_rate gauge\n" \
                        f"max_change_rate{my_validator_additional_info} {my_validator.get('commission', dict()).get('commission_rates', dict()).get('max_change_rate', -1)}\n" \
                        f"# HELP min_self_delegation Minimum self delegation\n" \
                        f"# TYPE min_self_delegation gauge\n" \
                        f"min_self_delegation{my_validator_additional_info} {my_validator.get('min_self_delegation', -1)}"

    return my_validator_info


def get_supply_info(supply_response: dict) -> str:
    supply_info = f"# HELP total_supply Total supply in network\n" \
                  f"# TYPE total_supply gauge\n" \
                  f"total_supply {supply_response['amount']['amount']}\n"
    return supply_info


def get_additional_info() -> str:
    response = requests.get(url=f"http://127.0.0.1:{RPC_API_PORT}/cosmos/bank/v1beta1/supply/aphoton")

    supply_info = get_supply_info(response.json())

    response = requests.get(
        url=f"http://127.0.0.1:{RPC_API_PORT}/cosmos/staking/v1beta1/validators?pagination.limit=999999999999999999")

    content = response.json()

    counter = get_count_validators_status(content)

    count_network_status = format_count_network_status(counter)

    my_validator = get_my_validator(content)
    if my_validator is None:
        return count_network_status

    my_validator_info = get_info_about_my_validator(my_validator)

    info = supply_info + count_network_status + my_validator_info
    return info
