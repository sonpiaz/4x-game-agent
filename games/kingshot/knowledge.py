"""
Kingshot Game Knowledge Base
Comprehensive data compiled from extensive research of kingshotguide.org,
kingshotmastery.com, kingshothandbook.com, kingshot.fandom.com, and
community resources. Used by the bot's strategic brain for long-term decisions.

Last updated: 2026-03-15
"""

# =============================================================================
# 1. TOWN CENTER (TC) PREREQUISITES — TC1 to TC30 + TrueGold
# =============================================================================

TC_PREREQUISITES = {
    # Level: {"prereqs": {...}, "resources": {...}, "time": str, "power": int}
    1: {
        "prereqs": {},
        "resources": {},
        "time": "0s",
        "power": 2000,
    },
    2: {
        "prereqs": {"Sawmill": 1},
        "resources": {"wood": 180},
        "time": "6s",
        "power": 3800,
    },
    3: {
        "prereqs": {"House 1": 2},
        "resources": {"wood": 805},
        "time": "1m",
        "power": 6500,
    },
    4: {
        "prereqs": {"Quarry": 3},
        "resources": {"wood": 1800, "coal": 360},
        "time": "3m",
        "power": 10100,
    },
    5: {
        "prereqs": {"Hero Hall": 1, "House 3": 3},
        "resources": {"wood": 7600, "coal": 1500},
        "time": "10m",
        "power": 15500,
    },
    6: {
        "prereqs": {"Iron Mine": 5},
        "resources": {"wood": 19000, "coal": 3800, "iron": 960},
        "time": "30m",
        "power": 23600,
    },
    7: {
        "prereqs": {"Mill": 6},
        "resources": {"wood": 69000, "coal": 13000, "iron": 3400},
        "time": "1h",
        "power": 35300,
    },
    8: {
        "prereqs": {"Barracks": 7},
        "resources": {"wood": 120000, "coal": 25000, "iron": 6300},
        "time": "2h 30m",
        "power": 47000,
    },
    9: {
        "prereqs": {"Embassy": 8, "Infirmary": 1},
        "resources": {"wood": 260000, "coal": 52000, "iron": 13000},
        "time": "4h 30m",
        "power": 58700,
    },
    10: {
        "prereqs": {"Range": 9, "Academy": 1},
        "resources": {"wood": 460000, "coal": 92000, "iron": 23000},
        "time": "6h",
        "power": 75700,
    },
    11: {
        "prereqs": {"Embassy": 10, "Stable": 10},
        "resources": {"bread": 1_300_000, "wood": 1_300_000, "coal": 20000, "iron": 65000},
        "time": "7h 30m",
        "power": 92700,
    },
    12: {
        "prereqs": {"Embassy": 11, "Command Center": 1},
        "resources": {"bread": 1_600_000, "wood": 1_600_000, "coal": 330000, "iron": 84000},
        "time": "9h",
        "power": 109700,
    },
    13: {
        "prereqs": {"Embassy": 12, "Barracks": 12},
        "resources": {"bread": 2_300_000, "wood": 2_300_000, "coal": 470000, "iron": 110000},
        "time": "11h",
        "power": 138400,
    },
    14: {
        "prereqs": {"Embassy": 13, "Range": 13},
        "resources": {"bread": 3_100_000, "wood": 3_100_000, "coal": 630000, "iron": 150000},
        "time": "14h",
        "power": 167100,
    },
    15: {
        "prereqs": {"Embassy": 14, "Stable": 14},
        "resources": {"bread": 4_600_000, "wood": 4_600_000, "coal": 930000, "iron": 230000},
        "time": "18h",
        "power": 195800,
    },
    16: {
        "prereqs": {"Embassy": 15, "Academy": 15},
        "resources": {"bread": 5_900_000, "wood": 5_900_000, "coal": 1_100_000, "iron": 290000},
        "time": "1d 6h 28m",
        "power": 236200,
    },
    17: {
        "prereqs": {"Embassy": 16, "Barracks": 16},
        "resources": {"bread": 9_300_000, "wood": 9_300_000, "coal": 1_800_000, "iron": 480000},
        "time": "1d 12h 34m",
        "power": 276600,
    },
    18: {
        "prereqs": {"Embassy": 17, "Range": 17},
        "resources": {"bread": 12_000_000, "wood": 12_000_000, "coal": 2_500_000, "iron": 620000},
        "time": "1d 19h 53m",
        "power": 317000,
    },
    19: {
        "prereqs": {"Embassy": 18, "Stable": 18},
        "resources": {"bread": 15_000_000, "wood": 15_000_000, "coal": 3_100_000, "iron": 780000},
        "time": "2d 17h 50m",
        "power": 374400,
    },
    20: {
        "prereqs": {"Embassy": 19, "Academy": 19},
        "resources": {"bread": 21_000_000, "wood": 21_000_000, "coal": 4_300_000, "iron": 1_000_000},
        "time": "3d 10h 18m",
        "power": 431800,
    },
    21: {
        "prereqs": {"Embassy": 20, "Barracks": 20},
        "resources": {"bread": 27_000_000, "wood": 27_000_000, "coal": 5_400_000, "iron": 1_300_000},
        "time": "4d 10h 59m",
        "power": 489200,
    },
    22: {
        "prereqs": {"Embassy": 21, "Range": 21},
        "resources": {"bread": 36_000_000, "wood": 36_000_000, "coal": 7_200_000, "iron": 1_800_000},
        "time": "6d 16h 29m",
        "power": 575300,
        "note": "Unlocks Governor Gear & 5th March Queue at TC22",
    },
    23: {
        "prereqs": {"Embassy": 22, "Stable": 22},
        "resources": {"bread": 44_000_000, "wood": 44_000_000, "coal": 8_900_000, "iron": 2_200_000},
        "time": "9d 8h 40m",
        "power": 661400,
    },
    24: {
        "prereqs": {"Embassy": 23, "Academy": 23},
        "resources": {"bread": 60_000_000, "wood": 60_000_000, "coal": 12_000_000, "iron": 3_000_000},
        "time": "13d 2h 33m",
        "power": 747500,
    },
    25: {
        "prereqs": {"Embassy": 24, "Barracks": 24},
        "resources": {"bread": 81_000_000, "wood": 81_000_000, "coal": 16_000_000, "iron": 4_000_000},
        "time": "18d 8h 22m",
        "power": 833600,
        "note": "Unlocks Governor Charms at TC25",
    },
    26: {
        "prereqs": {"Embassy": 25, "Range": 25},
        "resources": {"bread": 100_000_000, "wood": 100_000_000, "coal": 21_000_000, "iron": 5_200_000},
        "time": "21d 2h 26m",
        "power": 960100,
    },
    27: {
        "prereqs": {"Embassy": 26, "Stable": 26},
        "resources": {"bread": 140_000_000, "wood": 140_000_000, "coal": 24_000_000, "iron": 7_400_000},
        "time": "25d 7h 43m",
        "power": 1086600,
    },
    28: {
        "prereqs": {"Embassy": 27, "Academy": 27},
        "resources": {"bread": 190_000_000, "wood": 190_000_000, "coal": 39_000_000, "iron": 9_900_000},
        "time": "29d 2h 52m",
        "power": 1213100,
    },
    29: {
        "prereqs": {"Embassy": 28, "Barracks": 28},
        "resources": {"bread": 240_000_000, "wood": 240_000_000, "coal": 49_000_000, "iron": 12_000_000},
        "time": "33d 11h 42m",
        "power": 1339600,
    },
    30: {
        "prereqs": {"Embassy": 29, "Range": 29},
        "resources": {"bread": 300_000_000, "wood": 300_000_000, "coal": 60_000_000, "iron": 15_000_000},
        "time": "40d 4h 27m",
        "power": 1523500,
        "note": "Unlocks T10 troops, TrueGold progression begins",
    },
}

