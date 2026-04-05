"""FM player roles."""

from collections import namedtuple
from enum import StrEnum


class Duty(StrEnum):
    DEFEND = "Defend"
    SUPPORT = "Support"
    ATTACK = "Attack"
    STOPPER = "Stopper"
    COVER = "Cover"


class Role(namedtuple("RoleBase", "code short_name name duty")):
    __slots__ = ()

    @property
    def label(self):
        return f"{self.name} ({self.duty.value})"

    @property
    def short_label(self):
        return f"{self.short_name.upper()} ({self.duty.value[0]})"


class RoleFamily:
    def __init__(self, short_name, name, roles_by_duty):
        self.short_name = short_name
        self.name = name
        self.roles_by_duty = roles_by_duty

    @property
    def all(self):
        return tuple(self.roles_by_duty.values())


class DefendRoleFamily(RoleFamily):
    DEFEND: Role

    def __init__(self, short_name, name, roles_by_duty):
        super().__init__(short_name, name, roles_by_duty)
        self.DEFEND = roles_by_duty[Duty.DEFEND]


class SupportRoleFamily(RoleFamily):
    SUPPORT: Role

    def __init__(self, short_name, name, roles_by_duty):
        super().__init__(short_name, name, roles_by_duty)
        self.SUPPORT = roles_by_duty[Duty.SUPPORT]


class AttackRoleFamily(RoleFamily):
    ATTACK: Role

    def __init__(self, short_name, name, roles_by_duty):
        super().__init__(short_name, name, roles_by_duty)
        self.ATTACK = roles_by_duty[Duty.ATTACK]


class DefendSupportRoleFamily(RoleFamily):
    DEFEND: Role
    SUPPORT: Role

    def __init__(self, short_name, name, roles_by_duty):
        super().__init__(short_name, name, roles_by_duty)
        self.DEFEND = roles_by_duty[Duty.DEFEND]
        self.SUPPORT = roles_by_duty[Duty.SUPPORT]


class SupportAttackRoleFamily(RoleFamily):
    SUPPORT: Role
    ATTACK: Role

    def __init__(self, short_name, name, roles_by_duty):
        super().__init__(short_name, name, roles_by_duty)
        self.SUPPORT = roles_by_duty[Duty.SUPPORT]
        self.ATTACK = roles_by_duty[Duty.ATTACK]


class DefendSupportAttackRoleFamily(RoleFamily):
    DEFEND: Role
    SUPPORT: Role
    ATTACK: Role

    def __init__(self, short_name, name, roles_by_duty):
        super().__init__(short_name, name, roles_by_duty)
        self.DEFEND = roles_by_duty[Duty.DEFEND]
        self.SUPPORT = roles_by_duty[Duty.SUPPORT]
        self.ATTACK = roles_by_duty[Duty.ATTACK]


class DefendStopperCoverRoleFamily(RoleFamily):
    DEFEND: Role
    STOPPER: Role
    COVER: Role

    def __init__(self, short_name, name, roles_by_duty):
        super().__init__(short_name, name, roles_by_duty)
        self.DEFEND = roles_by_duty[Duty.DEFEND]
        self.STOPPER = roles_by_duty[Duty.STOPPER]
        self.COVER = roles_by_duty[Duty.COVER]


