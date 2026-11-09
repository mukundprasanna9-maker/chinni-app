"""Home Screen for Cadence (chinni-app).

Displays student profile, academic track scorecard, subject summaries,
and adherence metrics.
"""

import customtkinter as ctk
from ui import api_client


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, app_state, on_navigate):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_navigate = on_navigate

        self._build_header()
        self._build_content()
        self.refresh_data()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        header_frame.pack(fill="x", padx=15, pady=(10, 15))

        # Title & Subtitle
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=15)

        title = ctk.CTkLabel(
            title_box,
            text="CADENCE",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_box,
            text="Study Rhythm & Multi-Subject Score Tracker",
            font=ctk.CTkFont(size=12),
            text_color=("#64748B", "#94A3B8"),
        )
        subtitle.pack(anchor="w")

        # Student & Track Selector controls
        controls_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_box.pack(side="right", padx=20, pady=15)

        # Student Dropdown
        ctk.CTkLabel(controls_box, text="Student:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 6))
        self.student_var = ctk.StringVar()
        self.student_menu = ctk.CTkOptionMenu(
            controls_box,
            variable=self.student_var,
            values=["Loading..."],
            command=self._on_student_changed,
            width=140,
        )
        self.student_menu.pack(side="left", padx=(0, 15))

        # Track Dropdown
        ctk.CTkLabel(controls_box, text="Track:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 6))
        self.track_var = ctk.StringVar()
        self.track_menu = ctk.CTkOptionMenu(
            controls_box,
            variable=self.track_var,
            values=["Loading..."],
            command=self._on_track_changed,
            width=160,
        )
        self.track_menu.pack(side="left", padx=(0, 10))

    def _build_content(self):
        # Scrollable container for cards
        self.content_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_scroll.pack(fill="both", expand=True, padx=15, pady=5)

        # 1. Target & Score Hero Card
        self.hero_card = ctk.CTkFrame(self.content_scroll, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.hero_card.pack(fill="x", pady=10)

        hero_inner = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        hero_inner.pack(fill="x", padx=20, pady=20)

        # Left: Target & Latest
        left_box = ctk.CTkFrame(hero_inner, fg_color="transparent")
        left_box.pack(side="left", fill="both", expand=True)

        self.track_title_label = ctk.CTkLabel(
            left_box,
            text="JEE Main 2026",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        self.track_title_label.pack(anchor="w")

        self.score_display_label = ctk.CTkLabel(
            left_box,
            text="Latest: 205 / 300   |   Target: 235",
            font=ctk.CTkFont(size=15),
            text_color=("#2563EB", "#38BDF8"),
        )
        self.score_display_label.pack(anchor="w", pady=(5, 0))

        # Right: Metric Badges
        metrics_box = ctk.CTkFrame(hero_inner, fg_color="transparent")
        metrics_box.pack(side="right")

        self.gap_badge = ctk.CTkLabel(
            metrics_box,
            text="Gap: 30 Marks Needed",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#FEF3C7", "#78350F"),
            text_color=("#B45309", "#FDE68A"),
            corner_radius=8,
            padx=12,
            pady=6,
        )
        self.gap_badge.pack(side="left", padx=5)

        self.trend_badge = ctk.CTkLabel(
            metrics_box,
            text="+17.0 Momentum",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#D1FAE5", "#064E3B"),
            text_color=("#047857", "#6EE7B7"),
            corner_radius=8,
            padx=12,
            pady=6,
        )
        self.trend_badge.pack(side="left", padx=5)

        # 2. Subject Breakdown Section
        subj_header = ctk.CTkLabel(
            self.content_scroll,
            text="Subject Breakdown (Maths, Physics, Chemistry)",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        subj_header.pack(anchor="w", pady=(15, 8))

        self.subjects_container = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.subjects_container.pack(fill="x", pady=5)

        # 3. Action Buttons & Quick Nav
        actions_header = ctk.CTkLabel(
            self.content_scroll,
            text="Quick Navigation",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        actions_header.pack(anchor="w", pady=(20, 8))

        actions_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        actions_frame.pack(fill="x", pady=5)

        btn_log = ctk.CTkButton(
            actions_frame,
            text="📝 Log a Test (T1, T2, T3...)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            height=40,
            command=lambda: self.on_navigate("tests"),
        )
        btn_log.pack(side="left", fill="x", expand=True, padx=5)

        btn_trends = ctk.CTkButton(
            actions_frame,
            text="📈 Trends & Spend Ranking",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0D9488",
            hover_color="#0F766E",
            height=40,
            command=lambda: self.on_navigate("trends"),
        )
        btn_trends.pack(side="left", fill="x", expand=True, padx=5)

        btn_timer = ctk.CTkButton(
            actions_frame,
            text="⏱️ Focus Timer & Adherence",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            height=40,
            command=lambda: self.on_navigate("timer"),
        )
        btn_timer.pack(side="left", fill="x", expand=True, padx=5)

    def refresh_data(self):
        """Loads students, tracks, and active track scorecard."""
        try:
            students = api_client.get_students()
            if not students:
                self.student_menu.configure(values=["No Students"])
                return

            self.app_state["students"] = students
            student_names = [s["name"] for s in students]
            self.student_menu.configure(values=student_names)

            curr_s = self.app_state.get("current_student")
            if not curr_s or curr_s["name"] not in student_names:
                curr_s = students[0]
                self.app_state["current_student"] = curr_s

            self.student_var.set(curr_s["name"])

            # Load tracks for this student
            tracks = api_client.get_student_tracks(curr_s["id"])
            if not tracks:
                self.track_menu.configure(values=["No Tracks"])
                return

            self.app_state["tracks"] = tracks
            track_names = [t["name"] for t in tracks]
            self.track_menu.configure(values=track_names)

            curr_t = self.app_state.get("current_track")
            if not curr_t or curr_t["name"] not in track_names:
                curr_t = tracks[0]
                self.app_state["current_track"] = curr_t

            self.track_var.set(curr_t["name"])
            self._render_scorecard(curr_t["id"])

        except Exception as e:
            print(f"[HomeScreen Warning] Could not load data from API: {e}")

    def _render_scorecard(self, track_id: int):
        try:
            scorecard = api_client.get_track_scorecard(track_id)
            track = scorecard.get("track", {})

            self.track_title_label.configure(text=f"{track.get('name', 'Academic Track')}")
            latest = scorecard.get("latest_score", 0.0)
            max_s = track.get("max_score", 300)
            target = track.get("target_score", 235)

            self.score_display_label.configure(
                text=f"Latest Score: {latest:.1f} / {max_s}   |   Target Score: {target}"
            )

            gap = scorecard.get("gap_to_target", 0.0)
            if gap <= 0:
                self.gap_badge.configure(
                    text="🎯 Target Achieved!",
                    fg_color=("#D1FAE5", "#064E3B"),
                    text_color=("#047857", "#6EE7B7"),
                )
            else:
                self.gap_badge.configure(
                    text=f"Deficit: {gap:.1f} Marks Needed",
                    fg_color=("#FEF3C7", "#78350F"),
                    text_color=("#B45309", "#FDE68A"),
                )

            delta = scorecard.get("trend_delta", 0.0)
            prefix = "+" if delta >= 0 else ""
            self.trend_badge.configure(text=f"{prefix}{delta:.1f} Momentum (Test Trend)")

            # Render Subject Cards
            for w in self.subjects_container.winfo_children():
                w.destroy()

            sub_avgs = scorecard.get("subject_averages", {})
            if not sub_avgs:
                no_data = ctk.CTkLabel(
                    self.subjects_container,
                    text="No tests logged yet for this track. Click 'Log a Test' below to begin!",
                    text_color="#94A3B8",
                )
                no_data.pack(pady=10)
                return

            # Arrange cards horizontally in columns
            col_idx = 0
            for code, s_data in sub_avgs.items():
                card = ctk.CTkFrame(
                    self.subjects_container,
                    fg_color=("#E2E8F0", "#1E293B"),
                    corner_radius=10,
                    width=200,
                )
                card.pack(side="left", fill="both", expand=True, padx=6, pady=5)

                ctk.CTkLabel(
                    card,
                    text=f"{s_data['name']} ({code})",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#0F172A", "#F8FAFC"),
                ).pack(anchor="w", padx=15, pady=(12, 4))

                avg_val = s_data.get("avg_score", 0.0)
                max_val = s_data.get("avg_max", 100.0)
                pct_val = s_data.get("avg_percentage", 0.0)

                ctk.CTkLabel(
                    card,
                    text=f"Avg: {avg_val:.1f} / {max_val:.0f}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=("#2563EB", "#38BDF8"),
                ).pack(anchor="w", padx=15, pady=2)

                ctk.CTkLabel(
                    card,
                    text=f"Accuracy: {pct_val:.1f}% across {s_data.get('test_count', 0)} tests",
                    font=ctk.CTkFont(size=11),
                    text_color=("#64748B", "#94A3B8"),
                ).pack(anchor="w", padx=15, pady=(0, 12))

                col_idx += 1

        except Exception as e:
            print(f"[Scorecard Render Error] {e}")

    def _on_student_changed(self, choice: str):
        for s in self.app_state.get("students", []):
            if s["name"] == choice:
                self.app_state["current_student"] = s
                self.refresh_data()
                break

    def _on_track_changed(self, choice: str):
        for t in self.app_state.get("tracks", []):
            if t["name"] == choice:
                self.app_state["current_track"] = t
                self._render_scorecard(t["id"])
                break