# TrueGold (TG) stages after TC30
# Each TG level has a base + 4 sub-stages
TC_TRUEGOLD_STAGES = {
    "30_substages": {
        "stages": 4,  # 30-1 through 30-4
        "resources_per_stage": {"bread": 67_000_000, "wood": 67_000_000, "coal": 13_000_000, "iron": 3_300_000, "truegold": 132},
        "time_per_stage": "7d",
    },
    "TG1": {
        "base": {"bread": 67_000_000, "wood": 67_000_000, "coal": 13_000_000, "iron": 3_300_000, "truegold": 132, "time": "7d"},
        "substages": 4,
        "per_substage": {"bread": 72_000_000, "wood": 72_000_000, "coal": 14_000_000, "iron": 3_600_000, "truegold": 158, "time": "9d"},
        "total_truegold": 660,  # 132 base + 158*4 substages = ~792 total
    },
    "TG2": {
        "base": {"bread": 72_000_000, "wood": 72_000_000, "coal": 14_000_000, "iron": 3_600_000, "truegold": 158, "time": "9d"},
        "substages": 4,
        "per_substage": {"bread": 79_000_000, "wood": 79_000_000, "coal": 15_000_000, "iron": 3_900_000, "truegold": 238, "time": "11d"},
    },
    "TG3": {
        "base": {"bread": 79_000_000, "wood": 79_000_000, "coal": 15_000_000, "iron": 3_900_000, "truegold": 238, "time": "11d"},
        "substages": 4,
        "per_substage": {"bread": 82_000_000, "wood": 82_000_000, "coal": 16_000_000, "iron": 4_100_000, "truegold": 280, "time": "12d"},
    },
    "TG4": {
        "base": {"bread": 82_000_000, "wood": 82_000_000, "coal": 16_000_000, "iron": 4_100_000, "truegold": 280, "time": "12d"},
        "substages": 4,
        "per_substage": {"bread": 84_000_000, "wood": 84_000_000, "coal": 16_000_000, "iron": 4_200_000, "truegold": 335, "time": "14d"},
    },
    "TG5": {
        "base": {"bread": 84_000_000, "wood": 84_000_000, "coal": 16_000_000, "iron": 4_200_000, "truegold": 335, "time": "14d"},
        "substages": 4,
        "per_substage": {"bread": 84_000_000, "wood": 84_000_000, "coal": 16_000_000, "iron": 4_200_000, "truegold": 335, "time": "14d"},
    },
}


# =============================================================================
# 2. RESEARCH TREE
# =============================================================================

RESEARCH_TREE = {
    "overview": {
        "building": "Academy",
        "categories": ["Growth", "Economy", "Battle"],
        "total_time_growth": "883 days",
        "total_time_economy": "166 days",
        "total_time_battle": "3,911 days",
    },

    "growth": {
        "priority_order": [
            "Command Tactics",       # Unlocks 3 additional march queues
            "Tooling Up",            # +27.80% construction speed when maxed
            "Tool Enhancement",      # +27.80% research speed when maxed
        ],
        "skip": ["Camp Expansion"],  # Only increases batch capacity, not speed
        "notes": "Growth tree is the foundation. Max Tooling Up + Tool Enhancement first "
                 "for compounding speed benefits.",
    },

    "economy": {
        "priority_order": [
            "Gathering Speed (all types)",
            "March Load Capacity",
        ],
        "skip": [
            "Mill Output",
            "Iron Mine Output",
            "Sawmill Output",
            "Quarry Output",
        ],
        "notes": "Gathering gives 10-100x more resources than production buildings. "
                 "Max all gathering research, skip building output entirely. "
                 "Economy tree completes in 166 days — relatively quick.",
    },

    "battle": {
        "priority_order": [
            "Regimental Expansion",       # Increases rally troop count
            "Assault Techniques",         # Increases Lethality for all troops
            "Survival Techniques",        # Increases Health for all troops
            "Lethality (Archers/Cavalry)",
            "Health (Infantry)",
            "Special Defensive Training",
            "Weapons Prep",
        ],
        "notes": "Battle tree is by far the longest (3,911 days). "
                 "Lethality and Health are the key stats. "
                 "Focus on Assault + Survival Techniques for universal troop buffs.",
    },

    "war_academy": {
        "unlock_day": 220,
        "unlock_requirements": "TC30+, Server 220+ days old",
        "max_level": "TG5",
        "total_upgrade_cost_truegold": 1135,
        "research_rows": {
            "row1_deployment": "+3,000 squad deployment capacity (3 nodes, Lv5 each)",
            "row2_stats": "Health/Lethality for Infantry, Archers, Cavalry",
            "row3_rally": "+33,500 rally capacity per node maxed (3 nodes, Lv12 each; +100,500 total)",
            "row4_attack_defense": "Attack/Defense stats per troop type",
            "row5_t11_unlock": "Unlock T11 troops (requires Row 4 Attack+Defense at Lv12)",
            "row6_specialization": "Healing time reduction, Training cost reduction",
        },
        "t11_unlock_cost_per_type": {"truegold_dust": 2236, "gold": 1_000_000},
        "t11_total_cost_all": {"truegold_dust": 82122, "gold": 24_120_000, "truegold": 63171},
        "t11_vs_t10_cost_increase": "~150% more resources (2.5x)",
    },
}


# =============================================================================
# 3. TROOP SYSTEM
# =============================================================================

TROOP_TIERS = {
    # Tier: {unlock, training_sec_per_unit, batch_capacity, notes}
    # Training times are BASE values (before speed buffs)
    "T1": {"unlock": "Barracks Lv1", "base_sec_per_unit": 3.85, "batch_capacity": 17, "phase": "early"},
    "T2": {"unlock": "Barracks Lv4", "base_sec_per_unit": 5.5, "batch_capacity": 25, "phase": "early"},
    "T3": {"unlock": "Barracks Lv7", "base_sec_per_unit": 8.0, "batch_capacity": 35, "phase": "early"},
    "T4": {"unlock": "Barracks Lv11", "base_sec_per_unit": 11.0, "batch_capacity": 55, "phase": "early"},
    "T5": {"unlock": "Barracks Lv13", "base_sec_per_unit": 15.0, "batch_capacity": 70, "phase": "mid",
            "note": "Promotion system unlocks at TC13 / building Lv13"},
    "T6": {"unlock": "Barracks Lv16", "base_sec_per_unit": 20.0, "batch_capacity": 90, "phase": "mid"},
    "T7": {"unlock": "Barracks Lv19", "base_sec_per_unit": 26.0, "batch_capacity": 115, "phase": "mid",
            "note": "Advanced troop skills unlock (Cavalry bypass, Archer double-attack)"},
    "T8": {"unlock": "Barracks Lv22", "base_sec_per_unit": 33.0, "batch_capacity": 145, "phase": "late"},
    "T9": {"unlock": "Barracks Lv25", "base_sec_per_unit": 41.0, "batch_capacity": 175, "phase": "late"},
    "T10": {"unlock": "Barracks Lv30 (TC30)", "base_sec_per_unit": 48.78, "batch_capacity": 209, "phase": "endgame",
             "note": "Current endgame standard. T9->T10 promotion is most efficient for events."},
    "T11": {"unlock": "War Academy TG5 (Day 220+)", "base_sec_per_unit": 72.0, "batch_capacity": 250, "phase": "endgame",
             "note": "~150% costlier than T10. F2P should NOT pursue T11 — focus on T10 stat boosts."},
}

