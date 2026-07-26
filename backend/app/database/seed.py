import argparse
import os
import sqlite3
import json
from pathlib import Path
from backend.app.database.connection import get_connection, DATABASE_PATH

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def reset_database():
    """Drops the database file to start fresh."""
    if os.path.exists(DATABASE_PATH):
        print(f"Removing database at {DATABASE_PATH}...")
        os.remove(DATABASE_PATH)
    else:
        print("No existing database found to reset.")

def initialize_schema(conn: sqlite3.Connection):
    """Executes the schema.sql file."""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
    
    with open(SCHEMA_PATH, "r") as f:
        schema_script = f.read()
    
    print("Executing schema...")
    conn.executescript(schema_script)

def seed_trusted_organizations(conn: sqlite3.Connection):
    """Seeds default trusted organizations and their official numbers."""
    orgs = [
        ("org_001", "State Bank of India", "BANK")
    ]
    numbers = [
        ("1800112211", "org_001"),
        ("18004253800", "org_001")
    ]
    
    conn.executemany("""
        INSERT OR IGNORE INTO trusted_organizations (id, name, type)
        VALUES (?, ?, ?)
    """, orgs)
    
    conn.executemany("""
        INSERT OR IGNORE INTO official_numbers (number, organization_id)
        VALUES (?, ?)
    """, numbers)
    print("Seeded trusted organizations.")

