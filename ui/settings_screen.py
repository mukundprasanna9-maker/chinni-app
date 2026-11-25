"""Settings Screen for Cadence (chinni-app).

Allows the user to:
1. Edit their username or password (requires verifying current password first).
2. Manage academic tracks for the active student:
   - Edit each track's target score.
   - Add new tracks (CBSE 8th Grade, JEE Main 2026, CBSE 12th Board, or Custom).
   - Delete a track with an explicit "Are you sure?" data-deletion confirmation.
"""

import customtkinter as ctk
from ui import api_client


class ConfirmDeleteTrackDialog(ctk.CTkToplevel):
    """Modal confirmation dialog warning that deleting a track wipes all its data."""

    def __init__(self, parent, track_name: str, on_confirm):
        super().__init__(parent)
        self.title("Confirm Track Deletion")
        self.geometry("440x250")
        self.resizable(False, False)
        self.configure(fg_color=("#F8FAFC", "#0F172A"))
        self.on_confirm = on_confirm

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        card = ctk.CTkFrame(self, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            card,
            text="⚠️ Delete Track?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#EF4444",
        ).pack(pady=(16, 8))

        ctk.CTkLabel(
            card,
            text=(
                f"Are you sure you want to delete '{track_name}'?\n\n"
                "All tests, subject scores, and syllabus history\n"
                "for this track will be permanently deleted.\n"
                "This action cannot be undone."
            ),
            font=ctk.CTkFont(size=12),
            text_color=("#334155", "#E2E8F0"),
            justify="center",
        ).pack(padx=16, pady=(0, 18))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(0, 14))

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=120,
            height=36,
            fg_color="#475569",
            hover_color="#334155",
            command=self.destroy,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row,
            text="Yes, Delete Track",
            width=160,
            height=36,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._confirm,
        ).pack(side="left", padx=8)

    def _confirm(self):
        self.destroy()
        self.on_confirm()


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, parent, app_state, on_navigate, on_account_updated=None):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_navigate = on_navigate
        self.on_account_updated = on_account_updated

        self._target_entries = {}  # track_id -> CTkEntry
        self._build_ui()

    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        header_frame.pack(fill="x", padx=15, pady=(10, 15))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            title_box,
            text="ACCOUNT & TRACK SETTINGS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Manage login credentials, target scores, and academic tracks",
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

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # ── 1. Account Security & Credentials Card ──────────────────────
        acc_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        acc_card.pack(fill="x", pady=8)

        ctk.CTkLabel(
            acc_card,
            text="🔒 Account & Security",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w", padx=20, pady=(15, 4))

        self.current_user_label = ctk.CTkLabel(
            acc_card,
            text="Signed in as: ...",
            font=ctk.CTkFont(size=12),
            text_color=("#475569", "#94A3B8"),
        )
        self.current_user_label.pack(anchor="w", padx=20, pady=(0, 12))

        grid = ctk.CTkFrame(acc_card, fg_color="transparent")
        grid.pack(fill="x", padx=20)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # Current Password (Required security verification)
        cp_box = ctk.CTkFrame(grid, fg_color="transparent")
        cp_box.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)
        ctk.CTkLabel(
            cp_box,
            text="Current Password (Required to save changes):",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w")
        self.curr_pw_entry = ctk.CTkEntry(cp_box, show="*", placeholder_text="Enter current password")
        self.curr_pw_entry.pack(fill="x", pady=(4, 0))

        # New Username
        nu_box = ctk.CTkFrame(grid, fg_color="transparent")
        nu_box.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        ctk.CTkLabel(
            nu_box,
            text="New Username (leave blank to keep current):",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w")
        self.new_username_entry = ctk.CTkEntry(nu_box, placeholder_text="Enter new username")
        self.new_username_entry.pack(fill="x", pady=(4, 0))

        # New Password
        np_box = ctk.CTkFrame(grid, fg_color="transparent")
        np_box.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5)
        ctk.CTkLabel(
            np_box,
            text="New Password (leave blank to keep current):",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w")
        self.new_pw_entry = ctk.CTkEntry(np_box, show="*", placeholder_text="At least 4 characters")
        self.new_pw_entry.pack(fill="x", pady=(4, 0))

        # Confirm New Password
        cf_box = ctk.CTkFrame(grid, fg_color="transparent")
        cf_box.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        ctk.CTkLabel(
            cf_box,
            text="Confirm New Password:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w")
        self.confirm_pw_entry = ctk.CTkEntry(cf_box, show="*", placeholder_text="Re-enter new password")
        self.confirm_pw_entry.pack(fill="x", pady=(4, 0))

        acc_btn_row = ctk.CTkFrame(acc_card, fg_color="transparent")
        acc_btn_row.pack(fill="x", padx=20, pady=(10, 16))

        ctk.CTkButton(
            acc_btn_row,
            text="Save Account Changes",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            height=36,
            command=self._on_save_account,
        ).pack(side="left")

        self.acc_status_label = ctk.CTkLabel(acc_btn_row, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.acc_status_label.pack(side="left", padx=14)

        # ── 2. Existing Tracks & Target Scores Card ─────────────────────
        tracks_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        tracks_card.pack(fill="x", pady=10)

        t_head = ctk.CTkFrame(tracks_card, fg_color="transparent")
        t_head.pack(fill="x", padx=20, pady=(15, 6))

        ctk.CTkLabel(
            t_head,
            text="🎯 Your Tracks & Target Scores",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(side="left")

        self.student_context_label = ctk.CTkLabel(
            t_head,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#475569", "#94A3B8"),
        )
        self.student_context_label.pack(side="right")

        self.tracks_list_frame = ctk.CTkFrame(tracks_card, fg_color="transparent")
        self.tracks_list_frame.pack(fill="x", padx=20, pady=(4, 8))

        self.tracks_status_label = ctk.CTkLabel(tracks_card, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.tracks_status_label.pack(anchor="w", padx=20, pady=(0, 12))

        # ── 3. Add New Track Card ───────────────────────────────────────
        add_card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E2E8F0", "#1E293B"), corner_radius=12)
        add_card.pack(fill="x", pady=10)

        ctk.CTkLabel(
            add_card,
            text="➕ Add a New Track",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#0F172A", "#38BDF8"),
        ).pack(anchor="w", padx=20, pady=(15, 6))

        add_grid = ctk.CTkFrame(add_card, fg_color="transparent")
        add_grid.pack(fill="x", padx=20, pady=4)
        add_grid.grid_columnconfigure(0, weight=1)
        add_grid.grid_columnconfigure(1, weight=1)
        add_grid.grid_columnconfigure(2, weight=1)

        # Template Picker
        tpl_box = ctk.CTkFrame(add_grid, fg_color="transparent")
        tpl_box.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=4)
        ctk.CTkLabel(tpl_box, text="Track Template:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.template_var = ctk.StringVar(value="CBSE 8th Grade")
        ctk.CTkOptionMenu(
            tpl_box,
            variable=self.template_var,
            values=["CBSE 8th Grade", "JEE Main 2026", "CBSE 12th Board", "Custom Track"],
            command=self._on_template_changed,
        ).pack(fill="x", pady=(4, 0))

        # Track Name
        nm_box = ctk.CTkFrame(add_grid, fg_color="transparent")
        nm_box.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        ctk.CTkLabel(nm_box, text="Track Name:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.new_track_name_entry = ctk.CTkEntry(nm_box)
        self.new_track_name_entry.pack(fill="x", pady=(4, 0))

        # Target Score
        tg_box = ctk.CTkFrame(add_grid, fg_color="transparent")
        tg_box.grid(row=0, column=2, sticky="ew", padx=(10, 0), pady=4)
        self.new_target_label = ctk.CTkLabel(tg_box, text="Target Score (%):", font=ctk.CTkFont(size=12, weight="bold"))
        self.new_target_label.pack(anchor="w")
        self.new_track_target_entry = ctk.CTkEntry(tg_box)
        self.new_track_target_entry.pack(fill="x", pady=(4, 0))

        # Custom options row (shown for Custom Track)
        self.custom_row = ctk.CTkFrame(add_card, fg_color="transparent")
        self.custom_row.grid_columnconfigure(0, weight=1)
        self.custom_row.grid_columnconfigure(1, weight=1)
        self.custom_row.grid_columnconfigure(2, weight=2)

        em_box = ctk.CTkFrame(self.custom_row, fg_color="transparent")
        em_box.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=4)
        ctk.CTkLabel(em_box, text="Exam Format:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.exam_mode_var = ctk.StringVar(value="Single-Subject Exams")
        ctk.CTkOptionMenu(
            em_box,
            variable=self.exam_mode_var,
            values=["Single-Subject Exams", "Multi-Subject Exams"],
        ).pack(fill="x", pady=(4, 0))

        mx_box = ctk.CTkFrame(self.custom_row, fg_color="transparent")
        mx_box.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        ctk.CTkLabel(mx_box, text="Max Score:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.new_track_max_entry = ctk.CTkEntry(mx_box)
        self.new_track_max_entry.insert(0, "100")
        self.new_track_max_entry.pack(fill="x", pady=(4, 0))

        cs_box = ctk.CTkFrame(self.custom_row, fg_color="transparent")
        cs_box.grid(row=0, column=2, sticky="ew", padx=(10, 0), pady=4)
        ctk.CTkLabel(cs_box, text="Subjects (comma-separated):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.custom_subjects_entry = ctk.CTkEntry(cs_box, placeholder_text="e.g. Maths, Science, English")
        self.custom_subjects_entry.pack(fill="x", pady=(4, 0))

        self.template_hint_label = ctk.CTkLabel(
            add_card,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("#475569", "#94A3B8"),
        )
        self.template_hint_label.pack(anchor="w", padx=20, pady=(4, 4))

        add_btn_row = ctk.CTkFrame(add_card, fg_color="transparent")
        add_btn_row.pack(fill="x", padx=20, pady=(6, 16))

        ctk.CTkButton(
            add_btn_row,
            text="+ Add Track",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=36,
            command=self._on_add_track,
        ).pack(side="left")

        self.add_track_status_label = ctk.CTkLabel(add_btn_row, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.add_track_status_label.pack(side="left", padx=14)

        self._on_template_changed("CBSE 8th Grade")

    def refresh_settings(self):
        """Reload current user info and active student's tracks."""
        user = api_client.get_current_user() or {}
        role = "Admin" if user.get("is_admin") else "User"
        self.current_user_label.configure(
            text=f"Signed in as: {user.get('username', 'Unknown')} ({role})"
        )
        self.acc_status_label.configure(text="")
        self.tracks_status_label.configure(text="")
        self.add_track_status_label.configure(text="")

        curr_student = self.app_state.get("current_student")
        if not curr_student:
            try:
                students = api_client.get_students()
                if students:
                    curr_student = students[0]
                    self.app_state["students"] = students
                    self.app_state["current_student"] = curr_student
            except Exception:
                curr_student = None

        if not curr_student:
            self.student_context_label.configure(text="No active student profile")
            return

        self.student_context_label.configure(text=f"Student: {curr_student['name']}")
        self._render_tracks_list(curr_student["id"])

    def _render_tracks_list(self, student_id: int):
        for w in self.tracks_list_frame.winfo_children():
            w.destroy()
        self._target_entries.clear()

        try:
            tracks = api_client.get_student_tracks(student_id)
            self.app_state["tracks"] = tracks
            if not tracks:
                self.app_state["current_track"] = None
                ctk.CTkLabel(
                    self.tracks_list_frame,
                    text="No tracks yet. Use 'Add a New Track' below to create one.",
                    text_color="#94A3B8",
                ).pack(pady=10)
                return

            curr_t = self.app_state.get("current_track")
            if not curr_t or curr_t["id"] not in [t["id"] for t in tracks]:
                self.app_state["current_track"] = tracks[0]

            for t in tracks:
                tid = t["id"]
                is_single = t.get("exam_mode") == "SINGLE_SUBJECT"
                mode_badge = "Single-Subject Exams" if is_single else "Multi-Subject Exams"

                row = ctk.CTkFrame(self.tracks_list_frame, fg_color=("#CBD5E1", "#0F172A"), corner_radius=8)
                row.pack(fill="x", pady=5)

                inner = ctk.CTkFrame(row, fg_color="transparent")
                inner.pack(fill="x", padx=14, pady=10)

                left = ctk.CTkFrame(inner, fg_color="transparent")
                left.pack(side="left", fill="x", expand=True)

                ctk.CTkLabel(
                    left,
                    text=t["name"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                ).pack(anchor="w")

                sub_count = len(t.get("subjects", []))
                ctk.CTkLabel(
                    left,
                    text=f"{mode_badge}  •  {sub_count} subject{'s' if sub_count != 1 else ''}",
                    font=ctk.CTkFont(size=11),
                    text_color=("#475569", "#94A3B8"),
                ).pack(anchor="w")

                right = ctk.CTkFrame(inner, fg_color="transparent")
                right.pack(side="right")

                target_lbl = "Target (%):" if is_single else f"Target (/{t['max_score']}):"
                ctk.CTkLabel(right, text=target_lbl, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 6))

                t_entry = ctk.CTkEntry(right, width=70)
                t_entry.insert(0, str(t["target_score"]))
                t_entry.pack(side="left", padx=(0, 8))
                self._target_entries[tid] = t_entry

                ctk.CTkButton(
                    right,
                    text="Save Target",
                    width=95,
                    height=30,
                    fg_color="#0284C7",
                    hover_color="#0369A1",
                    command=lambda track=t: self._on_save_target(track),
                ).pack(side="left", padx=(0, 8))

                ctk.CTkButton(
                    right,
                    text="🗑️ Delete",
                    width=85,
                    height=30,
                    fg_color="#DC2626",
                    hover_color="#B91C1C",
                    command=lambda track=t: self._prompt_delete_track(track),
                ).pack(side="left")

        except Exception as e:
            self.tracks_status_label.configure(text=f"Error loading tracks: {e}", text_color="#EF4444")

    def _on_save_account(self):
        user = api_client.get_current_user()
        if not user:
            return

        curr_pw = self.curr_pw_entry.get().strip()
        new_uname = self.new_username_entry.get().strip()
        new_pw = self.new_pw_entry.get().strip()
        confirm_pw = self.confirm_pw_entry.get().strip()

        if not curr_pw:
            self.acc_status_label.configure(text="Enter your current password first.", text_color="#EF4444")
            return

        if not new_uname and not new_pw:
            self.acc_status_label.configure(text="Enter a new username or a new password.", text_color="#EF4444")
            return

        if new_pw:
            if len(new_pw) < 4:
                self.acc_status_label.configure(text="New password must be at least 4 characters.", text_color="#EF4444")
                return
            if new_pw != confirm_pw:
                self.acc_status_label.configure(text="New passwords do not match.", text_color="#EF4444")
                return

        try:
            updated = api_client.update_account(
                user_id=user["id"],
                current_password=curr_pw,
                new_username=new_uname or None,
                new_password=new_pw or None,
            )
            self.curr_pw_entry.delete(0, "end")
            self.new_username_entry.delete(0, "end")
            self.new_pw_entry.delete(0, "end")
            self.confirm_pw_entry.delete(0, "end")
            self.acc_status_label.configure(
                text=f"✓ Account updated ({updated['username']})!",
                text_color="#10B981",
            )
            if self.on_account_updated:
                self.on_account_updated()
            self.refresh_settings()
            self.acc_status_label.configure(
                text=f"✓ Account updated ({updated['username']})!",
                text_color="#10B981",
            )
        except Exception as e:
            err = str(e)
            if "401" in err:
                self.acc_status_label.configure(text="Current password is incorrect.", text_color="#EF4444")
            elif "409" in err:
                self.acc_status_label.configure(text="That username is already taken.", text_color="#EF4444")
            else:
                self.acc_status_label.configure(text=f"Update failed: {err[:55]}", text_color="#EF4444")

    def _on_save_target(self, track: dict):
        tid = track["id"]
        entry = self._target_entries.get(tid)
        if not entry:
            return
        try:
            new_target = int(entry.get().strip())
            if new_target <= 0:
                raise ValueError("Target must be positive")
            if track.get("exam_mode") == "SINGLE_SUBJECT" and new_target > int(track.get("max_score", 100)):
                self.tracks_status_label.configure(
                    text="Target percentage cannot exceed 100%.",
                    text_color="#EF4444",
                )
                return
            updated = api_client.update_track(tid, target_score=new_target)
            # Keep app_state["current_track"] synced if this track is selected
            if self.app_state.get("current_track") and self.app_state["current_track"]["id"] == tid:
                self.app_state["current_track"] = updated
            self.tracks_status_label.configure(
                text=f"✓ Updated target for '{updated['name']}' to {updated['target_score']}.",
                text_color="#10B981",
            )
            curr_student = self.app_state.get("current_student")
            if curr_student:
                self._render_tracks_list(curr_student["id"])
        except ValueError:
            self.tracks_status_label.configure(text="Enter a valid whole number for target score.", text_color="#EF4444")
        except Exception as e:
            self.tracks_status_label.configure(text=f"Error updating target: {e}", text_color="#EF4444")

    def _prompt_delete_track(self, track: dict):
        ConfirmDeleteTrackDialog(
            self,
            track_name=track["name"],
            on_confirm=lambda: self._execute_delete_track(track),
        )

    def _execute_delete_track(self, track: dict):
        try:
            api_client.delete_track(track["id"])
            if self.app_state.get("current_track") and self.app_state["current_track"]["id"] == track["id"]:
                self.app_state["current_track"] = None
            curr_student = self.app_state.get("current_student")
            if curr_student:
                self._render_tracks_list(curr_student["id"])
            self.tracks_status_label.configure(
                text=f"✓ Deleted '{track['name']}' and all its data.",
                text_color="#10B981",
            )
        except Exception as e:
            self.tracks_status_label.configure(text=f"Delete failed: {e}", text_color="#EF4444")

    def _on_template_changed(self, choice: str):
        self.new_track_name_entry.delete(0, "end")
        self.new_track_target_entry.delete(0, "end")
        self.new_track_max_entry.delete(0, "end")

        if choice == "CBSE 8th Grade":
            self.new_track_name_entry.insert(0, "CBSE 8th Grade")
            self.new_track_target_entry.insert(0, "85")
            self.new_track_max_entry.insert(0, "100")
            self.new_target_label.configure(text="Target Score (%):")
            self.custom_row.pack_forget()
            self.template_hint_label.configure(
                text="Single-subject exams with flexible total marks. Includes Maths, Science, Social Science, English & Hindi NCERT chapters."
            )
        elif choice == "JEE Main 2026":
            self.new_track_name_entry.insert(0, "JEE Main 2026")
            self.new_track_target_entry.insert(0, "235")
            self.new_track_max_entry.insert(0, "300")
            self.new_target_label.configure(text="Target Score (/300):")
            self.custom_row.pack_forget()
            self.template_hint_label.configure(
                text="Multi-subject exams (Maths, Physics, Chemistry) with 14 JEE syllabus chapters per subject."
            )
        elif choice == "CBSE 12th Board":
            self.new_track_name_entry.insert(0, "CBSE 12th Board")
            self.new_track_target_entry.insert(0, "470")
            self.new_track_max_entry.insert(0, "500")
            self.new_target_label.configure(text="Target Score (/500):")
            self.custom_row.pack_forget()
            self.template_hint_label.configure(
                text="Includes Class 12 Maths, Physics, Chemistry, English Core & Computer Science chapters."
            )
        else:
            self.new_track_name_entry.insert(0, "My Custom Track")
            self.new_track_target_entry.insert(0, "85")
            self.new_track_max_entry.insert(0, "100")
            self.new_target_label.configure(text="Target Score:")
            self.custom_row.pack(after=self.new_track_name_entry.master.master, fill="x", padx=20, pady=4)
            self.template_hint_label.configure(
                text="Create any custom track with single-subject or multi-subject exams."
            )

    def _on_add_track(self):
        curr_student = self.app_state.get("current_student")
        if not curr_student:
            self.add_track_status_label.configure(text="No active student selected.", text_color="#EF4444")
            return

        tpl = self.template_var.get()
        name = self.new_track_name_entry.get().strip()
        if not name:
            self.add_track_status_label.configure(text="Track name is required.", text_color="#EF4444")
            return

        try:
            target = int(self.new_track_target_entry.get().strip())
            max_s = int(self.new_track_max_entry.get().strip() or "100")
            if target <= 0 or max_s <= 0:
                raise ValueError
        except ValueError:
            self.add_track_status_label.configure(text="Target and max score must be positive integers.", text_color="#EF4444")
            return

        try:
            if tpl == "Custom Track":
                mode = "SINGLE_SUBJECT" if self.exam_mode_var.get() == "Single-Subject Exams" else "MULTI_SUBJECT"
                subs = [s.strip() for s in self.custom_subjects_entry.get().split(",") if s.strip()]
                created = api_client.create_track(
                    student_id=curr_student["id"],
                    name=name,
                    target_score=target,
                    max_score=max_s,
                    exam_mode=mode,
                    template="Custom",
                    custom_subjects=subs or ["General"],
                )
            else:
                mode = "SINGLE_SUBJECT" if tpl == "CBSE 8th Grade" else "MULTI_SUBJECT"
                created = api_client.create_track(
                    student_id=curr_student["id"],
                    name=name,
                    target_score=target,
                    max_score=max_s,
                    exam_mode=mode,
                    template=tpl,
                )

            self.app_state["current_track"] = created
            self._render_tracks_list(curr_student["id"])
            self.add_track_status_label.configure(
                text=f"✓ Added track '{created['name']}'!",
                text_color="#10B981",
            )
        except Exception as e:
            self.add_track_status_label.configure(text=f"Error creating track: {e}", text_color="#EF4444")