TROOP_EVENT_POINTS = {
    # Points awarded per troop trained/promoted during events
    # Event:   {T1, T2, T3, T4, T5, T6, T7, T8, T9, T10}
    "HoG":               [90, 120, 180, 265, 385, 595, 830, 1130, 1485, 1960],
    "Strongest_Governor": [1, 2, 3, 5, 7, 11, 16, 23, 30, 39],
    "KoP":               [3, 4, 5, 8, 12, 18, 25, 35, 45, 60],
    "Alliance_Brawl":    [1, 1, 2, 3, 4, 7, 10, 14, 18, 24],
}

TROOP_TYPES = {
    "infantry": {
        "role": "Frontline Tank",
        "stat_focus": "Health, Defense",
        "position": "Front line",
        "advantage": "Bonus DMG vs Cavalry",
        "level_19_skill": "Increased DEF vs Cavalry",
    },
    "cavalry": {
        "role": "Offensive Strike / Flanker",
        "stat_focus": "Lethality",
        "position": "Midline",
        "advantage": "Bonus DMG vs Archers",
        "level_19_skill": "20% chance to bypass Infantry and snipe Archers",
    },
    "archers": {
        "role": "Primary DPS",
        "stat_focus": "Lethality, Attack",
        "position": "Backline",
        "advantage": "Bonus DMG vs Infantry",
        "level_19_skill": "Chance to attack twice",
    },
    "siege": {
        "role": "Structure Damage",
        "stat_focus": "Attack",
        "position": "Support",
        "note": "Used for city attacks, not standard PvP",
    },
}

TROOP_FORMATIONS = {
    "standard_pvp": {"infantry": 50, "cavalry": 20, "archers": 30, "note": "5:2:3 ratio — balanced survival + damage"},
    "rally_attack": {"infantry": 45, "cavalry": 25, "archers": 30, "note": "Balanced pressure for rallies"},
    "defense_garrison": {"infantry": 60, "cavalry": 15, "archers": 25, "note": "Maximum survival"},
    "pve_bear_hunt": {"infantry": 10, "cavalry": 10, "archers": 80, "note": "Pure DPS, no return fire in PvE"},
    "rally_pve": {"infantry": 10, "cavalry": 10, "archers": 80, "note": "Same as bear hunt for beast rallies"},
}

TROOP_PROMOTION = {
    "best_strategy": "T9 -> T10 promotion during events (highest points-per-second across ALL events)",
    "preparation": "Train T9 during non-event periods. Promote to T10 during HoG/SG Troop Day.",
    "t9_to_t10_promotion_time": "~6.73 sec/troop (batch of 100 = 11 seconds)",
    "hog_points_per_second": 70.58,  # T9->T10 promotion PPS during HoG
    "sg_points_per_second": 1.34,
    "kop_points_per_second": 2.23,
    "key_insight": "Promotion always beats direct training because prep time occurs before the event.",
}

TROOP_CASUALTY_RATES = {
    # Location: {lightly_injured%, hospitalized%, permanent_loss%}
    "player_city_attack": {"lightly_injured": 55, "hospitalized": 10, "permanent_loss": 35},
    "level_4_outpost": {"lightly_injured": 60, "hospitalized": 30, "permanent_loss": 10},
    "sanctuary_fort": {"lightly_injured": 70, "hospitalized": 30, "permanent_loss": 0},
    "beast_hunt": {"lightly_injured": 98, "hospitalized": 2, "permanent_loss": 0},
}


# =============================================================================
# 4. HERO SYSTEM
# =============================================================================

HERO_GENERATIONS = {
    # Generation: {day_unlocked, stat_multipliers, heroes}
    1: {
        "server_day": 10,
        "attack_defense_multiplier": "Base",
        "heroes": {
            "Jabel": {"type": "Cavalry", "rarity": "Mythic", "role": "Core defensive foundation",
                       "key_skill": "Rally Flag — chance to reduce damage taken",
                       "f2p": True, "tier": "S+"},
            "Amadeus": {"type": "Infantry", "rarity": "Mythic", "role": "Best infantry hero (S-tier in Gen5+)",
                         "key_skill": "Offensive widget + Lethality Up + Attack Up",
                         "f2p": False, "tier": "S+", "note": "VIP 7+, HoG Top 10 reward"},
            "Helga": {"type": "Infantry", "rarity": "Mythic", "role": "Support infantry",
                       "f2p": False, "tier": "A"},
            "Saul": {"type": "Archer", "rarity": "Mythic", "role": "Archer DPS + construction buffs",
                      "key_skill": "Stun + attack speed boost",
                      "f2p": True, "tier": "S+"},
        },
    },
    2: {
        "server_day": 50,
        "attack_defense_multiplier": "240% AD, 60% W",
        "heroes": {
            "Zoe": {"type": "Infantry", "rarity": "Mythic", "role": "Ultimate F2P infantry tank",
                     "key_skill": "Last Stand — 40% HP self-heal, incredibly durable",
                     "f2p": True, "tier": "A", "note": "Hero Roulette accessible"},
            "Hilde": {"type": "Cavalry", "rarity": "Mythic", "role": "Top cavalry rally leader",
                       "key_skill": "Elixir of Strength — strongest offensive skill in game",
                       "f2p": False, "tier": "S"},
            "Marlin": {"type": "Archer", "rarity": "Mythic", "role": "AoE DPS with crowd control",
                        "f2p": True, "tier": "S+"},
        },
    },
    3: {
        "server_day": 120,
        "attack_defense_multiplier": "290% AD, 70% W",
        "heroes": {
            "Eric": {"type": "Infantry", "rarity": "Mythic", "role": "Mid-game infantry",
                      "f2p": True, "tier": "A"},
            "Petra": {"type": "Cavalry", "rarity": "Mythic", "role": "Highest raw damage output in game",
                       "key_skill": "Tarot card damage/debuffs",
                       "f2p": True, "tier": "S+", "note": "Core rally hero"},
            "Jaeger": {"type": "Archer", "rarity": "Mythic", "role": "Archer DPS",
                        "f2p": True, "tier": "S+"},
        },
    },
    4: {
        "server_day": 200,
        "attack_defense_multiplier": "370% AD, 92.5% W",
        "heroes": {
            "Alcar": {"type": "Infantry", "rarity": "Mythic", "role": "Late-game infantry",
                       "f2p": True, "tier": "S+"},
            "Margot": {"type": "Cavalry", "rarity": "Mythic", "role": "Cavalry specialist",
                        "f2p": True, "tier": "S+"},
            "Rosa": {"type": "Archer", "rarity": "Mythic", "role": "Best archer support, team-wide buffs",
                      "f2p": True, "tier": "S+"},
        },
    },
    5: {
        "server_day": 270,
        "attack_defense_multiplier": "444% AD, 111% W",
        "heroes": {
            "Long Fei": {"type": "Infantry", "rarity": "Mythic", "role": "Current top infantry",
                          "f2p": True, "tier": "S+"},
            "Thrud": {"type": "Cavalry", "rarity": "Mythic", "role": "Current top cavalry",
                       "f2p": True, "tier": "S+"},
            "Vivian": {"type": "Archer", "rarity": "Mythic", "role": "Current best DPS in game",
                        "key_skill": "Crouching Tiger — permanently +25% damage taken by all enemies; Focus Fire",
                        "f2p": True, "tier": "S+"},
        },
    },
    6: {
        "server_day": 340,
        "attack_defense_multiplier": "~530% AD (estimated)",
        "heroes": {
            "Triton": {"type": "Infantry", "rarity": "Mythic", "role": "Newest infantry",
                        "tier": "S+"},
            "Sophia": {"type": "Cavalry", "rarity": "Mythic", "role": "Newest cavalry",
                        "tier": "S+"},
            "Yang": {"type": "Archer", "rarity": "Mythic", "role": "Newest archer",
                      "tier": "S+"},
        },
    },
}

