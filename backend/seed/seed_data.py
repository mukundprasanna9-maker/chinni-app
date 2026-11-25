"""Seed script for Cadence (chinni-app).

Populates the database with:
- Admin account (admin / admin123)
- 3 user accounts with realistic, distinct student profiles, JEE Main 2026
  chapter-level syllabus (Maths, Physics, Chemistry), sample tests with
  ticked syllabus chapters, study plans, and focus sessions:
    1. Mukund Prasanna       / 1studyproject
    2. Sarvesh Umesh Kulkarni / 2studyproject
    3. Arya Nandan Srinivas  / 3studyproject
"""

import sys
from backend.repositories.database import init_db
from backend.repositories.user_repo import create_user, ensure_admin_exists, get_user_by_username
from backend.repositories.student_repo import create_student, get_all_students
from backend.repositories.track_repo import (
    create_track,
    create_subject,
    create_chapter,
    get_tracks_by_student,
)
from backend.repositories.test_repo import create_test
from backend.repositories.plan_repo import create_study_plan, create_focus_session


JEE_SYLLABUS = {
    "MATH": [
        ("M01", "Sets, Relations & Functions", "Sets, Equivalence relations, Domain, Range, Inverse & Composite functions", "Algebra"),
        ("M02", "Complex Numbers & Quadratic Equations", "Argand plane, De Moivre's theorem, Roots, Discriminant", "Algebra"),
        ("M03", "Matrices & Determinants", "Matrix algebra, Adjoint, Inverse, Cramer's rule, System of equations", "Algebra"),
        ("M04", "Permutations & Combinations", "Counting principle, Arrangements, Selections, Multinomial theorem", "Algebra"),
        ("M05", "Binomial Theorem & Sequences", "General term, AP, GP, HP, AGP, Sum of series", "Algebra"),
        ("M06", "Limits, Continuity & Differentiability", "L'Hopital's rule, Continuity, Differentiability, Chain rule", "Calculus"),
        ("M07", "Applications of Derivatives", "Tangents/Normals, Monotonicity, Maxima & Minima, Rolle's/MVT", "Calculus"),
        ("M08", "Indefinite & Definite Integrals", "Substitution, Parts, King's property, Area under curves", "Calculus"),
        ("M09", "Differential Equations", "Order/Degree, Variable separable, Homogeneous, Linear DE", "Calculus"),
        ("M10", "Straight Lines & Circles", "Slope forms, Distance, Pair of lines, Tangents & Chords", "Coordinate Geometry"),
        ("M11", "Conic Sections", "Parabola, Ellipse, Hyperbola, Tangents, Normals, Eccentricity", "Coordinate Geometry"),
        ("M12", "Vectors & 3D Geometry", "Dot/Cross products, Direction cosines, Lines, Shortest distance, Planes", "Vectors & 3D"),
        ("M13", "Trigonometry", "Identities, Equations, Properties of triangles, Inverse trig", "Trigonometry"),
        ("M14", "Statistics & Probability", "Mean, Variance, Standard deviation, Bayes' theorem, Distributions", "Algebra & Stats"),
    ],
    "PHY": [
        ("P01", "Units, Dimensions & Kinematics", "Error analysis, 1D/2D motion, Projectile, Relative velocity", "Mechanics"),
        ("P02", "Laws of Motion & Friction", "Newton's laws, Free body diagrams, Pseudo force, Circular dynamics", "Mechanics"),
        ("P03", "Work, Energy & Power", "Work-energy theorem, Conservation of energy, Collisions, Power", "Mechanics"),
        ("P04", "Rotational Motion & Centre of Mass", "Centre of mass, Moment of inertia, Torque, Rolling motion", "Mechanics"),
        ("P05", "Gravitation", "Kepler's laws, Gravitational potential, Escape & Orbital velocity", "Mechanics"),
        ("P06", "Properties of Solids & Fluids", "Elasticity, Viscosity, Bernoulli's principle, Surface tension", "Mechanics"),
        ("P07", "Thermal Physics & Thermodynamics", "Calorimetry, KTG, First & Second laws, Carnot engine, Heat transfer", "Thermal"),
        ("P08", "Oscillations & Waves", "SHM, Pendulum, Standing waves, Beats, Doppler effect", "Waves"),
        ("P09", "Electrostatics & Capacitors", "Coulomb's law, Gauss's law, Electric potential, Dielectrics", "Electrodynamics"),
        ("P10", "Current Electricity", "Ohm's law, Kirchhoff's rules, RC circuits, Wheatstone bridge", "Electrodynamics"),
        ("P11", "Magnetic Effects & Magnetism", "Biot-Savart, Ampere's law, Lorentz force, Galvanometer", "Electrodynamics"),
        ("P12", "EMI & Alternating Current", "Faraday's law, Lenz's law, Self/Mutual inductance, LCR circuits", "Electrodynamics"),
        ("P13", "Ray & Wave Optics", "Reflection, Refraction, Lenses, YDSE, Diffraction, Polarization", "Optics"),
        ("P14", "Modern Physics & Semiconductors", "Photoelectric effect, Bohr model, Nuclear physics, Diodes, Logic gates", "Modern Physics"),
    ],
    "CHEM": [
        ("C01", "Mole Concept & Atomic Structure", "Stoichiometry, Limiting reagent, Quantum numbers, Bohr's model", "Physical"),
        ("C02", "Chemical Bonding & Molecular Structure", "VSEPR, Hybridization, MOT, Hydrogen bonding", "Inorganic"),
        ("C03", "Thermodynamics & Equilibrium", "Enthalpy, Entropy, Gibbs energy, Kp/Kc, Ionic equilibrium, pH", "Physical"),
        ("C04", "Redox & Electrochemistry", "Oxidation numbers, Nernst equation, Conductance, Galvanic cells", "Physical"),
        ("C05", "Solutions & Chemical Kinetics", "Colligative properties, Raoult's law, Rate law, Arrhenius equation", "Physical"),
        ("C06", "Periodicity & Classification", "Periodic trends, Ionization energy, Electron affinity, Electronegativity", "Inorganic"),
        ("C07", "p-Block, d-Block & f-Block Elements", "Group 13-18 trends, Transition metals, KMnO4/K2Cr2O7", "Inorganic"),
        ("C08", "Coordination Compounds", "Werner's theory, IUPAC naming, Isomerism, CFT, Hybridization", "Inorganic"),
        ("C09", "General Organic Chemistry (GOC)", "Inductive/Resonance/Hyperconjugation, Isomerism, Intermediates", "Organic"),
        ("C10", "Hydrocarbons", "Alkanes, Alkenes, Alkynes, Benzene, Electrophilic substitution", "Organic"),
        ("C11", "Haloalkanes & Haloarenes", "SN1/SN2 mechanisms, Elimination, Aryl halides", "Organic"),
        ("C12", "Alcohols, Phenols & Ethers", "Dehydration, Oxidation, Reimer-Tiemann, Williamson synthesis", "Organic"),
        ("C13", "Aldehydes, Ketones & Carboxylic Acids", "Nucleophilic addition, Aldol, Cannizzaro, Acid strength", "Organic"),
        ("C14", "Amines & Biomolecules", "Diazonium salts, Carbylamine test, Carbohydrates, Amino acids", "Organic"),
    ],
}

