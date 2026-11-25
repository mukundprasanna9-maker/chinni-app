"""Focus Timer Screen for Cadence (chinni-app).

Provides an interactive Pomodoro / study focus timer connected directly to
the suggestive Focus Queue: surfaces "Suggested Next Up" right above the
timer, accepts one-click sprint presets from TrendsScreen, and feeds logged
sessions back into future focus suggestions.
"""

import customtkinter as ctk
from ui import api_client


class FocusTimerScreen(ctk.CTkFrame):
    def __init__(self, parent, app_state, on_navigate):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_navigate = on_navigate

        self.timer_seconds_left = 25 * 60
        self.selected_duration_minutes = 25
        self.timer_running = False
        self._timer_job = None

        self._subject_map = {}   # name -> subject dict
        self._chapter_map = {}   # "M01: Sets, Relations & Functions" -> chapter dict
        self._chapter_is_legacy_group = False
        self._top_suggestion = None
        self._preset_buttons = {}

        self._build_ui()
        self.refresh_timer_screen()

    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        header_frame.pack(fill="x", padx=15, pady=(10, 15))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            title_box,
            text="FOCUS TIMER & STUDY CADENCE",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Deep work sprints linked to your chapter suggestions and logged sessions",
            font=ctk.CTkFont(size=12),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w")

        ctk.CTkButton(
            header_frame,
            text="← Back to Dashboard",
            width=150,
            fg_color="#475569",
            hover_color="#334155",
            command=lambda: self.on_navigate("home"),
        ).pack(side="right", padx=20, pady=15)

        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # ✨ Suggested Next Up Banner (links Trends suggestions <-> Focus Timer)
        self.suggestion_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=("#DBEAFE", "#172554"),
            corner_radius=12,
        )
        self.suggestion_card.pack(fill="x", pady=(4, 10))

        sug_inner = ctk.CTkFrame(self.suggestion_card, fg_color="transparent")
        sug_inner.pack(fill="x", padx=18, pady=12)

        sug_left = ctk.CTkFrame(sug_inner, fg_color="transparent")
        sug_left.pack(side="left", fill="x", expand=True)

        self.suggestion_title = ctk.CTkLabel(
            sug_left,
            text="✨ Suggested Next Up: Checking your recent tests...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1E3A8A", "#93C5FD"),
        )
        self.suggestion_title.pack(anchor="w")

        self.suggestion_sub = ctk.CTkLabel(
            sug_left,
            text="Pick any slot in your day — your completed sprints automatically balance future suggestions.",
            font=ctk.CTkFont(size=11),
            text_color=("#3B82F6", "#BFDBFE"),
        )
        self.suggestion_sub.pack(anchor="w", pady=(2, 0))

        self.load_sug_btn = ctk.CTkButton(
            sug_inner,
            text="⚡ Load Suggested",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            width=135,
            height=34,
            command=self._apply_top_suggestion,
        )
        self.load_sug_btn.pack(side="right", padx=(10, 0))

        # Timer & Tagging Card
        self.timer_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.timer_card.pack(fill="x", pady=8)

        # Tagging Row (Subject & Chapter)
        tag_row = ctk.CTkFrame(self.timer_card, fg_color="transparent")
        tag_row.pack(fill="x", padx=20, pady=(15, 10))

        s_box = ctk.CTkFrame(tag_row, fg_color="transparent")
        s_box.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(s_box, text="Study Subject:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.subject_var = ctk.StringVar(value="Loading...")
        self.subject_menu = ctk.CTkOptionMenu(
            s_box,
            variable=self.subject_var,
            values=["Loading..."],
            command=self._on_subject_changed,
            width=180,
        )
        self.subject_menu.pack(pady=(4, 0))

        g_box = ctk.CTkFrame(tag_row, fg_color="transparent")
        g_box.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(g_box, text="Focus Chapter:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.group_var = ctk.StringVar(value="Loading...")
        self.group_menu = ctk.CTkOptionMenu(
            g_box,
            variable=self.group_var,
            values=["Loading..."],
            width=250,
        )
        self.group_menu.pack(pady=(4, 0))

        # Duration Preset Buttons
        p_box = ctk.CTkFrame(tag_row, fg_color="transparent")
        p_box.pack(side="right")
        ctk.CTkLabel(p_box, text="Sprint Blocks:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")

        p_btns = ctk.CTkFrame(p_box, fg_color="transparent")
        p_btns.pack(pady=(4, 0))

        for mins in (25, 45, 60):
            btn = ctk.CTkButton(
                p_btns,
                text=f"{mins}m",
                width=55,
                command=lambda m=mins: self._set_duration(m),
            )
            btn.pack(side="left", padx=2)
            self._preset_buttons[mins] = btn
        self._highlight_preset_button(25)

        # Big Digital Clock
        self.clock_label = ctk.CTkLabel(
            self.timer_card,
            text="25:00",
            font=ctk.CTkFont(size=64, weight="bold"),
            text_color=("#0284C7", "#38BDF8"),
        )
        self.clock_label.pack(pady=(16, 4))

        self.sprint_status_label = ctk.CTkLabel(
            self.timer_card,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10B981",
        )
        self.sprint_status_label.pack(pady=(0, 10))

        # Timer Controls
        ctrl_row = ctk.CTkFrame(self.timer_card, fg_color="transparent")
        ctrl_row.pack(pady=(0, 20))

        self.start_pause_btn = ctk.CTkButton(
            ctrl_row,
            text="▶ Start Focus",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            width=130,
            height=40,
            command=self._toggle_timer,
        )
        self.start_pause_btn.pack(side="left", padx=8)

        self.reset_btn = ctk.CTkButton(
            ctrl_row,
            text="↺ Reset",
            font=ctk.CTkFont(size=14),
            fg_color="#64748B",
            hover_color="#475569",
            width=90,
            height=40,
            command=self._reset_timer,
        )
        self.reset_btn.pack(side="left", padx=8)

        ctk.CTkButton(
            ctrl_row,
            text="✓ Log Completed Block",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            height=40,
            command=self._log_session,
        ).pack(side="left", padx=8)

        # Study Activity & Adherence Card
        self.adherence_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.adherence_card.pack(fill="x", pady=10)

        adh_inner = ctk.CTkFrame(self.adherence_card, fg_color="transparent")
        adh_inner.pack(fill="x", padx=20, pady=15)

        adh_left = ctk.CTkFrame(adh_inner, fg_color="transparent")
        adh_left.pack(side="left")

        self.timer_activity_label = ctk.CTkLabel(
            adh_left,
            text="Focus Timer Activity: Calculating...",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        self.timer_activity_label.pack(anchor="w")

        self.adherence_label = ctk.CTkLabel(
            adh_left,
            text="Weekly Study Adherence: Calculating...",
            font=ctk.CTkFont(size=12),
            text_color=("#64748B", "#94A3B8"),
        )
        self.adherence_label.pack(anchor="w", pady=(2, 0))

        self.adherence_badge = ctk.CTkLabel(
            adh_inner,
            text="ON TRACK",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#D1FAE5", "#064E3B"),
            text_color=("#047857", "#6EE7B7"),
            corner_radius=6,
            padx=10,
            pady=4,
        )
        self.adherence_badge.pack(side="right")

        # Recent Sessions List
        ctk.CTkLabel(
            self.scroll_frame,
            text="Recent Completed Focus Sessions",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(15, 8))

        self.sessions_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.sessions_container.pack(fill="x", pady=5)

    def _highlight_preset_button(self, active_minutes: int):
        for mins, btn in self._preset_buttons.items():
            if mins == active_minutes:
                btn.configure(fg_color="#0284C7", hover_color="#0369A1")
            else:
                btn.configure(fg_color="#475569", hover_color="#334155")

    def _apply_preset_dict(self, subject_name: str, chapter_label: str, minutes: int, status_msg: str = ""):
        if subject_name and subject_name in self._subject_map:
            self.subject_var.set(subject_name)
            self._populate_groups_for_subject(subject_name)
        if chapter_label and chapter_label in self._chapter_map:
            self.group_var.set(chapter_label)
        if minutes in (25, 45, 60):
            self._set_duration(minutes)
        if status_msg:
            self.sprint_status_label.configure(text=status_msg)

    def _apply_top_suggestion(self):
        if not self._top_suggestion:
            return
        ch_code = self._top_suggestion.get("chapter_code", "")
        ch_name = self._top_suggestion.get("chapter_name", "")
        label = f"{ch_code}: {ch_name}" if ch_code else ch_name
        mins = int(self._top_suggestion.get("suggested_minutes", 45))
        style = self._top_suggestion.get("cadence_style", "Focused Sprint")
        self._apply_preset_dict(
            self._top_suggestion.get("subject_name", ""),
            label,
            mins,
            status_msg=f"✓ Loaded {style}: {self._top_suggestion.get('subject_name', '')} • {label} ({mins}m)",
        )

    def refresh_timer_screen(self):
        curr_student = self.app_state.get("current_student")
        curr_track = self.app_state.get("current_track")
        if not curr_student:
            return

        self._load_subject_group_menus(curr_track)

        # Apply one-click preset if user clicked "▶ Start Xm Sprint" on TrendsScreen
        preset = self.app_state.pop("timer_preset", None)
        if preset:
            self._apply_preset_dict(
                preset.get("subject_name", ""),
                preset.get("chapter_label", ""),
                int(preset.get("minutes", 45)),
                status_msg=f"✓ Loaded {preset.get('style', 'Sprint')}: {preset.get('subject_name', '')} • {preset.get('chapter_label', '')} ({preset.get('minutes', 45)}m)",
            )

        # Load top suggestion for "Suggested Next Up" banner
        self._refresh_top_suggestion(curr_track)

        sid = curr_student["id"]

        # Load Adherence
        try:
            adh = api_client.get_student_adherence(sid)
            pct = adh.get("overall_adherence_percent", 100.0)
            status = adh.get("status", "ON TRACK")
            planned = adh.get("total_planned_hours", 0.0)
            actual = adh.get("total_actual_hours", 0.0)

            self.adherence_label.configure(
                text=f"Weekly Study Plan Adherence: {pct:.1f}% ({actual:.1f}h / {planned:.1f}h planned)"
            )
            color_bg = ("#D1FAE5", "#064E3B") if pct >= 80 else ("#FEF3C7", "#78350F")
            color_text = ("#047857", "#6EE7B7") if pct >= 80 else ("#B45309", "#FDE68A")
            self.adherence_badge.configure(text=status, fg_color=color_bg, text_color=color_text)
        except Exception as e:
            print(f"[Timer Adherence Error] {e}")

        # Load Sessions & Timer Activity Summary
        for w in self.sessions_container.winfo_children():
            w.destroy()

        try:
            sessions = api_client.get_focus_sessions(sid)
            total_mins = sum(int(s.get("duration_minutes") or 0) for s in sessions)
            hrs, rem = divmod(total_mins, 60)
            time_str = f"{hrs}h {rem}m" if hrs > 0 else f"{rem}m"
            sess_word = "session" if len(sessions) == 1 else "sessions"
            self.timer_activity_label.configure(
                text=f"Focus Timer Activity: {time_str} logged across {len(sessions)} {sess_word}"
            )

            if not sessions:
                ctk.CTkLabel(
                    self.sessions_container,
                    text="No focus sessions recorded yet. Start the timer and log your first sprint!",
                    text_color="#94A3B8",
                ).pack(pady=10)
                return

            for s in sessions[:8]:
                row = ctk.CTkFrame(self.sessions_container, fg_color=("#CBD5E1", "#0F172A"), corner_radius=8)
                row.pack(fill="x", pady=4)

                inner = ctk.CTkFrame(row, fg_color="transparent")
                inner.pack(fill="x", padx=15, pady=10)

                ctk.CTkLabel(
                    inner,
                    text=f"⏱️ {s['duration_minutes']} Mins",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=("#0284C7", "#38BDF8"),
                ).pack(side="left", padx=(0, 15))

                sub_str = s.get("subject_name") or "Subject Block"
                ch_name = s.get("chapter_name") or s.get("group_name")
                grp_str = f" • {ch_name}" if ch_name else ""
                ctk.CTkLabel(
                    inner,
                    text=f"{sub_str}{grp_str}",
                    font=ctk.CTkFont(size=13),
                ).pack(side="left")

                notes_str = f" — {s['notes']}" if s.get("notes") else ""
                ctk.CTkLabel(
                    inner,
                    text=f"{notes_str}",
                    font=ctk.CTkFont(size=11),
                    text_color="#94A3B8",
                ).pack(side="left", padx=10)

                status_pill = ctk.CTkLabel(
                    inner,
                    text=s.get("adherence_status", "COMPLETED"),
                    font=ctk.CTkFont(size=10, weight="bold"),
                    fg_color=("#D1FAE5", "#064E3B"),
                    text_color=("#047857", "#6EE7B7"),
                    corner_radius=6,
                    padx=6,
                    pady=2,
                )
                status_pill.pack(side="right")

        except Exception as e:
            print(f"[Timer Sessions Render Error] {e}")

    def _refresh_top_suggestion(self, curr_track):
        self._top_suggestion = None
        if not curr_track:
            return
        try:
            data = api_client.get_focus_rankings(curr_track["id"])
            suggestions = data.get("focus_suggestions") or []
            if not suggestions:
                self.suggestion_title.configure(text="✨ Suggested Next Up: Log a test with chapters to unlock smart sprint suggestions")
                self.suggestion_sub.configure(text="Or choose any subject and chapter below to start a free-form focus sprint.")
                self.load_sug_btn.configure(state="disabled")
                return

            top = suggestions[0]
            self._top_suggestion = top
            self.load_sug_btn.configure(state="normal")
            ch_code = top.get("chapter_code", "")
            ch_name = top.get("chapter_name", "")
            mins = int(top.get("suggested_minutes", 45))
            style = top.get("cadence_style", "Focused Drill")
            share = top.get("effort_share_percent", 25)
            self.suggestion_title.configure(
                text=f"✨ Suggested Next Up: {top.get('subject_name', '')} • {ch_code}: {ch_name}  ({mins}m {style})"
            )
            self.suggestion_sub.configure(
                text=f"~{share}% suggested priority  |  {top.get('reason', '')}"
            )
        except Exception as e:
            print(f"[Timer Suggestion Error] {e}")

    def _load_subject_group_menus(self, curr_track):
        """Populate subject and chapter selectors from actual track data."""
        self._subject_map.clear()
        self._chapter_map.clear()

        if not curr_track:
            return

        try:
            track_data = api_client.get_track(curr_track["id"])
            subjects = track_data.get("subjects", [])

            subject_names = [s["name"] for s in subjects]
            if not subject_names:
                return

            self._subject_map = {s["name"]: s for s in subjects}
            self._all_subjects_data = subjects

            self.subject_menu.configure(values=subject_names)
            first_subject = subjects[0]["name"]
            self.subject_var.set(first_subject)
            self._populate_groups_for_subject(first_subject)

        except Exception as e:
            print(f"[FocusTimer] Could not load track subjects: {e}")

    def _on_subject_changed(self, subject_name: str):
        self._populate_groups_for_subject(subject_name)

    def _populate_groups_for_subject(self, subject_name: str):
        """Update the chapter dropdown based on the selected subject."""
        self._chapter_map.clear()
        self._chapter_is_legacy_group = False
        subject_data = self._subject_map.get(subject_name)
        if not subject_data:
            self.group_menu.configure(values=["No chapters"])
            self.group_var.set("No chapters")
            return

        chapters = subject_data.get("chapters", [])
        if chapters:
            labels = []
            for ch in chapters:
                label = f"{ch['chapter_code']}: {ch['name']}"
                self._chapter_map[label] = ch
                labels.append(label)
            self.group_menu.configure(values=labels)
            self.group_var.set(labels[0])
            return

        groups = subject_data.get("groups", [])
        if groups:
            self._chapter_is_legacy_group = True
            labels = []
            for g in groups:
                label = f"{g['group_code']}: {g['name']}"
                self._chapter_map[label] = g
                labels.append(label)
            self.group_menu.configure(values=labels)
            self.group_var.set(labels[0])
            return

        self.group_menu.configure(values=["No chapters"])
        self.group_var.set("No chapters")

    def _set_duration(self, minutes: int):
        self._reset_timer()
        self.selected_duration_minutes = minutes
        self.timer_seconds_left = minutes * 60
        self._highlight_preset_button(minutes)
        self._update_clock_display()

    def _update_clock_display(self):
        m = self.timer_seconds_left // 60
        s = self.timer_seconds_left % 60
        self.clock_label.configure(text=f"{m:02d}:{s:02d}")

    def _toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_pause_btn.configure(text="▶ Resume Focus", fg_color="#10B981")
            if self._timer_job:
                self.after_cancel(self._timer_job)
        else:
            self.timer_running = True
            self.start_pause_btn.configure(text="⏸ Pause", fg_color="#F59E0B")
            self._timer_tick()

    def _timer_tick(self):
        if not self.timer_running:
            return
        if self.timer_seconds_left > 0:
            self.timer_seconds_left -= 1
            self._update_clock_display()
            self._timer_job = self.after(1000, self._timer_tick)
        else:
            self.timer_running = False
            self.start_pause_btn.configure(text="▶ Start Focus", fg_color="#10B981")
            self._log_session()

    def _reset_timer(self):
        self.timer_running = False
        if self._timer_job:
            self.after_cancel(self._timer_job)
        self.timer_seconds_left = self.selected_duration_minutes * 60
        self.start_pause_btn.configure(text="▶ Start Focus", fg_color="#10B981")
        self._update_clock_display()

    def _log_session(self):
        """Include subject_id and chapter_id, then refresh live suggestions."""
        curr_student = self.app_state.get("current_student")
        if not curr_student:
            return

        subject_name = self.subject_var.get()
        chapter_label = self.group_var.get()

        subject_data = self._subject_map.get(subject_name)
        chapter_data = self._chapter_map.get(chapter_label)

        subject_id = subject_data["id"] if subject_data else None

        payload = {
            "duration_minutes": self.selected_duration_minutes,
            "notes": f"Completed {subject_name} — {chapter_label} sprint",
            "adherence_status": "COMPLETED",
        }

        if subject_id is not None:
            payload["subject_id"] = subject_id
        if chapter_data is not None:
            if self._chapter_is_legacy_group:
                payload["group_id"] = chapter_data["id"]
            else:
                payload["chapter_id"] = chapter_data["id"]

        try:
            api_client.log_focus_session(curr_student["id"], payload)
            self.sprint_status_label.configure(
                text=f"✓ Logged {self.selected_duration_minutes}m sprint on {chapter_label} — suggestions updated!"
            )
            self._reset_timer()
            self.refresh_timer_screen()
        except Exception as e:
            print(f"[Log Session Error] {e}")
