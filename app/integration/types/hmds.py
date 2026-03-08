from enum import Enum


class HMD(Enum):
    unknown = (0, "Unknown")
    rift = (1, "Oculus Rift")
    vive = (2, "HTC Vive")
    vivePro = (4, "HTC Vive Pro")
    wmr = (8, "Windows Mixed Reality")
    riftS = (16, "Oculus Rift S")
    quest = (32, "Meta Quest (1st Gen)")
    picoNeo3 = (33, "Pico Neo 3")
    picoNeo2 = (34, "Pico Neo 2")
    vivePro2 = (35, "HTC Vive Pro 2")
    viveElite = (36, "HTC Vive Elite")
    miramar = (37, "Miramar VR")
    pimax8k = (38, "Pimax 8K")
    pimax5k = (39, "Pimax 5K")
    pimaxArtisan = (40, "Pimax Artisan")
    hpReverb = (41, "HP Reverb")
    samsungWmr = (42, "Samsung Odyssey")
    qiyuDream = (43, "Qiyu Dream VR")
    disco = (44, "Disco VR Headset")
    lenovoExplorer = (45, "Lenovo Explorer")
    acerWmr = (46, "Acer Windows MR")
    viveFocus = (47, "HTC Vive Focus")
    arpara = (48, "Arpara VR")
    dellVisor = (49, "Dell Visor")
    e3 = (50, "E3 VR")
    viveDvt = (51, "HTC Vive DVT")
    glasses20 = (52, "Glasses 2.0")
    hedy = (53, "Hedy VR")
    vaporeon = (54, "Vaporeon (Prototype)")
    huaweivr = (55, "Huawei VR")
    asusWmr = (56, "ASUS Mixed Reality")
    cloudxr = (57, "NVIDIA CloudXR")
    vridge = (58, "VRidge (Phone Streaming)")
    medion = (59, "Medion Mixed Reality")
    picoNeo4 = (60, "Pico Neo 4")
    questPro = (61, "Meta Quest Pro")
    pimaxCrystal = (62, "Pimax Crystal")
    e4 = (63, "E4 VR")
    index = (64, "Valve Index")
    controllable = (65, "Controllable / Generic HMD")
    bigscreenbeyond = (66, "Bigscreen Beyond")
    nolosonic = (67, "NOLO Sonic")
    hypereal = (68, "Hypereal VR")
    varjoaero = (69, "Varjo Aero")
    psvr2 = (70, "PlayStation VR2")
    megane1 = (71, "MeganeX 1")
    varjoxr3 = (72, "Varjo XR-3")
    meganexsuperlight = (73, "MeganeX Superlight")
    somniumvr1 = (74, "Somnium VR1")
    viveCosmos = (128, "HTC Vive Cosmos")
    quest2 = (256, "Meta Quest 2")
    quest3 = (512, "Meta Quest 3")
    quest3s = (513, "Meta Quest 3S")

    def __init__(self, value: int, readable_name: str):
        self._value_ = value
        self.readable_name = readable_name

    @classmethod
    def get_by_id(cls, hmd_id: int):
        """Retorna o enum correspondente ao ID."""
        for hmd in cls:
            if hmd.value == hmd_id:
                return hmd
        return cls.unknown

    @classmethod
    def get_name(cls, hmd_id: int) -> str:
        """Retorna o nome legível pelo ID."""
        return cls.get_by_id(hmd_id).readable_name

    @classmethod
    def get_id(cls, name: str) -> int:
        """Retorna o ID pelo nome legível ou técnico."""
        name_lower = name.lower()
        for hmd in cls:
            if hmd.name.lower() == name_lower or hmd.readable_name.lower() == name_lower:
                return hmd.value
        return 0
