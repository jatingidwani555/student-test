import streamlit as st
import pandas as pd
import time
import database
import styles

def format_time(seconds):
    """Format seconds into MM:SS."""
    if seconds < 0:
        return "00:00"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def show_student_dashboard():
    """Render the Student Dashboard and Exam Client."""
    # Apply custom style inject
    styles.inject_custom_css()
    
    # Initialize exam state keys in session state
    if 'active_exam_id' not in st.session_state:
        st.session_state.active_exam_id = None
    if 'exam_state' not in st.session_state:
        st.session_state.exam_state = None

    # IF EXAM IS ACTIVE, RENDER EXAM ENGINE (HIDING NORMAL LAYOUT)
    if st.session_state.active_exam_id is not None:
        render_exam_engine()
        return

    # Normal Dashboard Header
    st.markdown('<div class="gradient-text">Student Workspace</div>', unsafe_allow_html=True)
    st.markdown(f"Welcome, **{st.session_state.full_name}** | Student Portal")
    st.markdown("---")

    tab_dash, tab_exams = st.tabs([
        "🏠 Dashboard & Performance", 
        "📝 Available Examinations"
    ])

    # TAB 1: DASHBOARD & PERFORMANCE HISTORY
    with tab_dash:
        # Load attempts
        results = database.get_user_results(st.session_state.username)
        total_taken = len(results)
        
        # Calculate stats
        if total_taken > 0:
            df_res = pd.DataFrame([dict(r) for r in results])
            avg_score = round(df_res['percentage'].mean(), 1)
            highest_score = round(df_res['percentage'].max(), 1)
        else:
            avg_score = 0.0
            highest_score = 0.0

        # Custom Metrics Grid
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-box-label">Exams Completed</div>
                <div class="metric-box-value">{total_taken}</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Average Score</div>
                <div class="metric-box-value" style="color: #4D96FF;">{avg_score}%</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Highest Score</div>
                <div class="metric-box-value" style="color: #6BCB77;">{highest_score}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass-card-header">Performance Trend</div>', unsafe_allow_html=True)
        if total_taken > 0:
            col_chart, col_history = st.columns([3, 2])
            with col_chart:
                # Plotly-like area chart using Streamlit's native area chart
                # Chronological sorting for line charts
                df_chron = df_res.sort_values(by='completed_at').reset_index()
                df_chron['Attempt Number'] = df_chron.index + 1
                df_plot = df_chron[['Attempt Number', 'percentage']].set_index('Attempt Number')
                df_plot.columns = ['Score (%)']
                st.area_chart(df_plot, height=220)
                
            with col_history:
                st.markdown("**Recent Attempts**")
                for _, r in df_res.head(5).iterrows():
                    pass_fail = "PASS" if r['percentage'] >= 40 else "FAIL"
                    badge_style = "badge-success" if pass_fail == "PASS" else "badge-danger"
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid rgba(255,255,255,0.1);">
                        <div style="display:flex; justify-content:space-between; font-weight:600; font-size: 0.9rem;">
                            <span>{r['exam_title']}</span>
                            <span class="custom-badge {badge_style}">{pass_fail}</span>
                        </div>
                        <div style="font-size: 0.8rem; color:#a0aec0; margin-top:4px;">
                            Score: {r['score']}/{r['total_marks']} ({r['percentage']}%) | {r['completed_at'][:16]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("You haven't attempted any exams yet. Go to the 'Available Examinations' tab to start your first test!")

    # TAB 2: AVAILABLE EXAMS
    with tab_exams:
        st.markdown('<div class="glass-card-header">Select an Examination</div>', unsafe_allow_html=True)
        exams = database.get_all_exams()
        
        if exams:
            for exam in exams:
                # Render clean cards for each exam
                q_count = exam['question_count']
                
                # Check if exam has questions before letting student take it
                has_questions = q_count > 0
                
                # Glass Card layout
                col_info, col_act = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 12px; padding: 16px;">
                        <h4 style="margin: 0 0 6px 0; color: #ffffff;">{exam['title']}</h4>
                        <p style="margin: 0 0 10px 0; color: #a0aec0; font-size: 0.85rem;">{exam['description'] or "No description provided."}</p>
                        <div style="display: flex; gap: 16px; font-size: 0.8rem; color: #4D96FF;">
                            <span>⏱️ <b>{exam['duration_minutes']} Mins</b></span>
                            <span>📋 <b>{q_count} MCQ Questions</b></span>
                            <span>🏆 <b>{exam['total_marks'] or 0} Total Marks</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_act:
                    # Vertical alignment spacer
                    st.write("")
                    st.write("")
                    if has_questions:
                        if st.button("🚀 Start Exam", key=f"start_{exam['id']}", use_container_width=True):
                            initiate_exam(exam)
                    else:
                        st.button("⚠️ No Questions Available", key=f"disabled_{exam['id']}", disabled=True, use_container_width=True)
        else:
            st.info("No active examinations available at the moment. Please contact the administrator.")

def initiate_exam(exam):
    """Set up the active session states for the exam client."""
    questions = database.get_exam_questions(exam['id'])
    
    st.session_state.active_exam_id = exam['id']
    st.session_state.exam_state = {
        "exam_title": exam['title'],
        "duration_minutes": exam['duration_minutes'],
        "questions": [dict(q) for q in questions],
        "answers": {},  # {question_index: selected_option}
        "start_time": time.time(),
        "duration_seconds": exam['duration_minutes'] * 60,
        "current_index": 0,
        "submitted": False
    }
    st.rerun()

def render_exam_engine():
    """Render the active full-screen examination engine."""
    state = st.session_state.exam_state
    if not state:
        st.session_state.active_exam_id = None
        st.rerun()
        return

    # Anti-cheat note: We hide the standard navigation elements by not rendering headers/tabs
    
    # Calculate Timer
    elapsed = time.time() - state['start_time']
    remaining = state['duration_seconds'] - elapsed
    
    # AUTO-SUBMIT IF TIMER EXPIRES
    if remaining <= 0 and not state['submitted']:
        st.session_state.exam_state['submitted'] = True
        st.error("⏳ Time is up! Your exam is being automatically submitted...")
        time.sleep(1.5)
        finalize_exam()
        return

    # Exam Panel Header
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f'<div class="gradient-text-sub">{state["exam_title"]}</div>', unsafe_allow_html=True)
        st.markdown("⚠️ *Do not close or refresh this browser tab. Refreshing will invalidate your exam state.*")
    with col_t2:
        # Styled Countdown Timer box
        st.markdown(f"""
        <div class="exam-timer-box">
            <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #a0aec0; margin-bottom: 2px;">Time Remaining</div>
            <div class="timer-text">{format_time(remaining)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Trigger screen refresh frequently to keep the timer precise
        # This acts as a tick rate in Streamlit (usually every second is fine)
        # However, to be friendly, we can rely on standard Streamlit component refreshes.
        # Running an empty container with st.empty() or a quick sleep is nice, but Streamlit has a built-in st.empty helper or we can let them navigate, and we'll re-verify remaining time at every interaction.

    # If exam is already submitted (Viewing report card)
    if state['submitted']:
        render_results_card()
        return

    # Questions List & Navigation
    questions = state['questions']
    curr_idx = state['current_index']
    total_q = len(questions)
    
    if total_q == 0:
        st.error("No questions found in this exam. Returning to dashboard.")
        if st.button("Back"):
            st.session_state.active_exam_id = None
            st.rerun()
        return

    q = questions[curr_idx]
    
    st.markdown("---")

    # Outer Layout: Question View + Right Sidebar Question Grid
    col_q_body, col_q_grid = st.columns([3, 1])
    
    with col_q_body:
        # Question Details
        st.markdown(f"""
        <div class="question-card">
            <span class="custom-badge badge-primary">Question {curr_idx + 1} of {total_q}</span>
            <span style="float: right; color: #a0aec0; font-size: 0.85rem;">Weightage: <b>{q['marks']} Marks</b></span>
            <div class="question-title" style="margin-top: 12px;">{q['question_text']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulate Options
        options = {
            "A": q['option_a'],
            "B": q['option_b'],
            "C": q['option_c'],
            "D": q['option_d']
        }
        
        # Retain previous selection
        prev_ans = state['answers'].get(curr_idx, None)
        
        # Streamlit Radio for answering
        # We index the radio based on user's previous selection
        option_list = ["A", "B", "C", "D"]
        preselect_idx = option_list.index(prev_ans) if prev_ans in option_list else None
        
        ans_radio = st.radio(
            "Select the correct option:",
            options=["A", "B", "C", "D"],
            format_func=lambda x: f"({x})  {options[x]}",
            index=preselect_idx if preselect_idx is not None else 0,
            key=f"q_radio_{curr_idx}"
        )
        
        # If user selected an answer, save it
        # By default radio pre-selects index 0, so if they have never selected, we save 'A' or let them leave it.
        # A premium system registers an input if they actively check. To handle this, we can add a 'Clear Selection' or let index 0 be default.
        # Let's save the selected answer actively.
        state['answers'][curr_idx] = ans_radio
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation Buttons
        col_nav_prev, col_nav_spacer, col_nav_next = st.columns([1, 2, 1])
        with col_nav_prev:
            if curr_idx > 0:
                if st.button("◀️ Previous", use_container_width=True):
                    state['current_index'] -= 1
                    st.rerun()
        with col_nav_next:
            if curr_idx < total_q - 1:
                if st.button("Next ▶️", use_container_width=True):
                    state['current_index'] += 1
                    st.rerun()

    with col_q_grid:
        st.markdown('<div class="glass-card-header" style="font-size:1.1rem;">Exam Grid Map</div>', unsafe_allow_html=True)
        st.write("Click a number to jump directly to that question:")
        
        # Generate custom styled question map buttons using column groups
        grid_cols = st.columns(4)
        for i in range(total_q):
            col_target = grid_cols[i % 4]
            is_attempted = i in state['answers']
            is_current = i == curr_idx
            
            btn_class = "q-grid-btn-current" if is_current else ("q-grid-btn-attempted" if is_attempted else "q-grid-btn-unattempted")
            
            with col_target:
                if st.button(f"{i+1}", key=f"grid_btn_{i}", use_container_width=True):
                    state['current_index'] = i
                    st.rerun()
                    
        st.markdown("---")
        # Submit Examination
        submit_btn = st.button("🚨 Submit Examination", type="primary", use_container_width=True)
        if submit_btn:
            # Pop up standard confirmation dialog
            st.session_state.show_confirm = True

    if st.session_state.get('show_confirm', False):
        st.markdown("""
        <div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.3); border-radius: 12px; padding: 20px; margin-top:20px;">
            <h4 style="color:#FF6B6B; margin-top:0;">⚠️ Confirm Exam Submission</h4>
            <p>Are you sure you want to finalize and submit your examination? You will not be able to change your answers after submission.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("✅ Yes, Submit Now", use_container_width=True):
                st.session_state.show_confirm = False
                finalize_exam()
        with col_c2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_confirm = False
                st.rerun()

def finalize_exam():
    """Calculate exam scores, write attempt logs to database, and mark submitted."""
    state = st.session_state.exam_state
    questions = state['questions']
    answers = state['answers']
    
    score = 0
    total_marks = 0
    
    for idx, q in enumerate(questions):
        q_marks = q['marks'] or 1
        total_marks += q_marks
        
        user_answer = answers.get(idx, None)
        correct_answer = q['correct_option']
        
        if user_answer == correct_answer:
            score += q_marks
            
    percentage = round((score / total_marks) * 100, 1) if total_marks > 0 else 0.0
    
    # Save to Database
    database.save_result(
        st.session_state.username,
        st.session_state.active_exam_id,
        score,
        total_marks,
        percentage
    )
    
    # Set submitted state to render the review card
    st.session_state.exam_state['submitted'] = True
    st.session_state.exam_state['calculated_score'] = score
    st.session_state.exam_state['calculated_total'] = total_marks
    st.session_state.exam_state['calculated_pct'] = percentage
    st.rerun()

def render_results_card():
    """Display the detailed, beautifully-formatted scorecard and review sheets."""
    state = st.session_state.exam_state
    score = state['calculated_score']
    total_marks = state['calculated_total']
    pct = state['calculated_pct']
    
    # Success vs Fail parameters
    is_passed = pct >= 40
    status_text = "PASSED" if is_passed else "FAILED"
    status_class = "badge-success" if is_passed else "badge-danger"
    text_color = "#6BCB77" if is_passed else "#FF6B6B"
    
    st.markdown('<div class="gradient-text-sub">Exam Report Card</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="glass-card" style="text-align: center; border-left: 6px solid {text_color}; padding: 30px;">
        <span class="custom-badge {status_class}" style="font-size: 1rem; padding: 6px 16px;">{status_text}</span>
        <h2 style="margin: 16px 0 8px 0; font-size: 2.2rem; color: #ffffff;">{pct}% Score</h2>
        <div style="font-size: 1.2rem; color: #a0aec0;">
            Earned <b>{score}</b> out of <b>{total_marks}</b> possible marks.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exit button to dashboard
    if st.button("🏠 Back to Student Workspace", type="primary", use_container_width=True):
        st.session_state.active_exam_id = None
        st.session_state.exam_state = None
        st.rerun()
        
    st.markdown("### 📋 Question-by-Question Review")
    
    questions = state['questions']
    answers = state['answers']
    
    for idx, q in enumerate(questions):
        user_ans = answers.get(idx, "Unattempted")
        correct_ans = q['correct_option']
        is_correct = user_ans == correct_ans
        
        border_col = "#6BCB77" if is_correct else "#FF6B6B"
        icon = "✅" if is_correct else "❌"
        
        # Options map
        opts = {
            "A": q['option_a'],
            "B": q['option_b'],
            "C": q['option_c'],
            "D": q['option_d']
        }
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.02); border-left: 4px solid {border_col}; border-radius: 4px 12px 12px 4px; padding: 18px; margin-bottom: 16px;">
            <div style="font-weight:600; color:#ffffff; font-size:1.1rem; display:flex; justify-content:space-between;">
                <span>{idx+1}. {q['question_text']}</span>
                <span>{icon}</span>
            </div>
            <div style="margin-top: 12px; font-size:0.9rem;">
                <div style="margin-bottom: 4px; color: {'#6BCB77' if user_ans == 'A' else ('#FF6B6B' if not is_correct and user_ans == 'A' else '#a0aec0')}"><b>A:</b> {opts['A']}</div>
                <div style="margin-bottom: 4px; color: {'#6BCB77' if user_ans == 'B' else ('#FF6B6B' if not is_correct and user_ans == 'B' else '#a0aec0')}"><b>B:</b> {opts['B']}</div>
                <div style="margin-bottom: 4px; color: {'#6BCB77' if user_ans == 'C' else ('#FF6B6B' if not is_correct and user_ans == 'C' else '#a0aec0')}"><b>C:</b> {opts['C']}</div>
                <div style="margin-bottom: 4px; color: {'#6BCB77' if user_ans == 'D' else ('#FF6B6B' if not is_correct and user_ans == 'D' else '#a0aec0')}"><b>D:</b> {opts['D']}</div>
            </div>
            <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; gap: 20px; font-size: 0.85rem;">
                <span>Your Answer: <b style="color: {border_col};">{user_ans} ({opts.get(user_ans, 'N/A')})</b></span>
                <span>Correct Answer: <b style="color: #6BCB77;">{correct_ans} ({opts[correct_ans]})</b></span>
                <span style="margin-left:auto;">Weightage: <b>{q['marks']} Marks</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
