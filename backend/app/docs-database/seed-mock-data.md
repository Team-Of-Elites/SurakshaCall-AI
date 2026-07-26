# Mock Community Patterns (Seed Data)

This document outlines the 15 synthetic fraud patterns seeded into the SQLite database for testing the **Community Intelligence** and **Matcher** components of SurakshaCall AI.

These patterns are stored in the `community_patterns` table. They simulate structural metadata of past scams without containing any Personally Identifiable Information (PII) or raw audio.

## Seed Patterns

| ID | Scenario | Organization Type | Requested Action | Threat Type | Channel Switch | Tactics | Language Family |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **pattern_001** | `BANK_KYC` | `BANK` | `SECRET_CODE` | `ACCOUNT_FREEZE` | `NONE` | Authority, Urgency, Isolation | `HI_EN` |
| **pattern_002** | `DIGITAL_ARREST` | `LAW_ENFORCEMENT` | `MONEY_TRANSFER` | `IMMEDIATE_ARREST` | `VIDEO_CALL` | Authority, Threat, Isolation | `HI_EN` |
| **pattern_003** | `UPI_REFUND` | `PAYMENT_APP` | `PIN_ENTRY` | `LOSS_OF_FUNDS` | `NONE` | Urgency, Confusion | `HI` |
| **pattern_004** | `REMOTE_SUPPORT` | `TECH_SUPPORT` | `APP_INSTALL` | `DEVICE_COMPROMISE` | `SCREEN_SHARE` | Helpful, Technical Jargon | `EN` |
| **pattern_005** | `COURIER_SEIZURE` | `CUSTOMS` | `MONEY_TRANSFER` | `LEGAL_ACTION` | `NONE` | Authority, Urgency, Surprise | `HI_EN` |
| **pattern_006** | `CRYPTO_INVESTMENT` | `INVESTMENT_FIRM` | `MONEY_TRANSFER` | `MISSED_OPPORTUNITY` | `TELEGRAM` | Greed, Urgency, Social Proof | `HI_EN` |
| **pattern_007** | `PART_TIME_JOB` | `E_COMMERCE` | `MONEY_TRANSFER` | `LOSS_OF_FUNDS` | `WHATSAPP` | Greed, Trust Building, Sunken Cost | `HI_EN` |
| **pattern_008** | `LOAN_APPROVAL` | `BANK` | `MONEY_TRANSFER` | `MISSED_OPPORTUNITY` | `NONE` | Helpful, Urgency, Authority | `HI` |
| **pattern_009** | `PRIZE_WINNER` | `LOTTERY` | `MONEY_TRANSFER` | `MISSED_OPPORTUNITY` | `NONE` | Surprise, Greed, Urgency | `HI` |
| **pattern_010** | `SIM_BLOCK` | `TELECOM` | `APP_INSTALL` | `SERVICE_DISCONNECTION` | `NONE` | Threat, Urgency, Authority | `HI_EN` |
| **pattern_011** | `RELATIVE_EMERGENCY` | `HOSPITAL` | `MONEY_TRANSFER` | `MEDICAL_EMERGENCY` | `NONE` | Panic, Urgency, Emotional Manipulation | `HI_EN` |
| **pattern_012** | `TICKET_REFUND` | `AIRLINE` | `APP_INSTALL` | `LOSS_OF_FUNDS` | `SCREEN_SHARE` | Helpful, Confusion, Urgency | `HI_EN` |
| **pattern_013** | `POWER_DISCONNECTION` | `ELECTRICITY_BOARD` | `SECRET_CODE` | `SERVICE_DISCONNECTION` | `WHATSAPP` | Threat, Urgency, Authority | `HI` |
| **pattern_014** | `DELIVERY_FAILURE` | `POST_OFFICE` | `CLICK_LINK` | `PACKAGE_RETURN` | `SMS` | Urgency, Helpful, Confusion | `EN` |
| **pattern_015** | `REWARD_POINTS_EXPIRY` | `CREDIT_CARD` | `SECRET_CODE` | `LOSS_OF_FUNDS` | `NONE` | Urgency, Greed, Helpful | `HI_EN` |

---

## Trusted Directory Seed Data

The following mock organizations and official numbers are also seeded into the `trusted_organizations` and `official_numbers` tables to test the Identity Verification system.

### Organizations
- **org_001**: State Bank of India (Type: `BANK`)

### Official Numbers (Associated with org_001)
- `1800112211`
- `18004253800`

---
> **Note:** Run `python -m backend.app.database.seed --reset` at any time to purge the SQLite database and cleanly re-insert all records documented above.
