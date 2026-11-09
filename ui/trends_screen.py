"""Trends Screen for Cadence (chinni-app).

Displays score trends across tests and spend rankings (calculates where
the student should spend study hours to maximize score gain).
"""

import customtkinter as ctk
from ui import api_client


class TrendsScreen(ctk.CTkFrame):
    def __init__(self, parent, app_state, on_navigate):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_navigate = on_navigate

        self._build_ui()
        self.refresh_trends()

    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        header_frame.pack(fill="x", padx=15, pady=(10, 15))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            title_box,
            text="SCORE TRENDS & SPEND RANKING",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Data-driven guidance: Where to spend your next study hours",
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

        # 1. Spend Ranking Recommendations Card
        self.ranking_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.ranking_card.pack(fill="x", pady=10)

        rank_head = ctk.CTkFrame(self.ranking_card, fg_color="transparent")
        rank_head.pack(fill="x", padx=20, pady=(15, 8))

        ctk.CTkLabel(
            rank_head,
            text="🎯 Recommended Focus & Study Hour Allocation (Next 20 Hours)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(side="left")

        self.rankings_container = ctk.CTkFrame(self.ranking_card, fg_color="transparent")
        self.rankings_container.pack(fill="x", padx=20, pady=(0, 15))

        # 2. Score Progression Over Tests
        ctk.CTkLabel(
            self.scroll_frame,
            text="Test Score Progression (T1, T2, T3...)",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(15, 8))

        self.trend_table = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.trend_table.pack(fill="x", pady=5)

    def refresh_trends(self):
        curr_track = self.app_state.get("current_track")
        if not curr_track:
            return

        track_id = curr_track["id"]

        # Render Spend Rankings
        for w in self.rankings_container.winfo_children():
            w.destroy()

        try:
            rankings_data = api_client.get_focus_rankings(track_id, available_hours=20.0)
            allocations = rankings_data.get("recommended_allocations", [])

            if not allocations:
                ctk.CTkLabel(
                    self.rankings_container,
                    text="Log more tests to calculate subject and group focus recommendations.",
                    text_color="#94A3B8",
                ).pack(pady=10)
            else:
                for alloc in allocations:
                    row = ctk.CTkFrame(self.rankings_container, fg_color=("#CBD5E1", "#0F172A"), corner_radius=8)
                    row.pack(fill="x", pady=4)

                    inner = ctk.CTkFrame(row, fg_color="transparent")
                    inner.pack(fill="x", padx=12, pady=10)

                    # Priority badge
                    prio = alloc.get("priority", "MEDIUM")
                    badge_color = "#EF4444" if prio == "HIGH" else "#F59E0B"
                    ctk.CTkLabel(
                        inner,
                        text=f"[{prio}]",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=badge_color,
                    ).pack(side="left", padx=(0, 8))

                    # Group and Subject
                    ctk.CTkLabel(
                        inner,
                        text=f"{alloc.get('subject_name', '')} • {alloc.get('group_code', '')}: {alloc.get('group_name', '')}",
                        font=ctk.CTkFont(size=13, weight="bold"),
                    ).pack(side="left")

                    # Recommended hours
                    hrs = alloc.get("recommended_hours", 0.0)
                    ctk.CTkLabel(
                        inner,
                        text=f"Allocate {hrs:.1f} Hours",
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=("#0284C7", "#38BDF8"),
                    ).pack(side="right")

        except Exception as e:
            print(f"[TrendsScreen Ranking Error] {e}")

        # Render Progression Table
        for w in self.trend_table.winfo_children():
            w.destroy()

        try:
            tests = api_client.get_track_tests(track_id)
            if not tests:
                ctk.CTkLabel(self.trend_table, text="No tests recorded yet.", text_color="#94A3B8").pack(pady=15)
                return

            # Table Header
            th = ctk.CTkFrame(self.trend_table, fg_color="transparent")
            th.pack(fill="x", padx=15, pady=(12, 6))

            ctk.CTkLabel(th, text="Test", width=80, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(th, text="Date", width=110, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(th, text="Total Score", width=120, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(th, text="Maths", width=80, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(th, text="Physics", width=80, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(th, text="Chemistry", width=80, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(th, text="Notes", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)

            prev_score = None
            for t in tests:
                t_row = ctk.CTkFrame(self.trend_table, fg_color=("#CBD5E1", "#0F172A"), corner_radius=6)
                t_row.pack(fill="x", padx=15, pady=3)

                r_inner = ctk.CTkFrame(t_row, fg_color="transparent")
                r_inner.pack(fill="x", padx=10, pady=8)

                ctk.CTkLabel(r_inner, text=t["test_code"], width=70, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
                ctk.CTkLabel(r_inner, text=t["test_date"], width=110).pack(side="left")

                tot = t["total_score"]
                delta_str = ""
                if prev_score is not None:
                    d = tot - prev_score
                    delta_str = f" (+{d:.0f})" if d >= 0 else f" ({d:.0f})"
                prev_score = tot

                ctk.CTkLabel(
                    r_inner,
                    text=f"{tot:.0f} / {t['max_score']:.0f}{delta_str}",
                    width=120,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("#0284C7", "#38BDF8"),
                ).pack(side="left")

                # Extract subject scores
                sub_scores = {s.get("subject_code", s.get("subject_name", "")): s["score"] for s in t.get("subject_scores", [])}
                m_score = sub_scores.get("MATH", sub_scores.get("Mathematics", "-"))
                p_score = sub_scores.get("PHY", sub_scores.get("Physics", "-"))
                c_score = sub_scores.get("CHEM", sub_scores.get("Chemistry", "-"))

                ctk.CTkLabel(r_inner, text=f"{m_score}", width=80).pack(side="left")
                ctk.CTkLabel(r_inner, text=f"{p_score}", width=80).pack(side="left")
                ctk.CTkLabel(r_inner, text=f"{c_score}", width=80).pack(side="left")
                ctk.CTkLabel(r_inner, text=t.get("notes", "") or "-", text_color="#94A3B8").pack(side="left", padx=10)

            # Bottom padding
            ctk.CTkFrame(self.trend_table, height=10, fg_color="transparent").pack()

        except Exception as e:
            print(f"[TrendsScreen Table Error] {e}")
