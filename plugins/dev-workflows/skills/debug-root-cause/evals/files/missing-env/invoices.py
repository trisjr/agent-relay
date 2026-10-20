def invoice_id(request, lookup):
    invoice = lookup(request["invoice_key"])
    return invoice["id"]
