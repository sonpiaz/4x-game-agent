"""
Strategic Brain - Deep game knowledge + long-term planning
Built from extensive research of top 1% player strategies.
"""
import json
import os
import time
from datetime import datetime

STATE_FILE = "game_state.json"

STRATEGY_KNOWLEDGE = """
## YOU ARE A TOP 1% KINGSHOT PLAYER BOT
Account: TC9, Power 312K, Kingdom #892, F2P. Server is new (just joined today).

### CURRENT PHASE: EARLY GAME (TC1-13)
Goal: Rush TC13 ASAP → unlocks T5 troops + promotion system.

### GOLDEN RULES (NEVER BREAK):
1. NEVER let builders idle — 2 builders ALWAYS working
2. NEVER let Academy idle — always researching
3. NEVER let troop training idle — all 3 buildings (Barracks/Range/Stables) training 24/7
4. NEVER use speedups before maxing Alliance Help (each help = 1% of timer FREE)
5. NEVER spend gems on food/wood/stone/gold
6. NEVER upgrade resource buildings beyond TC prerequisite minimum
7. NEVER spread hero investment across 8+ heroes — focus 3 DEEP
8. Timers under 5 minutes auto-complete free — never waste speedups on these

### TC RUSH PREREQUISITES (COMPLETE):
- TC2: Wall Lv.1
- TC3: Wall Lv.2, Academy Lv.2
- TC4: Wall Lv.3, Academy Lv.3, Hospital Lv.1
- TC5: Wall Lv.4, Academy Lv.4, Hospital Lv.2, Barracks Lv.2
- TC6: Wall Lv.5, Academy Lv.5, Hospital Lv.3, Archery Range Lv.2
- TC7: Wall Lv.6, Academy Lv.6, Hospital Lv.4, Stable Lv.2
- TC8: Wall Lv.7, Academy Lv.7, Hospital Lv.5, Barracks Lv.3
- TC9: Wall Lv.8, Academy Lv.8, Hospital Lv.6, Range Lv.3, Stable Lv.3
- TC10: Wall Lv.9, Academy Lv.9, Hospital Lv.7, Range Lv.9
- TC11: Wall Lv.10, Academy Lv.10, Hospital Lv.8, Embassy Lv.10, Stable Lv.10
- TC12: Wall Lv.11, Academy Lv.11, Hospital Lv.9, Embassy Lv.11, Command Center Lv.1
- TC13: Wall Lv.12, Academy Lv.12, Hospital Lv.10, Embassy Lv.12, Barracks Lv.12

KEY INSIGHT: Wall, Academy, Hospital are needed for EVERY TC level.
Builder 1: Always on TC upgrade path
Builder 2: Prerequisites for NEXT TC level (Wall > Hospital > specific building)

### SECOND BUILDER: BUY IMMEDIATELY if not owned (cost ~1000 gems, we have 4472)
This is the #1 highest ROI gem spend. Every minute without 2nd builder = wasted progress.

### POWER GROWTH MATH:
- Troop training = primary power source (70-80% of combat power)
- Research = permanent stat boosts (cannot be lost)
- Building = unlocks capacity
- Hero promotion = 7,800-10,500 power per promotion at 4-star

### POWER BENCHMARKS (F2P):
- Day 7: 500K+ (good)
- Day 14: 1.2M+ (good)
- Day 30: 3.5M+ (good)
- Day 60: 10M+ (good)

### RESEARCH PRIORITY:
Economy tree first (weeks 1-4):
1. Construction Speed I-III
2. Research Speed I-III
3. Gathering Speed I-II
Then Military tree after TC15.

### TROOP STRATEGY:
- Train highest tier available, all 3 buildings 24/7
- Balanced ratio: 5 Infantry : 2 Cavalry : 3 Archer
- Pre-load T9 before events, promote T9→T10 during HoG Troop Day (1,960 pts/T10)
- NEVER train T10 directly during non-events — pre-load T9 instead

### HERO PRIORITY (F2P):
Focus order: Zoe → Jabel → Chenko
Gems: HERO ROULETTE ONLY (10x pulls for 50 gems = best hero shards ROI)
- Do NOT save gems for Marlin (15K gems = too expensive for F2P)
- Do NOT waste gems on speedups (events give free speedups)
Chenko = free from Path of Growth → mandatory for Bear Hunt later
Rule: 3 heroes at 4-stars > 8 heroes at 2-stars
Skill order: Max primary skill FIRST (e.g. Zoe: Last Stand → Iron Skin → Rally Point)

### VIP STRATEGY:
Rush VIP 6 ASAP → unlocks permanent +1 builder (3 builders total!)
- Use VIP points from events/dailies, NOT gems
- VIP 6 = biggest single F2P power spike after 2nd builder

### DAILY ROUTINE (priority order):
1. Collect login reward
2. Check/restart builder queues (BOTH builders)
3. Check/restart research queue (Academy)
4. Check/restart ALL troop training (Barracks + Range + Stables)
5. Collect floating resources on base
6. Alliance Help (tap all — 1% timer reduction per tap, FREE)
7. Alliance Tech donation (daily max)
8. Claim daily mission rewards
9. Conquest/Suppress stages (push for passive income)
10. Path of Growth tasks (free Chenko hero)
11. Send gathering marches to world map (Level 6+ tiles)
12. Check events and complete tasks

### ALLIANCE:
- Alliance Help BEFORE speedups ALWAYS (1% per tap = saves hours)
- Donate to alliance tech daily (blue thumbs-up = +20% bonus)
- Alliance Coins → spend on Advanced Teleports + Peace Shields only
- Join rallies when available
- Ghost rally: launch fake 1hr rally to protect troops when threatened

### EVENT OPTIMIZATION:
- HoG Troop Day: T10 = 1,960 pts, T9 = 1,485 pts (70-80% of winning totals)
- Strongest Governor: Mithril = 40,000 pts/use (highest single item)
- Bear Hunt (TC19+): 80% Archer formation, Chenko+Amane joiner combo = +12.5% dmg
- NEVER promote troops during Alliance Brawl (only 24 pts vs 1,960 in HoG)
- Speedups: SAVE for event training windows only (alliance training boost = 1 free day)

### RESOURCE MANAGEMENT:
- Keep 90% resources in Backpack — only claim before spending
- Gather on Level 6-8 tiles (best balance of speed + quantity)
- Gordon hero at skill Lv.5 = +25% gathering speed + 25% march capacity
- After TC22: 5th march slot unlocked = +25% gathering permanently

### HOSPITAL PLACEMENT:
- Place at edge or corner of base (prevents attackers farming kills)
- Max level Hospital heals more troops (survival in wars)
- Hospital is prerequisite for every TC level after TC4 — prioritize upgrading

### WHAT TO DO RIGHT NOW (TC9):
1. Buy second builder if not owned
2. Upgrade Wall to Lv.9 + Hospital to Lv.7 + Range to Lv.9 (TC10 prerequisites)
3. Start TC10 upgrade as soon as prerequisites met
4. Train troops in ALL 3 military buildings
5. Research Construction Speed
6. Clear Conquest Stage 50 (Path of Growth reward waiting)
7. Claim ALL red notification dots
8. Path of Growth tasks for free Chenko
"""


