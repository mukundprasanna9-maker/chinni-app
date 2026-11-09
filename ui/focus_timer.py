"""Focus Timer Screen for Cadence (chinni-app).

Provides an interactive Pomodoro / study focus timer, logs completed
sessions tagged by subject and group, and shows weekly plan adherence.
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
            text="FOCUS TIMER & STUDY ADHERENCE",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Deep work sessions tagged to subjects and prioritized groups",
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

        # Timer & Tagging Card
        self.timer_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.timer_card.pack(fill="x", pady=10)

        # Tagging Row (Subject & Group)
        tag_row = ctk.CTkFrame(self.timer_card, fg_color="transparent")
        tag_row.pack(fill="x", padx=20, pady=(15, 10))

        # Subject Selector
        s_box = ctk.CTkFrame(tag_row, fg_color="transparent")
        s_box.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(s_box, text="Study Subject:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.subject_var = ctk.StringVar(value="Mathematics")
        self.subject_menu = ctk.CTkOptionMenu(
            s_box,
            variable=self.subject_var,
            values=["Mathematics", "Physics", "Chemistry"],
            width=160,
        )
        self.subject_menu.pack(pady=(4, 0))

        # Group Selector
        g_box = ctk.CTkFrame(tag_row, fg_color="transparent")
        g_box.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(g_box, text="Focus Group:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.group_var = ctk.StringVar(value="G1")
        self.group_menu = ctk.CTkOptionMenu(
            g_box,
            variable=self.group_var,
            values=["G1", "G2", "G3"],
            width=140,
        )
        self.group_menu.pack(pady=(4, 0))

        # Duration Preset Buttons
        p_box = ctk.CTkFrame(tag_row, fg_color="transparent")
        p_box.pack(side="right")
        ctk.CTkLabel(p_box, text="Preset Blocks:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")

        p_btns = ctk.CTkFrame(p_box, fg_color="transparent")
        p_btns.pack(pady=(4, 0))

        ctk.CTkButton(p_btns, text="25m", width=55, command=lambda: self._set_duration(25)).pack(side="left", padx=2)
        ctk.CTkButton(p_btns, text="45m", width=55, command=lambda: self._set_duration(45)).pack(side="left", padx=2)
        ctk.CTkButton(p_btns, text="60m", width=55, command=lambda: self._set_duration(60)).pack(side="left", padx=2)

        # Big Digital Clock
        self.clock_label = ctk.CTkLabel(
            self.timer_card,
            text="25:00",
            font=ctk.CTkFont(size=64, weight="bold"),
            text_color=("#0284C7", "#38BDF8"),
        )
        self.clock_label.pack(pady=20)

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

        ctk.CTkButton(
            ctrl_row,
            text="↺ Reset",
            font=ctk.CTkFont(size=14),
            fg_color="#64748B",
            hover_color="#475569",
            width=90,
            height=40,
            command=self._reset_timer,
        )
        self.start_pause_btn.pack(side="left", padx=8)

        ctk.CTkButton(
            ctrl_row,
            text="✓ Log Completed Block",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            height=40,
            command=self._log_session,
        ).pack(side="left", padx=8)

        # Adherence Summary Card
        self.adherence_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.adherence_card.pack(fill="x", pady=10)

        adh_inner = ctk.CTkFrame(self.adherence_card, fg_color="transparent")
        adh_inner.pack(fill="x", padx=20, pady=15)

        self.adherence_label = ctk.CTkLabel(
            adh_inner,
            text="Weekly Study Adherence: Calculating...",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        self.adherence_label.pack(side="left")

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

    def refresh_timer_screen(self):
        curr_student = self.app_state.get("current_student")
        if not curr_student:
            return

        sid = curr_student["id"]

        # Load Adherence
        try:
            adh = api_client.get_student_adherence(sid)
            pct = adh.get("overall_adherence_percent", 100.0)
            status = adh.get("status", "ON TRACK")
            planned = adh.get("total_planned_hours", 0.0)
            actual = adh.get("total_actual_hours", 0.0)

            self.adherence_label.configure(
                text=f"Weekly Adherence: {pct:.1f}% ({actual:.1f}h completed / {planned:.1f}h planned)"
            )
            color_bg = ("#D1FAE5", "#064E3B") if pct >= 80 else ("#FEF3C7", "#78350F")
            color_text = ("#047857", "#6EE7B7") if pct >= 80 else ("#B45309", "#FDE68A")
            self.adherence_badge.configure(text=status, fg_color=color_bg, text_color=color_text)
        except Exception as e:
            print(f"[Timer Adherence Error] {e}")

        # Load Sessions
        for w in self.sessions_container.winfo_children():
            w.destroy()

        try:
            sessions = api_client.get_focus_sessions(sid)
            if not sessions:
                ctk.CTkLabel(
                    self.sessions_container,
                    text="No focus sessions recorded yet. Start the timer and log your first block!",
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
                grp_str = f" • {s.get('group_name')}" if s.get("group_name") else ""
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

    def _set_duration(self, minutes: int):
        self._reset_timer()
        self.selected_duration_minutes = minutes
        self.timer_seconds_left = minutes * 60
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
        curr_student = self.app_state.get("current_student")
        if not curr_student:
            return

        payload = {
            "duration_minutes": self.selected_duration_minutes,
            "notes": f"Completed {self.subject_var.get()} ({self.group_var.get()}) study block",
            "adherence_status": "COMPLETED",
        }
        try:
            api_client.log_focus_session(curr_student["id"], payload)
            self._reset_timer()
            self.refresh_timer_screen()
        except Exception as e:
            print(f"[Log Session Error] {e}")
