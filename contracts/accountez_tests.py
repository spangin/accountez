import smartpy as sp


AccounTez = sp.io.import_script_from_url("https://raw.githubusercontent.com/spangin/accountez/main/contracts/accountez.py").AccounTez


##############################################################################

# Tests
@sp.add_test(name = "AccounTez")
def test():
    userA = sp.test_account("UserA")
    userB = sp.test_account("UserB")
    scenario = sp.test_scenario()
    scenario.h1("AccounTez tests")
    acctez = AccounTez()
    scenario += acctez

    # invalid tx amount for register_alias()
    acctez.register_alias("usera").run(sender=userA, amount=sp.tez(1), valid=False)
    # invalid alias length
    acctez.register_alias("u2").run(sender=userA, valid=False)
    # invalid symbol
    acctez.register_alias("UserA").run(sender=userA, valid=False)
    # address can't be found by alias
    scenario.verify(~sp.view("get_address_by_alias", acctez.address, "usera", t = sp.TOption(sp.TAddress)).open_some().is_some())
    # account can't be found by address
    scenario.verify(~sp.view("get_account_by_address", acctez.address, userA.address, t = sp.TOption(AccounTez.get_account_type())).open_some().is_some())
    # alias is registred
    acctez.register_alias("usera").run(sender=userA)
    scenario.verify(sp.view("get_address_by_alias", acctez.address, "usera", t = sp.TOption(sp.TAddress)).open_some().open_some() == userA.address)
    scenario.verify(sp.view("get_account_by_address", acctez.address, userA.address, t = sp.TOption(AccounTez.get_account_type())).open_some().open_some().alias == "usera")
    # invalid tx amount for set_account_data()
    acctez.set_account_data(sp.map({"email": sp.utils.bytes_of_string("a@a.com")})).run(sender=userA, amount=sp.tez(1), valid=False)
    # account data is set
    acctez.set_account_data(sp.map({"email": sp.utils.bytes_of_string("a@a.com"),
                                    "twitter": sp.utils.bytes_of_string("@a_user"),
                                    "site": sp.utils.bytes_of_string("http://a.com")})).run(sender=userA)
    # invalid tx amount for remove_account_data()
    acctez.remove_account_data(sp.list(["site"])).run(sender=userA, amount=sp.tez(1), valid=False)
    # invalid account
    acctez.remove_account_data(sp.list(["site"])).run(sender=userB, valid=False)
    # account data is removed
    acctez.remove_account_data(sp.list(["site"])).run(sender=userA)
    # alias already exists
    acctez.register_alias("usera").run(sender=userA, valid=False)
    # alias can't be changed
    acctez.register_alias("usera_aaa").run(sender=userA, valid=False)

    acctez.set_account_data(sp.map({"email": sp.utils.bytes_of_string("b@b.com"),
                                    "twitter": sp.utils.bytes_of_string("@b_user")})).run(sender=userB)
    acctez.register_alias("userb").run(sender=userB)
    acctez.register_alias("userb_bbb").run(sender=userB, valid=False)
