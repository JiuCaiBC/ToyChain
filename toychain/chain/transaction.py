from hashlib import sha256


class Transaction:
    def __init__(self, sender, receiver, amount, transaction_message=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.message = transaction_message
        self.hash = self.hash_tx()

    def hash_tx(self):
        hasher = sha256()
        hasher.update('{}{}{}{}'.format(
            self.sender, self.receiver, self.amount, self.message).encode('utf8'))
        return hasher.hexdigest()