CBSE_CHAPTERS = {
    "MATH-12": [
        ("M12-1", "Relations, Functions & Inverse Trig", "Types of relations, Bijective functions, Principal values", "Algebra"),
        ("M12-2", "Matrices & Determinants", "Matrix operations, Inverse, System of linear equations", "Algebra"),
        ("M12-3", "Continuity, Differentiation & AOD", "Chain rule, Maxima/Minima, Rate of change", "Calculus"),
        ("M12-4", "Integrals, AOI & Differential Equations", "Definite integrals, Area under curve, Linear DE", "Calculus"),
        ("M12-5", "Vectors, 3D & Linear Programming", "Lines in 3D, LPP graphical, Conditional probability", "Vectors & Prob"),
    ],
    "PHY-12": [
        ("P12-1", "Electrostatics & Capacitance", "Gauss law, Electric dipole, Parallel plate capacitor", "Electrodynamics"),
        ("P12-2", "Current Electricity & Magnetism", "Kirchhoff laws, Moving coil galvanometer, Biot-Savart", "Electrodynamics"),
        ("P12-3", "EMI, AC & EM Waves", "Faraday law, Transformers, LCR resonance", "Electrodynamics"),
        ("P12-4", "Ray & Wave Optics", "Lens maker formula, Prism, YDSE interference", "Optics"),
        ("P12-5", "Modern Physics & Semiconductors", "Photoelectric effect, Nuclei, p-n junction diode", "Modern Physics"),
    ],
    "CHEM-12": [
        ("C12-1", "Solutions, Electrochemistry & Kinetics", "Raoult law, Nernst eq, First order kinetics", "Physical"),
        ("C12-2", "d/f-Block & Coordination Compounds", "Lanthanoid contraction, CFT, IUPAC naming", "Inorganic"),
        ("C12-3", "Haloalkanes, Alcohols & Phenols", "SN1/SN2, Lucas test, Kolbe/Reimer-Tiemann", "Organic"),
        ("C12-4", "Aldehydes, Ketones, Acids & Amines", "Aldol, Cannizzaro, Hinsberg test, Diazonium", "Organic"),
        ("C12-5", "Biomolecules", "Glucose structure, Proteins, Vitamins, Nucleic acids", "Organic"),
    ],
    "ENG-12": [
        ("E12-1", "Flamingo Prose & Poetry", "All prose chapters and poems", "Literature"),
        ("E12-2", "Vistas Supplementary Reader", "Short stories and comprehension", "Literature"),
        ("E12-3", "Reading & Writing Skills", "Unseen passages, Notice, Formal letter, Article", "Writing"),
    ],
    "CS-12": [
        ("CS12-1", "Python Functions & File Handling", "Text, Binary, CSV files, Exception handling", "Programming"),
        ("CS12-2", "Data Structures (Stacks)", "Push/Pop operations using Python lists", "Programming"),
        ("CS12-3", "Computer Networks & SQL", "Protocols, Topologies, SQL Joins & Group By", "Systems & DB"),
    ],
}


