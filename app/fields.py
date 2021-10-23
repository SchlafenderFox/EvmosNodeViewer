counter_fields = \
    [
        {
            "name": "total_bond_status_unspecified_validators",
            "description": "Number of validators in BOND_STATUS_UNSPECIFIED status",
            "type": "gauge",
            "counter_key": "BOND_STATUS_UNSPECIFIED"
        },
        {
            "name": "total_bond_status_unbounded_validators",
            "description": "Number of validators in BOND_STATUS_UNBONDED status",
            "type": "gauge",
            "counter_key": "BOND_STATUS_UNBONDED"
        },
        {
            "name": "total_bond_status_unbounding_validators",
            "description": "Number of validators in BOND_STATUS_UNBONDING status",
            "type": "gauge",
            "counter_key": "BOND_STATUS_UNBONDING"
        },
        {
            "name": "total_bond_status_bonded_validators",
            "description": "Number of validators in BOND_STATUS_BONDED status",
            "type": "gauge",
            "counter_key": "BOND_STATUS_BONDED"
        },
        {
            "name": "total_jailed_validators",
            "description": "Number of validators in jailed status",
            "type": "gauge",
            "counter_key": "JAILED"
        },
        {
            "name": "total_validators",
            "description": "total validators",
            "type": "gauge",
            "counter_key": "TOTAL"
        }
    ]