class _RoleNamespace:
    GOALKEEPER: DefendRoleFamily
    SWEEPER_KEEPER: DefendSupportAttackRoleFamily
    BALL_PLAYING_DEFENDER: DefendStopperCoverRoleFamily
    CENTRAL_DEFENDER: DefendStopperCoverRoleFamily
    COMPLETE_WING_BACK: SupportAttackRoleFamily
    FULL_BACK: DefendSupportAttackRoleFamily
    INVERTED_FULL_BACK: DefendRoleFamily
    INVERTED_WING_BACK: DefendSupportAttackRoleFamily
    LIBERO: DefendSupportRoleFamily
    NO_NONSENSE_CENTRE_BACK: DefendStopperCoverRoleFamily
    NO_NONSENSE_FULL_BACK: DefendRoleFamily
    WIDE_CENTRE_BACK: DefendSupportAttackRoleFamily
    WING_BACK: DefendSupportAttackRoleFamily
    ADVANCED_PLAYMAKER: SupportAttackRoleFamily
    ANCHOR: DefendRoleFamily
    ATTACKING_MIDFIELDER: SupportAttackRoleFamily
    BALL_WINNING_MIDFIELDER: DefendSupportRoleFamily
    BOX_TO_BOX_MIDFIELDER: SupportRoleFamily
    CARRILERO: SupportRoleFamily
    CENTRAL_MIDFIELDER: DefendSupportAttackRoleFamily
    DEEP_LYING_PLAYMAKER: DefendSupportRoleFamily
    DEFENSIVE_MIDFIELDER: DefendSupportRoleFamily
    DEFENSIVE_WINGER: DefendSupportRoleFamily
    ENGANCHE: SupportRoleFamily
    HALF_BACK: DefendRoleFamily
    INSIDE_FORWARD: SupportAttackRoleFamily
    INVERTED_WINGER: SupportAttackRoleFamily
    MEZZALA: SupportAttackRoleFamily
    RAUMDEUTER: AttackRoleFamily
    REGISTA: SupportRoleFamily
    ROAMING_PLAYMAKER: SupportRoleFamily
    SEGUNDO_VOLANTE: SupportAttackRoleFamily
    SHADOW_STRIKER: AttackRoleFamily
    WIDE_MIDFIELDER: DefendSupportAttackRoleFamily
    WIDE_PLAYMAKER: SupportAttackRoleFamily
    WIDE_TARGET_FORWARD: SupportAttackRoleFamily
    WINGER: SupportAttackRoleFamily
    ADVANCED_FORWARD: AttackRoleFamily
    COMPLETE_FORWARD: SupportAttackRoleFamily
    DEEP_LYING_FORWARD: SupportAttackRoleFamily
    FALSE_NINE: SupportRoleFamily
    POACHER: AttackRoleFamily
    PRESSING_FORWARD: DefendSupportAttackRoleFamily
    TARGET_FORWARD: SupportAttackRoleFamily
    TREQUARTISTA: AttackRoleFamily


ROLE = _RoleNamespace()
ROLE_BY_CODE = {}
DUTY_CODE_SUFFIX = {Duty.DEFEND: "d", Duty.SUPPORT: "s", Duty.ATTACK: "a", Duty.STOPPER: "s", Duty.COVER: "c"}


def _register_role_family(namespace_name, family_type, short_name, full_name, *duties):
    roles_by_duty = {}
    for duty in duties:
        code = f"{short_name}{DUTY_CODE_SUFFIX[duty]}"
        role = Role(code=code, short_name=short_name, name=full_name, duty=duty)
        roles_by_duty[duty] = role
        ROLE_BY_CODE[code] = role

    setattr(ROLE, namespace_name, family_type(short_name, full_name, roles_by_duty))