DEFAULT_ACCOUNTS = [
    {
        "username": "Mukund Prasanna",
        "password": "1studyproject",
        "target_score": 235,
        "tests": [
            # (test_code, test_date, notes, (m, p, c), chapter_indices_per_subj)
            ("T1", "2026-09-15", "Part Test 1 - Algebra, Kinematics & Mole Concept", (48.0, 54.0, 60.0), ([0, 1, 2], [0, 1, 2], [0, 1])),
            ("T2", "2026-10-10", "Part Test 2 - Calculus, Rotational & Thermodynamics", (58.0, 64.0, 66.0), ([5, 6, 7], [2, 3, 6], [2, 3, 8])),
            ("T3", "2026-11-01", "Cumulative Mock 3 - Mixed JEE Main Syllabus", (65.0, 68.0, 72.0), ([0, 1, 5, 7, 9], [0, 3, 8, 9, 12], [0, 1, 2, 8, 9])),
        ],
        "plan": ("2026-11-10", 3.5, "Focus on Definite Integrals and Area Under Curve"),
        "focus": (50, "Solved 15 PYQs on Indefinite & Definite Integrals", "MATH", 7),
    },
    {
        "username": "Sarvesh Umesh Kulkarni",
        "password": "2studyproject",
        "target_score": 250,
        "tests": [
            ("T1", "2026-09-16", "Part Test 1 - Strong Physics Kinematics & NLM", (55.0, 66.0, 58.0), ([0, 1, 3], [0, 1, 2], [0, 1, 5])),
            ("T2", "2026-10-11", "Part Test 2 - Electrodynamics & Organic Chemistry", (60.0, 70.0, 68.0), ([5, 6, 10], [8, 9, 10], [8, 9, 10])),
            ("T3", "2026-11-02", "Cumulative Mock 3 - Steady upward trend", (68.0, 76.0, 71.0), ([1, 5, 7, 11], [1, 3, 8, 9, 11], [1, 2, 7, 8, 12])),
        ],
        "plan": ("2026-11-12", 4.0, "Master Electrodynamics and EMI problem sets"),
        "focus": (60, "Completed 20 Electrostatics numericals", "PHY", 8),
    },
    {
        "username": "Arya Nandan Srinivas",
        "password": "3studyproject",
        "target_score": 240,
        "tests": [
            ("T1", "2026-09-17", "Part Test 1 - High Chemistry accuracy", (52.0, 50.0, 68.0), ([0, 2, 4], [0, 1, 4], [0, 1, 2])),
            ("T2", "2026-10-12", "Part Test 2 - Optics, Vectors & Coordination", (62.0, 58.0, 72.0), ([3, 9, 11], [3, 7, 12], [6, 7, 8])),
            ("T3", "2026-11-03", "Cumulative Mock 3 - Balanced across all 3 subjects", (70.0, 64.0, 78.0), ([0, 5, 7, 11, 13], [0, 3, 6, 12, 13], [0, 2, 7, 9, 12])),
        ],
        "plan": ("2026-11-14", 3.0, "Strengthen Rotation & Ray Optics fundamentals"),
        "focus": (45, "Revised Rotational Dynamics concepts & PYQs", "PHY", 3),
    },
]


