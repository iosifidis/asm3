
import asm3.additional
import asm3.al
import asm3.animal
import asm3.asynctask
import asm3.cachedisk
import asm3.configuration
import asm3.dbupdate
import asm3.financial
import asm3.i18n
import asm3.media
import asm3.medical
import asm3.movement
import asm3.person
import asm3.utils

import datetime
import re
import sys

VALID_FIELDS = [
    "ANIMALNAME", "ANIMALSEX", "ANIMALTYPE", "ANIMALCOLOR", "ANIMALBREED1", 
    "ANIMALBREED2", "ANIMALDOB", "ANIMALLOCATION", "ANIMALUNIT", 
    "ANIMALSPECIES", "ANIMALAGE", 
    "ANIMALCOMMENTS", "ANIMALMARKINGS", "ANIMALNEUTERED", "ANIMALNEUTEREDDATE", "ANIMALMICROCHIP", "ANIMALMICROCHIPDATE", 
    "ANIMALENTRYDATE", "ANIMALDECEASEDDATE", "ANIMALCODE", "ANIMALFLAGS",
    "ANIMALREASONFORENTRY", "ANIMALHIDDENDETAILS", "ANIMALNOTFORADOPTION", "ANIMALNONSHELTER", 
    "ANIMALGOODWITHCATS", "ANIMALGOODWITHDOGS", "ANIMALGOODWITHKIDS", 
    "ANIMALHOUSETRAINED", "ANIMALHEALTHPROBLEMS", "ANIMALIMAGE",
    "VACCINATIONTYPE", "VACCINATIONDUEDATE", "VACCINATIONGIVENDATE", "VACCINATIONEXPIRESDATE", 
    "VACCINATIONMANUFACTURER", "VACCINATIONBATCHNUMBER", "VACCINATIONCOMMENTS", 
    "TESTTYPE", "TESTDUEDATE", "TESTPERFORMEDDATE", "TESTRESULT", "TESTCOMMENTS",
    "MEDICALNAME", "MEDICALDOSAGE", "MEDICALGIVENDATE", "MEDICALCOMMENTS",
    "ORIGINALOWNERTITLE", "ORIGINALOWNERINITIALS", "ORIGINALOWNERFIRSTNAME",
    "ORIGINALOWNERLASTNAME", "ORIGINALOWNERADDRESS", "ORIGINALOWNERCITY",
    "ORIGINALOWNERSTATE", "ORIGINALOWNERZIPCODE", "ORIGINALOWNERJURISDICTION", "ORIGINALOWNERHOMEPHONE",
    "ORIGINALOWNERWORKPHONE", "ORIGINALOWNERCELLPHONE", "ORIGINALOWNEREMAIL",
    "DONATIONDATE", "DONATIONAMOUNT", "DONATIONFEE", "DONATIONCHECKNUMBER", "DONATIONCOMMENTS", "DONATIONTYPE", "DONATIONPAYMENT", "DONATIONGIFTAID",
    "LICENSETYPE", "LICENSENUMBER", "LICENSEFEE", "LICENSEISSUEDATE", "LICENSEEXPIRESDATE", "LICENSECOMMENTS",
    "PERSONTITLE", "PERSONINITIALS", "PERSONFIRSTNAME", "PERSONLASTNAME", "PERSONNAME",
    "PERSONADDRESS", "PERSONCITY", "PERSONSTATE",
    "PERSONZIPCODE", "PERSONJURISDICTION", "PERSONFOSTERER", "PERSONDONOR",
    "PERSONFLAGS", "PERSONCOMMENTS", "PERSONHOMEPHONE", "PERSONWORKPHONE",
    "PERSONCELLPHONE", "PERSONEMAIL", "PERSONGDPRCONTACT", "PERSONCLASS",
    "PERSONMEMBER", "PERSONMEMBERSHIPNUMBER", "PERSONMEMBERSHIPEXPIRY",
    "PERSONMATCHACTIVE", "PERSONMATCHADDED", "PERSONMATCHEXPIRES",
    "PERSONMATCHSEX", "PERSONMATCHSIZE", "PERSONMATCHCOLOR", "PERSONMATCHAGEFROM", "PERSONMATCHAGETO",
    "PERSONMATCHTYPE", "PERSONMATCHSPECIES", "PERSONMATCHBREED1", "PERSONMATCHBREED2",
    "PERSONMATCHGOODWITHCATS", "PERSONMATCHGOODWITHDOGS", "PERSONMATCHGOODWITHCHILDREN", "PERSONMATCHHOUSETRAINED",
    "PERSONMATCHCOMMENTSCONTAIN"
]

def gkc(m, f):
    """ reads field f from map m, assuming a currency amount and returning 
        an integer """
    if f not in m: return 0
    try:
        # Remove non-numeric characters
        v = re.sub(r'[^\d\-\.]+', '', str(m[f]))
        fl = float(v)
        fl *= 100
        return int(fl)
    except:
        return 0

def gks(m, f):
    """ reads field f from map m, returning a string. 
        string is empty if key not present """
    if f not in m: return ""
    return str(asm3.utils.strip_non_ascii(m[f]))

def gkd(dbo, m, f, usetoday = False):
    """ reads field f from map m, returning a display date. 
        string is empty if key not present or date is invalid.
        If usetoday is set to True, then today's date is returned
        if the date is blank.
    """
    if f not in m: return ""
    lv = str(m[f])
    # If there's a space, then I guess we have time info - throw it away
    if lv.find(" ") > 0:
        lv = lv[0:lv.find(" ")]
    # Now split it by either / or - or .
    b = lv.split("/")
    if lv.find("-") != -1: b = lv.split("-")
    if lv.find(".") != -1: b = lv.split(".")
    # We should have three date bits now
    if len(b) != 3:
        # We don't have a valid date, if use today is on return that
        if usetoday:
            return asm3.i18n.python2display(dbo.locale, asm3.i18n.now(dbo.timezone))
        else:
            return ""
    else:
        try:
            # Which of our 3 bits is the year?
            if asm3.utils.cint(b[0]) > 1900:
                # it's Y/M/D
                d = datetime.datetime(asm3.utils.cint(b[0]), asm3.utils.cint(b[1]), asm3.utils.cint(b[2]))
            elif dbo.locale == "en" or dbo.locale == "en_CA":
                # Assume it's M/D/Y for US and Canada
                d = datetime.datetime(asm3.utils.cint(b[2]), asm3.utils.cint(b[0]), asm3.utils.cint(b[1]))
            else:
                # Assume it's D/M/Y
                d = datetime.datetime(asm3.utils.cint(b[2]), asm3.utils.cint(b[1]), asm3.utils.cint(b[0]))
            return asm3.i18n.python2display(dbo.locale, d)
        except:
            # We've got an invalid date - return today
            if usetoday:
                return asm3.i18n.python2display(dbo.locale, asm3.i18n.now(dbo.timezone))
            else:
                return ""

def gkb(m, f):
    """ reads field f from map m, returning a boolean. 
        boolean is false if key not present. Interprets
        anything but blank, 0 or N as yes """
    if f not in m: return False
    if m[f] == "" or m[f] == "0" or m[f].upper().startswith("N"): return False
    return True

