"""
SurakshaCall AI — Phone Number Normalizer
Owner: Lakshay
Task: L-09
"""
import re
import phonenumbers
from phonenumbers import geocoder, carrier, number_type, PhoneNumberType
from dataclasses import dataclass
from typing import Optional


@dataclass
class PhoneInfo:
    raw_input: str
    e164: Optional[str]
    is_valid: bool
    is_mobile: bool
    is_voip: bool
    is_trai_160: bool        # TRAI commercial/service range
    country: str
    region: str
    carrier_name: str
    source: str              # "user_provided" or "auto"


def normalize_phone(raw: str, source: str = "user_provided") -> PhoneInfo:
    """
    Parse and normalize an Indian phone number.
    Returns metadata for identity verification.
    """
    try:
        parsed = phonenumbers.parse(raw, "IN")
        valid = phonenumbers.is_valid_number(parsed)
        e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164) if valid else None
        ntype = number_type(parsed)
        is_mobile = ntype in (PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE)
        is_voip = ntype == PhoneNumberType.VOIP
        region = geocoder.description_for_number(parsed, "en")
        carr = carrier.name_for_number(parsed, "en")

        clean_num = re.sub(r"^\+91|^91|^0", "", raw.replace(" ", "").replace("-", ""))
        is_trai_160 = clean_num.startswith("160")

        return PhoneInfo(
            raw_input=raw,
            e164=e164,
            is_valid=valid,
            is_mobile=is_mobile,
            is_voip=is_voip,
            is_trai_160=is_trai_160,
            country="India" if valid else "Unknown",
            region=region or "Unknown",
            carrier_name=carr or "Unknown",
            source=source,
        )
    except Exception:
        return PhoneInfo(
            raw_input=raw,
            e164=None,
            is_valid=False,
            is_mobile=False,
            is_voip=False,
            is_trai_160=False,
            country="Unknown",
            region="Unknown",
            carrier_name="Unknown",
            source=source,
        )
