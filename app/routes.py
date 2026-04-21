from flask import render_template, request
from web3 import Web3
import qrcode
import os

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
print("Connected:", w3.is_connected())


def init_routes(app):

    #  UTILS
    def string_to_hex(s):
        return "0x" + s.encode("utf-8").hex()

    def hex_to_string(hex_str):
        try:
            return bytes.fromhex(hex_str[2:]).decode("utf-8")
        except:
            return "Invalid data"

    def generate_qr(tx_hash):
        img = qrcode.make(tx_hash)
        path = os.path.join("static", "qr.png")
        img.save(path)

    # ===== SEND TX =====
    def send_tx(data_str):
        account = w3.eth.accounts[0]

        tx = {
            'from': account,
            'to': account,
            'value': 0,
            'data': string_to_hex(data_str),
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': w3.eth.get_transaction_count(account)
        }

        tx_hash = w3.eth.send_transaction(tx)
        return tx_hash.hex()  # luôn có 0x

    #  VERIFY
    def verify_tx(tx_hash):
        tx = w3.eth.get_transaction(tx_hash)
        block = w3.eth.get_block(tx.blockNumber)

        print("RAW INPUT:", tx.input)  # debug

        #
        if tx.input and tx.input != "0x":
            decoded = hex_to_string(tx.input)
        else:
            decoded = "No data found"

        return {
            "data": decoded,
            "from": tx["from"],
            "block": tx.blockNumber,
            "timestamp": block.timestamp
        }

    #  ROUTES
    @app.route("/", methods=["GET", "POST"])
    def index():
        tx_hash = None

        if request.method == "POST":
            data = request.form["data"]

            # send transaction
            tx_hash = send_tx(data)

            # create QR from TX HASH
            generate_qr(tx_hash)

            print("NEW TX:", tx_hash)

        return render_template("index.html", tx_hash=tx_hash)

    @app.route("/verify", methods=["POST"])
    def verify():
        tx_hash = request.form["tx_hash"].strip()

        #  FIX miss  0x
        if not tx_hash.startswith("0x"):
            tx_hash = "0x" + tx_hash

        print("VERIFY HASH:", tx_hash)

        try:
            result = verify_tx(tx_hash)
        except Exception as e:
            print("VERIFY ERROR:", e)
            result = {
                "data": "Transaction not found / invalid",
                "from": "-",
                "block": "-",
                "timestamp": "-"
            }

        return render_template("verify.html", result=result)