def _populate_chapters(subject_id: int, subject_code: str) -> list[dict]:
    """Insert syllabus chapters for a subject from JEE or CBSE definitions."""
    chapter_defs = JEE_SYLLABUS.get(subject_code) or CBSE_CHAPTERS.get(subject_code, [])
    created = []
    for code, name, topics, unit in chapter_defs:
        created.append(create_chapter(subject_id, code, name, topics=topics, unit=unit))
    return created


def create_default_jee_track(student_id: int, target_score: int = 235) -> dict:
    """Create the default JEE Main 2026 track with Maths, Physics, Chemistry and chapter-wise JEE syllabus."""
    jee_track = create_track(
        student_id=student_id,
        name="JEE Main 2026",
        target_score=target_score,
        max_score=300,
    )

    math = create_subject(jee_track["id"], "Mathematics", "MATH", max_marks=100, target_marks=80)
    phy = create_subject(jee_track["id"], "Physics", "PHY", max_marks=100, target_marks=80)
    chem = create_subject(jee_track["id"], "Chemistry", "CHEM", max_marks=100, target_marks=75)

    math_chapters = _populate_chapters(math["id"], "MATH")
    phy_chapters = _populate_chapters(phy["id"], "PHY")
    chem_chapters = _populate_chapters(chem["id"], "CHEM")

    return {
        "track": jee_track,
        "subjects": (math, phy, chem),
        "chapters": {
            "MATH": math_chapters,
            "PHY": phy_chapters,
            "CHEM": chem_chapters,
        },
    }