def gkbi(m, f):
    """ reads boolean field f from map m, returning 1 for yes or 0 for no """
    if gkb(m,f):
        return "1"
    else:
        return "0"

def gkbc(m, f):
    """ reads boolean field f from map m, returning a fake checkbox 
        field of blank for no, "on" for yes """
    if gkb(m,f):
        return "on"
    else:
        return ""

def gkynu(m, f):
    """ reads field f from map m, returning a tri-state
        switch. Returns 2 (unknown) for a blank field
        Input should start with Y/N/U or 0/1/2 """
    if f not in m: return 2
    if m[f].upper().startswith("A") or m[f] == "-1": return "-1" # (any) for match good with
    if m[f].upper().startswith("Y") or m[f] == "0": return "0"
    if m[f].upper().startswith("N") or m[f] == "1": return "1"
    return "2"

def gkbr(dbo, m, f, speciesid, create):
    """ reads lookup field f from map m, returning a str(int) that
        corresponds to a lookup match for BreedName in breed.
        if create is True, adds a row to the table if it doesn't
        find a match and then returns str(newid)
        speciesid is the linked species for any newly created breed
        returns "0" if key not present, or if no match was found and create is off """
    if f not in m: return "0"
    lv = m[f]
    matchid = dbo.query_int("SELECT ID FROM breed WHERE LOWER(BreedName) = ?", [ lv.strip().lower().replace("'", "`")] )
    if matchid == 0 and create:
        nextid = dbo.get_id("breed")
        sql = "INSERT INTO breed (ID, SpeciesID, BreedName) VALUES (?,?,?)"
        dbo.execute(sql, (nextid, speciesid, lv.replace("'", "`")))
        return str(nextid)
    return str(matchid)

def gkl(dbo, m, f, table, namefield, create):
    """ reads lookup field f from map m, returning a str(int) that
        corresponds to a lookup match for namefield in table.
        if create is True, adds a row to the table if it doesn't
        find a match and then returns str(newid)
        if the value is an empty string, (blank) is used instead.
        returns "0" if key not present, or if no match was found and create is off """
    if f not in m: return "0"
    lv = m[f]
    matchid = dbo.query_int("SELECT ID FROM %s WHERE LOWER(%s) = ?" % (table, namefield), [ lv.strip().lower().replace("'", "`") ])
    if matchid == 0 and create:
        if lv.strip() == "":
            l = dbo.locale
            lv = asm3.i18n._("(blank)", l)
        nextid = dbo.insert(table, {
            namefield:  lv
        }, setRecordVersion=False, setCreated=False, writeAudit=False)
        return str(nextid)
    return str(matchid)

def gksx(m, f):
    """ 
    Reads a value for Sex from field f in map m
    """
    if f not in m: return ""
    x = m[f].lower()
    if x.startswith("f"): return "0"
    elif x.startswith("m"): return "1"
    elif x.startswith("u"): return "2"
    elif x.startswith("a"): return "-1"
    else: return ""

def create_additional_fields(dbo, row, errors, rowno, csvkey = "ANIMALADDITIONAL", linktype = "animal", linkid = 0):
    # Identify any additional fields that may have been specified with
    # ANIMALADDITIONAL<fieldname>
    for a in asm3.additional.get_field_definitions(dbo, linktype):
        v = gks(row, csvkey + str(a.fieldname).upper())
        if v != "":
            try:
                dbo.insert("additional", {
                    "LinkType":             a.linktype,
                    "LinkID":               linkid,
                    "AdditionalFieldID":    a.id,
                    "Value":                v
                }, generateID=False)
            except Exception as e:
                errors.append( (rowno, str(row), str(e)) )

def row_error(errors, rowtype, rowno, row, e, dbo, exinfo):
    """ 
    Handles error messages during import 
    errors: List of errors to append to
    rowtype: The area of processing for the row (eg: animal)
    rowno: The row number
    row: The row data itself
    e: The exception thrown
    exinfo: execution info for logging
    """
    errmsg = str(e)
    if type(e) == asm3.utils.ASMValidationError: errmsg = e.getMsg()
    # If ANIMALIMAGE contains a data-uri, squash it for legibility
    if "ANIMALIMAGE" in row and row["ANIMALIMAGE"].startswith("data"):
        row["ANIMALIMAGE"] = "data:,"
    asm3.al.error("row %d %s: (%s): %s" % (rowno, rowtype, str(row), errmsg), "csvimport.row_error", dbo, exinfo)
    errors.append( (rowno, str(row), errmsg) )

