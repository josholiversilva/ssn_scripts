from enum import Enum

class Users(str, Enum):
    JEN = "jen"
    BWI = "brian"
    JOSH = "josh"
    IRIS = "iris"
    VINCE = "vincent"
    BURNA = "bryan"
    ERIC = "eric"
    RYAN = "ryan"
    ANA = "ana"
    SUSAN = "susan"
    EUNBI = "eunbi"
    SHAWN = "shawn"
    VIC = "victoria"

    def get_all():
        return [u.value for u in Users]

    def get_girls():
        return [Users.VIC.value, Users.IRIS.value, Users.SUSAN.value, Users.EUNBI.value, Users.JEN.value, Users.ANA.value]

    def get_girls_to_rig():
        return [Users.EUNBI.value, Users.SUSAN.value]