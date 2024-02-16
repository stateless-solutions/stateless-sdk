from typing import Any, Optional, TypedDict, cast
import json
from web3 import Web3


class Attestation(TypedDict):
    signature: str
    msg: str
    signatureFormat: Optional[str]
    hashAlgo: Optional[str]
    identity: Optional[str]

class StatelessRPCResponse(TypedDict):
    id: str
    jsonrpc: str
    result: dict[str, Any]
    attestations: list[Attestation]

class IntegrityError(Exception):
    pass


def make_error_message(method_name, params, acceptance, providers, attestations):
    attestation_str = "Message hash of {} (from {}) and {} (from {}) are inconsistent from the signatures".format(attestations[0]["msg"], providers[0], attestations[1]["msg"], providers[1])
    return "The integrity of the following RPC request could not be confirmed based on the acceptance threshold of {} between the the providers: {}. \n Method: {}, Parameters: {}. \n {}".format(acceptance, providers, method_name, json.dumps(params, indent=2), attestation_str)


class StatelessProvider(Web3.HTTPProvider):
    def __init__(self, url, acceptance_threshold: int, providers: list[str], *args, **kwargs):
        self.acceptance_threshold = acceptance_threshold
        self.provider = providers
        super().__init__(url, *args, **kwargs)

    def make_request(self, method, params):
        resp = super().make_request(method, params)
        resp = cast(StatelessRPCResponse, resp)
        if resp["attestations"][0]["msg"] != resp["attestations"][1]["msg"]:
            raise IntegrityError(method, params, self.acceptance_threshold, self.provider, resp["attestations"])
        return resp

    def _verifiy_replication(self, resp: StatelessRPCResponse) -> bool:
        return True

    def _verify_get_logs_inclusion(self, resp: StatelessRPCResponse) -> bool:
        return True