EPIC_HEROES = {
    "Chenko": {"type": "Cavalry", "role": "Rally joiner MVP", "key_skill": "Stand of Arms — +25% Lethality buff",
               "source": "Path of Growth (free)", "priority": "Must-have for rallies"},
    "Amane": {"type": "Archer", "role": "Rally joiner support", "key_skill": "Strong first expedition skill",
              "source": "Various", "priority": "Top 4 joiner hero"},
    "Gordon": {"type": "Cavalry", "role": "Gathering specialist", "key_skill": "+25% gathering speed, +25% march capacity at Skill Lv5",
               "source": "Various", "priority": "Essential for resource gathering"},
    "Yeonwoo": {"type": "Archer", "role": "Growth/building hero", "key_skill": "Strong first expedition skill",
                "source": "Various", "priority": "Top 4 joiner hero"},
    "Diana": {"type": "Archer", "role": "Stamina efficiency", "key_skill": "Iron Constitution — -20% stamina cost",
              "source": "Various", "priority": "Intel missions specialist"},
    "Fahd": {"type": "Cavalry", "role": "Combat support", "source": "Various", "priority": "Low"},
    "Howard": {"type": "Infantry", "role": "Early infantry tank", "source": "Various", "priority": "Early game only"},
    "Quinn": {"type": "Archer", "role": "Early archer DPS", "source": "Various", "priority": "Early game only"},
}

RARE_HEROES = {
    "Olive": {"type": "Archer"}, "Edwin": {"type": "Cavalry"},
    "Seth": {"type": "Infantry"}, "Forrest": {"type": "Infantry"},
}

HERO_ROULETTE = {
    "cost_per_spin": 1500,          # gems (or 1 Lucky Chip)
    "cost_10_spins": 13500,         # gems (discounted)
    "cost_120_spins": 162000,       # gems total
    "cost_120_with_free": 157500,   # gems (3 free spins from event)
    "free_spins_per_event": 3,      # 1 per day, 3-day event
    "event_duration_days": 3,
    "event_trigger": "Starts Day 2 of HoG/SG/KoP events",

    "drop_rates": {
        "5_hero_shards": 0.0437,    # 4.37%
        "1_hero_shard": 0.3281,     # 32.81%
    },
    "expected_shards_per_spin": 0.575,  # ~0.55-0.60 average
    "shards_from_120_spins": "66-72 from spins alone",

    "milestone_rewards": {
        5: "Small shard chest",
        15: "Medium shard chest",
        35: "Large shard chest",
        70: "30 hero fragments",
        120: "50 hero fragments",
    },
    "total_shards_at_120": "165-200+ fragments (spins + milestones)",

    "strategy": {
        "minimum_target": 70,       # Don't spin if can't reach 70
        "optimal_target": 120,      # Best value at 120 spins
        "rule": "If you can't reach 70 spins, DON'T SPIN. Save gems.",
        "timing": "Spend all spins on Day 1 — do not spread across 3 days",
        "hero_priority": "Skip Gen1 Saul. Target Gen2+ heroes (Zoe, Petra, etc.)",
    },

    "gems_to_4_star": 450000,  # Approximate gems needed per hero to reach 4-star
}

HERO_SKILL_SYSTEM = {
    "types": {
        "conquest": "PvP/Arena skills — damage, CC, burst",
        "expedition": "Rally/open-world skills — army-wide buffs, scale with Widgets",
    },
    "widget_system": {
        "description": "Multiplicative bonuses up to 15% at max level",
        "types": ["Rally Squad Widget", "Defender Squad Widget"],
        "priority": "Levels 1-5 give best bonus per fragment. Levels 8-10 have diminishing returns.",
        "rule": "Get priority heroes to widget Lv5 before pushing any to Lv10",
    },
    "star_levels": {
        "note": "Star upgrades from hero shards. Each star is a major power spike.",
        "investment_rule": "3-star = competitive baseline, 4-star = major spike, 5-star = endgame max",
    },
    "rally_joiner_mechanics": {
        "rule": "Joiners only contribute the FIRST expedition skill of hero in slot 1",
        "top_joiner_heroes": ["Chenko", "Amane", "Gordon", "Yeonwoo"],
        "skill_slot_selection": "Priority by: (1) Skill level first, (2) Rally join order for ties",
        "max_joiner_skills": 4,
    },
    "f2p_hero_path": "Zoe -> Jabel -> Save for Petra/Rosa (Gen 3-4)",
}

HERO_TIER_LIST = {
    "S+": ["Vivian", "Thrud", "Sophia", "Jabel", "Jaeger", "Petra", "Amadeus", "Triton", "Yang", "Marlin",
            "Long Fei", "Alcar", "Margot", "Rosa"],
    "S": ["Hilde", "Saul"],
    "A": ["Eric", "Zoe", "Helga"],
    "B": ["Yeonwoo", "Amane", "Chenko", "Gordon"],
    "C": ["Quinn", "Howard", "Fahd", "Diana", "Olive", "Edwin", "Seth", "Forrest"],
    "note": "B-tier heroes (Chenko, Amane, Gordon, Yeonwoo) are rated lower overall but are "
            "ESSENTIAL for rally joining. Tier list reflects general value, not joiner-specific value.",
}


# =============================================================================
# 5. EVENT SYSTEM
# =============================================================================

