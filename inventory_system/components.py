#encoding: utf8

class Equippable(ItemComponentBase):
    EQUIP_SLOT_LEFT_HAND = 0
    EQUIP_SLOT_RIGHT_HAND = 1
    EQUIP_SLOT_HEAD = 2
    EQUIP_SLOT_FEET = 3
    EQUIP_SLOT_BODY = 4
    def __init__(self, equip_slot, on_equip_fn, on_unequip_fn):
        self._equip_slot = equip_slot
        self._on_fn = on_equip_fn
        self._off_fn = on_unequip_fn
