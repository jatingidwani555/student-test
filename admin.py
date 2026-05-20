import streamlit as st
import pandas as pd
import io
import database
import auth
import styles

def get_csv_template():
    """Generate sample CSV template for bulk importing questions."""
    template_data = {
        "question_text": [
            "What is the output of print(2 ** 3) in Python?",
            "Which of the following is used to define a block of code in Python?",
            "Which built-in function returns the length of a list?"
        ],
        "option_a": ["6", "Curly braces", "len()"],
        "option_b": ["8", "Parentheses", "length()"],
        "option_c": ["9", "Indentation", "size()"],
        "option_d": ["5", "Quotations", "count()"],
        "correct_option": ["B", "C", "A"],
        "marks": [2, 1, 1]
    }
    df = pd.DataFrame(template_data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def show_admin_dashboard():
    """Render the comprehensive Administrative Dashboard."""
    # Apply custom style inject
    styles.inject_custom_css()
    
    # Header
    st.markdown('<div class="gradient-text">Admin Control Panel</div>', unsafe_allow_html=True)
    st.markdown(f"Welcome back, **{st.session_state.full_name}** | Mode: System Administrator")
    st.markdown("---")

    # Tabs for administrative tasks
    tab_overview, tab_exams, tab_bulk_upload, tab_manual_q, tab_students, tab_reports = st.tabs([
        "📊 Dashboard Overview", 
        "📝 Manage Exams", 
        "📤 Bulk MCQ Upload", 
        "➕ Add Question Manually",
        "👥 Manage Students",
        "📈 Attempt Reports & Analytics"
    ])

    # 1. OVERVIEW & ANALYTICS TAB
    with tab_overview:
        st.markdown('<div class="glass-card-header">System Metrics</div>', unsafe_allow_html=True)
        
        # Load Stats
        students = database.get_all_students()
        exams = database.get_all_exams()
        results = database.get_all_results()
        
        total_students = len(students)
        total_exams = len(exams)
        total_attempts = len(results)
        
        if total_attempts > 0:
            df_res = pd.DataFrame([dict(r) for r in results])
            global_avg = round(df_res['percentage'].mean(), 1)
        else:
            global_avg = 0.0

        # Custom Metrics Grid
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-box-label">Total Registered Students</div>
                <div class="metric-box-value">{total_students}</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Exams Created</div>
                <div class="metric-box-value">{total_exams}</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Total Exam Attempts</div>
                <div class="metric-box-value">{total_attempts}</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Global Avg Score</div>
                <div class="metric-box-value" style="color: #6BCB77;">{global_avg}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="glass-card-header">Exam Wise Attempts</div>', unsafe_allow_html=True)
            if total_attempts > 0:
                attempt_counts = df_res['exam_title'].value_counts().reset_index()
                attempt_counts.columns = ['Exam Title', 'Attempts']
                st.bar_chart(attempt_counts.set_index('Exam Title'), height=250)
            else:
                st.info("No exam attempts recorded yet.")
                
        with col2:
            st.markdown('<div class="glass-card-header">Score Range Distribution</div>', unsafe_allow_html=True)
            if total_attempts > 0:
                # Group scores into bins
                bins = [0, 39, 59, 79, 100]
                labels = ['Fail (<40%)', 'Pass (40-60%)', 'First Class (60-80%)', 'Distinction (>80%)']
                df_res['score_grade'] = pd.cut(df_res['percentage'], bins=bins, labels=labels, include_lowest=True)
                grade_counts = df_res['score_grade'].value_counts().reindex(labels).fillna(0).reset_index()
                grade_counts.columns = ['Performance Category', 'Count']
                st.bar_chart(grade_counts.set_index('Performance Category'), height=250)
            else:
                st.info("No student scores available yet.")

    # 2. MANAGE EXAMS TAB
    with tab_exams:
        col_list, col_create = st.columns([3, 2])
        
        with col_list:
            st.markdown('<div class="glass-card-header">Active Examinations</div>', unsafe_allow_html=True)
            exams_list = database.get_all_exams()
            if exams_list:
                df_exams = pd.DataFrame([dict(e) for e in exams_list])
                df_exams = df_exams[['id', 'title', 'duration_minutes', 'question_count', 'total_marks', 'created_at']]
                df_exams.columns = ['Exam ID', 'Title', 'Duration (mins)', 'Questions', 'Total Marks', 'Date Created']
                st.dataframe(df_exams, use_container_width=True, hide_index=True)
                
                # Delete Exam form
                st.markdown("---")
                st.markdown("⚠️ **Danger Zone**")
                del_exam_id = st.selectbox("Select Exam to Delete", [e['id'] for e in exams_list], 
                                           format_func=lambda x: next(e['title'] for e in exams_list if e['id'] == x))
                if st.button("🚨 Permanently Delete Selected Exam", use_container_width=True):
                    if database.delete_exam(del_exam_id):
                        st.success("Exam deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete exam.")
            else:
                st.info("No active examinations found. Create one on the right panel!")
                
        with col_create:
            st.markdown('<div class="glass-card-header">Create New Exam</div>', unsafe_allow_html=True)
            with st.form("create_exam_form"):
                new_title = st.text_input("Exam Title", placeholder="e.g., Data Structures Midterm")
                new_desc = st.text_area("Exam Description", placeholder="e.g., Covers Arrays, Stacks, Queues, and Trees...")
                new_duration = st.number_input("Exam Duration (Minutes)", min_value=1, max_value=300, value=30)
                submit_exam = st.form_submit_button("Add Exam Base", use_container_width=True)
                
                if submit_exam:
                    if not new_title.strip():
                        st.error("Exam title cannot be empty.")
                    else:
                        exam_id = database.create_exam(new_title, new_desc, new_duration)
                        if exam_id:
                            st.success(f"Exam '{new_title}' successfully created with ID {exam_id}!")
                            st.rerun()
                        else:
                            st.error("Failed to create exam. Please try again.")

    # 3. BULK MCQ UPLOADER TAB (THE MAIN REQUIREMENT FOR DATASET UPLOADING)
    with tab_bulk_upload:
        st.markdown('<div class="glass-card-header">Dataset Question Uploader (CSV / Excel)</div>', unsafe_allow_html=True)
        st.markdown("""
        Easily upload your entire dataset of questions at once. 
        Select the target exam, download the template below to ensure proper formatting, and drop your dataset!
        """)
        
        active_exams = database.get_all_exams()
        if not active_exams:
            st.warning("Please create an exam in the 'Manage Exams' tab first before uploading questions.")
        else:
            target_exam_id = st.selectbox(
                "Select Target Exam to Populate",
                [e['id'] for e in active_exams],
                format_func=lambda x: next(e['title'] for e in active_exams if e['id'] == x),
                key="bulk_target_exam"
            )
            
            # Offer download of the template
            template_csv = get_csv_template()
            st.download_button(
                label="📥 Download Standard MCQ CSV Template",
                data=template_csv,
                file_name="exam_mcq_template.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown("---")
            
            # File Uploader
            uploaded_file = st.file_uploader("Upload Question Dataset File (CSV or XLSX)", type=["csv", "xlsx"])
            
            if uploaded_file is not None:
                try:
                    # Parse based on file type
                    if uploaded_file.name.endswith(".csv"):
                        df_upload = pd.read_csv(uploaded_file)
                    else:
                        df_upload = pd.read_excel(uploaded_file)
                    
                    st.markdown("### Previewing Uploaded Dataset")
                    st.dataframe(df_upload.head(10), use_container_width=True)
                    
                    # Columns Validation
                    required_cols = ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option"]
                    missing_cols = [col for col in required_cols if col not in df_upload.columns]
                    
                    if missing_cols:
                        st.error(f"Failed to import. Missing required column(s): {', '.join(missing_cols)}")
                    else:
                        # Validate and Process
                        import_button = st.button("🚀 Confirm Bulk Import into SQLite Database", use_container_width=True)
                        if import_button:
                            success_count = 0
                            error_rows = []
                            
                            for idx, row in df_upload.iterrows():
                                q_text = str(row['question_text']).strip()
                                opt_a = str(row['option_a']).strip()
                                opt_b = str(row['option_b']).strip()
                                opt_c = str(row['option_c']).strip()
                                opt_d = str(row['option_d']).strip()
                                correct = str(row['correct_option']).strip().upper()
                                
                                # Default marks to 1 if not present or NaN
                                marks = 1
                                if 'marks' in df_upload.columns and not pd.isna(row['marks']):
                                    try:
                                        marks = int(row['marks'])
                                    except ValueError:
                                        pass
                                
                                # Row level validations
                                if not q_text or not opt_a or not opt_b or not opt_c or not opt_d:
                                    error_rows.append(f"Row {idx+2}: Missing question text or option fields.")
                                    continue
                                    
                                if correct not in ['A', 'B', 'C', 'D']:
                                    error_rows.append(f"Row {idx+2}: Invalid correct option '{correct}' (Must be A, B, C, or D).")
                                    continue
                                
                                # Insert Question
                                inserted = database.add_question(
                                    target_exam_id, q_text, opt_a, opt_b, opt_c, opt_d, correct, marks
                                )
                                if inserted:
                                    success_count += 1
                                else:
                                    error_rows.append(f"Row {idx+2}: Database insertion error.")
                                    
                            if success_count > 0:
                                st.balloons()
                                st.success(f"Successfully imported {success_count} questions into the exam!")
                            
                            if error_rows:
                                st.warning("Some rows failed validation:")
                                for err in error_rows[:15]: # Show first 15 errors
                                    st.write(f"- {err}")
                                if len(error_rows) > 15:
                                    st.write(f"...and {len(error_rows)-15} more rows.")
                                    
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")

    # 4. ADD QUESTION MANUALLY TAB
    with tab_manual_q:
        st.markdown('<div class="glass-card-header">Add Question Manually</div>', unsafe_allow_html=True)
        active_exams = database.get_all_exams()
        
        if not active_exams:
            st.warning("Please create an exam in the 'Manage Exams' tab first.")
        else:
            with st.form("manual_question_form"):
                target_exam = st.selectbox(
                    "Target Exam",
                    [e['id'] for e in active_exams],
                    format_func=lambda x: next(e['title'] for e in active_exams if e['id'] == x)
                )
                q_text = st.text_area("Question Text", placeholder="What is...")
                col_opts_ab, col_opts_cd = st.columns(2)
                with col_opts_ab:
                    opt_a = st.text_input("Option A")
                    opt_b = st.text_input("Option B")
                with col_opts_cd:
                    opt_c = st.text_input("Option C")
                    opt_d = st.text_input("Option D")
                    
                col_c_m = st.columns(2)
                with col_c_m:
                    correct_opt = st.selectbox("Correct Option", ["A", "B", "C", "D"])
                with col_c_m:
                    q_marks = st.number_input("Marks/Weightage", min_value=1, max_value=20, value=1)
                    
                submit_q = st.form_submit_button("Add Question", use_container_width=True)
                
                if submit_q:
                    if not q_text.strip() or not opt_a.strip() or not opt_b.strip() or not opt_c.strip() or not opt_d.strip():
                        st.error("Please fill in all question fields.")
                    else:
                        success = database.add_question(target_exam, q_text, opt_a, opt_b, opt_c, opt_d, correct_opt, q_marks)
                        if success:
                            st.success("Question added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add question to database.")

    # 5. MANAGE STUDENTS TAB
    with tab_students:
        col_stud_list, col_stud_add = st.columns([3, 2])
        
        with col_stud_list:
            st.markdown('<div class="glass-card-header">Student Directory</div>', unsafe_allow_html=True)
            students_list = database.get_all_students()
            if students_list:
                df_studs = pd.DataFrame([dict(s) for s in students_list])
                df_studs.columns = ['Username', 'Full Name']
                st.dataframe(df_studs, use_container_width=True, hide_index=True)
                
                # Delete Student Form
                st.markdown("---")
                delete_target = st.selectbox("Select Student to Remove", df_studs['Username'].tolist())
                if st.button("🚨 Remove Student Account", use_container_width=True):
                    if delete_target == st.session_state.username:
                        st.error("You cannot delete your own admin account!")
                    else:
                        succ, msg = database.delete_user(delete_target)
                        if succ:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.info("No registered students found.")
                
        with col_stud_add:
            st.markdown('<div class="glass-card-header">Register Student / Admin</div>', unsafe_allow_html=True)
            with st.form("register_user_form"):
                new_username = st.text_input("Username", placeholder="e.g., johndoe")
                new_name = st.text_input("Full Name", placeholder="e.g., John Doe")
                new_role = st.selectbox("Role", ["student", "admin"])
                new_pwd = st.text_input("Password", type="password")
                new_pwd_confirm = st.text_input("Confirm Password", type="password")
                
                submit_register = st.form_submit_button("Register User", use_container_width=True)
                
                if submit_register:
                    succ, msg = auth.register_user(new_username, new_pwd, new_pwd_confirm, new_name, new_role)
                    if succ:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # 6. ATTEMPT REPORTS & ANALYTICS TAB
    with tab_reports:
        st.markdown('<div class="glass-card-header">Exam Performance Reports</div>', unsafe_allow_html=True)
        results_list = database.get_all_results()
        
        if results_list:
            df_results = pd.DataFrame([dict(r) for r in results_list])
            
            # Format display
            df_disp = df_results[['username', 'full_name', 'exam_title', 'score', 'total_marks', 'percentage', 'completed_at']].copy()
            df_disp.columns = ['Username', 'Student Name', 'Exam Title', 'Score', 'Total Marks', 'Percentage (%)', 'Date Completed']
            
            # Dynamic filtering
            filter_exam = st.selectbox("Filter Report by Exam", ["All Exams"] + df_results['exam_title'].unique().tolist())
            if filter_exam != "All Exams":
                df_disp = df_disp[df_disp['Exam Title'] == filter_exam]
                
            st.dataframe(df_disp, use_container_width=True, hide_index=True)
            
            # CSV Download using Pandas
            csv_buffer = io.StringIO()
            df_disp.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="📥 Export Report to CSV (Pandas Download)",
                data=csv_buffer.getvalue(),
                file_name=f"exam_performance_{filter_exam.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Extra statistics
            if len(df_disp) > 0:
                st.markdown("### Quick Statistics")
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                stat_col1.metric("Selected Exam Attempts", len(df_disp))
                stat_col2.metric("Highest Percentage", f"{df_disp['Percentage (%)'].max()}%")
                stat_col3.metric("Average Percentage", f"{round(df_disp['Percentage (%)'].mean(), 1)}%")
        else:
            st.info("No exam attempts registered yet. When students complete examinations, they will display here.")
