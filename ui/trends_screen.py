"""Trends Screen for Cadence (chinni-app).

Displays score trends across tests and a flexible, suggestive study mix
that adapts to logged tests and Focus Timer blocks without assuming fixed
weekly hours. Each suggestion can launch directly into the Focus Timer.
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
            text="SCORE TRENDS & SUGGESTED STUDY MIX",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Flexible chapter guidance that adapts to your tests and Focus Timer sessions",
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

        # 1. Suggestive Focus Mix Card
        self.ranking_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.ranking_card.pack(fill="x", pady=10)

        rank_head = ctk.CTkFrame(self.ranking_card, fg_color="transparent")
        rank_head.pack(fill="x", padx=20, pady=(15, 8))

        head_left = ctk.CTkFrame(rank_head, fg_color="transparent")
        head_left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            head_left,
            text="🧭 Suggested Study Mix (Fits Around Your Schedule)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            head_left,
            text="No rigid hour quotas — use these relative priorities whenever you have a free slot, or jump straight into a sprint",
            font=ctk.CTkFont(size=11),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w", pady=(2, 0))

        self.timer_total_badge = ctk.CTkLabel(
            rank_head,
            text="⏱️ 0m logged",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#CBD5E1", "#0F172A"),
            text_color=("#0284C7", "#38BDF8"),
            corner_radius=8,
            padx=10,
            pady=5,
        )
        self.timer_total_badge.pack(side="right")

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

    def _start_sprint_from_suggestion(self, suggestion: dict):
        """Send the chosen chapter & sprint preset directly to the Focus Timer."""
        ch_code = suggestion.get("chapter_code") or ""
        ch_name = suggestion.get("chapter_name") or ""
        chapter_label = f"{ch_code}: {ch_name}" if ch_code else ch_name
        self.app_state["timer_preset"] = {
            "subject_name": suggestion.get("subject_name", ""),
            "chapter_label": chapter_label,
            "minutes": int(suggestion.get("suggested_minutes", 45)),
            "style": suggestion.get("cadence_style", "Focused Drill"),
        }
        self.on_navigate("timer")

    def refresh_trends(self):
        curr_track = self.app_state.get("current_track")
        if not curr_track:
            return

        track_id = curr_track["id"]

        # Render Suggestive Focus Mix
        for w in self.rankings_container.winfo_children():
            w.destroy()

        try:
            rankings_data = api_client.get_focus_rankings(track_id)
            timer_summary = rankings_data.get("timer_summary", {})
            total_mins = int(timer_summary.get("total_minutes", 0))
            sess_count = int(timer_summary.get("session_count", 0))
            hrs, rem = divmod(total_mins, 60)
            time_str = f"{hrs}h {rem}m" if hrs > 0 else f"{rem}m"
            self.timer_total_badge.configure(text=f"⏱️ {time_str} across {sess_count} sprints")

            suggestions = rankings_data.get("focus_suggestions") or []
            if not suggestions:
                ctk.CTkLabel(
                    self.rankings_container,
                    text="Log tests with syllabus chapters to get personalized study suggestions.",
                    text_color="#94A3B8",
                ).pack(pady=10)
            else:
                tier_labels = {
                    "HIGH": ("HIGH LEVERAGE", "#EF4444"),
                    "MEDIUM": ("MOMENTUM", "#F59E0B"),
                    "LOW": ("KEEP SHARP", "#10B981"),
                }
                for sug in suggestions:
                    row = ctk.CTkFrame(self.rankings_container, fg_color=("#CBD5E1", "#0F172A"), corner_radius=8)
                    row.pack(fill="x", pady=5)

                    inner = ctk.CTkFrame(row, fg_color="transparent")
                    inner.pack(fill="x", padx=14, pady=10)

                    # Left column: Tier + Chapter + Suggestive Reason
                    left = ctk.CTkFrame(inner, fg_color="transparent")
                    left.pack(side="left", fill="x", expand=True)

                    top_line = ctk.CTkFrame(left, fg_color="transparent")
                    top_line.pack(anchor="w")

                    prio = sug.get("priority", "MEDIUM")
                    tier_txt, badge_color = tier_labels.get(prio, ("FOCUS", "#38BDF8"))
                    ctk.CTkLabel(
                        top_line,
                        text=f"[{tier_txt}]",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=badge_color,
                    ).pack(side="left", padx=(0, 8))

                    ch_code = sug.get("chapter_code", "")
                    ch_name = sug.get("chapter_name", "")
                    ctk.CTkLabel(
                        top_line,
                        text=f"{sug.get('subject_name', '')} • {ch_code}: {ch_name}",
                        font=ctk.CTkFont(size=13, weight="bold"),
                    ).pack(side="left")

                    share_pct = sug.get("effort_share_percent", 20)
                    style = sug.get("cadence_style", "Timed Practice")
                    reason = sug.get("reason", "")
                    ctk.CTkLabel(
                        left,
                        text=f"Suggested: {style} (~{share_pct}% of your study time)   |   {reason}",
                        font=ctk.CTkFont(size=11),
                        text_color=("#475569", "#94A3B8"),
                    ).pack(anchor="w", pady=(3, 0))

                    # Right: Direct Launch Sprint Button -> Focus Timer
                    mins = int(sug.get("suggested_minutes", 45))
                    ctk.CTkButton(
                        inner,
                        text=f"▶ Start {mins}m Sprint",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        fg_color="#7C3AED",
                        hover_color="#6D28D9",
                        width=140,
                        height=34,
                        command=lambda s=sug: self._start_sprint_from_suggestion(s),
                    ).pack(side="right", padx=(10, 0))

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

            th = ctk.CTkFrame(self.trend_table, fg_color="transparent")
            th.pack(fill="x", padx=15, pady=(12, 6))

            ctk.CTkLabel(th, text="Test", width=80, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(th, text="Date", width=110, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(th, text="Total Score", width=120, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

            subject_code_order = []
            seen_codes = set()
            for t in tests:
                for s in t.get("subject_scores", []):
                    code = s.get("subject_code") or s.get("subject_name", "?")
                    if code not in seen_codes:
                        seen_codes.add(code)
                        subject_code_order.append(code)

            for code in subject_code_order:
                ctk.CTkLabel(th, text=code, width=80, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
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

                sub_scores = {
                    s.get("subject_code") or s.get("subject_name", "?"): s["score"]
                    for s in t.get("subject_scores", [])
                }
                for code in subject_code_order:
                    score_val = sub_scores.get(code, "-")
                    display = f"{score_val:.0f}" if isinstance(score_val, (int, float)) else str(score_val)
                    ctk.CTkLabel(r_inner, text=display, width=80).pack(side="left")
                ctk.CTkLabel(r_inner, text=t.get("notes", "") or "-", text_color="#94A3B8").pack(side="left", padx=10)

            ctk.CTkFrame(self.trend_table, height=10, fg_color="transparent").pack()

        except Exception as e:
            print(f"[TrendsScreen Table Error] {e}")