def csvimport(dbo, csvdata, encoding = "utf-8-sig", user = "", createmissinglookups = False, cleartables = False, checkduplicates = False):
    """
    Imports csvdata (bytes string, encoded with encoding)
    createmissinglookups: If a lookup value is given that's not in our data, add it
    cleartables: Clear down the animal, owner and adoption tables before import
    """

    if user == "":
        user = "import"
    else:
        user = "import/%s" % user

    rows = asm3.utils.csv_parse( asm3.utils.cunicode(csvdata, encoding=encoding) )

    # Make sure we have a valid header
    if len(rows) == 0:
        asm3.asynctask.set_last_error(dbo, "Your CSV file is empty")
        return

    onevalid = False
    hasanimal = False
    hasanimalname = False
    hasmed = False
    hastest = False
    hasvacc = False
    hasperson = False
    haspersonlastname = False
    haspersonname = False
    haslicence = False
    haslicencenumber = False
    hasmovement = False
    hasmovementdate = False
    hasdonation = False
    hasdonationamount = False
    hasoriginalowner = False
    hasoriginalownerlastname = False
    cols = rows[0].keys()
    for col in cols:
        if col in VALID_FIELDS: onevalid = True
        if col.startswith("ANIMAL"): hasanimal = True
        if col == "ANIMALNAME": hasanimalname = True
        if col.startswith("ORIGINALOWNER"): hasoriginalowner = True
        if col.startswith("VACCINATION"): hasvacc = True
        if col.startswith("TEST"): hastest = True
        if col.startswith("MEDICAL"): hasmed = True
        if col.startswith("LICENSE"): haslicence = True
        if col == "LICENSENUMBER": haslicencenumber = True
        if col == "ORIGINALOWNERLASTNAME": hasoriginalownerlastname = True
        if col.startswith("PERSON"): hasperson = True
        if col == "PERSONLASTNAME": haspersonlastname = True
        if col == "PERSONNAME": haspersonname = True
        if col.startswith("MOVEMENT"): hasmovement = True
        if col == "MOVEMENTDATE": hasmovementdate = True
        if col.startswith("DONATION"): hasdonation = True
        if col == "DONATIONAMOUNT": hasdonationamount = True

    # Any valid fields?
    if not onevalid:
        asm3.asynctask.set_last_error(dbo, "Your CSV file did not contain any fields that ASM recognises")
        return

    # If we have any animal fields, make sure at least ANIMALNAME is supplied
    if hasanimal and not hasanimalname:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has animal fields, but no ANIMALNAME column")
        return

    # If we have any person fields, make sure at least PERSONLASTNAME or PERSONNAME is supplied
    if hasperson and not haspersonlastname and not haspersonname:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has person fields, but no PERSONNAME or PERSONLASTNAME column")
        return

    # If we have any original owner fields, make sure at least ORIGINALOWNERLASTNAME is supplied
    if hasoriginalowner and not hasoriginalownerlastname:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has original owner fields, but no ORIGINALOWNERLASTNAME column")
        return

    # If we have any movement fields, make sure MOVEMENTDATE is supplied
    if hasmovement and not hasmovementdate:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has movement fields, but no MOVEMENTDATE column")
        return

    # If we have any donation fields, we need an amount
    if hasdonation and not hasdonationamount:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has donation fields, but no DONATIONAMOUNT column")
        return

    # We also need a valid person
    if hasdonation and not (haspersonlastname or haspersonname):
        asm3.asynctask.set_last_error(dbo, "Your CSV file has donation fields, but no person to apply the donation to")
        return

    # If we have any med fields, we need an animal
    if hasmed and not hasanimal:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has medical fields, but no animal to apply them to")
        return

    # If we have any vacc fields, we need an animal
    if hasvacc and not hasanimal:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has vaccination fields, but no animal to apply them to")
        return

    # If we have any test fields, we need an animal
    if hastest and not hasanimal:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has test fields, but no animal to apply them to")
        return

    # If we have licence fields, we need a number
    if haslicence and not haslicencenumber:
        asm3.asynctask.set_last_error(dbo, "Your CSV file has license fields, but no LICENSENUMBER column")
        return

    # We also need a valid person
    if haslicence and not (haspersonlastname or haspersonname):
        asm3.asynctask.set_last_error(dbo, "Your CSV file has license fields, but no person to apply the license to")

    asm3.al.debug("reading CSV data, found %d rows" % len(rows), "csvimport.csvimport", dbo)

    # If we're clearing down tables first, do it now
    if cleartables:
        asm3.al.warn("Resetting the database by removing all non-lookup data", "csvimport.csvimport", dbo)
        asm3.dbupdate.reset_db(dbo)

    # Now that we've read them in, go through all the rows
    # and start importing.
    errors = []
    rowno = 1
    asm3.asynctask.set_progress_max(dbo, len(rows))
    for row in rows:

        asm3.al.debug("import csv: row %d of %d" % (rowno, len(rows)), "csvimport.csvimport", dbo)
        asm3.asynctask.increment_progress_value(dbo)

        # Should we stop?
        if asm3.asynctask.get_cancel(dbo): break

        # Do we have animal data to read?
        animalid = 0
        if hasanimal and gks(row, "ANIMALNAME") != "":
            a = {}
            a["animalname"] = gks(row, "ANIMALNAME")
            a["sheltercode"] = gks(row, "ANIMALCODE")
            a["shortcode"] = gks(row, "ANIMALCODE")
            if gks(row, "ANIMALSEX") == "": 
                a["sex"] = "2" # Default unknown if not set
            else:
                a["sex"] = gksx(row, "ANIMALSEX")
            a["basecolour"] = gkl(dbo, row, "ANIMALCOLOR", "basecolour", "BaseColour", createmissinglookups)
            if a["basecolour"] == "0":
                a["basecolour"] = str(asm3.configuration.default_colour(dbo))
            a["species"] = gkl(dbo, row, "ANIMALSPECIES", "species", "SpeciesName", createmissinglookups)
            if a["species"] == "0":
                a["species"] = str(asm3.configuration.default_species(dbo))
            a["animaltype"] = gkl(dbo, row, "ANIMALTYPE", "animaltype", "AnimalType", createmissinglookups)
            if a["animaltype"] == "0":
                a["animaltype"] = str(asm3.configuration.default_type(dbo))
            a["breed1"] = gkbr(dbo, row, "ANIMALBREED1", a["species"], createmissinglookups)
            if a["breed1"] == "0":
                a["breed1"] = str(asm3.configuration.default_breed(dbo))
            a["breed2"] = gkbr(dbo, row, "ANIMALBREED2", a["species"], createmissinglookups)
            if a["breed2"] != "0" and a["breed2"] != a["breed1"]:
                a["crossbreed"] = "on"
            a["size"] = gkl(dbo, row, "ANIMALSIZE", "lksize", "Size", False)
            if gks(row, "ANIMALSIZE") == "": 
                a["size"] = str(asm3.configuration.default_size(dbo))
            a["weight"] = gks(row, "ANIMALWEIGHT")
            a["internallocation"] = gkl(dbo, row, "ANIMALLOCATION", "internallocation", "LocationName", createmissinglookups)
            if a["internallocation"] == "0":
                a["internallocation"] = str(asm3.configuration.default_location(dbo))
            a["unit"] = gks(row, "ANIMALUNIT")
            a["comments"] = gks(row, "ANIMALCOMMENTS")
            a["markings"] = gks(row, "ANIMALMARKINGS")
            a["hiddenanimaldetails"] = gks(row, "ANIMALHIDDENDETAILS")
            a["healthproblems"] = gks(row, "ANIMALHEALTHPROBLEMS")
            a["notforadoption"] = gkbi(row, "ANIMALNOTFORADOPTION")
            a["nonshelter"] = gkbc(row, "ANIMALNONSHELTER")
            a["housetrained"] = gkynu(row, "ANIMALHOUSETRAINED")
            a["goodwithcats"] = gkynu(row, "ANIMALGOODWITHCATS")
            a["goodwithdogs"] = gkynu(row, "ANIMALGOODWITHDOGS")
            a["goodwithkids"] = gkynu(row, "ANIMALGOODWITHKIDS")
            a["reasonforentry"] = gks(row, "ANIMALREASONFORENTRY")
            a["estimatedage"] = gks(row, "ANIMALAGE")
            a["dateofbirth"] = gkd(dbo, row, "ANIMALDOB", True)
            if gks(row, "ANIMALDOB") == "" and a["estimatedage"] != "":
                a["dateofbirth"] = "" # if we had an age and dob was blank, prefer the age
            a["datebroughtin"] = gkd(dbo, row, "ANIMALENTRYDATE", True)
            a["deceaseddate"] = gkd(dbo, row, "ANIMALDECEASEDDATE")
            a["neutered"] = gkbc(row, "ANIMALNEUTERED")
            a["neutereddate"] = gkd(dbo, row, "ANIMALNEUTEREDDATE")
            if a["neutereddate"] != "": a["neutered"] = "on"
            a["microchipnumber"] = gks(row, "ANIMALMICROCHIP")
            if a["microchipnumber"] != "": a["microchipped"] = "on"
            a["microchipdate"] = gkd(dbo, row, "ANIMALMICROCHIPDATE")
            a["flags"] = gks(row, "ANIMALFLAGS")
            # image data if any was supplied
            imagedata = gks(row, "ANIMALIMAGE")
            if imagedata.startswith("http"):
                # It's a URL, get the image from the remote server
                r = asm3.utils.get_image_url(imagedata, timeout=5000)
                if r["status"] == 200:
                    asm3.al.debug("retrieved image from %s (%s bytes)" % (imagedata, len(r["response"])), "csvimport.csvimport", dbo)
                    imagedata = "data:image/jpeg;base64,%s" % asm3.utils.base64encode(r["response"])
                else:
                    row_error(errors, "animal", rowno, row, "error reading image from '%s': %s" % (imagedata, r), dbo, sys.exc_info())
                    continue
            elif imagedata.startswith("data:image"):
                # It's a base64 encoded data URI - do nothing as attach_file requires it
                pass
            else:
                # We don't know what it is, don't try and do anything with it
                imagedata = ""
            # If an original owner is specified, create a person record
            # for them and attach it to the animal as original owner
            if gks(row, "ORIGINALOWNERLASTNAME") != "":
                p = {}
                p["title"] = gks(row, "ORIGINALOWNERTITLE")
                p["initials"] = gks(row, "ORIGINALOWNERINITIALS")
                p["forenames"] = gks(row, "ORIGINALOWNERFIRSTNAME")
                p["surname"] = gks(row, "ORIGINALOWNERLASTNAME")
                p["address"] = gks(row, "ORIGINALOWNERADDRESS")
                p["town"] = gks(row, "ORIGINALOWNERCITY")
                p["county"] = gks(row, "ORIGINALOWNERSTATE")
                p["postcode"] = gks(row, "ORIGINALOWNERZIPCODE")
                p["jurisdiction"] = gkl(dbo, row, "ORIGINALOWNERJURISDICTION", "jurisdiction", "JurisdictionName", createmissinglookups)
                p["hometelephone"] = gks(row, "ORIGINALOWNERHOMEPHONE")
                p["worktelephone"] = gks(row, "ORIGINALOWNERWORKPHONE")
                p["mobiletelephone"] = gks(row, "ORIGINALOWNERCELLPHONE")
                p["emailaddress"] = gks(row, "ORIGINALOWNEREMAIL")
                try:
                    if checkduplicates:
                        dups = asm3.person.get_person_similar(dbo, p["emailaddress"], p["mobiletelephone"], p["surname"], p["forenames"], p["address"])
                        if len(dups) > 0:
                            a["originalowner"] = str(dups[0]["ID"])
                    if "originalowner" not in a:
                        ooid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(p, dbo.locale), user, geocode=False)
                        a["originalowner"] = str(ooid)
                        # Identify an ORIGINALOWNERADDITIONAL additional fields and create them
                        create_additional_fields(dbo, row, errors, rowno, "ORIGINALOWNERADDITIONAL", "person", ooid)
                except Exception as e:
                    row_error(errors, "originalowner", rowno, row, e, dbo, sys.exc_info())
            try:
                if checkduplicates:
                    dup = asm3.animal.get_animal_sheltercode(dbo, a["sheltercode"])
                    if dup is not None:
                        animalid = dup.ID
                        # The animal is a duplicate. Update certain key fields if they are present
                        if a["healthproblems"] != "":
                            dbo.update("animal", dup.ID, { "HealthProblems": a["healthproblems"] }, user)
                        if a["microchipnumber"] != "":
                            dbo.update("animal", dup.ID, { 
                                "Identichipped": 1,
                                "IdentichipNumber": a["microchipnumber"],
                                "IdentichipDate": asm3.i18n.display2python(dbo.locale, a["microchipdate"])
                            }, user)
                        if a["neutered"] == "on":
                            dbo.update("animal", dup.ID, { 
                                "Neutered": 1, 
                                "NeuteredDate": asm3.i18n.display2python(dbo.locale, a["neutereddate"]) 
                            }, user)
                        if a["flags"] != "":
                            asm3.animal.update_flags(dbo, user, dup.ID, a["flags"])
                if animalid == 0:
                    animalid, dummy = asm3.animal.insert_animal_from_form(dbo, asm3.utils.PostedData(a, dbo.locale), user)
                    # Identify any ANIMALADDITIONAL additional fields and create them
                    create_additional_fields(dbo, row, errors, rowno, "ANIMALADDITIONAL", "animal", animalid)
                    # Add any flags that were set
                    if a["flags"] != "":
                        asm3.animal.update_flags(dbo, user, animalid, a["flags"])
                # If we have some image data, add it to the animal
                if len(imagedata) > 0:
                    imagepost = asm3.utils.PostedData({ "filename": "image.jpg", "filetype": "image/jpeg", "filedata": imagedata }, dbo.locale)
                    asm3.media.attach_file_from_form(dbo, user, asm3.media.ANIMAL, animalid, imagepost)
            except Exception as e:
                row_error(errors, "animal", rowno, row, e, dbo, sys.exc_info())

        # Person data?
        personid = 0
        if hasperson and (gks(row, "PERSONLASTNAME") != "" or gks(row, "PERSONNAME") != ""):
            p = {}
            p["ownertype"] = gks(row, "PERSONCLASS")
            if p["ownertype"] != "1" and p["ownertype"] != "2": 
                p["ownertype"] = "1"
            p["title"] = gks(row, "PERSONTITLE")
            p["initials"] = gks(row, "PERSONINITIALS")
            p["forenames"] = gks(row, "PERSONFIRSTNAME")
            p["surname"] = gks(row, "PERSONLASTNAME")
            # If we have a person name, all upto the last space is first names,
            # everything after the last name
            if gks(row, "PERSONNAME") != "":
                pname = gks(row, "PERSONNAME")
                if pname.find(" ") != -1:
                    p["forenames"] = pname[0:pname.rfind(" ")]
                    p["surname"] = pname[pname.rfind(" ")+1:]
                else:
                    p["surname"] = pname
            p["address"] = gks(row, "PERSONADDRESS")
            p["town"] = gks(row, "PERSONCITY")
            p["county"] = gks(row, "PERSONSTATE")
            p["postcode"] = gks(row, "PERSONZIPCODE")
            p["jurisdiction"] = gkl(dbo, row, "PERSONJURISDICTION", "jurisdiction", "JurisdictionName", createmissinglookups)
            p["hometelephone"] = gks(row, "PERSONHOMEPHONE")
            p["worktelephone"] = gks(row, "PERSONWORKPHONE")
            p["mobiletelephone"] = gks(row, "PERSONCELLPHONE")
            p["emailaddress"] = gks(row, "PERSONEMAIL")
            p["gdprcontactoptin"] = gks(row, "PERSONGDPRCONTACTOPTIN")
            flags = gks(row, "PERSONFLAGS")
            if gkb(row, "PERSONFOSTERER"): flags += ",fosterer"
            if gkb(row, "PERSONMEMBER"): flags += ",member"
            if gkb(row, "PERSONDONOR"): flags += ",donor"
            p["flags"] = flags
            p["comments"] = gks(row, "PERSONCOMMENTS")
            p["membershipnumber"] = gks(row, "PERSONMEMBERSHIPNUMBER")
            p["membershipexpires"] = gkd(dbo, row, "PERSONMEMBERSHIPEXPIRY")
            p["matchactive"] = gkbi(row, "PERSONMATCHACTIVE")
            if p["matchactive"] == "1":
                if "PERSONMATCHADDED" in cols: p["matchadded"] = gkd(dbo, row, "PERSONMATCHADDED")
                if "PERSONMATCHEXPIRES" in cols: p["matchexpires"] = gkd(dbo, row, "PERSONMATCHEXPIRES")
                if "PERSONMATCHSEX" in cols: p["matchsex"] = gksx(row, "PERSONMATCHSEX")
                if "PERSONMATCHSIZE" in cols: p["matchsize"] = gkl(dbo, row, "PERSONMATCHSIZE", "lksize", "Size", False)
                if "PERSONMATCHCOLOR" in cols: p["matchcolour"] = gkl(dbo, row, "PERSONMATCHCOLOR", "basecolour", "BaseColour", createmissinglookups)
                if "PERSONMATCHAGEFROM" in cols: p["agedfrom"] = gks(row, "PERSONMATCHAGEFROM")
                if "PERSONMATCHAGETO" in cols: p["agedto"] = gks(row, "PERSONMATCHAGETO")
                if "PERSONMATCHTYPE" in cols: p["matchanimaltype"] = gkl(dbo, row, "PERSONMATCHTYPE", "animaltype", "AnimalType", createmissinglookups)
                if "PERSONMATCHSPECIES" in cols: p["matchspecies"] = gkl(dbo, row, "PERSONMATCHSPECIES", "species", "SpeciesName", createmissinglookups)
                if "PERSONMATCHBREED1" in cols: p["matchbreed"] = gkbr(dbo, row, "PERSONMATCHBREED1", p["matchspecies"], createmissinglookups)
                if "PERSONMATCHBREED2" in cols: p["matchbreed2"] = gkbr(dbo, row, "PERSONMATCHBREED2", p["matchspecies"], createmissinglookups)
                if "PERSONMATCHGOODWITHCATS" in cols: p["matchgoodwithcats"] = gkynu(row, "PERSONMATCHGOODWITHCATS")
                if "PERSONMATCHGOODWITHDOGS" in cols: p["matchgoodwithdogs"] = gkynu(row, "PERSONMATCHGOODWITHDOGS")
                if "PERSONMATCHGOODWITHCHILDREN" in cols: p["matchgoodwithchildren"] = gkynu(row, "PERSONMATCHGOODWITHCHILDREN")
                if "PERSONMATCHHOUSETRAINED" in cols: p["matchhousetrained"] = gkynu(row, "PERSONMATCHHOUSETRAINED")
                if "PERSONMATCHCOMMENTSCONTAIN" in cols: p["matchcommentscontain"] = gks(row, "PERSONMATCHCOMMENTSCONTAIN")
            try:
                if checkduplicates:
                    dups = asm3.person.get_person_similar(dbo, p["emailaddress"], p["mobiletelephone"], p["surname"], p["forenames"], p["address"])
                    if len(dups) > 0:
                        personid = dups[0].ID
                        # Merge flags and any extra details
                        asm3.person.merge_flags(dbo, user, personid, flags)
                        asm3.person.merge_gdpr_flags(dbo, user, personid, p["gdprcontactoptin"])
                        # If we deduplicated on the email address, and address details are
                        # present, assume that they are newer than the ones we had and update them
                        # (we do this by setting force=True parameter to merge_person_details,
                        # otherwise we do a regular merge which only fills in any blanks)
                        asm3.person.merge_person_details(dbo, user, personid, p, force=dups[0].EMAILADDRESS == p["emailaddress"])
                if personid == 0:
                    personid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(p, dbo.locale), user, geocode=False)
                    # Identify any PERSONADDITIONAL additional fields and create them
                    create_additional_fields(dbo, row, errors, rowno, "PERSONADDITIONAL", "person", personid)
            except Exception as e:
                row_error(errors, "person", rowno, row, e, dbo, sys.exc_info())

        # Movement to tie animal/person together?
        movementid = 0
        if hasmovement and personid != 0 and animalid != 0 and gks(row, "MOVEMENTDATE") != "":
            m = {}
            m["person"] = str(personid)
            m["animal"] = str(animalid)
            movetype = gks(row, "MOVEMENTTYPE")
            if movetype == "": movetype = "1" # Default to adoption if not supplied
            m["type"] = str(movetype)
            m["movementdate"] = gkd(dbo, row, "MOVEMENTDATE", True)
            m["returndate"] = gkd(dbo, row, "MOVEMENTRETURNDATE")
            m["comments"] = gks(row, "MOVEMENTCOMMENTS")
            m["returncategory"] = str(asm3.configuration.default_entry_reason(dbo))
            try:
                movementid = asm3.movement.insert_movement_from_form(dbo, user, asm3.utils.PostedData(m, dbo.locale))
            except Exception as e:
                row_error(errors, "movement", rowno, row, e, dbo, sys.exc_info())

        # Donation?
        if hasdonation and personid != 0 and gkc(row, "DONATIONAMOUNT") != 0:
            d = {}
            d["person"] = str(personid)
            d["animal"] = str(animalid)
            d["movement"] = str(movementid)
            d["amount"] = str(gkc(row, "DONATIONAMOUNT"))
            d["fee"] = str(gkc(row, "DONATIONFEE"))
            d["comments"] = gks(row, "DONATIONCOMMENTS")
            d["received"] = gkd(dbo, row, "DONATIONDATE", True)
            d["chequenumber"] = gks(row, "DONATIONCHECKNUMBER")
            d["type"] = gkl(dbo, row, "DONATIONTYPE", "donationtype", "DonationName", createmissinglookups)
            if d["type"] == "0":
                d["type"] = str(asm3.configuration.default_donation_type(dbo))
            d["giftaid"] = gkbc(row, "DONATIONGIFTAID")
            d["payment"] = gkl(dbo, row, "DONATIONPAYMENT", "donationpayment", "PaymentName", createmissinglookups)
            if d["payment"] == "0":
                d["payment"] = "1"
            try:
                asm3.financial.insert_donation_from_form(dbo, user, asm3.utils.PostedData(d, dbo.locale))
            except Exception as e:
                row_error(errors, "payment", rowno, row, e, dbo, sys.exc_info())
            if movementid != 0: asm3.movement.update_movement_donation(dbo, movementid)

        # Vaccination?
        if hasvacc and animalid != 0 and gks(row, "VACCINATIONDUEDATE") != "":
            v = {}
            v["animal"] = str(animalid)
            v["type"] = gkl(dbo, row, "VACCINATIONTYPE", "vaccinationtype", "VaccinationType", createmissinglookups)
            if v["type"] == "0":
                v["type"] = str(asm3.configuration.default_vaccination_type(dbo))
            v["required"] = gkd(dbo, row, "VACCINATIONDUEDATE", True)
            v["given"] = gkd(dbo, row, "VACCINATIONGIVENDATE")
            v["expires"] = gkd(dbo, row, "VACCINATIONEXPIRESDATE")
            v["batchnumber"] = gks(row, "VACCINATIONBATCHNUMBER")
            v["manufacturer"] = gks(row, "VACCINATIONMANUFACTURER")
            v["comments"] = gks(row, "VACCINATIONCOMMENTS")
            try:
                asm3.medical.insert_vaccination_from_form(dbo, user, asm3.utils.PostedData(v, dbo.locale))
            except Exception as e:
                row_error(errors, "vaccination", rowno, row, e, dbo, sys.exc_info())

        # Test?
        if hastest and animalid != 0 and gks(row, "TESTDUEDATE") != "":
            v = {}
            v["animal"] = str(animalid)
            v["type"] = gkl(dbo, row, "TESTTYPE", "testtype", "TestName", createmissinglookups)
            v["result"] = gkl(dbo, row, "TESTRESULT", "testresult", "ResultName", createmissinglookups)
            v["required"] = gkd(dbo, row, "TESTDUEDATE", True)
            v["given"] = gkd(dbo, row, "TESTPERFORMEDDATE")
            v["comments"] = gks(row, "TESTCOMMENTS")
            try:
                asm3.medical.insert_test_from_form(dbo, user, asm3.utils.PostedData(v, dbo.locale))
            except Exception as e:
                row_error(errors, "test", rowno, row, e, dbo, sys.exc_info())

        # Medical?
        if hasmed and animalid != 0 and gks(row, "MEDICALGIVENDATE") != "" and gks(row, "MEDICALNAME") != "":
            m = {}
            m["animal"] = str(animalid)
            m["treatmentname"] = gks(row, "MEDICALNAME")
            m["dosage"] = gks(row, "MEDICALDOSAGE")
            m["startdate"] = gkd(dbo, row, "MEDICALGIVENDATE")
            m["comments"] = gks(row, "MEDICALCOMMENTS")
            m["singlemulti"] = "0" # single treatment
            m["status"] = "2" # completed
            try:
                asm3.medical.insert_regimen_from_form(dbo, user, asm3.utils.PostedData(m, dbo.locale))
            except Exception as e:
                row_error(errors, "medical", rowno, row, e, dbo, sys.exc_info())

        # License?
        if haslicence and personid != 0 and gks(row, "LICENSENUMBER") != "":
            l = {}
            l["person"] = str(personid)
            l["animal"] = str(animalid)
            l["type"] = gkl(dbo, row, "LICENSETYPE", "licencetype", "LicenceTypeName", createmissinglookups)
            if l["type"] == "0": l["type"] = 1
            l["number"] = gks(row, "LICENSENUMBER")
            l["fee"] = str(gkc(row, "LICENSEFEE"))
            l["issuedate"] = gkd(dbo, row, "LICENSEISSUEDATE")
            l["expirydate"] = gkd(dbo, row, "LICENSEEXPIRESDATE")
            l["comments"] = gks(row, "LICENSECOMMENTS")
            try:
                asm3.financial.insert_licence_from_form(dbo, user, asm3.utils.PostedData(l, dbo.locale))
            except Exception as e:
                row_error(errors, "license", rowno, row, e, dbo, sys.exc_info())

        rowno += 1

    h = [ "<p>%d success, %d errors</p><table>" % (len(rows) - len(errors), len(errors)) ]
    for rowno, row, err in errors:
        h.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (rowno, row, err))
    h.append("</table>")
    return "".join(h)

