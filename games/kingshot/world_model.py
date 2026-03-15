"""
World Model — The bot's persistent understanding of game state.
Updated by observations, not rebuilt each cycle.
Predicts future state (timer completions) to enable proactive scheduling.
"""
import json
import os
import time

MODEL_FILE = "world_model.json"


class WorldModel:
    """Persistent game state with timer predictions."""

    def __init__(self, log_fn=None):
        self.log = log_fn or print
        self.state = self._load()

    def _load(self):
        if os.path.exists(MODEL_FILE):
            with open(MODEL_FILE) as f:
                data = json.load(f)
            default = self._default_state()
            for key in default:
                if key not in data:
                    data[key] = default[key]
            return data
        return self._default_state()

    def _default_state(self):
        return {
            "account": {
                "tc_level": 9,
                "power": 314000,
                "vip_level": 2,
                "gems": 4472,
                "kingdom": 892,
                "second_builder": False,
            },
            "buildings": {
                "town_center":   {"level": 9, "upgrading": False, "timer_end": None},
                "wall":          {"level": 8, "upgrading": False, "timer_end": None},
                "academy":       {"level": 8, "upgrading": False, "timer_end": None},
                "hospital":      {"level": 6, "upgrading": False, "timer_end": None},
                "barracks":      {"level": 7, "upgrading": False, "timer_end": None},
                "archery_range": {"level": 6, "upgrading": False, "timer_end": None},
                "stables":       {"level": 6, "upgrading": False, "timer_end": None},
                "embassy":       {"level": 8, "upgrading": False, "timer_end": None},
            },
            "research": {
                "active": False,
                "timer_end": None,
            },
            "training": {
                "barracks":      {"active": False, "timer_end": None},
                "archery_range": {"active": False, "timer_end": None},
                "stables":       {"active": False, "timer_end": None},
            },
            "resources": {
                "food": 0, "wood": 0, "stone": 0, "gold": 0,
            },
            "last_observations": {},
            "power_history": [],
            "session_start": time.time(),
            "session_start_power": 314000,
            "daily_done": {},
            "lessons": [],
            "cached_positions": {},  # building_name → {x, y, hits, misses}
        }

    def save(self):
        with open(MODEL_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    # =========================================================
    # OBSERVATION UPDATES — called when we see something
    # =========================================================

    def observe_screen(self, ocr_data: dict, screen_type: str):
        """Update model from OCR observation."""
        now = time.time()

        if screen_type == "home_city":
            if ocr_data.get("power"):
                self.state["account"]["power"] = ocr_data["power"]
                self.state["last_observations"]["power"] = now
                self._track_power(ocr_data["power"])
            if ocr_data.get("gems"):
                self.state["account"]["gems"] = ocr_data["gems"]
            if ocr_data.get("vip_level"):
                self.state["account"]["vip_level"] = ocr_data["vip_level"]
            if ocr_data.get("food"):
                self.state["resources"]["food"] = ocr_data["food"]

        self._expire_timers()
        self.save()

    def observe_upgrade_started(self, building_name: str, duration_secs: float = 0):
        """Record that a building upgrade was started."""
        b = self.state["buildings"].get(building_name)
        if b:
            b["upgrading"] = True
            if duration_secs > 0:
                b["timer_end"] = time.time() + duration_secs
            self.save()
            self.log(f"WORLD: {building_name} upgrade started")

    def observe_upgrade_complete(self, building_name: str):
        """Record that a building upgrade completed."""
        b = self.state["buildings"].get(building_name)
        if b:
            b["level"] += 1
            b["upgrading"] = False
            b["timer_end"] = None
            # Update TC level if town_center
            if building_name == "town_center":
                self.state["account"]["tc_level"] = b["level"]
            self.save()
            self.log(f"WORLD: {building_name} → level {b['level']}")

    def observe_research_started(self, duration_secs: float = 0):
        """Record research started."""
        self.state["research"]["active"] = True
        if duration_secs > 0:
            self.state["research"]["timer_end"] = time.time() + duration_secs
        self.save()

    def observe_training_started(self, building_name: str, duration_secs: float = 0):
        """Record troop training started."""
        t = self.state["training"].get(building_name)
        if t:
            t["active"] = True
            if duration_secs > 0:
                t["timer_end"] = time.time() + duration_secs
            self.save()

    # =========================================================
    # STATE QUERIES — what does the bot know?
    # =========================================================

    def _expire_timers(self):
        """Auto-expire timers that have passed."""
        now = time.time()
        for name, b in self.state["buildings"].items():
            if b["upgrading"] and b.get("timer_end") and b["timer_end"] < now:
                self.observe_upgrade_complete(name)

        r = self.state["research"]
        if r["active"] and r.get("timer_end") and r["timer_end"] < now:
            r["active"] = False
            r["timer_end"] = None

        for name, t in self.state["training"].items():
            if t["active"] and t.get("timer_end") and t["timer_end"] < now:
                t["active"] = False
                t["timer_end"] = None

    def builders_available(self) -> int:
        """How many builders are free right now?"""
        self._expire_timers()
        busy = sum(1 for b in self.state["buildings"].values() if b["upgrading"])
        max_builders = 1
        if self.state["account"].get("second_builder"):
            max_builders = 2
        if self.state["account"].get("vip_level", 0) >= 6:
            max_builders = 3
        return max(0, max_builders - busy)

    def research_idle(self) -> bool:
        self._expire_timers()
        return not self.state["research"]["active"]

    def training_idle(self) -> list:
        """Which training buildings are idle?"""
        self._expire_timers()
        return [name for name, t in self.state["training"].items() if not t["active"]]

    def get_idle_queues(self) -> list:
        """All idle queues sorted by priority.
        Returns [(type, name, priority), ...]"""
        idles = []
        if self.builders_available() > 0:
            idles.append(("builder", "builder", 0))
        if self.research_idle():
            idles.append(("research", "academy", 0))
        for name in self.training_idle():
            idles.append(("training", name, 1))
        idles.sort(key=lambda x: x[2])
        return idles

    def next_timer_completion(self):
        """Returns (unix_time, description) or None."""
        events = []
        now = time.time()

        for name, b in self.state["buildings"].items():
            if b["upgrading"] and b.get("timer_end") and b["timer_end"] > now:
                events.append((b["timer_end"], f"builder:{name}"))

        r = self.state["research"]
        if r["active"] and r.get("timer_end") and r["timer_end"] > now:
            events.append((r["timer_end"], "research"))

        for name, t in self.state["training"].items():
            if t["active"] and t.get("timer_end") and t["timer_end"] > now:
                events.append((t["timer_end"], f"training:{name}"))

        if not events:
            return None
        events.sort()
        return events[0]

    def seconds_until_next_event(self) -> float:
        nxt = self.next_timer_completion()
        return max(0, nxt[0] - time.time()) if nxt else float("inf")

    def power_per_hour(self) -> int:
        elapsed = time.time() - self.state.get("session_start", time.time())
        if elapsed < 60:
            return 0
        gained = self.state["account"].get("power", 0) - self.state.get("session_start_power", 0)
        return int(gained / (elapsed / 3600))

    def data_age(self, field: str) -> float:
        """Seconds since field was last observed. inf if never."""
        last = self.state.get("last_observations", {}).get(field, 0)
        return float("inf") if last == 0 else time.time() - last

    def get_tc_level(self) -> int:
        return self.state["account"].get("tc_level", 9)

    def get_building_level(self, name: str) -> int:
        return self.state["buildings"].get(name, {}).get("level", 0)

    def is_daily_done(self, task: str) -> bool:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        return self.state.get("daily_done", {}).get(task) == today

    def mark_daily_done(self, task: str):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        self.state.setdefault("daily_done", {})[task] = today
        self.save()

    def add_lesson(self, lesson: str):
        lessons = self.state.get("lessons", [])
        lessons.append({"text": lesson, "time": time.time()})
        if len(lessons) > 50:
            lessons = lessons[-50:]
        self.state["lessons"] = lessons
        self.save()

    # =========================================================
    # TIMER SYNC FROM SCREEN
    # =========================================================

    def sync_timers_from_screen(self, active_timers: list):
        """Sync world model timers from OCR-detected timers on screen.

        Maps timer positions to nearest cached building positions,
        then updates timer_end fields accordingly.

        Args:
            active_timers: List of {timer: "HH:MM:SS", x: int, y: int}
                           from OCR read_game_state.
        """
        if not active_timers:
            return

        cached = self.state.get("cached_positions", {})
        now = time.time()
        synced = []

        for timer_data in active_timers:
            timer_text = timer_data.get("timer", "")
            tx, ty = timer_data.get("x", 0), timer_data.get("y", 0)

            # Parse timer duration
            secs = self._parse_timer(timer_text)
            if secs <= 0:
                continue

            # Find nearest building to this timer position
            best_building = None
            best_dist = 300  # Max distance to associate timer with building

            for name, pos in cached.items():
                bx, by = pos.get("x", 0), pos.get("y", 0)
                dist = ((tx - bx) ** 2 + (ty - by) ** 2) ** 0.5
                if dist < best_dist:
                    best_dist = dist
                    best_building = name

            if best_building:
                # Check if this building is in our buildings dict
                b = self.state["buildings"].get(best_building)
                if b and not b["upgrading"]:
                    # Timer near a building that model thinks is idle — fix it
                    b["upgrading"] = True
                    b["timer_end"] = now + secs
                    synced.append(f"{best_building}={timer_text}")
            else:
                # Timer not near any known building — could be research or training
                # Check if timer is near center-right (research) or bottom (training)
                if tx > 1000 and 400 < ty < 800:
                    # Likely research timer
                    if not self.state["research"]["active"]:
                        self.state["research"]["active"] = True
                        self.state["research"]["timer_end"] = now + secs
                        synced.append(f"research={timer_text}")
                elif ty > 1000:
                    # Could be training timer — check training buildings
                    for tname, t in self.state["training"].items():
                        if not t["active"]:
                            t["active"] = True
                            t["timer_end"] = now + secs
                            synced.append(f"training:{tname}={timer_text}")
                            break

        if synced:
            self.save()
            self.log(f"WORLD: Timer sync: {', '.join(synced)}")

    @staticmethod
    def _parse_timer(timer_text: str) -> int:
        """Parse timer text like "1:23:45" or "23:45" to seconds."""
        parts = timer_text.strip().split(":")
        try:
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        except (ValueError, IndexError):
            pass
        return 0

    # =========================================================
    # ADAPTIVE COORDINATE CACHING
    # =========================================================

    def get_cached_position(self, name: str):
        """Get cached building position if available. Returns (x, y) or None."""
        cached = self.state.get("cached_positions", {}).get(name)
        if cached and cached.get("hits", 0) > 0:
            return (cached["x"], cached["y"])
        return None

    def cache_position(self, name: str, x: int, y: int):
        """Cache a working building position."""
        positions = self.state.setdefault("cached_positions", {})
        if name in positions:
            positions[name]["x"] = x
            positions[name]["y"] = y
            positions[name]["hits"] = positions[name].get("hits", 0) + 1
        else:
            positions[name] = {"x": x, "y": y, "hits": 1, "misses": 0}
        self.save()

    def invalidate_position(self, name: str):
        """Mark a cached position as unreliable."""
        positions = self.state.get("cached_positions", {})
        if name in positions:
            positions[name]["misses"] = positions[name].get("misses", 0) + 1
            if positions[name]["misses"] > positions[name].get("hits", 0):
                del positions[name]  # Too many misses, remove entirely
            self.save()

    def _track_power(self, power):
        history = self.state.get("power_history", [])
        history.append({"power": power, "time": time.time()})
        if len(history) > 200:
            history = history[-200:]
        self.state["power_history"] = history

    def get_summary(self) -> str:
        tc = self.state["account"].get("tc_level", "?")
        power = self.state["account"].get("power", 0)
        avail = self.builders_available()
        research = "idle" if self.research_idle() else "active"
        t_idle = self.training_idle()
        training = f"{len(t_idle)} idle" if t_idle else "all active"
        nxt = self.next_timer_completion()
        nxt_str = ""
        if nxt:
            secs = max(0, nxt[0] - time.time())
            nxt_str = f" | Next: {nxt[1]} in {secs/60:.0f}m"
        return (f"TC{tc} Power:{power:,} | Builders:{avail} free | "
                f"Research:{research} | Training:{training}{nxt_str}")
