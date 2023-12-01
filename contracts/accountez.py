import smartpy as sp


class AccounTez(sp.Contract):

    CFG_ALIAS_MIN_LENGTH = 3
    CFG_ALIAS_MAX_LENGTH = 15
    CFG_ALIAS_SYMBOLS = "abcdefghijklmnopqrstuvwxyz0123456789_"

    ERR_INVALID_TX_AMOUNT         = "ACCTEZ_ERR invalid tx amount"
    ERR_INVALID_SYMBOL            = "ACCTEZ_ERR invalid symbol"
    ERR_ACCOUNT_NOT_FOUND         = "ACCTEZ_ERR account is not found"
    ERR_ACCOUNT_ALREADY_REGISTRED = "ACCTEZ_ERR account is already registered"
    ERR_ALIAS_ALREADY_EXISTS      = "ACCTEZ_ERR alias already exists"
    ERR_ALIAS_LENGTH_OUT_OF_RANGE = "ACCTEZ_ERR alias length has to be in [{}..{}]".format(CFG_ALIAS_MIN_LENGTH, CFG_ALIAS_MAX_LENGTH)


    def get_account_type():
        return sp.TRecord(alias = sp.TString, reg_date = sp.TTimestamp, data = sp.TMap(k = sp.TString, v = sp.TBytes))

    def create_account(alias):
        return sp.record(alias = alias, reg_date = sp.now, data = sp.map(l = {}, tkey = sp.TString, tvalue = sp.TBytes))


    def __init__(self):
        self.init(
            dns = sp.big_map(tkey = sp.TString, tvalue = sp.TAddress),
            accounts = sp.big_map(tkey = sp.TAddress, tvalue = AccounTez.get_account_type()),
        )


    @sp.entry_point()
    def delete_user(self, alias):
        del self.data.accounts[self.data.dns[alias]]
        del self.data.dns[alias]
        

    @sp.onchain_view()
    def get_address_by_alias(self, alias):
        sp.set_type(alias, sp.TString)
        sp.result(self.data.dns.get_opt(alias))


    @sp.onchain_view()
    def get_account_by_address(self, address):
        sp.set_type(address, sp.TAddress)
        sp.result(self.data.accounts.get_opt(address))

        
    @sp.entry_point()
    def register_alias(self, alias):
        sp.set_type(alias, sp.TString)
        sp.verify(sp.amount == sp.mutez(0), message = AccounTez.ERR_INVALID_TX_AMOUNT)
        sp.verify((sp.len(alias) >= AccounTez.CFG_ALIAS_MIN_LENGTH) & (sp.len(alias) <= AccounTez.CFG_ALIAS_MAX_LENGTH),
                  message = AccounTez.ERR_ALIAS_LENGTH_OUT_OF_RANGE)
        d = sp.local("d", sp.set({k : for k in AccounTez.CFG_ALIAS_SYMBOLS}))
        c = sp.local("c", "")
        sp.for i in sp.range(0, sp.len(alias)):
            c.value = sp.slice(alias, i, 1).open_some()
            sp.verify(d.value.contains(c.value), message = AccounTez.ERR_INVALID_SYMBOL + ": " + c.value)
        sp.verify(~self.data.dns.contains(alias), message = AccounTez.ERR_ALIAS_ALREADY_EXISTS)
        account = sp.local("a", self.data.accounts.get(sp.sender, default_value = AccounTez.create_account("")))
        sp.verify(sp.len(account.value.alias) == 0, message = AccounTez.ERR_ACCOUNT_ALREADY_REGISTRED)
        account.value.alias = alias
        self.data.accounts[sp.sender] = account.value
        self.data.dns[alias] = sp.sender
    

    @sp.entry_point()
    def set_account_data(self, params):
        sp.set_type(params, sp.TMap(k = sp.TString, v = sp.TBytes))
        sp.verify(sp.amount == sp.mutez(0), message = AccounTez.ERR_INVALID_TX_AMOUNT)
        account = sp.local("a", self.data.accounts.get(sp.sender, default_value = AccounTez.create_account("")))
        sp.for entry in params.items():
            account.value.data[entry.key] = entry.value
        self.data.accounts[sp.sender] = account.value


    @sp.entry_point()
    def remove_account_data(self, params):
        sp.set_type(params, sp.TList(t = sp.TString))
        sp.verify(sp.amount == sp.mutez(0), message = AccounTez.ERR_INVALID_TX_AMOUNT)
        data = sp.local("data", self.data.accounts.get(sp.sender, message = AccounTez.ERR_ACCOUNT_NOT_FOUND).data)
        sp.for key in params:
            del data.value[key]
        self.data.accounts[sp.sender].data = data.value