def csvimport_paypal(dbo, csvdata, donationtypeid, donationpaymentid, flags, user = "", encoding="utf-8-sig"):
    """
    Imports a PayPal CSV file of transactions.
    """
    def v(r, n, n2 = "", n3 = "", n4 = "", n5 = ""):
        """ Read values n(x) from a dictionary r depending on which is present, 
            if none are present empty string is returned """
        if n in r: return r[n]
        if n2 != "" and n2 in r: return r[n2]
        if n3 != "" and n3 in r: return r[n3]
        if n4 != "" and n4 in r: return r[n4]
        if n5 != "" and n5 in r: return r[n5]
        return ""

    if user == "":
        user = "import"
    else:
        user = "import/%s" % user

    rows = asm3.utils.csv_parse( asm3.utils.cunicode(csvdata, encoding=encoding) )
    print(rows[0])

    errors = []
    rowno = 1
    asm3.asynctask.set_progress_max(dbo, len(rows))

    if len(rows) == 0:
        asm3.asynctask.set_last_error(dbo, "CSV file is empty")
        return

    REQUIRED_FIELDS = [ "Date", "Currency", "Gross", "Fee", "Net", "From Email Address", "Status", "Type" ]
    for rf in REQUIRED_FIELDS:
        if rf not in rows[0]:
            asm3.asynctask.set_last_error(dbo, "This CSV file does not look like a PayPal CSV (missing %s)" % rf)
            return

    for r in rows:

        # Skip blank rows
        if len(r) == 0: continue

        # Should we stop?
        if asm3.asynctask.get_cancel(dbo): break

        asm3.al.debug("import paypal csv: row %d of %d" % (rowno, len(rows)), "csvimport.csvimport_paypal", dbo)
        asm3.asynctask.increment_progress_value(dbo)

        if r["Status"] != "Completed":
            asm3.al.debug("skipping: Status='%s' (!= Completed), Type='%s'" % (r["Status"], r["Type"]), "csvimport.csvimport_paypal", dbo)
            continue

        if r["Type"].find("Payment") == -1:
            asm3.al.debug("skipping: Status='%s', Type='%s' (!Payment)" % (r["Status"], r["Type"]), "csvimport.csvimport_paypal", dbo)
            continue

        # Parse name (use all up to last space for first names if only Name exists)
        name = v(r, "Name")
        firstname = v(r, "First Name")
        lastname = v(r, "Last Name")
        if name != "" and firstname == "" and lastname == "":
            if name.find(" ") != -1:
                firstname =name[0:name.rfind(" ")]
                lastname =name[name.rfind(" ")+1:]
            else:
                lastname = name

        # Person data
        personid = 0
        p = {}
        p["ownertype"] = "1"
        p["forenames"] = firstname
        p["surname"] = lastname
        p["address"] = v(r, "Address Line 1", "Street Address 1")
        p["town"] = v(r, "Town/City", "Town", "City")
        p["county"] = v(r, "County", "State", "Province", "Region", "State/Province/Region/County/Territory/Prefecture/Republic")
        p["postcode"] = v(r, "Postcode", "Zip Code", "Zip/Postal Code")
        p["hometelephone"] = v(r, "Contact Phone Number", "Phone Number")
        p["emailaddress"] = v(r, "From Email Address")
        p["flags"] = flags
        try:
            dups = asm3.person.get_person_similar(dbo, p["emailaddress"], p["hometelephone"], p["surname"], p["forenames"], p["address"])
            if len(dups) > 0:
                personid = dups[0]["ID"]
                # Merge flags and any extra details
                asm3.person.merge_flags(dbo, user, personid, flags)
                asm3.person.merge_person_details(dbo, user, personid, p)
            if personid == 0:
                personid = asm3.person.insert_person_from_form(dbo, asm3.utils.PostedData(p, dbo.locale), user, geocode=False)
        except Exception as e:
            row_error(errors, "person", rowno, r, e, dbo, sys.exc_info())

        # Donation info
        gross = asm3.utils.cint(asm3.utils.cfloat(v(r, "Gross")) * 100) 
        net = asm3.utils.cint(asm3.utils.cfloat(v(r, "Net")) * 100) 
        fee = abs(asm3.utils.cint(asm3.utils.cfloat(v(r, "Fee")) * 100)) # Fee is a negative amount
        if net > gross: gross = net # I've seen PayPal files where net/gross are the wrong way around
        if personid != 0 and net > 0:
            pdate = asm3.i18n.display2python(dbo.locale, v(r, "Date")) # parse the date (we do this to fix 2 digit years, which I've also seen)
            if pdate is None: pdate = dbo.today() # use today if parsing failed
            d = {}
            d["person"] = str(personid)
            d["animal"] = "0"
            d["movement"] = "0"
            d["amount"] = str(gross)
            d["fee"] = str(fee)
            d["chequenumber"] = str(v(r, "Transaction ID"))
            comments = "PayPal ID: %s \nItem: %s %s \nCurrency: %s \nGross: %s \nFee: %s \nNet: %s \nSubject: %s \nNote: %s" % \
                ( v(r, "Transaction ID"), v(r, "Item ID", "Item Number"), v(r, "Item Title"), v(r, "Currency"), 
                v(r, "Gross"), v(r, "Fee"), v(r, "Net"), v(r, "Subject"), v(r, "Note") )
            d["comments"] = comments
            d["received"] = asm3.i18n.python2display(dbo.locale, pdate)
            d["type"] = str(donationtypeid)
            d["payment"] = str(donationpaymentid)
            try:
                asm3.financial.insert_donation_from_form(dbo, user, asm3.utils.PostedData(d, dbo.locale))
            except Exception as e:
                row_error(errors, "payment", rowno, r, e, dbo, sys.exc_info())

        rowno += 1

    h = [ "<p>%d success, %d errors</p><table>" % (len(rows) - len(errors), len(errors)) ]
    for rowno, row, err in errors:
        h.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (rowno, row, err))
    h.append("</table>")
    return "".join(h)

