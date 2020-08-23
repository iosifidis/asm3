
import asm3.financial
import asm3.utils

class ProcessorError(Exception):
    pass
class PayRefError(ProcessorError):
    pass
class AlreadyReceivedError(ProcessorError):
    pass

class PaymentProcessor(object):
    """ Abstract class that encapsulates payment processor functionality """
    dbo = None
    name = ""

    def __init__(self, dbo, name):
        self.dbo = dbo
        self.name = name

    def checkoutPage(self, payref, return_url = "", item_description = ""):
        """ 
        Method to return the provider's checkout page 
        payref: The payments we are charging for (str OWNERCODE-RECEIPTNUMBER)
        return_url: The URL to redirect the browser to when payment is successful
        item_description: A description of what we are charging for (if blank the payment types are used)
        """
        raise NotImplementedError()

    def receive(self, rawdata):
        """ 
        Method to be called by the provider via an endpoint on receipt of payment.
        rawdata is a str containing the data in whatever format we get from the provider for parsing.
        (eg: PayPal send URLencoded values, Stripe send JSON)
        """
        raise NotImplementedError()

    def getDataParam(self, data, p):
        """ Returns a URL encoded parameter p from data (str). """
        for b in data.split("&"):
            if b.startswith(p):
                return b.split("=")[1]
        return ""

    def getDataParamF(self, data, p):
        """ Returns a data parameter as a float """
        return asm3.utils.cfloat(self.getDataParam(data, p))

    def getDataParamC(self, data, p):
        """ Returns a data parameter as a currency integer """
        return asm3.utils.cint( asm3.utils.cfloat(self.getDataParam(data, p)) * 100 )

    def getPayments(self, payref):
        """ Returns the list of payment records for payref (largest first) """
        receiptnumber = self.getReceiptNumber(payref)
        return self.dbo.query(asm3.financial.get_donation_query(self.dbo) + " WHERE od.ReceiptNumber=? AND od.Date Is Null ORDER BY od.Donation DESC", [receiptnumber])

    def getReceiptNumber(self, payref):
        """ Extracts the receipt number from a payref """
        return payref.split("-")[1]

    def isPaymentReceived(self, payref):
        """ Returns False if the payment(s) comprising payref have not been received """
        receiptnumber = self.getReceiptNumber(payref)
        return 0 == self.dbo.query_int("select count(*) from ownerdonation where receiptnumber=? and date is null", [receiptnumber])

    def markPaymentReceived(self, payref, trxid, received, vat, fee, rawdata):
        """ 
        Marks all payments in payref received.
        The fee is only applied to the first payment if there are multiple payments in the payref.
        It is expected that received, vat and fee are all integer currency amounts in whole pence.
        """
        receiptnumber = self.getReceiptNumber(payref)
        rows = self.dbo.query("select donation, id from ownerdonation where receiptnumber=?", [receiptnumber])
        for i, r in enumerate(rows):
            asm3.financial.receive_donation(self.dbo, "system/%s" % self.name, 
                r.id, 
                chequenumber=trxid,
                fee=asm3.utils.iif(i==0 and fee>0, fee, 0),
                rawdata=rawdata )

    def validatePaymentReference(self, payref):
        """
        Checks that payref is valid
        Payment references should start with a person code, followed by a dash, then the receipt number.
        Eg: RT002984-00005712
        This code also verifies that the receipt number belongs to the person. This makes it
        virtually impossible to guess payment references and stops people spamming the endpoint and
        incrementing the receipt number to try and view other records.
        Returns True if the payment reference is valid.
        """
        b = payref.split("-")
        if len(b) != 2: return False
        ownercode, receipt = payref.split("-")
        # Each element should be at least 8 chars long and no longer than 12
        if len(ownercode) < 8 or len(ownercode) > 12: return False
        if len(receipt) < 8 or len(receipt) > 12: return False
        # Can we find this receipt and owner?
        return 0 != self.dbo.query_int("SELECT COUNT(*) FROM ownerdonation od " \
            "INNER JOIN owner o ON o.ID = od.OwnerID " \
            "WHERE o.OwnerCode=? AND od.ReceiptNumber=?", [ownercode, receipt])