_register_role_family("GOALKEEPER", DefendRoleFamily, "gk", "Goalkeeper", Duty.DEFEND)
_register_role_family("SWEEPER_KEEPER", DefendSupportAttackRoleFamily, "sk", "Sweeper Keeper", Duty.DEFEND, Duty.SUPPORT, Duty.ATTACK)
_register_role_family("BALL_PLAYING_DEFENDER", DefendStopperCoverRoleFamily, "bpd", "Ball-Playing Defender", Duty.DEFEND, Duty.STOPPER, Duty.COVER)
_register_role_family("CENTRAL_DEFENDER", DefendStopperCoverRoleFamily, "cd", "Central Defender", Duty.DEFEND, Duty.STOPPER, Duty.COVER)
_register_role_family("COMPLETE_WING_BACK", SupportAttackRoleFamily, "cwb", "Complete Wing-Back", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("FULL_BACK", DefendSupportAttackRoleFamily, "fb", "Full-Back", Duty.DEFEND, Duty.SUPPORT, Duty.ATTACK)
_register_role_family("INVERTED_FULL_BACK", DefendRoleFamily, "ifb", "Inverted Full-Back", Duty.DEFEND)
_register_role_family("INVERTED_WING_BACK", DefendSupportAttackRoleFamily, "iwb", "Inverted Wing-Back", Duty.DEFEND, Duty.SUPPORT, Duty.ATTACK)
_register_role_family("LIBERO", DefendSupportRoleFamily, "l", "Libero", Duty.DEFEND, Duty.SUPPORT)
_register_role_family(
    "NO_NONSENSE_CENTRE_BACK", DefendStopperCoverRoleFamily, "ncb", "No-Nonsense Centre-Back", Duty.DEFEND, Duty.STOPPER, Duty.COVER
)
_register_role_family("NO_NONSENSE_FULL_BACK", DefendRoleFamily, "nfb", "No-Nonsense Full-Back", Duty.DEFEND)
_register_role_family("WIDE_CENTRE_BACK", DefendSupportAttackRoleFamily, "wcb", "Wide Centre-Back", Duty.DEFEND, Duty.SUPPORT, Duty.ATTACK)
_register_role_family("WING_BACK", DefendSupportAttackRoleFamily, "wb", "Wing-Back", Duty.DEFEND, Duty.SUPPORT, Duty.ATTACK)
_register_role_family("ADVANCED_PLAYMAKER", SupportAttackRoleFamily, "ap", "Advanced Playmaker", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("ANCHOR", DefendRoleFamily, "a", "Anchor", Duty.DEFEND)
_register_role_family("ATTACKING_MIDFIELDER", SupportAttackRoleFamily, "am", "Attacking Midfielder", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("BALL_WINNING_MIDFIELDER", DefendSupportRoleFamily, "bwm", "Ball-Winning Midfielder", Duty.DEFEND, Duty.SUPPORT)
_register_role_family("BOX_TO_BOX_MIDFIELDER", SupportRoleFamily, "b2b", "Box-to-Box Midfielder", Duty.SUPPORT)
_register_role_family("CARRILERO", SupportRoleFamily, "car", "Carrilero", Duty.SUPPORT)
_register_role_family("CENTRAL_MIDFIELDER", DefendSupportAttackRoleFamily, "cm", "Central Midfielder", Duty.DEFEND, Duty.SUPPORT, Duty.ATTACK)
_register_role_family("DEEP_LYING_PLAYMAKER", DefendSupportRoleFamily, "dlp", "Deep-Lying Playmaker", Duty.DEFEND, Duty.SUPPORT)
_register_role_family("DEFENSIVE_MIDFIELDER", DefendSupportRoleFamily, "dm", "Defensive Midfielder", Duty.DEFEND, Duty.SUPPORT)
_register_role_family("DEFENSIVE_WINGER", DefendSupportRoleFamily, "dw", "Defensive Winger", Duty.DEFEND, Duty.SUPPORT)
_register_role_family("ENGANCHE", SupportRoleFamily, "eng", "Enganche", Duty.SUPPORT)
_register_role_family("HALF_BACK", DefendRoleFamily, "hb", "Half Back", Duty.DEFEND)
_register_role_family("INSIDE_FORWARD", SupportAttackRoleFamily, "if", "Inside Forward", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("INVERTED_WINGER", SupportAttackRoleFamily, "iw", "Inverted Winger", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("MEZZALA", SupportAttackRoleFamily, "mez", "Mezzala", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("RAUMDEUTER", AttackRoleFamily, "rau", "Raumdeuter", Duty.ATTACK)
_register_role_family("REGISTA", SupportRoleFamily, "rga", "Regista", Duty.SUPPORT)
_register_role_family("ROAMING_PLAYMAKER", SupportRoleFamily, "rp", "Roaming Playmaker", Duty.SUPPORT)
_register_role_family("SEGUNDO_VOLANTE", SupportAttackRoleFamily, "vol", "Segundo Volante", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("SHADOW_STRIKER", AttackRoleFamily, "ss", "Shadow Striker", Duty.ATTACK)
_register_role_family("WIDE_MIDFIELDER", DefendSupportAttackRoleFamily, "wm", "Wide Midfielder", Duty.DEFEND, Duty.SUPPORT, Duty.ATTACK)
_register_role_family("WIDE_PLAYMAKER", SupportAttackRoleFamily, "wp", "Wide Playmaker", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("WIDE_TARGET_FORWARD", SupportAttackRoleFamily, "wtf", "Wide Target Forward", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("WINGER", SupportAttackRoleFamily, "w", "Winger", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("ADVANCED_FORWARD", AttackRoleFamily, "af", "Advanced Forward", Duty.ATTACK)
_register_role_family("COMPLETE_FORWARD", SupportAttackRoleFamily, "cf", "Complete Forward", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("DEEP_LYING_FORWARD", SupportAttackRoleFamily, "dlf", "Deep-Lying Forward", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("FALSE_NINE", SupportRoleFamily, "f9", "False Nine", Duty.SUPPORT)
_register_role_family("POACHER", AttackRoleFamily, "p", "Poacher", Duty.ATTACK)
_register_role_family("PRESSING_FORWARD", DefendSupportAttackRoleFamily, "pf", "Pressing Forward", Duty.DEFEND, Duty.SUPPORT, Duty.ATTACK)
_register_role_family("TARGET_FORWARD", SupportAttackRoleFamily, "tf", "Target Forward", Duty.SUPPORT, Duty.ATTACK)
_register_role_family("TREQUARTISTA", AttackRoleFamily, "tre", "Trequartista", Duty.ATTACK)


def parse_role(role):
    if isinstance(role, Role):
        return role
    try:
        return ROLE_BY_CODE[role]
    except KeyError as exc:
        raise ValueError(f"Unknown FM role code: {role!r}") from exc