def csvexport_animals(dbo, dataset, animalids = "", includephoto = False):
    """
    Export CSV data for a set of animals.
    dataset: The named set of data to use
    animalids: If dataset == selshelter, a comma separated list of animals to export
    includephoto: Output a base64 encoded version of the animal's photo if True
    """
    l = dbo.locale
    q = ""
    out = asm3.utils.stringio()
    
    if dataset == "all": q = "SELECT ID FROM animal ORDER BY ID"
    elif dataset == "shelter": q = "SELECT ID FROM animal WHERE Archived=0 ORDER BY ID"
    elif dataset == "nonshelter": q = "SELECT ID FROM animal WHERE NonShelterAnimal=1 ORDER BY ID"
    elif dataset == "selshelter": q = "SELECT ID FROM animal WHERE ID IN (%s) ORDER BY ID" % animalids
    
    ids = dbo.query(q)

    keys = [ "ANIMALCODE", "ANIMALNAME", "ANIMALIMAGE", "ANIMALSEX", "ANIMALTYPE", "ANIMALWEIGHT", "ANIMALCOLOR", "ANIMALBREED1",
        "ANIMALBREED2", "ANIMALDOB", "ANIMALLOCATION", "ANIMALUNIT", "ANIMALSPECIES", "ANIMALCOMMENTS",
        "ANIMALHIDDENDETAILS", "ANIMALHEALTHPROBLEMS", "ANIMALMARKINGS", "ANIMALREASONFORENTRY", "ANIMALNEUTERED",
        "ANIMALNEUTEREDDATE", "ANIMALMICROCHIP", "ANIMALMICROCHIPDATE", "ANIMALENTRYDATE", "ANIMALDECEASEDDATE",
        "ANIMALNOTFORADOPTION", "ANIMALNONSHELTER", "ANIMALGOODWITHCATS", "ANIMALGOODWITHDOGS", "ANIMALGOODWITHKIDS",
        "ANIMALHOUSETRAINED", "ORIGINALOWNERTITLE", "ORIGINALOWNERINITIALS", "ORIGINALOWNERFIRSTNAME",
        "ORIGINALOWNERLASTNAME", "ORIGINALOWNERADDRESS", "ORIGINALOWNERCITY", "ORIGINALOWNERSTATE", "ORIGINALOWNERZIPCODE",
        "ORIGINALOWNERHOMEPHONE", "ORIGINALOWNERWORKPHONE", "ORIGINALOWNERCELLPHONE", "ORIGINALOWNEREMAIL", "MOVEMENTTYPE",
        "MOVEMENTDATE", "PERSONTITLE", "PERSONINITIALS", "PERSONFIRSTNAME", "PERSONLASTNAME", "PERSONADDRESS", "PERSONCITY",
        "PERSONSTATE", "PERSONZIPCODE", "PERSONFOSTERER", "PERSONHOMEPHONE", "PERSONWORKPHONE", "PERSONCELLPHONE", "PERSONEMAIL",
        "TESTTYPE", "TESTRESULT", "TESTDUEDATE", "TESTPERFORMEDDATE", "TESTCOMMENTS",
        "VACCINATIONTYPE", "VACCINATIONDUEDATE", "VACCINATIONGIVENDATE", "VACCINATIONEXPIRESDATE", "VACCINATIONMANUFACTURER",
        "VACCINATIONBATCHNUMBER", "VACCINATIONCOMMENTS", "MEDICALNAME", "MEDICALDOSAGE", "MEDICALGIVENDATE", "MEDICALCOMMENTS" ]
    
    def tocsv(row):
        r = []
        for k in keys:
            if k in row: 
                r.append("\"%s\"" % row[k])
            else:
                r.append("\"\"")
        return ",".join(r) + "\n"

    firstrow = True
    asm3.asynctask.set_progress_max(dbo, len(ids))
    for aid in ids:

        # Should we stop?
        if asm3.asynctask.get_cancel(dbo): break

        if firstrow:
            firstrow = False
            out.write(",".join(keys) + "\n")

        row = {}
        a = asm3.animal.get_animal(dbo, aid.ID)
        if a is None: continue

        asm3.asynctask.increment_progress_value(dbo)

        row["ANIMALCODE"] = a["SHELTERCODE"]
        row["ANIMALNAME"] = a["ANIMALNAME"]
        if a["WEBSITEIMAGECOUNT"] > 0 and includephoto:
            dummy, mdata = asm3.media.get_image_file_data(dbo, "animal", a["ID"])
            row["ANIMALIMAGE"] = "data:image/jpg;base64,%s" % asm3.utils.base64encode(mdata)
        row["ANIMALSEX"] = a["SEXNAME"]
        row["ANIMALTYPE"] = a["ANIMALTYPENAME"]
        row["ANIMALCOLOR"] = a["BASECOLOURNAME"]
        row["ANIMALBREED1"] = a["BREEDNAME1"]
        row["ANIMALBREED2"] = a["BREEDNAME2"]
        row["ANIMALDOB"] = asm3.i18n.python2display(l, a["DATEOFBIRTH"])
        row["ANIMALSIZE"] = a["SIZENAME"]
        row["ANIMALWEIGHT"] = a["WEIGHT"]
        row["ANIMALLOCATION"] = a["SHELTERLOCATIONNAME"]
        row["ANIMALUNIT"] = a["SHELTERLOCATIONUNIT"]
        row["ANIMALSPECIES"] = a["SPECIESNAME"]
        row["ANIMALCOMMENTS"] = a["ANIMALCOMMENTS"]
        row["ANIMALHIDDENDETAILS"] = a["HIDDENANIMALDETAILS"]
        row["ANIMALHEALTHPROBLEMS"] = a["HEALTHPROBLEMS"]
        row["ANIMALMARKINGS"] = a["MARKINGS"]
        row["ANIMALREASONFORENTRY"] = a["REASONFORENTRY"]
        row["ANIMALNEUTERED"] = a["NEUTERED"]
        row["ANIMALNEUTEREDDATE"] = asm3.i18n.python2display(l, a["NEUTEREDDATE"])
        row["ANIMALMICROCHIP"] = a["IDENTICHIPNUMBER"]
        row["ANIMALMICROCHIPDATE"] = asm3.i18n.python2display(l, a["IDENTICHIPDATE"])
        row["ANIMALENTRYDATE"] = asm3.i18n.python2display(l, a["DATEBROUGHTIN"])
        row["ANIMALDECEASEDDATE"] = asm3.i18n.python2display(l, a["DECEASEDDATE"])
        row["ANIMALNOTFORADOPTION"] = a["ISNOTAVAILABLEFORADOPTION"]
        row["ANIMALNONSHELTER"] = a["NONSHELTERANIMAL"]
        row["ANIMALGOODWITHCATS"] = a["ISGOODWITHCATSNAME"]
        row["ANIMALGOODWITHDOGS"] = a["ISGOODWITHDOGSNAME"]
        row["ANIMALGOODWITHKIDS"] = a["ISGOODWITHCHILDRENNAME"]
        row["ANIMALHOUSETRAINED"] = a["ISHOUSETRAINEDNAME"]
        row["ORIGINALOWNERTITLE"] = a["ORIGINALOWNERTITLE"]
        row["ORIGINALOWNERINITIALS"] = a["ORIGINALOWNERINITIALS"]
        row["ORIGINALOWNERFIRSTNAME"] = a["ORIGINALOWNERFORENAMES"]
        row["ORIGINALOWNERLASTNAME"] = a["ORIGINALOWNERSURNAME"]
        row["ORIGINALOWNERADDRESS"] = a["ORIGINALOWNERADDRESS"]
        row["ORIGINALOWNERCITY"] = a["ORIGINALOWNERTOWN"]
        row["ORIGINALOWNERSTATE"] = a["ORIGINALOWNERCOUNTY"]
        row["ORIGINALOWNERZIPCODE"] = a["ORIGINALOWNERPOSTCODE"]
        row["ORIGINALOWNERHOMEPHONE"] = a["ORIGINALOWNERHOMETELEPHONE"]
        row["ORIGINALOWNERWORKPHONE"] = a["ORIGINALOWNERWORKTELEPHONE"]
        row["ORIGINALOWNERCELLPHONE"] = a["ORIGINALOWNERMOBILETELEPHONE"]
        row["ORIGINALOWNEREMAIL"] = a["ORIGINALOWNEREMAILADDRESS"]
        row["MOVEMENTTYPE"] = a["ACTIVEMOVEMENTTYPE"]
        row["MOVEMENTDATE"] = asm3.i18n.python2display(l, a["ACTIVEMOVEMENTDATE"])
        row["PERSONTITLE"] = a["CURRENTOWNERTITLE"]
        row["PERSONINITIALS"] = a["CURRENTOWNERINITIALS"]
        row["PERSONFIRSTNAME"] = a["CURRENTOWNERFORENAMES"]
        row["PERSONLASTNAME"] = a["CURRENTOWNERSURNAME"]
        row["PERSONADDRESS"] = a["CURRENTOWNERADDRESS"]
        row["PERSONCITY"] = a["CURRENTOWNERTOWN"]
        row["PERSONSTATE"] = a["CURRENTOWNERCOUNTY"]
        row["PERSONZIPCODE"] = a["CURRENTOWNERPOSTCODE"]
        row["PERSONFOSTERER"] = a["ACTIVEMOVEMENTTYPE"] == 2 and 1 or 0
        row["PERSONHOMEPHONE"] = a["CURRENTOWNERHOMETELEPHONE"]
        row["PERSONWORKPHONE"] = a["CURRENTOWNERWORKTELEPHONE"]
        row["PERSONCELLPHONE"] = a["CURRENTOWNERMOBILETELEPHONE"]
        row["PERSONEMAIL"] = a["CURRENTOWNEREMAILADDRESS"]
        out.write(tocsv(row))

        for v in asm3.medical.get_vaccinations(dbo, a["ID"]):
            row = {}
            row["VACCINATIONTYPE"] = v["VACCINATIONTYPE"]
            row["VACCINATIONDUEDATE"] = asm3.i18n.python2display(l, v["DATEREQUIRED"])
            row["VACCINATIONGIVENDATE"] = asm3.i18n.python2display(l, v["DATEOFVACCINATION"])
            row["VACCINATIONEXPIRESDATE"] = asm3.i18n.python2display(l, v["DATEEXPIRES"])
            row["VACCINATIONMANUFACTURER"] = v["MANUFACTURER"]
            row["VACCINATIONBATCHNUMBER"] = v["BATCHNUMBER"]
            row["VACCINATIONCOMMENTS"] = v["COMMENTS"]
            row["ANIMALCODE"] = a["SHELTERCODE"]
            row["ANIMALNAME"] = a["ANIMALNAME"]
            out.write(tocsv(row))

        for t in asm3.medical.get_tests(dbo, a["ID"]):
            row = {}
            row["TESTTYPE"] = t["TESTNAME"]
            row["TESTRESULT"] = t["RESULTNAME"]
            row["TESTDUEDATE"] = asm3.i18n.python2display(l, t["DATEREQUIRED"])
            row["TESTPERFORMEDDATE"] = asm3.i18n.python2display(l, t["DATEOFTEST"])
            row["TESTCOMMENTS"] = t["COMMENTS"]
            row["ANIMALCODE"] = a["SHELTERCODE"]
            row["ANIMALNAME"] = a["ANIMALNAME"]
            out.write(tocsv(row))

        for m in asm3.medical.get_regimens(dbo, a["ID"]):
            row = {}
            row["MEDICALNAME"] = m["TREATMENTNAME"]
            row["MEDICALDOSAGE"] = m["DOSAGE"]
            row["MEDICALGIVENDATE"] = asm3.i18n.python2display(l, m["STARTDATE"])
            row["MEDICALCOMMENTS"] = m["COMMENTS"]
            row["ANIMALCODE"] = a["SHELTERCODE"]
            row["ANIMALNAME"] = a["ANIMALNAME"]
            out.write(tocsv(row))

        del a
        del row

    # Generate a disk cache key and store the data in the cache so it can be retrieved for the next hour
    key = asm3.utils.uuid_str()
    asm3.cachedisk.put(key, dbo.database, out.getvalue(), 3600)
    h = '<p>%s <a target="_blank" href="csvexport_animals?get=%s"><b>%s</b></p>' % ( \
        asm3.i18n._("Export complete ({0} entries).", l).format(len(ids)), key, asm3.i18n._("Download File", l) )
    return h