EVENT_SCHEDULE = {
    "server_timeline": {
        "day_0": "Kingdom created. Gen 1 heroes available (Jabel, Amadeus, Helga, Saul)",
        "day_6": "First Hall of Governors event",
        "day_10": "Gen 1 heroes fully available",
        "day_40_50": "Gen 2 heroes release (Zoe, Hilde, Marlin)",
        "day_55_60": "First Pet unlock wave (Gray Wolf, Lynx, Bison)",
        "day_70": "Age of Truegold begins. KoP eligibility opens.",
        "day_75_80": "Gen 2 Pets available",
        "day_105_120": "Gen 3 heroes (Eric, Petra, Jaeger) + Gen 3 Pets",
        "day_150": "TG4-5 + Truegold Crucible unlock",
        "day_190_200": "Gen 4 heroes (Alcar, Margot, Rosa) + Gen 4 Pets",
        "day_220": "War Academy + T11 unlock",
        "day_270_280": "Gen 5 heroes (Long Fei, Thrud, Vivian) + Gen 5 Pets",
        "day_340": "Gen 6 heroes (Triton, Sophia, Yang)",
    },

    "recurring_events": {
        "Hall of Governors (HoG)": {
            "cycle": "Every ~2 weeks (biweekly)",
            "duration": "5 days",
            "stages_v1": ["City Construction", "Hero Development", "Train Troops", "Beast Slay", "Power Boost"],
            "stages_v2": ["City Construction", "Hero Development", "Train Troops", "Gather Resources",
                          "Power Boost", "Governor Gear"],
            "key_reward": "Amadeus shards (Top 10 leaderboard only)",
            "strategy": "Troop Day is backbone of HoG. Higher tier = more points. "
                        "T10 = 1,960 pts. Pre-load T9, promote during event.",
        },
        "Strongest Governor (SG)": {
            "cycle": "Monthly (1st week of month)",
            "duration": "7 days",
            "scope": "Cross-kingdom (6 kingdoms compete)",
            "stages": {
                "day1": "City Construction — Truegold for building (2,000 pts), speedups (30 pts/1m)",
                "day2": "Hero Development — Mithril (40K pts), Hero Roulette (8K pts), Mythic Shard (3,040 pts)",
                "day3": "Basic Skills Up — Adv. Taming Mark (15K pts), Hero Roulette (8K pts)",
                "day4": "Combat Training — Mithril (40K pts), T10 train (39 pts/troop), T9 (30 pts/troop)",
                "day5": "Basic Skills Up — Mithril (40K pts), Truegold (2K pts), speedups (30 pts/1m)",
                "day6": "Combat Training — similar to Day 4",
                "day7": "Hero Development — Adv. Taming Mark (15K pts), Mythic Shard (3,040 pts)",
            },
            "highest_value_item": "Mithril = 40,000 pts/use (save ALL Mithril for SG)",
            "minimum_target": "250,000 points for kingdom-level rewards",
        },
        "Kingdom of Power (KvK)": {
            "cycle": "Monthly (4th week of month)",
            "eligibility": "Kingdom 70+ days old",
            "phases": {
                "matchmaking": "2 days — system matches kingdoms by top 100 governors' power",
                "preparation": "5 days — point competition. Winner gets +15% healing, +200% enlistment",
                "battle": "12 hours (10:00-22:00 UTC). Winner attacks, loser defends.",
                "field_triage": "2 days — troop recovery (30-90% recovery rate)",
            },
            "rewards": "Kingdom Coins, exclusive skins, server-wide buffs, 'High King' title",
            "winner_reward": "50 Kingdom Coins",
        },
        "Swordland Showdown": {
            "cycle": "Recurring alliance PvP event",
            "format": "2 alliances, 30 combatants + 10 subs per Legion",
            "duration": "1 hour battle",
            "objective": "Capture Relic Points from structures on battlefield",
            "strategy": "Prioritize Royal Stables first (faster teleports), then capture Sanctums",
        },
        "Tri-Alliance Clash": {
            "format": "3 alliances compete",
            "objective": "Capture buildings and earn points",
            "strategy": "Early game: capture Transit Centers for mobility advantage",
        },
        "Alliance Championship": {
            "note": "Major alliance competitive event",
        },
        "Alliance Mobilization": {
            "note": "Alliance-wide activity event",
        },
        "Viking Vengeance": {
            "cycle": "Every 2 weeks, Tuesday and Thursday",
            "format": "Defend against 20 waves of AI Viking troops",
            "strategy": "Reinforce others and keep your city empty. "
                        "Send only Infantry + Cavalry. Put Chenko/Amadeus/Yeonwoo/Amane in slot 1.",
            "success_threshold": "Kill 50%+ of attacking troops per wave",
        },
        "Bear Hunt": {
            "unlock": "TC19+",
            "formation": "80% Archers, 10% Infantry, 10% Cavalry",
            "key_heroes": "Chenko + Amane joiner combo = +12.5% damage",
            "reward": "Forge Hammers (NO alternative source — never miss this event)",
        },
        "Hero Roulette": {
            "trigger": "Day 2 of HoG/SG/KoP events",
            "duration": "3 days",
            "details": "See HERO_ROULETTE constant above",
        },
        "Merchant Empire": {
            "format": "Caravan escort event with hero squads (3 heroes per squad)",
        },
        "Alliance Brawl": {
            "note": "Low troop point values (24 pts for T10) — NOT worth promoting troops during this event",
        },
    },
}

STRONGEST_GOVERNOR_POINTS = {
    # Task: points per unit
    "mithril": 40000,
    "widget_hero_exclusive_gear": 8000,
    "hero_roulette_spin": 8000,
    "hero_gear_forgehammer": 4000,
    "mythic_hero_shard": 3040,
    "truegold_building": 2000,
    "epic_hero_shard": 1220,
    "advanced_taming_mark": 15000,
    "common_taming_mark": 1150,
    "rare_hero_shard": 350,
    "governor_gear_charm_+1": 70,
    "pet_advancement_+1": 50,
    "train_t10": 39,
    "train_t9": 30,
    "train_t8": 23,
    "train_t7": 16,
    "train_t6": 11,
    "train_t5": 7,
    "train_t4": 5,
    "train_t3": 3,
    "train_t2": 2,
    "train_t1": 1,
    "1m_speedup": 30,
    "gather_bread_2500": 3,
}


# =============================================================================
# 6. BUILDING SYSTEM
# =============================================================================

BUILDINGS = {
    "core": {
        "Town Center": {
            "function": "Main building. Gates ALL other building levels, troop tiers, research, features.",
            "priority": "ABSOLUTE #1 — never let TC idle",
        },
        "Embassy": {
            "function": "Alliance reinforcements, alliance help, prerequisite for TC11+",
            "priority": "Required for every TC upgrade from TC11-TC30",
            "pattern": "Prereq pattern alternates: Embassy needed at every level, "
                       "plus Barracks/Range/Stable/Academy in rotation",
        },
        "Academy": {
            "function": "All research (permanent power gains). Houses Growth/Economy/Battle trees.",
            "priority": "#2 — keep 1 level behind TC target",
        },
    },
    "military": {
        "Barracks": {"function": "Train Infantry", "copies": 4, "note": "More buildings = more simultaneous queues"},
        "Range": {"function": "Train Archers", "copies": 4},
        "Stable": {"function": "Train Cavalry", "copies": 4},
        "Command Center": {
            "function": "Rally capacity + solo march troop deployment",
            "priority": "Low for F2P (high for rally leaders)",
            "data": "See COMMAND_CENTER_DATA",
        },
        "Guard Station": {"function": "Garrison defense, troop defense when defending city"},
    },
    "support": {
        "Infirmary (Hospital)": {
            "function": "Heals wounded troops. Saves troops from permanent death.",
            "priority": "#3 — dead troops = wasted resources",
            "placement": "Place at edge/corner of base",
        },
        "Wall": {
            "function": "City defense. MUST equal TC level to progress.",
            "priority": "HIGH — mandatory for every TC upgrade",
        },
    },
    "resource": {
        "Mill": {"produces": "Bread", "priority": "Low — gathering gives 10-100x more"},
        "Sawmill": {"produces": "Wood", "priority": "Low"},
        "Quarry": {"produces": "Coal/Stone", "priority": "Low"},
        "Iron Mine": {"produces": "Iron", "priority": "Low"},
        "note": "Only upgrade resource buildings when required for TC prerequisites. "
                "Gathering from world map tiles is far more efficient.",
    },
    "special": {
        "Truegold Crucible": {
            "function": "Refines TrueGold currency",
            "unlock": "Kingdom TG Lv5 (~Day 150)",
            "daily_output": "~10.5 TrueGold/day (5 refinements)",
            "refinement_drop_rates": {1: 0.40, 2: 0.30, 3: 0.15, 4: 0.10, 5: 0.05},
            "daily_resource_cost": {"bread": 105000, "wood": 105000, "stone": 105000, "iron": 105000},
        },
        "Hero Hall": {"function": "Hero management and upgrades"},
        "Kitchen": {"function": "Resident worker hub, item production"},
        "House": {"function": "Residents + gold production. Affects comfort/mood."},
        "Watchtower": {"function": "Intel Missions (unlocks at TC7). See INTEL_MISSIONS."},
    },
}

