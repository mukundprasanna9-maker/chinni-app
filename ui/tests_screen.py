"""Tests Screen for Cadence (chinni-app).

Implements the 'Log a Test' screen with chapter-level syllabus selection:
Captures Test code, Test Date, Notes, Subject scores (and max marks for
full or part-syllabus tests), and checkboxes to tick the exact chapters
covered in the test's syllabus.
"""

from datetime import date
import customtkinter as ctk
from ui import api_client


class TestsScreen(ctk.CTkFrame):
    def __init__(self, parent, app_state, on_navigate):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_navigate = on_navigate

        self.subject_entries = {}       # subject_id -> CTkEntry (score)
        self.subject_max_entries = {}   # subject_id -> CTkEntry (max_score)
        self.chapter_vars = {}          # chapter_id -> ctk.BooleanVar
        self.subject_chapters = {}      # subject_id -> list[int] of chapter_ids
        self.subject_count_labels = {}  # subject_id -> CTkLabel

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
            text="Enter your subject scores and tick the syllabus chapters included in this test",
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

        # Scrollable container for Form + History
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Form Card
        self.form_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        self.form_card.pack(fill="x", pady=10)

        # Test Basic Details Row
        row1 = ctk.CTkFrame(self.form_card, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(15, 10))

        c_box = ctk.CTkFrame(row1, fg_color="transparent")
        c_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(c_box, text="Test Code / Label (e.g. T4, Part Test 3):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.test_code_entry = ctk.CTkEntry(c_box, placeholder_text="T4")
        self.test_code_entry.pack(fill="x", pady=(4, 0))

        d_box = ctk.CTkFrame(row1, fg_color="transparent")
        d_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(d_box, text="Test Date (YYYY-MM-DD):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.test_date_entry = ctk.CTkEntry(d_box)
        self.test_date_entry.insert(0, str(date.today()))
        self.test_date_entry.pack(fill="x", pady=(4, 0))

        n_box = ctk.CTkFrame(row1, fg_color="transparent")
        n_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(n_box, text="Notes / Observations:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.notes_entry = ctk.CTkEntry(n_box, placeholder_text="e.g. Part syllabus mock on Calculus & Optics")
        self.notes_entry.pack(fill="x", pady=(4, 0))

        # Dynamic Subjects & Chapter Checkboxes Container
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
        """Loads active track structure and renders subject score inputs + chapter checkboxes."""
        curr_track = self.app_state.get("current_track")
        if not curr_track:
            return

        try:
            track_data = api_client.get_track(curr_track["id"])
            self.app_state["current_track_full"] = track_data

            for w in self.subjects_form_frame.winfo_children():
                w.destroy()
            self.subject_entries.clear()
            self.subject_max_entries.clear()
            self.chapter_vars.clear()
            self.subject_chapters.clear()
            self.subject_count_labels.clear()

            subjects = track_data.get("subjects", [])
            for sub in subjects:
                sid = sub["id"]
                sub_card = ctk.CTkFrame(self.subjects_form_frame, fg_color=("#CBD5E1", "#0F172A"), corner_radius=10)
                sub_card.pack(fill="x", pady=8)

                # Subject Header: Name, Select All/Clear, Count, Score / Max
                top_row = ctk.CTkFrame(sub_card, fg_color="transparent")
                top_row.pack(fill="x", padx=15, pady=(12, 8))

                ctk.CTkLabel(
                    top_row,
                    text=f"{sub['name']} ({sub['code']})",
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=("#0F172A", "#38BDF8"),
                ).pack(side="left")

                # Score / Max Marks inputs on right
                score_box = ctk.CTkFrame(top_row, fg_color="transparent")
                score_box.pack(side="right")

                ctk.CTkLabel(score_box, text="Score:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 5))
                s_entry = ctk.CTkEntry(score_box, width=80, placeholder_text="0")
                s_entry.pack(side="left")
                self.subject_entries[sid] = s_entry

                ctk.CTkLabel(score_box, text="/", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
                m_entry = ctk.CTkEntry(score_box, width=65)
                m_entry.insert(0, str(sub.get("max_marks", 100)))
                m_entry.pack(side="left")
                self.subject_max_entries[sid] = m_entry

                # Chapter Syllabus Selection Controls + Checkboxes
                chapters = sub.get("chapters", [])
                self.subject_chapters[sid] = [ch["id"] for ch in chapters]

                if chapters:
                    ctrl_row = ctk.CTkFrame(sub_card, fg_color="transparent")
                    ctrl_row.pack(fill="x", padx=15, pady=(0, 6))

                    ctk.CTkLabel(
                        ctrl_row,
                        text="Test Syllabus — tick chapters included in this exam:",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=("#475569", "#94A3B8"),
                    ).pack(side="left")

                    count_lbl = ctk.CTkLabel(
                        ctrl_row,
                        text=f"0 / {len(chapters)} selected",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=("#0284C7", "#38BDF8"),
                    )
                    count_lbl.pack(side="right", padx=(10, 0))
                    self.subject_count_labels[sid] = count_lbl

                    ctk.CTkButton(
                        ctrl_row,
                        text="Clear",
                        width=55,
                        height=24,
                        font=ctk.CTkFont(size=11),
                        fg_color="#475569",
                        hover_color="#334155",
                        command=lambda s=sid: self._set_all_chapters(s, False),
                    ).pack(side="right", padx=4)

                    ctk.CTkButton(
                        ctrl_row,
                        text="Select All",
                        width=70,
                        height=24,
                        font=ctk.CTkFont(size=11),
                        fg_color="#0284C7",
                        hover_color="#0369A1",
                        command=lambda s=sid: self._set_all_chapters(s, True),
                    ).pack(side="right", padx=4)

                    # 2-column grid of chapter checkboxes + topics
                    grid_frame = ctk.CTkFrame(sub_card, fg_color="transparent")
                    grid_frame.pack(fill="x", padx=15, pady=(0, 12))
                    grid_frame.grid_columnconfigure(0, weight=1, uniform="ch_col")
                    grid_frame.grid_columnconfigure(1, weight=1, uniform="ch_col")

                    for idx, ch in enumerate(chapters):
                        var = ctk.BooleanVar(value=False)
                        self.chapter_vars[ch["id"]] = var

                        cell = ctk.CTkFrame(grid_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=8)
                        cell.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=4, pady=4)

                        cb = ctk.CTkCheckBox(
                            cell,
                            text=f"{ch['chapter_code']} — {ch['name']}",
                            variable=var,
                            font=ctk.CTkFont(size=12, weight="bold"),
                            checkbox_width=18,
                            checkbox_height=18,
                            command=lambda s=sid: self._update_subject_count(s),
                        )
                        cb.pack(anchor="w", padx=10, pady=(8, 2))

                        topics_txt = ch.get("topics") or ""
                        if topics_txt:
                            ctk.CTkLabel(
                                cell,
                                text=topics_txt,
                                font=ctk.CTkFont(size=10),
                                text_color=("#64748B", "#94A3B8"),
                                wraplength=350,
                                justify="left",
                            ).pack(anchor="w", padx=36, pady=(0, 8))
                else:
                    ctk.CTkLabel(
                        sub_card,
                        text="No chapters configured for this subject yet.",
                        font=ctk.CTkFont(size=11),
                        text_color="#94A3B8",
                    ).pack(anchor="w", padx=15, pady=(0, 12))

            self._refresh_history(curr_track["id"])

        except Exception as e:
            print(f"[TestsScreen Warning] Could not load track details: {e}")

    def _set_all_chapters(self, subject_id: int, value: bool):
        for cid in self.subject_chapters.get(subject_id, []):
            if cid in self.chapter_vars:
                self.chapter_vars[cid].set(value)
        self._update_subject_count(subject_id)

    def _update_subject_count(self, subject_id: int):
        cids = self.subject_chapters.get(subject_id, [])
        selected = sum(1 for cid in cids if self.chapter_vars.get(cid) and self.chapter_vars[cid].get())
        lbl = self.subject_count_labels.get(subject_id)
        if lbl:
            lbl.configure(text=f"{selected} / {len(cids)} selected")

    def _refresh_history(self, track_id: int):
        for w in self.history_container.winfo_children():
            w.destroy()

        try:
            tests = api_client.get_track_tests(track_id)
            if not tests:
                ctk.CTkLabel(
                    self.history_container,
                    text="No tests logged yet. Enter scores, tick syllabus chapters above, and click 'Save Test Attempt'.",
                    text_color="#94A3B8",
                ).pack(pady=10)
                return

            for t in reversed(tests):
                card = ctk.CTkFrame(self.history_container, fg_color=("#E2E8F0", "#1E293B"), corner_radius=10)
                card.pack(fill="x", pady=6)

                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=(12, 6))

                left = ctk.CTkFrame(row, fg_color="transparent")
                left.pack(side="left")

                ctk.CTkLabel(
                    left,
                    text=f"{t['test_code']}  —  {t['test_date']}",
                    font=ctk.CTkFont(size=15, weight="bold"),
                ).pack(anchor="w")

                if t.get("notes"):
                    ctk.CTkLabel(left, text=t["notes"], font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(anchor="w")

                mid = ctk.CTkFrame(row, fg_color="transparent")
                mid.pack(side="left", padx=30)

                ctk.CTkLabel(
                    mid,
                    text=f"Total: {t['total_score']:.1f} / {t['max_score']:.0f}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=("#0284C7", "#38BDF8"),
                ).pack()

                sub_box = ctk.CTkFrame(row, fg_color="transparent")
                sub_box.pack(side="right")

                for s in t.get("subject_scores", []):
                    pill = ctk.CTkLabel(
                        sub_box,
                        text=f"{s.get('subject_code', 'SUB')}: {s['score']:.0f}/{s.get('max_score', 100):.0f}",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        fg_color=("#CBD5E1", "#334155"),
                        corner_radius=6,
                        padx=8,
                        pady=3,
                    )
                    pill.pack(side="left", padx=4)

                # Syllabus chapters covered in this test
                chapters = t.get("chapters", [])
                if chapters:
                    ch_names = [f"{c.get('subject_code', '')}: {c.get('name', '')}" for c in chapters]
                    preview = "  •  ".join(ch_names)
                    ctk.CTkLabel(
                        card,
                        text=f"Syllabus ({len(chapters)} chapters): {preview}",
                        font=ctk.CTkFont(size=11),
                        text_color=("#475569", "#94A3B8"),
                        wraplength=780,
                        justify="left",
                    ).pack(anchor="w", padx=15, pady=(0, 12))
                else:
                    ctk.CTkLabel(
                        card,
                        text="Syllabus: Full / Unspecified",
                        font=ctk.CTkFont(size=11),
                        text_color="#64748B",
                    ).pack(anchor="w", padx=15, pady=(0, 12))

        except Exception as e:
            print(f"[History Render Warning] {e}")

    def _on_save_test(self):
        curr_track = self.app_state.get("current_track")
        if not curr_track:
            self._show_status("Error: No active track selected", False)
            return

        code = self.test_code_entry.get().strip() or "T"
        t_date = self.test_date_entry.get().strip()
        notes = self.notes_entry.get().strip()

        subject_scores = []
        total_score = 0.0
        total_max_score = 0.0

        try:
            for sid, entry in self.subject_entries.items():
                val_str = entry.get().strip()
                max_str = self.subject_max_entries[sid].get().strip()
                score_val = float(val_str) if val_str else 0.0
                max_val = float(max_str) if max_str else 100.0
                if max_val <= 0:
                    self._show_status("Max marks must be greater than 0.", False)
                    return
                if score_val < 0 or score_val > max_val:
                    self._show_status(f"Score ({score_val}) must be between 0 and {max_val}.", False)
                    return
                subject_scores.append({
                    "subject_id": sid,
                    "score": score_val,
                    "max_score": max_val,
                })
                total_score += score_val
                total_max_score += max_val
        except ValueError:
            self._show_status("Please enter valid numbers for subject scores.", False)
            return

        ticked_chapter_ids = [
            cid for cid, var in self.chapter_vars.items() if var.get()
        ]

        if not ticked_chapter_ids and any(self.subject_chapters.values()):
            self._show_status("Please tick at least one syllabus chapter for this test.", False)
            return

        payload = {
            "test_code": code,
            "test_date": t_date,
            "total_score": total_score,
            "max_score": total_max_score if total_max_score > 0 else float(curr_track.get("max_score", 300.0)),
            "notes": notes,
            "subject_scores": subject_scores,
            "chapter_ids": ticked_chapter_ids,
        }

        try:
            saved_test = api_client.log_test(curr_track["id"], payload)
            self._show_status(
                f"✓ Saved {saved_test['test_code']} ({saved_test['total_score']:.1f}/{saved_test['max_score']:.0f}, {len(ticked_chapter_ids)} chapters)!",
                True,
            )
            self._refresh_history(curr_track["id"])
            self.test_code_entry.delete(0, "end")
            self.notes_entry.delete(0, "end")
            for e in self.subject_entries.values():
                e.delete(0, "end")
            for sid in self.subject_chapters:
                self._set_all_chapters(sid, False)
        except Exception as e:
            self._show_status(f"Error saving test: {e}", False)

    def _show_status(self, msg: str, success: bool):
        color = "#10B981" if success else "#EF4444"
        self.status_label.configure(text=msg, text_color=color)
