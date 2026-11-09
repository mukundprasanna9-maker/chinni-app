"""Tests Screen for Cadence (chinni-app).

Implements the end-to-end 'Log a Test' slice:
Captures Test code (T1, T2, T3...), Test Date, Multi-Subject breakdown
(Maths, Physics, Chemistry), and Group breakdown (G1, G2, G3).
"""

from datetime import date
import customtkinter as ctk
from ui import api_client


class TestsScreen(ctk.CTkFrame):
    def __init__(self, parent, app_state, on_navigate):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_navigate = on_navigate

        self.subject_entries = {}  # subject_id -> CTkEntry
        self.group_entries = {}    # group_id -> CTkEntry

        self._build_ui()
        self.refresh_form()

    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        header_frame.pack(fill="x", padx=15, pady=(10, 15))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            title_box,
            text="LOG A TEST ATTEMPT",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Trace a test through UI -> API Client -> Routes -> Service -> SQL",
            font=ctk.CTkFont(size=12),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w")

        # Back to Home Button
        ctk.CTkButton(
            header_frame,
            text="← Back to Dashboard",
            width=150,
            fg_color="#475569",
            hover_color="#334155",
            command=lambda: self.on_navigate("home"),
        ).pack(side="right", padx=20, pady=15)

        # Scrollable container for Form + History
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Form Card
        self.form_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.form_card.pack(fill="x", pady=10)

        # Test Basic Details Row
        row1 = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(15, 10))

        # Test Code (e.g. T4)
        c_box = ctk.CTkFrame(row1, fg_color="transparent")
        c_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(c_box, text="Test Code / Label (e.g. T4, Mock 4):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.test_code_entry = ctk.CTkEntry(c_box, placeholder_text="T4")
        self.test_code_entry.pack(fill="x", pady=(4, 0))

        # Test Date
        d_box = ctk.CTkFrame(row1, fg_color="transparent")
        d_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(d_box, text="Test Date (YYYY-MM-DD):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.test_date_entry = ctk.CTkEntry(d_box)
        self.test_date_entry.insert(0, str(date.today()))
        self.test_date_entry.pack(fill="x", pady=(4, 0))

        # Notes
        n_box = ctk.CTkFrame(row1, fg_color="transparent")
        n_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(n_box, text="Notes / Observations:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.notes_entry = ctk.CTkEntry(n_box, placeholder_text="e.g. Attempted with strict timer")
        self.notes_entry.pack(fill="x", pady=(4, 0))

        # Dynamic Subjects & Groups Form Container
        self.subjects_form_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.subjects_form_frame.pack(fill="x", padx=20, pady=10)

        # Save Button & Status Row
        btn_row = ctk.CTkFrame(self.form_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(10, 15))

        self.save_btn = ctk.CTkButton(
            btn_row,
            text="💾 Save Test Attempt",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            height=42,
            command=self._on_save_test,
        )
        self.save_btn.pack(side="left", padx=(0, 15))

        self.status_label = ctk.CTkLabel(
            btn_row,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.status_label.pack(side="left")

        # History Section
        ctk.CTkLabel(
            self.scroll_frame,
            text="Logged Test History",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(20, 8))

        self.history_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.history_container.pack(fill="x", pady=5)

    def refresh_form(self):
        """Loads active track structure and dynamically renders subject & group input rows."""
        curr_track = self.app_state.get("current_track")
        if not curr_track:
            return

        # Fetch full track with subjects and groups
        try:
            track_data = api_client.get_track(curr_track["id"])
            self.app_state["current_track_full"] = track_data

            # Clear existing form entries
            for w in self.subjects_form_frame.winfo_children():
                w.destroy()
            self.subject_entries.clear()
            self.group_entries.clear()

            subjects = track_data.get("subjects", [])
            for sub in subjects:
                sub_card = ctk.CTkFrame(self.subjects_form_frame, fg_color=("#CBD5E1", "#0F172A"), corner_radius=8)
                sub_card.pack(fill="x", pady=6)

                # Subject Header with Total Subject Score
                top_row = ctk.CTkFrame(sub_card, fg_color="transparent")
                top_row.pack(fill="x", padx=15, pady=(10, 6))

                ctk.CTkLabel(
                    top_row,
                    text=f"{sub['name']} ({sub['code']})",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#0F172A", "#38BDF8"),
                ).pack(side="left")

                s_entry = ctk.CTkEntry(top_row, width=100, placeholder_text=f"Score / {sub['max_marks']}")
                s_entry.pack(side="right")
                self.subject_entries[sub["id"]] = s_entry

                # Groups Breakdown for this Subject (G1, G2, G3)
                groups = sub.get("groups", [])
                if groups:
                    grp_row = ctk.CTkFrame(sub_card, fg_color="transparent")
                    grp_row.pack(fill="x", padx=15, pady=(0, 10))

                    for grp in groups:
                        g_box = ctk.CTkFrame(grp_row, fg_color="transparent")
                        g_box.pack(side="left", fill="x", expand=True, padx=4)

                        ctk.CTkLabel(
                            g_box,
                            text=f"{grp['group_code']}: {grp['name']}",
                            font=ctk.CTkFont(size=11),
                            text_color=("#475569", "#94A3B8"),
                        ).pack(anchor="w")

                        g_entry = ctk.CTkEntry(g_box, placeholder_text=f"Score (max ~{grp.get('weight_percentage', 33.3):.0f})")
                        g_entry.pack(fill="x", pady=(2, 0))
                        self.group_entries[grp["id"]] = g_entry

            self._refresh_history(curr_track["id"])

        except Exception as e:
            print(f"[TestsScreen Warning] Could not load track details: {e}")

    def _refresh_history(self, track_id: int):
        for w in self.history_container.winfo_children():
            w.destroy()

        try:
            tests = api_client.get_track_tests(track_id)
            if not tests:
                ctk.CTkLabel(
                    self.history_container,
                    text="No tests logged yet. Enter scores above and click 'Save Test Attempt'.",
                    text_color="#94A3B8",
                ).pack(pady=10)
                return

            for t in reversed(tests):
                card = ctk.CTkFrame(self.history_container, fg_color=("#E2E8F0", "#1E293B"), corner_radius=10)
                card.pack(fill="x", pady=6)

                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=12)

                # Code & Date
                left = ctk.CTkFrame(row, fg_color="transparent")
                left.pack(side="left")

                ctk.CTkLabel(
                    left,
                    text=f"{t['test_code']}  —  {t['test_date']}",
                    font=ctk.CTkFont(size=15, weight="bold"),
                ).pack(anchor="w")

                if t.get("notes"):
                    ctk.CTkLabel(left, text=t["notes"], font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(anchor="w")

                # Total Score Badge
                mid = ctk.CTkFrame(row, fg_color="transparent")
                mid.pack(side="left", padx=30)

                ctk.CTkLabel(
                    mid,
                    text=f"Total: {t['total_score']:.1f} / {t['max_score']:.0f}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=("#0284C7", "#38BDF8"),
                ).pack()

                # Subject breakdown pills
                sub_box = ctk.CTkFrame(row, fg_color="transparent")
                sub_box.pack(side="right")

                for s in t.get("subject_scores", []):
                    pill = ctk.CTkLabel(
                        sub_box,
                        text=f"{s.get('subject_code', 'SUB')}: {s['score']:.0f}",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        fg_color=("#CBD5E1", "#334155"),
                        corner_radius=6,
                        padx=8,
                        pady=3,
                    )
                    pill.pack(side="left", padx=4)

        except Exception as e:
            print(f"[History Render Warning] {e}")

    def _on_save_test(self):
        """Viva Trace Step 1: User clicks Save.

        Gathers entries, sends POST request via api_client.
        """
        curr_track = self.app_state.get("current_track")
        if not curr_track:
            self._show_status("Error: No active track selected", False)
            return

        code = self.test_code_entry.get().strip() or "T"
        t_date = self.test_date_entry.get().strip()
        notes = self.notes_entry.get().strip()

        # Gather Subject Scores
        subject_scores = []
        total_score = 0.0

        for sid, entry in self.subject_entries.items():
            val_str = entry.get().strip()
            score_val = float(val_str) if val_str else 0.0
            subject_scores.append({
                "subject_id": sid,
                "score": score_val,
                "max_score": 100.0,
            })
            total_score += score_val

        # Gather Group Scores (G1, G2, G3)
        group_scores = []
        for gid, entry in self.group_entries.items():
            val_str = entry.get().strip()
            score_val = float(val_str) if val_str else 0.0
            group_scores.append({
                "group_id": gid,
                "score": score_val,
                "max_score": 33.3,
            })

        payload = {
            "test_code": code,
            "test_date": t_date,
            "total_score": total_score,
            "max_score": float(curr_track.get("max_score", 300.0)),
            "notes": notes,
            "subject_scores": subject_scores,
            "group_scores": group_scores,
        }

        try:
            # Viva Step 2: UI calls api_client.log_test
            saved_test = api_client.log_test(curr_track["id"], payload)
            self._show_status(f"✓ Saved {saved_test['test_code']} with Score {saved_test['total_score']:.1f}!", True)
            self._refresh_history(curr_track["id"])
            # Clear entries
            self.test_code_entry.delete(0, "end")
            self.notes_entry.delete(0, "end")
            for e in self.subject_entries.values():
                e.delete(0, "end")
            for e in self.group_entries.values():
                e.delete(0, "end")
        except Exception as e:
            self._show_status(f"Error saving test: {e}", False)

    def _show_status(self, msg: str, success: bool):
        color = "#10B981" if success else "#EF4444"
        self.status_label.configure(text=msg, text_color=color)