BUILDING_PRIORITY_ORDER = [
    "Town Center",
    "Wall (must match TC level)",
    "Academy (1 level behind TC)",
    "Infirmary/Hospital",
    "Embassy (TC11+)",
    "Barracks/Range/Stable (prerequisite building for next TC)",
    "Command Center (rally leaders only)",
    "Resource buildings (only when TC prereqs require)",
    "Everything else",
]

COMMAND_CENTER_DATA = {
    # Level: {rally_capacity, march_troops}
    1: {"rally_capacity": 1500, "march_troops": 400},
    2: {"rally_capacity": 3500, "march_troops": 700},
    3: {"rally_capacity": 5700, "march_troops": 1000},
    4: {"rally_capacity": 8000, "march_troops": 1400},
    5: {"rally_capacity": 11500, "march_troops": 1800},
    10: {"rally_capacity": 35500, "march_troops": 8000},
    20: {"rally_capacity": 195000, "march_troops": 38000},
    30: {"rally_capacity": 840000, "march_troops": 67000},
    # TG stages continue: TG1 ~845-865K rally, TG5 ~945-965K rally
}


# =============================================================================
# 7. ALLIANCE MECHANICS
# =============================================================================

ALLIANCE_SYSTEM = {
    "help_system": {
        "reduction_per_help": "1% of remaining timer",
        "cost": "FREE (costs nothing to help or receive help)",
        "rule": "ALWAYS request alliance help BEFORE using speedups",
        "max_helps": "Depends on alliance size (30-50 members = 30-50 helps per request)",
    },
    "tech_tree": {
        "categories": ["Growth", "Battle"],
        "donation_method": "Members contribute gems or personal resources",
        "rewards_per_donation": "Alliance Tech Contribution points, Alliance XP, Alliance Tokens",
        "preferred_tech_bonus": "R4/R5 can set preferred tech — +20% reward chance for donating to it",
        "infinite_tech": "Covenant Making I (bottom of Battle tree) — allows infinite contributions when trees maxed",
        "daily_target": "300-600 contribution points per member per day",
    },
    "tokens_shop": {
        "currency": "Alliance Tokens (from donations + rally participation)",
        "buy_priority": ["Advanced Teleports", "Peace Shields", "Speedups", "VIP tokens"],
    },
    "territory": {
        "alliance_hq": "Central building for territory control. Free first build.",
        "banners": "Expand territory. Must connect to existing territory.",
        "resource_tiles": "75% of tile must be in territory for alliance resource bonus",
        "plains": "Opens after 14 days. Build Plains HQ for richer resource area.",
    },
    "rally_mechanics": {
        "leader_provides": [
            "All personal stats and buffs (research, gear, consumables, pets)",
            "All 3 heroes' expedition skills",
            "Troop contributions",
            "Sets rally capacity (Command Center level)",
        ],
        "joiner_provides": [
            "Troops only (buffed by LEADER's stats, not their own)",
            "ONE Priority Expedition Skill from first hero's first skill",
        ],
        "stat_skills_stack": True,   # e.g., Chenko's +25% Lethality stacks
        "chance_skills_stack": False,  # e.g., Jabel's damage reduction — independent rolls
        "consumable_rule": "ONLY rally leaders/garrison defenders should use buff items. "
                           "Joiner consumables provide ZERO value.",
        "ghost_rally": "Launch fake 1hr rally to protect troops when threatened by attackers",
    },
}


# =============================================================================
# 8. DAILY/WEEKLY ROUTINE OPTIMIZATION
# =============================================================================

DAILY_ROUTINE = {
    "priority_order": [
        {"task": "Collect login rewards", "priority": "P0", "time": "30s"},
        {"task": "Check/restart ALL builder queues (both/all builders)", "priority": "P0", "time": "1m"},
        {"task": "Check/restart Academy research queue", "priority": "P0", "time": "30s"},
        {"task": "Check/restart ALL troop training (Barracks + Range + Stable)", "priority": "P0", "time": "1m"},
        {"task": "Collect floating resources on base (tap resource bubbles)", "priority": "P1", "time": "30s"},
        {"task": "Alliance Help — tap all clasped hands icons", "priority": "P1", "time": "30s",
         "note": "1% timer reduction per tap, completely FREE"},
        {"task": "Alliance Tech donation (daily max, prioritize blue-thumbed tech)", "priority": "P1", "time": "30s"},
        {"task": "Claim daily mission rewards (check red dots)", "priority": "P1", "time": "1m"},
        {"task": "Intel Missions (Watchtower) — morning + evening refresh", "priority": "P1", "time": "15-25m total",
         "note": "Refresh at 08:00 UTC and 16:00 UTC. Gives gems, troops, Hunting Arrows."},
        {"task": "Conquest/Suppress stages (push for passive income)", "priority": "P2", "time": "5m"},
        {"task": "Path of Growth tasks (free Chenko hero)", "priority": "P2", "time": "2m"},
        {"task": "Send gathering marches to world map (Level 6+ tiles)", "priority": "P2", "time": "1m"},
        {"task": "Check active events and complete tasks", "priority": "P2", "time": "varies"},
        {"task": "Truegold Crucible refinements (5x daily after Day 150)", "priority": "P2", "time": "1m"},
    ],
    "total_time": "~30 minutes per day",
    "key_rules": [
        "NEVER let builders idle — single biggest progression loss",
        "NEVER let Academy idle — research provides permanent power",
        "NEVER let training buildings idle — troops are primary power source",
        "NEVER use speedups before Alliance Help (free 1% per tap)",
        "NEVER claim backpack resources until ready to spend (protects from raids)",
        "Consistency beats intensity — daily routine > occasional marathon sessions",
    ],
}

WEEKLY_ROUTINE = {
    "monday": "Check for new events starting. Alliance events often start Monday.",
    "tuesday_thursday": "Viking Vengeance event days (every 2 weeks)",
    "event_prep": "Stockpile resources/speedups Mon-Wed for weekend events",
    "weekly_targets": [
        "All daily missions completed every day",
        "Alliance tech donation maxed daily",
        "Gathering marches running 24/7",
        "Event task pre-loading (train T9 for upcoming HoG Troop Day)",
    ],
}

INTEL_MISSIONS = {
    "unlock": "Town Center Level 7 (Watchtower)",
    "refresh": "Twice daily at 08:00 UTC and 16:00 UTC",
    "mission_types": ["Hunt beasts", "Rescue refugees", "Bustling Inn Conquest battles"],
    "rewards": ["Resources", "Troops", "Gems", "Hunting Arrows"],
    "max_level": 20,
    "stamina": {
        "regen": "1 stamina every 5 minutes",
        "storehouse": "~120 stamina every 12 hours (manual collection required)",
        "diana_discount": "Iron Constitution skill reduces stamina cost up to 20%",
    },
    "hunting_arrows": {
        "per_player_daily": "~24 arrows",
        "alliance_40_members": "~960 arrows/day",
        "pitfall_max_bonus": "+25% Attack against Raging Bear (Level 5 Pitfall)",
    },
    "golden_glaives_trick": "Complete morning missions without collecting rewards, skip evening, "
                            "then claim during event for nearly 2x Goldstone rewards.",
}


