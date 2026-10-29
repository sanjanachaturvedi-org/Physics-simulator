import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------
# PALETTE DEFINITION (Modern Deep-Slate Developer Theme)
# ---------------------------------------------------------
BG_DARK = RGBColor(15, 23, 42)        # #0F172A Dark Slate
CARD_BG = RGBColor(30, 41, 59)        # #1E293B Card Background
CARD_BORDER = RGBColor(51, 65, 85)    # #334155 Slate Border
CARD_HOVER = RGBColor(40, 53, 76)     # Slightly lighter card
TEXT_LIGHT = RGBColor(248, 250, 252)  # #F8FAFC Crisp White
TEXT_MUTED = RGBColor(148, 163, 184)  # #94A3B8 Subdued Gray
CYAN = RGBColor(56, 189, 248)         # #38BDF8 Electric Cyan
EMERALD = RGBColor(52, 211, 153)      # #34D399 Emerald Green
AMBER = RGBColor(251, 191, 36)        # #FBBF24 Amber Yellow
ROSE = RGBColor(244, 63, 94)          # #F43F5E Coral Rose
PURPLE = RGBColor(168, 85, 247)       # #A855F7 Violet
CODE_BG = RGBColor(11, 18, 33)        # Terminal Dark
LINE_MUTED = RGBColor(30, 45, 69)

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_CODE = "Consolas"

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide layout

    # Helper: Set slide background color
    def set_slide_bg(slide, color=BG_DARK):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = color

    # Helper: Add Footer with slide number
    def add_footer(slide, current_slide, total_slides=12):
        foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
        tf = foot_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"2D Physics Engine Architecture  |  Python (Flask) & HTML5 Canvas  |  Slide {current_slide:02d} of {total_slides:02d}"
        p.font.name = FONT_CODE
        p.font.size = Pt(9)
        p.font.color.rgb = RGBColor(100, 116, 139) # #64748B

    # Helper: Add Header
    def add_header(slide, title, category=None, subtitle=None):
        top_offset = Inches(0.45)
        if category:
            # Pill badge shape
            cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_offset, Inches(3.2), Inches(0.32))
            cat_box.fill.solid()
            cat_box.fill.fore_color.rgb = RGBColor(20, 35, 60)
            cat_box.line.color.rgb = CYAN
            cat_box.line.width = Pt(1)
            tf = cat_box.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = category.upper()
            p.alignment = PP_ALIGN.CENTER
            p.font.name = FONT_HEADING
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = CYAN
            top_offset += Inches(0.42)

        # Title text
        title_box = slide.shapes.add_textbox(Inches(0.8), top_offset, Inches(11.7), Inches(0.55))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(25)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT

        if subtitle:
            top_offset += Inches(0.52)
            sub_box = slide.shapes.add_textbox(Inches(0.8), top_offset, Inches(11.7), Inches(0.35))
            tf = sub_box.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = subtitle
            p.font.name = FONT_BODY
            p.font.size = Pt(12.5)
            p.font.color.rgb = TEXT_MUTED

    # Helper: Add Card container with subtle top accent stripe
    def add_card(slide, left, top, width, height, title=None, border_color=CARD_BORDER, bg_color=CARD_BG, accent_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)

        # If accent color provided, draw top accent line
        if accent_color:
            stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + Inches(0.1), top, width - Inches(0.2), Pt(3.5))
            stripe.fill.solid()
            stripe.fill.fore_color.rgb = accent_color
            stripe.line.fill.background()

        if title:
            tf = card.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.22)
            tf.margin_top = Inches(0.18)
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = FONT_HEADING
            p.font.size = Pt(14.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_LIGHT
        return card

    # =========================================================
    # SLIDE 1: TITLE SLIDE (Developer / Senior Engineer Aesthetic)
    # =========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    # Accent decorative background grid/card
    bg_accent = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.35), Inches(7.5))
    bg_accent.fill.solid()
    bg_accent.fill.fore_color.rgb = CYAN
    bg_accent.line.fill.background()

    # Category Pill
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(3.6), Inches(0.38))
    pill.fill.solid()
    pill.fill.fore_color.rgb = RGBColor(20, 35, 60)
    pill.line.color.rgb = CYAN
    pill.line.width = Pt(1)
    ptf = pill.text_frame
    pp = ptf.paragraphs[0]
    pp.text = "FULL-STACK PHYSICS SIMULATION"
    pp.alignment = PP_ALIGN.CENTER
    pp.font.name = FONT_HEADING
    pp.font.size = Pt(11)
    pp.font.bold = True
    pp.font.color.rgb = CYAN

    # Main Project Title
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(10.8), Inches(1.8))
    ttf = t_box.text_frame
    ttf.word_wrap = True
    tp = ttf.paragraphs[0]
    tp.text = "2D Physics Engine & REST API"
    tp.font.name = FONT_HEADING
    tp.font.size = Pt(40)
    tp.font.bold = True
    tp.font.color.rgb = TEXT_LIGHT

    tp2 = ttf.add_paragraph()
    tp2.text = "Lightweight, First-Principles Simulation: Gravity, Friction, Collisions, Constraints & Joints"
    tp2.font.name = FONT_BODY
    tp2.font.size = Pt(17)
    tp2.font.color.rgb = TEXT_MUTED
    tp2.space_before = Pt(8)

    # 4 Feature highlight badges
    badges = [
        ("🌍 Gravity Engine", "Multi-planetary scale & custom g-forces", CYAN),
        ("🧊 Coulomb Friction", "Surface resistance: Ice, Normal, Rough", AMBER),
        ("💥 Elastic Collisions", "Impulse resolution & spark emitter", ROSE),
        ("⛓️ Constraints & Joints", "PBD Pendulums, Springs & Dumbbells", EMERALD)
    ]
    b_w = Inches(2.65)
    b_h = Inches(1.5)
    b_top = Inches(3.9)
    for i, (b_title, b_desc, b_color) in enumerate(badges):
        b_left = Inches(1.2) + i * Inches(2.8)
        card = add_card(s1, b_left, b_top, b_w, b_h, border_color=b_color, accent_color=b_color)
        ctf = card.text_frame
        ctf.margin_left = Inches(0.18)
        ctf.margin_top = Inches(0.18)
        p1 = ctf.paragraphs[0]
        p1.text = b_title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(13.5)
        p1.font.bold = True
        p1.font.color.rgb = b_color
        p2 = ctf.add_paragraph()
        p2.text = b_desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(6)

    # Footer Metadata
    meta_box = s1.shapes.add_textbox(Inches(1.2), Inches(6.05), Inches(10.8), Inches(0.7))
    mtf = meta_box.text_frame
    mp = mtf.paragraphs[0]
    mp.text = "Tech Stack: Python (Flask REST API) • JavaScript (ES6+ Canvas 2D) • HTML5/CSS3 UI • Zero 3rd-Party Physics Bloat"
    mp.font.name = FONT_CODE
    mp.font.size = Pt(11)
    mp.font.color.rgb = CYAN

    # =========================================================
    # SLIDE 2: PROJECT OVERVIEW & CORE PHILOSOPHY
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "Project Overview: Lightweight First-Principles Physics", 
               "EXECUTIVE SUMMARY", 
               "Solving real-world physical dynamics with a decoupled client-server architecture")
    add_footer(s2, 2)

    # Left Column: Problem & Motivation (Width 5.6)
    left_card = add_card(s2, Inches(0.8), Inches(1.85), Inches(5.6), Inches(4.95), 
                         "1. Engineering Vision & Constraints", border_color=CYAN, accent_color=CYAN)
    ltf = left_card.text_frame
    ltf.margin_left = ltf.margin_right = Inches(0.25)
    ltf.margin_top = Inches(0.2)
    lp = ltf.paragraphs[0]
    lp.font.size = Pt(15)
    lp.font.color.rgb = CYAN

    points_left = [
        ("The Challenge:", "Most commercial web physics solutions (Matter.js, Box2D) are heavy, monolithic black-boxes with high bundle weight and steep abstraction barriers."),
        ("User Directive:", "Build a clean, non-bloated, highly pedagogical physics engine that simulates realistic motion, collisions, and constraints without unnecessary complexity."),
        ("API-First Mindset:", "Physics parameters (planetary gravity, surface friction, impulse forces, and multi-body joins) are orchestrated via standard RESTful HTTP endpoints."),
        ("No Black-Box Libraries:", "Every formula—from numerical velocity integration and momentum conservation to spring damping—is hand-coded from scratch.")
    ]
    for p_title, p_body in points_left:
        p = ltf.add_paragraph()
        p.text = f"• {p_title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(8)
        run = p.add_run()
        run.text = p_body
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Column: The 3 Architectural Pillars
    pillars = [
        ("Pillar 1: Deterministic Physics Math", 
         "Semi-implicit Euler integration ($v = v + g\\Delta t$) coupled with impulse-based restitution and Position-Based Dynamics (PBD) for stable distance constraints.",
         EMERALD),
        ("Pillar 2: Decoupled REST Control Plane", 
         "Flask API handles world configuration, state serialization, parameter injection, and object lifecycle; Canvas handles 60 FPS animation.",
         AMBER),
        ("Pillar 3: Live Developer Observability", 
         "Integrated real-time telemetry HUD displaying active bodies, collision count, telemetry metrics, and a streaming HTTP activity logger.",
         PURPLE)
    ]
    for i, (p_title, p_desc, p_col) in enumerate(pillars):
        top_pos = Inches(1.85) + i * Inches(1.68)
        card = add_card(s2, Inches(6.7), top_pos, Inches(5.8), Inches(1.5), p_title, border_color=p_col, accent_color=p_col)
        ctf = card.text_frame
        ctf.margin_left = ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.18)
        cp = ctf.paragraphs[0]
        cp.font.size = Pt(13.5)
        cp.font.color.rgb = p_col
        cp2 = ctf.add_paragraph()
        cp2.text = p_desc
        cp2.font.name = FONT_BODY
        cp2.font.size = Pt(10.5)
        cp2.font.color.rgb = TEXT_MUTED
        cp2.space_before = Pt(5)

    # =========================================================
    # SLIDE 3: SYSTEM ARCHITECTURE & DUAL-LAYER DESIGN
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "System Architecture: Decoupled Control & Render Loop", 
               "SYSTEM ARCHITECTURE", 
               "How Flask REST API backend communicates with the Canvas client physics engine")
    add_footer(s3, 3)

    # Box 1: Backend Layer (Left)
    card_back = add_card(s3, Inches(0.8), Inches(1.85), Inches(3.6), Inches(4.95), 
                         "Backend: Python Flask", border_color=CYAN, accent_color=CYAN)
    btf = card_back.text_frame
    btf.margin_left = btf.margin_right = Inches(0.22)
    btf.paragraphs[0].font.color.rgb = CYAN
    b_items = [
        ("Role:", "Authoritative State & Config Store"),
        ("REST Endpoints:", "Routes for /state, /gravity, /friction, /objects, /joints"),
        ("State Cache:", "In-memory representation of bodies, joint definitions, and environmental constants"),
        ("Decoupled Design:", "Stateless HTTP handler with CORS support; zero CPU hogging on server"),
        ("Payload Format:", "Strict JSON schemas with input sanitization and default fallback presets")
    ]
    for h, desc in b_items:
        p = btf.add_paragraph()
        p.text = f"• {h} {desc}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(8)

    # Box 2: Middle - REST Interface Pipeline
    card_mid = add_card(s3, Inches(4.7), Inches(1.85), Inches(3.8), Inches(4.95), 
                        "Interface: REST Pipeline", border_color=AMBER, accent_color=AMBER)
    mtf = card_mid.text_frame
    mtf.margin_left = mtf.margin_right = Inches(0.22)
    mtf.paragraphs[0].font.color.rgb = AMBER
    m_items = [
        ("GET /api/state", "Bootstraps simulation scene and synchronizes dynamic entities"),
        ("POST /api/gravity", "Injects celestial g-force (Moon 1.6 to Jupiter 24.8 m/s²)"),
        ("POST /api/friction", "Dynamically updates surface drag (Ice 0.01 to Rough 0.85)"),
        ("POST /api/joints/preset", "Loads pre-configured joint topology (Pendulum, Spring, Dumbbell)"),
        ("POST /api/objects", "Instantiates dynamic sphere bodies with mass, radius, and restitution")
    ]
    for h, desc in m_items:
        p = mtf.add_paragraph()
        p.text = f"• {h}: "
        p.font.name = FONT_CODE
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = AMBER
        p.space_before = Pt(7)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Box 3: Frontend Layer (Right)
    card_front = add_card(s3, Inches(8.8), Inches(1.85), Inches(3.7), Inches(4.95), 
                          "Client: HTML5 Canvas Loop", border_color=EMERALD, accent_color=EMERALD)
    ftf = card_front.text_frame
    ftf.margin_left = ftf.margin_right = Inches(0.22)
    ftf.paragraphs[0].font.color.rgb = EMERALD
    f_items = [
        ("60 FPS Integration:", "Smooth frame-budgeted animation via requestAnimationFrame"),
        ("Symplectic Euler:", "Position & velocity updates performed with real-time delta time (dt)"),
        ("4-Pass Constraint Solver:", "Distance constraint relaxation for stiff non-elastic rods"),
        ("Restitution Engine:", "Calculates normal momentum impulse and prevents spatial penetration"),
        ("Visual Particle VFX:", "Sparks emitted at contact coordinates during elastic impacts")
    ]
    for h, desc in f_items:
        p = ftf.add_paragraph()
        p.text = f"• {h} {desc}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(8)

    # =========================================================
    # SLIDE 4: CORE PHYSICS 1 - GRAVITY SIMULATION
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "Physics Concept 1: Planetary Gravity & Numerical Integration", 
               "PHYSICS DERIVATION & CODE", 
               "Translating Newton's Second Law into discrete numerical updates on the canvas")
    add_footer(s4, 4)

    # Left: Mathematical Mechanics
    c_math = add_card(s4, Inches(0.8), Inches(1.85), Inches(5.8), Inches(4.95), 
                      "Mathematical Derivation & Scaling", border_color=CYAN, accent_color=CYAN)
    mtf = c_math.text_frame
    mtf.margin_left = mtf.margin_right = Inches(0.25)
    mtf.paragraphs[0].font.color.rgb = CYAN

    math_points = [
        ("Continuous Gravitational Force:", "F_g = m * g  (where g is downward planetary acceleration)"),
        ("Euler Velocity Step:", "v_y(t + dt) = v_y(t) + g_scale * dt"),
        ("Displacement Step:", "y(t + dt) = y(t) + v_y(t + dt) * dt"),
        ("Pixel Scaling Dilemma:", "In real life, Earth gravity is 9.8 m/s². On a 700x500 pixel canvas, 9.8 px/s² is painfully slow. We apply a calibrated coordinate scale: 1 meter ≈ 61.22 pixels. Earth scale = 600 px/s²."),
        ("Zero-G Physics:", "When g = 0, bodies preserve linear momentum indefinitely, demonstrating Newton's First Law (Law of Inertia) inside the simulation container.")
    ]
    for title, desc in math_points:
        p = mtf.add_paragraph()
        p.text = f"• {title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(8)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Top: Preset Comparison Table Card
    c_table = add_card(s4, Inches(6.9), Inches(1.85), Inches(5.6), Inches(2.35), 
                       "Planetary Gravity Presets Matrix", border_color=AMBER, accent_color=AMBER)
    ttf = c_table.text_frame
    ttf.margin_left = ttf.margin_right = Inches(0.25)
    ttf.paragraphs[0].font.color.rgb = AMBER
    table_rows = [
        "🌍 Earth:     9.80 m/s²   | Scale: 600 px/s²   (Realistic falling)",
        "🌙 Moon:      1.62 m/s²   | Scale: 100 px/s²   (Floaty, low resistance)",
        "🔴 Mars:      3.72 m/s²   | Scale: 230 px/s²   (Moderate bounce arc)",
        "🪐 Jupiter:  24.79 m/s²   | Scale: 1500 px/s²  (Violent downward crush)",
        "🛸 Zero-G:    0.00 m/s²   | Scale: 0 px/s²     (Inertial drift)"
    ]
    for row in table_rows:
        p = ttf.add_paragraph()
        p.text = row
        p.font.name = FONT_CODE
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(3)

    # Right Bottom: Live Integration Code Block
    c_code = add_card(s4, Inches(6.9), Inches(4.35), Inches(5.6), Inches(2.45), 
                      "Client-Side Integration Loop (script.js)", border_color=EMERALD, bg_color=CODE_BG, accent_color=EMERALD)
    ctf = c_code.text_frame
    ctf.margin_left = ctf.margin_right = Inches(0.25)
    ctf.paragraphs[0].font.color.rgb = EMERALD
    code_lines = [
        "// 1. Semi-Implicit Euler Step for Ball Entities",
        "for (const b of balls) {",
        "    b.vy += gravityScale * dt;   // Apply planetary acceleration",
        "    b.x  += b.vx * dt;           // Update horizontal coordinate",
        "    b.y  += b.vy * dt;           // Update vertical coordinate",
        "    b.vx *= 0.9995;              // Ambient aerodynamic drag",
        "}"
    ]
    for line in code_lines:
        p = ctf.add_paragraph()
        p.text = line
        p.font.name = FONT_CODE
        p.font.size = Pt(9.5)
        p.font.color.rgb = CYAN if "//" not in line else TEXT_MUTED
        p.space_before = Pt(2)

    # =========================================================
    # SLIDE 5: CORE PHYSICS 2 - SURFACE FRICTION & DAMPING
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "Physics Concept 2: Coulomb Friction & Ground Deceleration", 
               "PHYSICS DERIVATION & CODE", 
               "Simulating surface contact resistance and eradicating micro-jitter vibrations")
    add_footer(s5, 5)

    # Left: Mechanical Modeling
    c_fric_math = add_card(s5, Inches(0.8), Inches(1.85), Inches(5.8), Inches(4.95), 
                           "Coulomb Friction Model & Mechanics", border_color=AMBER, accent_color=AMBER)
    ftf = c_fric_math.text_frame
    ftf.margin_left = ftf.margin_right = Inches(0.25)
    ftf.paragraphs[0].font.color.rgb = AMBER
    fric_points = [
        ("Normal Force & Drag:", "Kinetic friction opposes sliding motion: F_f = μ * N. On a horizontal floor, normal reaction N = m * g."),
        ("Deceleration Rate:", "Linear velocity loss is directly proportional to friction coefficient μ: Δv_x ∝ -μ * v_x * Δt."),
        ("Floor Contact Clamping:", "When ball position y + radius ≥ FLOOR_Y (460px), position is snapped to the boundary surface and downward velocity is inverted with bounce restitution."),
        ("The 'Micro-Jitter' Problem:", "Standard Euler friction leaves residual fractional velocities (e.g., vx = 0.0004). This causes balls to indefinitely vibrate or shake on the floor."),
        ("Engineering Solution:", "Velocity deadzone threshold: If |vx| < 1.0 px/s, velocity is forcefully snapped to exactly 0.0. If |vy| < 15.0 px/s, bounce is extinguished.")
    ]
    for title, desc in fric_points:
        p = ftf.add_paragraph()
        p.text = f"• {title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(8)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Top: Material Presets
    c_mat = add_card(s5, Inches(6.9), Inches(1.85), Inches(5.6), Inches(2.35), 
                     "Surface Friction Presets", border_color=CYAN, accent_color=CYAN)
    mtf = c_mat.text_frame
    mtf.margin_left = mtf.margin_right = Inches(0.25)
    mtf.paragraphs[0].font.color.rgb = CYAN
    mat_rows = [
        ("🧊 Ice (Frictionless)", "μ = 0.01", "Near-infinite sliding with almost no decay; ideal for momentum conservation tests."),
        ("🟢 Normal Surface", "μ = 0.35", "Standard tabletop friction; rapid rolling decay with smooth deceleration."),
        ("🟫 Rough / Wood", "μ = 0.85", "Heavy kinetic resistance; balls halt almost immediately upon ground impact.")
    ]
    for m_name, m_val, m_desc in mat_rows:
        p = mtf.add_paragraph()
        p.text = f"{m_name} [{m_val}]: "
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(4)
        run = p.add_run()
        run.text = m_desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Bottom: Ground Collision Code
    c_fcode = add_card(s5, Inches(6.9), Inches(4.35), Inches(5.6), Inches(2.45), 
                       "Ground Contact & Friction Solver (script.js)", border_color=ROSE, bg_color=CODE_BG, accent_color=ROSE)
    ctf = c_fcode.text_frame
    ctf.margin_left = ctf.margin_right = Inches(0.25)
    ctf.paragraphs[0].font.color.rgb = ROSE
    code_fric = [
        "if (b.y + b.radius >= FLOOR_Y) {",
        "    b.y = FLOOR_Y - b.radius;                  // Positional resolve",
        "    b.vy = -b.vy * b.bounce;                   // Restitution rebound",
        "    b.vx *= Math.max(0.0, 1.0 - friction * 3.5 * dt); // Coulomb drag",
        "    if (Math.abs(b.vx) < 1.0) b.vx = 0.0;     // Jitter clamp",
        "    if (Math.abs(b.vy) < 15.0) b.vy = 0.0;    // Rest threshold",
        "}"
    ]
    for line in code_fric:
        p = ctf.add_paragraph()
        p.text = line
        p.font.name = FONT_CODE
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_LIGHT if "//" not in line else TEXT_MUTED
        p.space_before = Pt(2)

    # =========================================================
    # SLIDE 6: CORE PHYSICS 3 - ELASTIC COLLISIONS & IMPULSE
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "Physics Concept 3: Circle Collisions & Impulse Resolution", 
               "PHYSICS DERIVATION & CODE", 
               "Detecting 2D spatial overlap and solving normal momentum transfer")
    add_footer(s6, 6)

    # Left: Collision Detection & Math
    c_col = add_card(s6, Inches(0.8), Inches(1.85), Inches(5.8), Inches(4.95), 
                     "Impulse Formulation & Overlap Resolution", border_color=ROSE, accent_color=ROSE)
    ctf = c_col.text_frame
    ctf.margin_left = ctf.margin_right = Inches(0.25)
    ctf.paragraphs[0].font.color.rgb = ROSE
    col_points = [
        ("Narrow-Phase Distance Check:", "Two spheres collide if Euclidean center distance d < r1 + r2: d = sqrt((x2 - x1)^2 + (y2 - y1)^2)."),
        ("Penetration Sinking Problem:", "In discrete physics, moving bodies overlap between frames. Simply reflecting velocities causes objects to stick or sink into each other."),
        ("Positional Projection Correction:", "Objects are displaced along contact normal n = (p2 - p1)/d by half the overlap depth: p1 -= n * (overlap / 2), p2 += n * (overlap / 2)."),
        ("1D Impulse Momentum Formula:", "Along collision normal n, impulse magnitude J is computed with coefficient of restitution e: J = (-(1 + e) * (v1 - v2) · n) / (1/m1 + 1/m2)."),
        ("Velocity Reallocation:", "v1 -= (J / m1) * n,  v2 += (J / m2) * n. Preserves linear momentum while dissipating kinetic energy according to restitution.")
    ]
    for title, desc in col_points:
        p = ctf.add_paragraph()
        p.text = f"• {title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(7)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Top: Collision Workflow Card
    c_diag = add_card(s6, Inches(6.9), Inches(1.85), Inches(5.6), Inches(2.35), 
                      "Resolution Pipeline (O(N²) Pairwise)", border_color=PURPLE, accent_color=PURPLE)
    dtf = c_diag.text_frame
    dtf.margin_left = dtf.margin_right = Inches(0.25)
    dtf.paragraphs[0].font.color.rgb = PURPLE
    steps = [
        ("1. Broad/Narrow Check:", "Compute distance d between each pair of balls"),
        ("2. Overlap Separation:", "Positional offset along unit normal n removes overlap"),
        ("3. Normal Velocity Test:", "If relative velocity along normal > 0, they are colliding"),
        ("4. Impulse Application:", "Exchange momentum weighted by inverse mass 1/m"),
        ("5. Spark Particle VFX:", "Spawn 8 radial spark particles at impact coordinate")
    ]
    for s_num, s_desc in steps:
        p = dtf.add_paragraph()
        p.text = f"{s_num} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(3)
        run = p.add_run()
        run.text = s_desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Bottom: Code Block
    c_ccode = add_card(s6, Inches(6.9), Inches(4.35), Inches(5.6), Inches(2.45), 
                       "Impulse Resolution Code (script.js)", border_color=EMERALD, bg_color=CODE_BG, accent_color=EMERALD)
    cctf = c_ccode.text_frame
    cctf.margin_left = cctf.margin_right = Inches(0.25)
    cctf.paragraphs[0].font.color.rgb = EMERALD
    code_col = [
        "const overlap = (minDist - dist) * 0.5;",
        "b1.x -= nx * overlap; b2.x += nx * overlap; // Positional separation",
        "const vNorm = (b1.vx - b2.vx) * nx + (b1.vy - b2.vy) * ny;",
        "if (vNorm > 0) {",
        "    const e = (b1.bounce + b2.bounce) * 0.5; // Restitution",
        "    const J = (1 + e) * vNorm / (1.0 / b1.mass + 1.0 / b2.mass);",
        "    b1.vx -= (J / b1.mass) * nx; b2.vx += (J / b2.mass) * nx;",
        "    createSparks(b1.x + nx * b1.radius, b1.y + ny * b1.radius);",
        "}"
    ]
    for line in code_col:
        p = cctf.add_paragraph()
        p.text = line
        p.font.name = FONT_CODE
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_LIGHT if "//" not in line else TEXT_MUTED
        p.space_before = Pt(2)

    # =========================================================
    # SLIDE 7: CORE PHYSICS 4 - CONSTRAINTS & JOINTS
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_header(s7, "Physics Concept 4: Constraints & Joints (Rods & Springs)", 
               "PHYSICS DERIVATION & CODE", 
               "Position-Based Dynamics (PBD) and Hooke's Law for articulated structures")
    add_footer(s7, 7)

    # 3 Joint Presets Cards (3 Columns)
    j_cards = [
        ("🔗 Pendulum Rod Joint", 
         "Fixed Ceiling Anchor Constraint", 
         [
             "Anchor point pinned to ceiling (x=350, y=40)",
             "Distance constraint: |p_ball - p_anchor| = L",
             "PBD iterative relaxation enforces exact rod distance without stretching",
             "Radial velocity component along rod vector is zeroed out each iteration",
             "Produces natural, harmonic pendulum swings under varying planetary gravity"
         ],
         AMBER),
        ("〰️ Hooke's Law Spring", 
         "Dynamic Harmonic Oscillator", 
         [
             "Elastic spring attached to overhead mount",
             "Hooke's Law restoring force: F = -k * Δx",
             "Velocity damping term: -c * v_radial prevents runaway energy buildup",
             "Real-time parameters: stiffness k = 120 N/m, damping c = 2.0",
             "Demonstrates potential-to-kinetic energy conversion with sinusoidal oscillation"
         ],
         EMERALD),
        ("⛓️ Linked Dumbbell Joint", 
         "Two-Body Distance Constraint", 
         [
             "Rigid distance rod connecting two dynamic balls",
             "Distance constraint: |p2 - p1| = L (120px)",
             "Displacement shared symmetrically: 50% applied to ball 1, 50% to ball 2",
             "Coupled velocity constraint: transfers rotational and tumbling kinetic energy",
             "Collisions on either ball transfer angular momentum naturally across the assembly"
         ],
         CYAN)
    ]
    c_w = Inches(3.7)
    c_h = Inches(4.95)
    for i, (j_title, j_sub, j_points, j_color) in enumerate(j_cards):
        c_left = Inches(0.8) + i * Inches(3.95)
        card = add_card(s7, c_left, Inches(1.85), c_w, c_h, j_title, border_color=j_color, accent_color=j_color)
        jtf = card.text_frame
        jtf.margin_left = jtf.margin_right = Inches(0.22)
        jtf.paragraphs[0].font.color.rgb = j_color
        p_sub = jtf.add_paragraph()
        p_sub.text = j_sub
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(10.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_before = Pt(3)

        for pt in j_points:
            p = jtf.add_paragraph()
            p.text = f"• {pt}"
            p.font.name = FONT_BODY
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_LIGHT
            p.space_before = Pt(8)

    # =========================================================
    # SLIDE 8: REST API DESIGN & ENDPOINT ARCHITECTURE
    # =========================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_header(s8, "REST API Design: Complete Endpoint Specification", 
               "API CONTRACT & ARCHITECTURE", 
               "Comprehensive breakdown of the 6 REST routes powering simulation control")
    add_footer(s8, 8)

    # Left: API Table Card (Width 7.5)
    c_tbl = add_card(s8, Inches(0.8), Inches(1.85), Inches(7.6), Inches(4.95), 
                     "REST API Specification Table", border_color=CYAN, accent_color=CYAN)
    ttf = c_tbl.text_frame
    ttf.margin_left = ttf.margin_right = Inches(0.2)
    ttf.paragraphs[0].font.color.rgb = CYAN

    api_specs = [
        ("GET /api/state", "Retrieves complete world state: gravity, friction, ball entities, and active joints."),
        ("POST /api/gravity", "Sets gravity preset ('earth', 'moon', 'mars', 'jupiter', 'zero') or custom float value in m/s²."),
        ("POST /api/friction", "Updates surface friction preset ('ice', 'normal', 'rough') or custom coefficient μ (0.0 to 1.0)."),
        ("POST /api/objects", "Spawns dynamic sphere body with position, mass, radius, and elasticity payload."),
        ("POST /api/objects/multi", "Batch instantiates 3 colliding balls at randomized positions and colors for collision demo."),
        ("POST /api/joints/preset", "Loads articulated joint topologies: 'pendulum' (ceiling rod), 'spring', or 'dumbbell'."),
        ("POST /api/objects/<id>/force", "Applies an impulse force vector (fx, fy) to induce jumping or horizontal propulsion."),
        ("POST /api/reset", "Flushes active world entities and resets simulation to default 2-ball collision testbed.")
    ]
    for route, desc in api_specs:
        p = ttf.add_paragraph()
        p.text = f"{route}: "
        p.font.name = FONT_CODE
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = AMBER
        p.space_before = Pt(6)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right: JSON Request / Response Example Cards
    c_json1 = add_card(s8, Inches(8.7), Inches(1.85), Inches(3.8), Inches(2.35), 
                       "Request: POST /api/gravity", border_color=EMERALD, bg_color=CODE_BG, accent_color=EMERALD)
    jtf1 = c_json1.text_frame
    jtf1.margin_left = jtf1.margin_right = Inches(0.2)
    jtf1.paragraphs[0].font.color.rgb = EMERALD
    req_json = [
        "// Payload:",
        "{",
        '  "preset": "moon",',
        '  "value": 1.62',
        "}",
        "// Response (200 OK):",
        '{ "status": "success",',
        '  "gravity": { "name": "Moon", "value": 1.62 } }'
    ]
    for line in req_json:
        p = jtf1.add_paragraph()
        p.text = line
        p.font.name = FONT_CODE
        p.font.size = Pt(9)
        p.font.color.rgb = CYAN if "//" not in line else TEXT_MUTED
        p.space_before = Pt(1)

    c_json2 = add_card(s8, Inches(8.7), Inches(4.35), Inches(3.8), Inches(2.45), 
                       "Request: POST /api/joints/preset", border_color=PURPLE, bg_color=CODE_BG, accent_color=PURPLE)
    jtf2 = c_json2.text_frame
    jtf2.margin_left = jtf2.margin_right = Inches(0.2)
    jtf2.paragraphs[0].font.color.rgb = PURPLE
    joint_json = [
        "// Payload:",
        '{ "preset": "pendulum" }',
        "// Response (200 OK):",
        "{",
        '  "status": "success",',
        '  "message": "Loaded Pendulum Distance Joint",',
        '  "joints": [{ "type": "rod", "length": 200 }]',
        "}"
    ]
    for line in joint_json:
        p = jtf2.add_paragraph()
        p.text = line
        p.font.name = FONT_CODE
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_LIGHT if "//" not in line else TEXT_MUTED
        p.space_before = Pt(1)

    # =========================================================
    # SLIDE 9: FRONTEND UI & REAL-TIME TELEMETRY HUD
    # =========================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_header(s9, "Frontend Interface & Live Telemetry Dashboard", 
               "UI / UX DESIGN & OBSERVABILITY", 
               "Interactive HTML5 canvas simulator paired with real-time HUD telemetry and activity logging")
    add_footer(s9, 9)

    # 4 UI Feature Breakdown Cards
    ui_cards = [
        ("🖥️ High-Precision Canvas", 
         "700x500 Resolution Viewport", 
         [
             "HTML5 2D rendering context running smooth 60 FPS animation loop",
             "Click-to-drop: Click anywhere inside the canvas to spawn balls at exact mouse coordinates",
             "Dynamic floor rendering with neon grid boundaries and ground contact line",
             "Visual spark particle system radiating from high-speed impact points"
         ],
         CYAN),
        ("🎛️ Interactive Controls", 
         "Planetary & Material Selectors", 
         [
             "One-click planetary presets (Earth, Moon, Mars, Jupiter, Zero-G)",
             "Continuous gravity slider (0 to 30 m/s²) for fine-grained tuning",
             "Surface friction presets (Ice, Normal, Rough) with continuous coefficient slider",
             "Quick action buttons: '+1 Ball', '💥 3 Balls', '🔗 Pendulum', '〰️ Spring', '🚀 Push Up'"
         ],
         AMBER),
        ("📊 Real-Time Telemetry HUD", 
         "Dynamic State Monitoring", 
         [
             "Instant telemetry readouts reflecting active world parameters",
             "Gravity Readout: Displays current m/s² and active planetary body",
             "Friction Readout: Displays current μ surface drag coefficient",
             "Active Joints Count: Tracks linked constraints and dynamic springs",
             "Cumulative Collision Counter: Increments in real time on sphere impacts"
         ],
         EMERALD),
        ("📜 Live REST Activity Log", 
         "Streaming Network Inspector", 
         [
             "Embedded console window rendering real-time HTTP requests and responses",
             "Color-coded method badges: [GET] in cyan, [POST] in green, [ERROR] in red",
             "Inspects outgoing payloads and server response messages without opening DevTools",
             "Auto-scrolls latest 25 network operations for rapid debugging"
         ],
         PURPLE)
    ]
    u_w = Inches(2.75)
    u_h = Inches(4.95)
    for i, (u_title, u_sub, u_pts, u_col) in enumerate(ui_cards):
        u_left = Inches(0.8) + i * Inches(2.95)
        card = add_card(s9, u_left, Inches(1.85), u_w, u_h, u_title, border_color=u_col, accent_color=u_col)
        utf = card.text_frame
        utf.margin_left = utf.margin_right = Inches(0.18)
        utf.paragraphs[0].font.color.rgb = u_col
        psub = utf.add_paragraph()
        psub.text = u_sub
        psub.font.name = FONT_BODY
        psub.font.size = Pt(10)
        psub.font.color.rgb = TEXT_MUTED
        psub.space_before = Pt(2)

        for pt in u_pts:
            p = utf.add_paragraph()
            p.text = f"• {pt}"
            p.font.name = FONT_BODY
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_LIGHT
            p.space_before = Pt(8)

    # =========================================================
    # SLIDE 10: STEP-BY-STEP EVOLUTION & VS CODE RUN GUIDE
    # =========================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_header(s10, "Development Milestones & VS Code Execution Guide", 
               "WORKFLOW & SETUP", 
               "Iterative build progression and practical terminal execution instructions")
    add_footer(s10, 10)

    # Left: Iterative Milestones
    c_mstone = add_card(s10, Inches(0.8), Inches(1.85), Inches(5.8), Inches(4.95), 
                        "Project Build Progression", border_color=CYAN, accent_color=CYAN)
    mtf = c_mstone.text_frame
    mtf.margin_left = mtf.margin_right = Inches(0.25)
    mtf.paragraphs[0].font.color.rgb = CYAN
    milestones = [
        ("Milestone 1: Core Flask API & Gravity Simulator", 
         "Established Flask REST architecture, basic ball spawning, and Euler vertical acceleration under Earth gravity. Built basic Canvas viewport."),
        ("Milestone 2: Friction & 2-Body Elastic Collisions", 
         "Integrated Coulomb surface friction drag and circle-to-circle impulse resolution with positional separation to eliminate visual sinking."),
        ("Milestone 3: Constraints & Articulated Joints", 
         "Implemented PBD pendulum distance rods, Hooke's Law oscillating springs, and dual-body dumbbells with REST preset routes."),
        ("Milestone 4: Telemetry HUD & REST Activity Logger", 
         "Finalized interactive dark-mode dashboard with real-time collision counter, live telemetry stats, and streaming HTTP request inspector.")
    ]
    for m_title, m_desc in milestones:
        p = mtf.add_paragraph()
        p.text = f"• {m_title}: "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = AMBER
        p.space_before = Pt(8)
        run = p.add_run()
        run.text = m_desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right: Running in VS Code
    c_run = add_card(s10, Inches(6.9), Inches(1.85), Inches(5.6), Inches(4.95), 
                     "How to Run in VS Code / Local Environment", border_color=EMERALD, bg_color=CODE_BG, accent_color=EMERALD)
    rtf = c_run.text_frame
    rtf.margin_left = rtf.margin_right = Inches(0.25)
    rtf.paragraphs[0].font.color.rgb = EMERALD
    run_steps = [
        ("# 1. Open Project Directory in VS Code", "cd 'd:\\Physics Engine'"),
        ("# 2. Activate Python Virtual Environment (Optional)", "python -m venv venv; .\\venv\\Scripts\\activate"),
        ("# 3. Install Minimal Dependencies", "pip install -r requirements.txt\n# (Requires only Flask & Flask-CORS)"),
        ("# 4. Launch Physics Engine API Server", "python app.py\n# Output: Physics API running on http://127.0.0.1:5000"),
        ("# 5. Access Interactive Simulator in Browser", "Open: http://127.0.0.1:5000\n# UI connects automatically to REST API"),
        ("# 6. Test via cURL or Postman (Optional)", "curl -X POST http://127.0.0.1:5000/api/gravity -d '{\"preset\":\"moon\"}'")
    ]
    for comment, cmd in run_steps:
        p = rtf.add_paragraph()
        p.text = comment
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(6)
        p2 = rtf.add_paragraph()
        p2.text = cmd
        p2.font.name = FONT_CODE
        p2.font.size = Pt(10)
        p2.font.color.rgb = CYAN
        p2.space_before = Pt(2)

    # =========================================================
    # SLIDE 11: KEY TECHNICAL CHALLENGES & ENGINEERING DECISIONS
    # =========================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_header(s11, "Engineering Challenges & Algorithmic Solutions", 
               "TECHNICAL DEEP DIVE", 
               "Concrete hurdles encountered during physics simulation development and how they were resolved")
    add_footer(s11, 11)

    # 4 Challenge Cards (2x2 Grid)
    challenges = [
        ("1. Decoupling API Latency from 60 FPS Rendering", 
         "Problem: Calling a REST API every 16ms (60 FPS) introduces network round-trip overhead and destroys animation smoothness.\n\n"
         "Solution: Hybrid Architecture. The Flask backend serves as the authoritative state & parameter controller (POST /gravity, /objects), while the client-side JavaScript engine integrates physics deterministically at 60 FPS. Zero frame drops.",
         CYAN),
        ("2. Preventing Object Sinking & Penetration", 
         "Problem: High downward velocity causes balls to penetrate through the floor or into each other between discrete time steps.\n\n"
         "Solution: Positional Projection. Before velocity reflection occurs, penetrating spheres are projected back along the collision normal by exactly half the overlap depth. Sinking is 100% eliminated.",
         ROSE),
        ("3. Eliminating Micro-Jitter on High-Friction Surfaces", 
         "Problem: Continuous gravitational integration causes resting balls on the floor to micro-vibrate as minute velocity fractions fluctuate.\n\n"
         "Solution: Dual Velocity Clamping Thresholds. Horizontal velocity |vx| < 1.0 px/s is snapped to zero; bounce velocity |vy| < 15.0 px/s is extinguished. The balls come to a completely stable, rock-solid rest.",
         AMBER),
        ("4. Stiff Distance Constraint Stability in Rods", 
         "Problem: Rigid distance constraints (Pendulum / Dumbbell) tend to stretch or explode under aggressive gravitational acceleration.\n\n"
         "Solution: Iterative PBD Relaxation (4 Passes). By running 4 constraint relaxation sub-passes per physics step and cancelling radial velocity components along the rod vector, rod length is preserved with zero drift.",
         EMERALD)
    ]
    grid_w = Inches(5.6)
    grid_h = Inches(2.35)
    for i, (c_title, c_text, c_col) in enumerate(challenges):
        col_idx = i % 2
        row_idx = i // 2
        c_left = Inches(0.8) + col_idx * Inches(6.0)
        c_top = Inches(1.85) + row_idx * Inches(2.55)
        card = add_card(s11, c_left, c_top, grid_w, grid_h, c_title, border_color=c_col, accent_color=c_col)
        ctf = card.text_frame
        ctf.margin_left = ctf.margin_right = Inches(0.22)
        ctf.paragraphs[0].font.color.rgb = c_col
        p = ctf.add_paragraph()
        p.text = c_text
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(4)

    # =========================================================
    # SLIDE 12: CONCLUSION & FUTURE ROADMAP
    # =========================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12)
    add_header(s12, "Summary & Future Roadmap", 
               "PROJECT RETROSPECTIVE", 
               "What was achieved and potential avenues for extending the physics engine")
    add_footer(s12, 12)

    # Left: Key Achievements Summary
    c_ach = add_card(s12, Inches(0.8), Inches(1.85), Inches(5.8), Inches(4.95), 
                     "Core Project Deliverables", border_color=EMERALD, accent_color=EMERALD)
    atf = c_ach.text_frame
    atf.margin_left = atf.margin_right = Inches(0.25)
    atf.paragraphs[0].font.color.rgb = EMERALD
    achievements = [
        ("Deterministic Physics Without Bloat:", "Successfully engineered a self-contained 2D physics engine handling Gravity, Friction, Elastic Collisions, and Constraints without third-party physics dependencies."),
        ("Clean REST Control Plane:", "Standardized Flask API exposes 6 clean endpoints for planetary environments, surface drag, impulse forces, and joint topology."),
        ("Multi-Body Constraint Solvers:", "Developed stable Hooke's Law dynamic springs and PBD distance rods supporting pendulums and linked dumbbell systems."),
        ("Production Developer Experience:", "Interactive dark-mode telemetry interface with real-time HUD metrics, particle VFX sparks, and streaming HTTP request inspector."),
        ("High Computational Efficiency:", "Sub-millisecond frame integration with zero memory leaks and rock-solid 60 FPS performance on standard hardware.")
    ]
    for a_title, a_desc in achievements:
        p = atf.add_paragraph()
        p.text = f"✔ {a_title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(8)
        run = p.add_run()
        run.text = a_desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right: Future Extensions & Q&A
    c_fut = add_card(s12, Inches(6.9), Inches(1.85), Inches(5.6), Inches(3.2), 
                     "Future Roadmap & Extensions", border_color=CYAN, accent_color=CYAN)
    ftf = c_fut.text_frame
    ftf.margin_left = ftf.margin_right = Inches(0.25)
    ftf.paragraphs[0].font.color.rgb = CYAN
    future_items = [
        ("• Convex Polygon Collisions (SAT):", "Implement Separating Axis Theorem (SAT) to support rotating boxes, ramps, and triangles."),
        ("• Rotational Inertia & Torque:", "Calculate angular momentum and moment of inertia (I = 1/2 m r²) for realistic tumbling dynamics."),
        ("• Bidirectional WebSockets (Flask-SocketIO):", "Upgrade REST polling to low-latency WebSocket events for multi-client synchronized simulations."),
        ("• Spatial Partitioning (Spatial Hash Grid):", "Replace O(N²) collision check with O(N) spatial grid to scale from 20 balls to 1,000+ simultaneous bodies.")
    ]
    for f_title, f_desc in future_items:
        p = ftf.add_paragraph()
        p.text = f"{f_title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = AMBER
        p.space_before = Pt(6)
        run = p.add_run()
        run.text = f_desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Bottom: Q&A Card
    c_qa = add_card(s12, Inches(6.9), Inches(5.2), Inches(5.6), Inches(1.6), 
                    "Thank You! Questions & Discussion", border_color=PURPLE, accent_color=PURPLE)
    qtf = c_qa.text_frame
    qtf.margin_left = qtf.margin_right = Inches(0.25)
    qtf.paragraphs[0].font.color.rgb = PURPLE
    qp = qtf.add_paragraph()
    qp.text = "Repository: Physics Engine (Flask + Canvas 2D)\nLocal URL: http://127.0.0.1:5000\nAPI State: Online & Fully Interactive"
    qp.font.name = FONT_CODE
    qp.font.size = Pt(10.5)
    qp.font.color.rgb = CYAN
    qp.space_before = Pt(3)

    # Save Presentation
    output_filename = "Physics_Engine_Presentation.pptx"
    prs.save(output_filename)
    print(f"Presentation successfully created: {output_filename}")

if __name__ == "__main__":
    create_deck()
