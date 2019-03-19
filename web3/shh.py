from web3._utils.filters import (
    ShhFilter,
)
from web3.method import (
    Method,
)


def version():
    return Method(
        "shh_version",
        mungers=None
    )


def info():
    return Method(
        "shh_info",
        mungers=None
    )


def setMaxMessageSize(self, size):
    return self.web3.manager.request_blocking("shh_setMaxMessageSize", [size])


def setMinPoW(self, min_pow):
    return self.web3.manager.request_blocking("shh_setMinPoW", [min_pow])


def markTrustedPeer(self, enode):
    return self.web3.manager.request_blocking("shh_markTrustedPeer", [enode])


def newKeyPair():
    return Method(
        "shh_newKeyPair",
        mungers=None
    )


def addPrivateKey(self, key):
    return self.web3.manager.request_blocking("shh_addPrivateKey", [key])

def deleteKeyPair(self, id):
    return self.web3.manager.request_blocking("shh_deleteKeyPair", [id])

def hasKeyPair(self, id):
    return self.web3.manager.request_blocking("shh_hasKeyPair", [id])

def getPublicKey(self, id):
    return self.web3.manager.request_blocking("shh_getPublicKey", [id])

def getPrivateKey(self, id):
    return self.web3.manager.request_blocking("shh_getPrivateKey", [id])

def newSymKey(self):
    return self.web3.manager.request_blocking("shh_newSymKey", [])

def addSymKey(self, key):
    return self.web3.manager.request_blocking("shh_addSymKey", [key])

def generateSymKeyFromPassword(self, password):
    return self.web3.manager.request_blocking("shh_generateSymKeyFromPassword", [password])

def hasSymKey(self, id):
    return self.web3.manager.request_blocking("shh_hasSymKey", [id])

def getSymKey(self, id):
    return self.web3.manager.request_blocking("shh_getSymKey", [id])

def deleteSymKey(self, id):
    return self.web3.manager.request_blocking("shh_deleteSymKey", [id])

def post(self, message):
    if message and ("payload" in message):
        return self.web3.manager.request_blocking("shh_post", [message])
    else:
        raise ValueError(
            "message cannot be None or does not contain field 'payload'"
        )

def newMessageFilter(self, criteria, poll_interval=None):
    filter_id = self.web3.manager.request_blocking("shh_newMessageFilter", [criteria])
    return ShhFilter(self.web3, filter_id, poll_interval=poll_interval)

def deleteMessageFilter(self, filter_id):
    return self.web3.manager.request_blocking("shh_deleteMessageFilter", [filter_id])

def getMessages(self, filter_id):
    return self.web3.manager.request_blocking("shh_getFilterMessages", [filter_id])
