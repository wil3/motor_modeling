
class MSPStatusMessage():#MSPMessage):
    ARMING_DISABLED_NO_GYRO         = (1 << 0)
    ARMING_DISABLED_FAILSAFE        = (1 << 1)
    ARMING_DISABLED_RX_FAILSAFE     = (1 << 2)
    ARMING_DISABLED_BAD_RX_RECOVERY = (1 << 3)
    ARMING_DISABLED_BOXFAILSAFE     = (1 << 4)
    ARMING_DISABLED_THROTTLE        = (1 << 5)
    ARMING_DISABLED_ANGLE           = (1 << 6)
    ARMING_DISABLED_BOOT_GRACE_TIME = (1 << 7)
    ARMING_DISABLED_NOPREARM        = (1 << 8)
    ARMING_DISABLED_LOAD            = (1 << 9)
    ARMING_DISABLED_CALIBRATING     = (1 << 10)
    ARMING_DISABLED_CLI             = (1 << 11)
    ARMING_DISABLED_CMS_MENU        = (1 << 12)
    ARMING_DISABLED_OSD_MENU        = (1 << 13)
    ARMING_DISABLED_BST             = (1 << 14)
    ARMING_DISABLED_MSP             = (1 << 15)
    ARMING_DISABLED_ARM_SWITCH      = (1 << 16)

    armingDisableFlagNames= ["NOGYRO", "FAILSAFE", "RXLOSS", "BADRX", "BOXFAILSAFE", "THROTTLE", "ANGLE", "BOOTGRACE", "NOPREARM", "LOAD",  "CALIB", "CLI", "CMS", "OSD", "BST", "MSP", "ARMSWITCH"] 

    BOX_NAMES = ["BOXARM",
    "BOXANGLE",
    "BOXHORIZON",
    "BOXBARO",
    "BOXANTIGRAVITY",
    "BOXMAG",
    "BOXHEADFREE",
    "BOXHEADADJ",
    "BOXCAMSTAB",
    "BOXCAMTRIG",
    "BOXGPSHOME",
    "BOXGPSHOLD",
    "BOXPASSTHRU",
    "BOXBEEPERON",
    "BOXLEDMAX",
    "BOXLEDLOW",
    "BOXLLIGHTS",
    "BOXCALIB",
    "BOXGOV",
    "BOXOSD",
    "BOXTELEMETRY",
    "BOXGTUNE",
    "BOXSONAR",
    "BOXSERVO1",
    "BOXSERVO2",
    "BOXSERVO3",
    "BOXBLACKBOX",
    "BOXFAILSAFE",
    "BOXAIRMODE",
    "BOX3DDISABLE",
    "BOXFPVANGLEMIX",
    "BOXBLACKBOXERASE",
    "BOXCAMERA1",
    "BOXCAMERA2",
    "BOXCAMERA3",
    "BOXFLIPOVERAFTERCRASH",
    "BOXPREARM",
    "BOXBEEPGPSCOUNT",
    "BOX3DONASWITCH",
    "CHECKBOX_ITEM_COUNT"
    ]

    def __init__(self):#, direction=MSPMessage.TO_FC, size=0, data=[], crc=None):

        self.dt = None
        self.ic2_error_count = None
        self.sensors = None
        self.flight_mode_flags = None
        self.pid_profile_index = None 
        self.system_load = None
        self.gyro_cycle_time = None 
        self.size_conditional_flight_mode_flags = None 
        self.conditional_flight_mode_flags = None 
        self.num_disarming_flags = None 
        self.arming_disabled_flags = None
        self.num_disarming_flags = None
        self.arming_disabled_flags = None

        #super().__init__(direction=direction, size=size, id=MSPMessage.STATUS, data=data)

    def get_arming_disabled_flags_by_name(self):
        names = []
        bits = list(reversed("{0:b}".format(self.arming_disabled_flags)))
        for i in range(len(bits)):
            if bits[i] == "1": # enabled
                names.append(self.armingDisableFlagNames[i])
        return names

    def get_enabled_boxes(self):
        names = []
        bits = list(reversed("{0:b}".format(self.flight_mode_flags)))
        #logger.debug("Modes={} to bits= {}", self.flight_mode_flags, bits)
        for i in range(len(bits)):
            if bits[i] == "1":
                names.append(self.BOX_NAMES[i])
        return names

    def has_disable_flag(self, flag):
        return (self.arming_disabled_flags & flag) == flag

    def is_mode_set(self, mode):
        pass
