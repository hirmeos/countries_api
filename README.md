# JWT API
[![Build Status](https://travis-ci.org/hirmeos/tokens_api.svg?branch=master)](https://travis-ci.org/hirmeos/tokens_api)


## Create user account
Account registration is only allowed via HTTP (`POST /accounts`) after at least one account has been registered via CLI, i.e. HTTP registration requires a token, which are only issued to accounts.

The easiest way is to run python on the api container:

```
docker exec -it tokens_api python
```

Then call the `create_account()` method in `AccountController()`:
```
from api import *
accountctrl.AccountController.create_account("email@obp.com", "secure_password", "Name", "Surname", "admin")
```

## Auth tokens
Tokens can be obtained making a POST request to `/tokens`, providing "email" and "password" with values equal to those used in account creation.

## Debugging
You may set env variable `API_DEBUG` to `True` in order to enable debugging
