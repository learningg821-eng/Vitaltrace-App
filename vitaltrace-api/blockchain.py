import os
import json
from web3 import Web3

GANACHE_RPC_URL = os.getenv("GANACHE_RPC_URL", "http://127.0.0.1:7545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "_vitalId", "type": "uint256"},
            {"internalType": "uint256", "name": "_patientId", "type": "uint256"},
            {"internalType": "string", "name": "_vitalHash", "type": "string"}
        ],
        "name": "recordVital",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_index", "type": "uint256"}],
        "name": "getRecord",
        "outputs": [
            {"internalType": "uint256", "name": "vitalId", "type": "uint256"},
            {"internalType": "uint256", "name": "patientId", "type": "uint256"},
            {"internalType": "string", "name": "vitalHash", "type": "string"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getRecordCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]


def get_web3():
    w3 = Web3(Web3.HTTPProvider(GANACHE_RPC_URL))
    return w3


def record_vital_on_chain(vital_id: int, patient_id: int, vital_hash: str):
    try:
        w3 = get_web3()

        if not w3.is_connected():
            print("❌ Blockchain not connected")
            return None, None

        contract = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=ABI
        )

        account = w3.eth.account.from_key(PRIVATE_KEY)

        tx = contract.functions.recordVital(
            vital_id,
            patient_id,
            vital_hash
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"✅ Blockchain recorded: tx={tx_hash.hex()} block={receipt.blockNumber}")

        return tx_hash.hex(), receipt.blockNumber

    except Exception as e:
        print(f"❌ Blockchain error: {e}")
        return None, None