def _seed_account(account: dict) -> None:
    """Create a user account (if missing) and populate its student, tracks, tests, and plans."""
    username = account["username"]
    user = get_user_by_username(username)
    if not user:
        user = create_user(username, account["password"], is_admin=False)
        print(f"[Seed] Created user '{username}' (ID: {user['id']})")
    else:
        print(f"[Seed] User '{username}' already exists (ID: {user['id']}).")

    existing_students = get_all_students(user_id=user["id"])
    if existing_students:
        student = existing_students[0]
        if get_tracks_by_student(student["id"]):
            print(f"[Seed] Student '{student['name']}' already has seeded tracks. Skipping.")
            return
    else:
        student = create_student(name=username, target_score=account["target_score"], user_id=user["id"])
        print(f"[Seed] Created student '{student['name']}' (ID: {student['id']})")

    student_id = student["id"]

    # 1. JEE Main 2026 Track (with full JEE chapters & topics)
    jee_bundle = create_default_jee_track(student_id, target_score=account["target_score"])
    jee_track = jee_bundle["track"]
    math, phy, chem = jee_bundle["subjects"]
    ch_map = jee_bundle["chapters"]

    # 2. CBSE 12th Board Track
    cbse_track = create_track(
        student_id=student_id,
        name="CBSE 12th Board",
        target_score=470,
        max_score=500,
    )
    for s_name, s_code, s_target in [
        ("Mathematics", "MATH-12", 95),
        ("Physics", "PHY-12", 95),
        ("Chemistry", "CHEM-12", 95),
        ("English Core", "ENG-12", 95),
        ("Computer Science", "CS-12", 90),
    ]:
        sub = create_subject(cbse_track["id"], s_name, s_code, 100, s_target)
        _populate_chapters(sub["id"], s_code)

    # 3. Sample Tests (T1, T2, T3) with ticked syllabus chapters
    for code, t_date, notes, (m_s, p_s, c_s), (m_idx, p_idx, c_idx) in account["tests"]:
        total = m_s + p_s + c_s
        ticked_chapter_ids = (
            [ch_map["MATH"][i]["id"] for i in m_idx]
            + [ch_map["PHY"][i]["id"] for i in p_idx]
            + [ch_map["CHEM"][i]["id"] for i in c_idx]
        )
        create_test(
            track_id=jee_track["id"],
            test_code=code,
            test_date=t_date,
            total_score=total,
            max_score=300.0,
            notes=notes,
            subject_scores=[
                {"subject_id": math["id"], "score": m_s, "max_score": 100.0, "accuracy_percent": 75.0, "time_spent_minutes": 60},
                {"subject_id": phy["id"], "score": p_s, "max_score": 100.0, "accuracy_percent": 78.0, "time_spent_minutes": 55},
                {"subject_id": chem["id"], "score": c_s, "max_score": 100.0, "accuracy_percent": 82.0, "time_spent_minutes": 50},
            ],
            chapter_ids=ticked_chapter_ids,
        )

    # 4. Sample Study Plan & Chapter-Tagged Focus Session
    plan_date, plan_hrs, plan_notes = account["plan"]
    create_study_plan(
        student_id=student_id,
        group_id=None,
        subject_id=math["id"],
        target_date=plan_date,
        planned_hours=plan_hrs,
        notes=plan_notes,
    )
    focus_mins, focus_notes, focus_subj_code, focus_ch_idx = account["focus"]
    focus_sub_id = {"MATH": math["id"], "PHY": phy["id"], "CHEM": chem["id"]}[focus_subj_code]
    focus_ch_id = ch_map[focus_subj_code][focus_ch_idx]["id"]
    create_focus_session(
        student_id=student_id,
        subject_id=focus_sub_id,
        group_id=None,
        chapter_id=focus_ch_id,
        duration_minutes=focus_mins,
        notes=focus_notes,
        adherence_status="COMPLETED",
    )
    print(f"[Seed] Seeded JEE chapters, tests (T1-T3), plan, and focus session for '{username}'.")


def seed_database(student_name: str | None = None, target_score: int = 235):
    """Initializes the DB, ensures admin exists, and seeds the 3 accounts (or a custom one if specified)."""
    print("Initializing database schema...")
    init_db()
    ensure_admin_exists()

    if student_name:
        _seed_account({
            "username": student_name,
            "password": "1studyproject",
            "target_score": target_score,
            "tests": DEFAULT_ACCOUNTS[0]["tests"],
            "plan": DEFAULT_ACCOUNTS[0]["plan"],
            "focus": DEFAULT_ACCOUNTS[0]["focus"],
        })
    else:
        for account in DEFAULT_ACCOUNTS:
            _seed_account(account)

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    name_arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    seed_database(student_name=name_arg)