# =============================================================================
# 9. POWER CALCULATION
# =============================================================================

POWER_SYSTEM = {
    "components": {
        "troop_power": "70-80% of combat power. Primary power source. Higher tiers = more power per unit.",
        "research_power": "Permanent. Cannot be lost. Every tech completion adds power.",
        "building_power": "Each building level adds power. TC gives most building power.",
        "hero_power": {
            "sources": ["Hero XP/leveling", "Hero star promotions (shards)", "Hero gear"],
            "per_promotion_4star": "7,800-10,500 power per promotion",
        },
        "hero_gear_power": "From Bear Hunt forge hammers and gear upgrades",
        "governor_gear_power": "Unlocks at TC22. Charm Level 11 = 1,320,000 power.",
        "pet_power": "Pet levels, refinement, and advancement all contribute power.",
    },
    "investment_priority_for_power": [
        "Troops (train highest tier 24/7 — bulk of power)",
        "Research (permanent, never lost — compound returns)",
        "Buildings (gates progression — indirect power multiplier)",
        "Heroes (star upgrades give biggest per-action spike)",
        "Governor Gear + Charms (TC25+ — massive late-game power)",
        "Pets (incremental but compounds)",
    ],
    "f2p_power_benchmarks": {
        "day_7": {"tc": "8-10", "avg_power": 300000, "good_power": 500000},
        "day_14": {"tc": "12-14", "avg_power": 800000, "good_power": 1200000},
        "day_30": {"tc": "17-19", "avg_power": 2_000_000, "good_power": 3_500_000},
        "day_60": {"tc": "22-24", "avg_power": 6_000_000, "good_power": 10_000_000},
        "day_200": {"tc": "28-30", "avg_power": 25_000_000, "good_power": 40_000_000},
    },
    "progression_phases": {
        "phase1_foundation": {"tc": "1-10", "days": "1-14", "power": "0-1M", "focus": "Rush TC, unlock systems"},
        "phase2_growth": {"tc": "11-19", "days": "14-40", "power": "1-5M", "focus": "Economy + hero development"},
        "phase3_acceleration": {"tc": "20-25", "days": "40-110", "power": "5-20M", "focus": "Hero max, gear investment"},
        "phase4_endgame": {"tc": "26-30+", "days": "110+", "power": "20M+", "focus": "TrueGold, charms, widgets"},
    },
}


# =============================================================================
# 10. COMBAT MECHANICS
# =============================================================================

COMBAT_MECHANICS = {
    "stat_priority": {
        "S_tier": ["Health (infantry focus)", "Lethality (archer/cavalry focus)"],
        "A_tier": ["Defense"],
        "B_tier": ["Attack"],
        "note": "Speed is fixed at 11 for all troops — provides no strategic value",
    },
    "buff_system": {
        "standard_buffs": {
            "sources": ["Governor gear", "Charms", "Skins", "Alliance/personal research", "Alliance buildings"],
            "stacking": "Additive (two 10% buffs = 20%)",
        },
        "special_buffs": {
            "sources": ["Hero abilities", "Exclusive widgets", "Kingdom titles", "Consumables (12h/24h)", "Debuffs"],
            "stacking": "Multiplicative",
            "formula": "(Base Stat x (1 + Standard Buff Total)) x (1 + Special Buff %)",
            "example": "200% standard + 40% special = 320% effective, not 240%",
        },
    },
    "combat_flow": [
        "1. Deployment: Infantry -> Cavalry -> Archers",
        "2. Target selection: frontmost enemy line (20% Cavalry dive exception)",
        "3. Damage: Lethality vs Health",
        "4. Casualty removal",
        "5. Defender phase mirrors attacker",
        "6. Line collapse -> retargeting",
        "7. Victory when one side = 0 troops",
    ],
    "gear_priority_order": [
        "Infantry Health + Defense (frontline survival)",
        "Archer Lethality + Health",
        "Cavalry (lowest priority)",
    ],
    "governor_gear": {
        "unlock": "TC22",
        "slots": 6,
        "charms_unlock": "TC25",
        "rarities": ["Green (0-1 star)", "Blue (0-3 star)", "Purple (0-3 star)", "Purple T1 (0-3 star)"],
        "upgrade_materials": ["Satin", "Gilded Threads", "Artisan's Vision"],
        "charm_max_level": 11,
        "charm_level_11_power": 1_320_000,
        "upgrade_rule": "Level all 6 pieces evenly before advancing any single piece",
    },
}


# =============================================================================
# 11. PET SYSTEM
# =============================================================================

PET_SYSTEM = {
    "unlock": "Town Center Level 18 (after server reaches required age)",
    "building": "Beast Cage",
    "stats": {
        "primary": ["Squad Attack", "Squad Defense"],  # Scale with level automatically
        "secondary": ["Infantry Lethality", "Infantry Health", "Cavalry Lethality",
                       "Cavalry Health", "Archer Lethality", "Archer Health"],
        "secondary_unlock": "Pet Level 10",
    },
    "tier_list": {
        "S_tier_universal": ["Lion", "Mighty Bison"],
        "S_tier_combat": ["Rhino (Rally Leaders)", "Moose", "Grizzly"],
        "A_tier_economic": ["Bison (F2P)", "Cheetah (F2P)"],
    },
    "refinement": {
        "system": "Taming Marks for Lethality/Health bonuses",
        "ratchet_rule": "One-way protection — locked stats never drop below their color tier",
    },
    "investment_rules": [
        "Don't pour resources into Gen 1 pets — get them functional, then SAVE for Gen 3-4",
        "Promotion Medallions are strictly bottlenecked — prioritize which pets hit Level 50+",
        "Pet generation timing: Gen1 Day 55, Gen2 Day 75, Gen3 Day 105, Gen4 Day 195, Gen5 Day 280",
    ],
}


# =============================================================================
# 12. TRUEGOLD SYSTEM
# =============================================================================

TRUEGOLD_SYSTEM = {
    "unlock_day": 70,
    "crucible_unlock_day": 150,
    "sources": [
        "Event Rewards (Armament Competition, Strongest Governor)",
        "Kingdom Shop (Kingdom of Power Shop)",
        "Watchtower Intel Missions (after TC30)",
        "Store bundles (paid)",
        "Truegold Crucible (primary daily source)",
    ],
    "crucible": {
        "daily_output": "~10.5 TrueGold/day (5 refinements)",
        "refinement_costs": {
            1: 5000,   # per resource type
            2: 10000,
            3: 20000,
            4: 30000,
            5: 40000,
        },
        "total_daily_cost": "105,000 each of bread, wood, stone, iron",
        "drop_rates": {1: 0.40, 2: 0.30, 3: 0.15, 4: 0.10, 5: 0.05},
    },
    "buildings_using_truegold": [
        "Town Center", "Embassy", "Command Center", "Infirmary",
        "Barracks", "Range", "Stable",
    ],
    "upgrade_priority": [
        "1. Town Center + troop buildings (Barracks/Range/Stable)",
        "2. Infirmary + Embassy",
        "3. Command Center (unless rally leader)",
    ],
    "truegold_dust": {
        "used_for": "War Academy research (T11 unlock)",
        "sources": [
            "Top-up Center packs",
            "Daily exchange: 5,000 Gold -> 1 Dust (up to 20x/day)",
            "Daily exchange: 10 Truegold -> 13 Dust (up to 200x/day)",
        ],
    },
}