class GameStateMemory:
    """Persistent memory of game state between cycles"""

    def __init__(self):
        self.state = self._load()

    def _load(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        return self._default_state()

    def _default_state(self):
        return {
            "tc_level": 9,
            "power": 312827,
            "vip_level": 2,
            "gems": 4472,
            "kills": 0,
            "kingdom": 892,
            "alliance": "ATA",
            "second_builder": False,
            "conquest_stage": 49,
            "path_of_growth": 4,
            "heroes": {"focus": ["Zoe", "Jabel", "Chenko"]},
            "research_tree": "economy",
            "current_goal": "rush_tc13",
            "daily_done": {},
            "last_alliance_help": 0,
            "last_donation": 0,
            "last_gather_send": 0,
            "power_history": [],
            "session_start_power": 312827,
            "session_start_time": time.time(),
            "lessons_learned": [],
            "updated_at": datetime.now().isoformat()
        }

    def save(self):
        self.state["updated_at"] = datetime.now().isoformat()
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def update(self, key, value):
        self.state[key] = value
        self.save()

    def get(self, key, default=None):
        return self.state.get(key, default)

    def track_power(self, power):
        self.state["power"] = power
        history = self.state.get("power_history", [])
        history.append({"power": power, "time": time.time()})
        if len(history) > 200:
            history = history[-200:]
        self.state["power_history"] = history
        self.save()

    def power_per_hour(self):
        elapsed = time.time() - self.state.get("session_start_time", time.time())
        if elapsed < 60:
            return 0
        gained = self.state.get("power", 0) - self.state.get("session_start_power", 0)
        return int(gained / (elapsed / 3600))

    def should_do_daily(self, task_name):
        today = datetime.now().strftime("%Y-%m-%d")
        done = self.state.get("daily_done", {})
        return done.get(task_name) != today

    def mark_daily_done(self, task_name):
        today = datetime.now().strftime("%Y-%m-%d")
        if "daily_done" not in self.state:
            self.state["daily_done"] = {}
        self.state["daily_done"][task_name] = today
        self.save()

    def add_lesson(self, lesson):
        """Learning: record what worked and what didn't"""
        lessons = self.state.get("lessons_learned", [])
        lessons.append({
            "lesson": lesson,
            "time": datetime.now().isoformat(),
            "power_at_time": self.state.get("power", 0)
        })
        if len(lessons) > 50:
            lessons = lessons[-50:]
        self.state["lessons_learned"] = lessons
        self.save()

    def get_current_goal(self):
        tc = self.state.get("tc_level", 9)
        if tc < 13:
            return "rush_tc13"
        elif tc < 22:
            return "rush_tc22"
        elif tc < 25:
            return "rush_tc25"
        else:
            return "optimize_power"

    def get_strategic_context(self):
        goal = self.get_current_goal()
        pph = self.power_per_hour()
        tc = self.state.get('tc_level', 9)

        ctx = f"""
CURRENT ACCOUNT STATE:
- TC Level: {tc}
- Power: {self.state.get('power', '?'):,} (growth: {pph:,}/hour)
- VIP: {self.state.get('vip_level', '?')}
- Gems: {self.state.get('gems', '?'):,}
- Second Builder: {'YES' if self.state.get('second_builder') else 'UNKNOWN - CHECK AND BUY IF NOT OWNED'}
- Conquest Stage: {self.state.get('conquest_stage', '?')}
- Path of Growth: {self.state.get('path_of_growth', '?')}/120

STRATEGIC GOAL: {goal.upper()}
"""
        if goal == "rush_tc13":
            ctx += f"""
TC9 → TC13 RUSH CHECKLIST:
- TC10 needs: Range Lv.9 + Academy (any level)
- TC11 needs: Embassy Lv.10 + Stable Lv.10
- TC12 needs: Embassy Lv.11 + Command Center Lv.1
- TC13 needs: Embassy Lv.12 + Barracks Lv.12
- PRIORITY: Check if Range is Lv.9 yet, check Academy exists
- Second builder: MUST have (1000 gems, we have {self.state.get('gems', 0)})
"""
        recent_lessons = self.state.get("lessons_learned", [])[-5:]
        if recent_lessons:
            ctx += "\nRECENT LESSONS:\n"
            for l in recent_lessons:
                ctx += f"- {l['lesson']}\n"

        return ctx
