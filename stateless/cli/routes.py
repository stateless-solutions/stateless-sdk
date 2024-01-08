class BaseUrl:
    V1 = "https://api.stateless.solutions/v1"


class V1Routes:
    ACCOUNT_PROFILE = BaseUrl.V1 + "/accounts/profile"

    USERS = BaseUrl.V1 + "/users"
    LIST_USERS = USERS + "/list"
    CURRENT_USER = USERS + "/current"

    BUCKETS = BaseUrl.V1 + "/buckets"
    LIST_BUCKETS = BUCKETS + "/list"

    OFFERINGS = BaseUrl.V1 + "/offerings"
    LIST_OFFERINGS = OFFERINGS + "/list"

    ENTRYPOINTS = BaseUrl.V1 + "/entrypoints"

    API_KEYS = BaseUrl.V1 + "/api_keys"
    LIST_API_KEYS = API_KEYS + "/list"

    CHAINS = BaseUrl.V1 + "/chains"
    LIST_CHAINS = CHAINS + "/list"

    PROVIDERS = BaseUrl.V1 + "/providers"
    LIST_PROVIDERS = PROVIDERS + "/list"

    REGIONS = BaseUrl.V1 + "/regions"
    LIST_REGIONS = REGIONS + "/"