# =============================================================================
# 13. F2P STRATEGY GUIDE
# =============================================================================

F2P_STRATEGY = {
    "golden_rules": [
        "Save ALL gems for Hero Roulette — no exceptions",
        "Focus exclusively on 3 heroes maximum",
        "Keep resources in backpack storage (protected from raids)",
        "Maintain constant builder activity (buy 2nd builder ASAP — ~1000 gems)",
        "Join an alliance by TC6",
        "NEVER spend gems on speedups, VIP XP, shop refreshes, or resources",
    ],
    "gem_budget": {
        "hero_4star_cost": 450000,  # gems per hero to 4-star via Roulette
        "second_builder": 1000,     # gems — HIGHEST ROI purchase
        "note": "Choose VIP path OR hero roulette path — can't afford both simultaneously",
    },
    "vip_strategy": {
        "target": "VIP 6 (unlocks permanent +1 builder = 3 builders total)",
        "method": "VIP points from events/dailies, NOT gems",
        "note": "VIP 6 = biggest single F2P power spike after 2nd builder",
    },
    "hero_core_trio": {
        "tank": "Zoe (Infantry) — 40% HP self-heal, Hero Roulette accessible",
        "dps": "Jabel (Cavalry) — F2P accessible, core defensive foundation",
        "support": "Chenko (Cavalry, Epic) — free from Path of Growth, +25% Lethality",
    },
    "progression_timeline": {
        "week_1": "TC 7+, establish 3-hero core, join alliance, daily routine",
        "month_1": "TC 15-20, first Roulette investment, all events",
        "month_2_3": "TC 25+, 3-4 star core heroes, premium alliance rank",
        "month_6": "Compete with moderate spenders, 4+ star meta roster",
    },
    "resource_management": {
        "rule": "90% resources in Backpack — only claim before spending",
        "gathering": "Level 6-8 tiles (best speed-to-quantity balance)",
        "gordon_skill": "+25% gathering speed + 25% march capacity at Skill Lv5",
        "tc22_bonus": "5th march slot = +25% gathering permanently",
    },
    "event_priority": [
        "1. Hero Roulette (gem-only spending — most valuable)",
        "2. Construction events (deploy accumulated speedups)",
        "3. Training events (bulk troop production)",
        "4. Alliance events (mandatory participation)",
        "5. Suppress/Conquest modes (daily completion for rewards)",
    ],
    "critical_mistakes": [
        "Hero spreading: Focus 3 heroes deep > 8 heroes shallow",
        "Gem misallocation: Only Roulette + 2nd builder",
        "Speedup timing: Events give 3x+ rewards vs random usage",
        "Bear Hunt neglect: Forge Hammers have NO alternative source",
        "Storehouse gaps: Uncapped resources get raided, especially during KvK",
    ],
}


# =============================================================================
# 14. UI LAYOUT KNOWLEDGE (for bot screen identification)
# =============================================================================

UI_KNOWLEDGE = {
    "main_screens": {
        "city_view": {
            "identifier": "Town Center building visible in center",
            "bottom_bar": ["City", "World", "Heroes", "Alliance", "More"],
            "resource_bar": "Top of screen: Bread, Wood, Coal, Iron, Gems",
            "builder_icon": "Hammer icon near top — shows active builders",
        },
        "world_map": {
            "identifier": "Zoomed-out terrain with resource tiles and other cities",
            "bottom_bar": "Same as city view",
            "search_button": "Top right area",
        },
        "hero_screen": {
            "identifier": "Hero portraits in grid layout",
            "tabs": ["All", "Infantry", "Cavalry", "Archer"],
        },
        "alliance_screen": {
            "identifier": "Alliance name and member list",
            "tabs": ["Overview", "Members", "Tech", "Shop", "Territory"],
        },
    },
    "common_popups": {
        "alliance_help": {
            "identifier": "Clasped Hands icon with number",
            "close": "Tap the hands icon or close button",
        },
        "daily_login": {
            "identifier": "Reward grid with 'Claim' button",
            "close": "Tap 'Claim' then X or outside popup",
        },
        "event_notification": {
            "identifier": "Event banner/popup with 'Go' button",
            "close": "X button top-right of popup or tap outside",
        },
        "speed_up_dialog": {
            "identifier": "'Free' button if timer < 5 minutes, otherwise 'Use' speedup button",
            "rule": "Auto-complete free if under 5 minutes",
        },
        "level_up_celebration": {
            "identifier": "Large animation/banner with 'Claim' button",
            "close": "Tap 'Claim' or anywhere on screen",
        },
    },
    "building_interaction": {
        "tap_building": "Opens building menu with upgrade/info options",
        "upgrade_button": "Usually bottom-center of building detail view",
        "prerequisites_display": "Shows required buildings if not met",
        "help_request": "Alliance help icon appears after starting upgrade",
    },
    "navigation_structure": {
        "city_to_building": "Tap building on city view",
        "building_to_upgrade": "Tap upgrade button in building detail",
        "city_to_world": "Tap 'World' in bottom bar",
        "world_to_gather": "Tap resource tile -> Send troops",
        "city_to_academy": "Tap Academy building -> Research tab",
        "city_to_heroes": "Tap 'Heroes' in bottom bar",
        "city_to_alliance": "Tap 'Alliance' in bottom bar",
        "city_to_events": "Tap event icon (calendar/banner) on right side of screen",
    },
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_tc_prereqs(level: int) -> dict:
    """Get prerequisites for a specific TC level."""
    return TC_PREREQUISITES.get(level, {})


def get_next_tc_prereqs(current_level: int) -> dict:
    """Get what's needed for the next TC level."""
    return TC_PREREQUISITES.get(current_level + 1, {})


def get_event_points(event: str, tier: int) -> int:
    """Get event points for training a specific troop tier."""
    points = TROOP_EVENT_POINTS.get(event, [])
    if 1 <= tier <= len(points):
        return points[tier - 1]
    return 0


def get_hero_info(name: str) -> dict:
    """Look up a hero by name across all generations."""
    for gen_num, gen_data in HERO_GENERATIONS.items():
        heroes = gen_data.get("heroes", {})
        if name in heroes:
            info = heroes[name].copy()
            info["generation"] = gen_num
            info["server_day_available"] = gen_data["server_day"]
            return info
    # Check epic heroes
    if name in EPIC_HEROES:
        info = EPIC_HEROES[name].copy()
        info["rarity"] = "Epic"
        return info
    if name in RARE_HEROES:
        info = RARE_HEROES[name].copy()
        info["rarity"] = "Rare"
        return info
    return {}


def get_power_benchmark(day: int) -> dict:
    """Get F2P power benchmark for a given server day."""
    benchmarks = POWER_SYSTEM["f2p_power_benchmarks"]
    closest = None
    for key, data in benchmarks.items():
        benchmark_day = int(key.split("_")[1])
        if benchmark_day <= day:
            closest = data
    return closest or {}


def should_promote_during_event(event: str) -> bool:
    """Check if troop promotion is worthwhile during a specific event."""
    low_value_events = ["Alliance_Brawl"]
    return event not in low_value_events


def get_sg_day_focus(day: int) -> str:
    """Get the focus area for a specific Strongest Governor day."""
    sg = EVENT_SCHEDULE["recurring_events"]["Strongest Governor (SG)"]["stages"]
    day_key = f"day{day}"
    return sg.get(day_key, "Unknown day")