def seed_community_patterns(conn: sqlite3.Connection):
    """Seeds synthetic community fraud patterns."""
    patterns = [
        {
            "id": "pattern_001",
            "tactics": json.dumps(["AUTHORITY", "URGENCY", "ISOLATION"]),
            "organization_type": "BANK",
            "scenario": "BANK_KYC",
            "requested_action": "SECRET_CODE",
            "threat_type": "ACCOUNT_FREEZE",
            "channel_switch": "NONE",
            "language_family": "HI_EN"
        },
        {
            "id": "pattern_002",
            "tactics": json.dumps(["AUTHORITY", "THREAT", "ISOLATION"]),
            "organization_type": "LAW_ENFORCEMENT",
            "scenario": "DIGITAL_ARREST",
            "requested_action": "MONEY_TRANSFER",
            "threat_type": "IMMEDIATE_ARREST",
            "channel_switch": "VIDEO_CALL",
            "language_family": "HI_EN"
        },
        {
            "id": "pattern_003",
            "tactics": json.dumps(["URGENCY", "CONFUSION"]),
            "organization_type": "PAYMENT_APP",
            "scenario": "UPI_REFUND",
            "requested_action": "PIN_ENTRY",
            "threat_type": "LOSS_OF_FUNDS",
            "channel_switch": "NONE",
            "language_family": "HI"
        },
        {
            "id": "pattern_004",
            "tactics": json.dumps(["HELPFUL", "TECHNICAL_JARGON"]),
            "organization_type": "TECH_SUPPORT",
            "scenario": "REMOTE_SUPPORT",
            "requested_action": "APP_INSTALL",
            "threat_type": "DEVICE_COMPROMISE",
            "channel_switch": "SCREEN_SHARE",
            "language_family": "EN"
        },
        {
            "id": "pattern_005",
            "tactics": json.dumps(["AUTHORITY", "URGENCY", "SURPRISE"]),
            "organization_type": "CUSTOMS",
            "scenario": "COURIER_SEIZURE",
            "requested_action": "MONEY_TRANSFER",
            "threat_type": "LEGAL_ACTION",
            "channel_switch": "NONE",
            "language_family": "HI_EN"
        },
        {
            "id": "pattern_006",
            "tactics": json.dumps(["GREED", "URGENCY", "SOCIAL_PROOF"]),
            "organization_type": "INVESTMENT_FIRM",
            "scenario": "CRYPTO_INVESTMENT",
            "requested_action": "MONEY_TRANSFER",
            "threat_type": "MISSED_OPPORTUNITY",
            "channel_switch": "TELEGRAM",
            "language_family": "HI_EN"
        },
        {
            "id": "pattern_007",
            "tactics": json.dumps(["GREED", "TRUST_BUILDING", "SUNKEN_COST"]),
            "organization_type": "E_COMMERCE",
            "scenario": "PART_TIME_JOB",
            "requested_action": "MONEY_TRANSFER",
            "threat_type": "LOSS_OF_FUNDS",
            "channel_switch": "WHATSAPP",
            "language_family": "HI_EN"
        },
        {
            "id": "pattern_008",
            "tactics": json.dumps(["HELPFUL", "URGENCY", "AUTHORITY"]),
            "organization_type": "BANK",
            "scenario": "LOAN_APPROVAL",
            "requested_action": "MONEY_TRANSFER",
            "threat_type": "MISSED_OPPORTUNITY",
            "channel_switch": "NONE",
            "language_family": "HI"
        },
        {
            "id": "pattern_009",
            "tactics": json.dumps(["SURPRISE", "GREED", "URGENCY"]),
            "organization_type": "LOTTERY",
            "scenario": "PRIZE_WINNER",
            "requested_action": "MONEY_TRANSFER",
            "threat_type": "MISSED_OPPORTUNITY",
            "channel_switch": "NONE",
            "language_family": "HI"
        },
        {
            "id": "pattern_010",
            "tactics": json.dumps(["THREAT", "URGENCY", "AUTHORITY"]),
            "organization_type": "TELECOM",
            "scenario": "SIM_BLOCK",
            "requested_action": "APP_INSTALL",
            "threat_type": "SERVICE_DISCONNECTION",
            "channel_switch": "NONE",
            "language_family": "HI_EN"
        },
        {
            "id": "pattern_011",
            "tactics": json.dumps(["PANIC", "URGENCY", "EMOTIONAL_MANIPULATION"]),
            "organization_type": "HOSPITAL",
            "scenario": "RELATIVE_EMERGENCY",
            "requested_action": "MONEY_TRANSFER",
            "threat_type": "MEDICAL_EMERGENCY",
            "channel_switch": "NONE",
            "language_family": "HI_EN"
        },
        {
            "id": "pattern_012",
            "tactics": json.dumps(["HELPFUL", "CONFUSION", "URGENCY"]),
            "organization_type": "AIRLINE",
            "scenario": "TICKET_REFUND",
            "requested_action": "APP_INSTALL",
            "threat_type": "LOSS_OF_FUNDS",
            "channel_switch": "SCREEN_SHARE",
            "language_family": "HI_EN"
        },
        {
            "id": "pattern_013",
            "tactics": json.dumps(["THREAT", "URGENCY", "AUTHORITY"]),
            "organization_type": "ELECTRICITY_BOARD",
            "scenario": "POWER_DISCONNECTION",
            "requested_action": "SECRET_CODE",
            "threat_type": "SERVICE_DISCONNECTION",
            "channel_switch": "WHATSAPP",
            "language_family": "HI"
        },
        {
            "id": "pattern_014",
            "tactics": json.dumps(["URGENCY", "HELPFUL", "CONFUSION"]),
            "organization_type": "POST_OFFICE",
            "scenario": "DELIVERY_FAILURE",
            "requested_action": "CLICK_LINK",
            "threat_type": "PACKAGE_RETURN",
            "channel_switch": "SMS",
            "language_family": "EN"
        },
        {
            "id": "pattern_015",
            "tactics": json.dumps(["URGENCY", "GREED", "HELPFUL"]),
            "organization_type": "CREDIT_CARD",
            "scenario": "REWARD_POINTS_EXPIRY",
            "requested_action": "SECRET_CODE",
            "threat_type": "LOSS_OF_FUNDS",
            "channel_switch": "NONE",
            "language_family": "HI_EN"
        }
    ]
    
    for p in patterns:
        conn.execute("""
            INSERT OR IGNORE INTO community_patterns 
            (id, schema_version, tactics, organization_type, scenario, requested_action, threat_type, channel_switch, language_family)
            VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
        """, (p["id"], p["tactics"], p["organization_type"], p["scenario"], p["requested_action"], p["threat_type"], p["channel_switch"], p["language_family"]))
        
    print("Seeded community patterns.")

def main():
    parser = argparse.ArgumentParser(description="Seed the SurakshaCall database.")
    parser.add_argument("--reset", action="store_true", help="Reset the database before seeding.")
    args = parser.parse_args()

    if args.reset:
        reset_database()

    # get_connection ensures the directory exists and foreign keys are enabled
    conn = get_connection()
    try:
        with conn: # Use transaction
            initialize_schema(conn)
            seed_trusted_organizations(conn)
            seed_community_patterns(conn)
        print("Database seeding completed successfully.")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()