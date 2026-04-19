# ==========================================================
# AI WORKSHEET GENERATOR MAIN APPLICATION
# ==========================================================

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rag_engine import build_index, search_index

import uuid
import os
import shutil

from docx_builder import build_docx

# AI
from pdf_engine import extract_text_and_images_from_pdf
from worksheet_engine import generate_worksheet
from pdf_builder import build_student_pdf, build_teacher_pdf

# Database
from database import (
    init_db,
    create_user,
    get_user,
    log_download,
    get_user_downloads,
    ensure_default_admin,
    get_adaptive_difficulty   # 🔴 NEW
)

# Auth
from auth import (
    hash_password,
    verify_password,
    create_token,
    get_current_user
)

from rate_limiter import check_login_allowed, record_failed_login
from analytics import downloads_per_user, downloads_per_day, top_files

# ==========================================================
# APP INIT
# ==========================================================

app = FastAPI(title="AI Learning Studio")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ FIXED TEMPLATE PATH
templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

lesson_indexes = {}
lesson_chunks = {}

# STATIC FILES
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/lesson_files", StaticFiles(directory="lesson_files"), name="lesson_files")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# DATABASE INIT
init_db()
ensure_default_admin(hash_password)

from database import get_connection

# ==========================================================
# ADMIN DATA
# ==========================================================

@app.get("/admin-data")
def admin_data(request: Request):

    user = get_current_user(request)

    if user["role"] != "admin":
        raise HTTPException(status_code=403)

    with get_connection() as conn:
        users = conn.execute("SELECT username, role, created_at FROM users").fetchall()
        downloads = conn.execute("SELECT username, file_name, download_time FROM downloads").fetchall()

    return {
        "users": [dict(u) for u in users],
        "downloads": [dict(d) for d in downloads]
    }

# ==========================================================
# ADMIN PANEL
# ==========================================================

@app.get("/head-control", response_class=HTMLResponse)
def head_control(request: Request):

    try:
        user = get_current_user(request)
    except:
        user = {"username": "Guest", "role": "guest"}

    from database import get_connection

    with get_connection() as conn:
        users = conn.execute(
            "SELECT username, role, created_at FROM users"
        ).fetchall()

        downloads = conn.execute(
            "SELECT username, file_name, download_time FROM downloads"
        ).fetchall()

    return templates.TemplateResponse(
        request,
        "admin_panel.html",
        {
            "request": request,
            "user": user,
            "users": users,
            "downloads": downloads
        }
    )
# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
async def root(request: Request):

    try:
        user = get_current_user(request)

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {"request": request, "user": user}
        )

    except:
        return RedirectResponse("/login")

# ==========================================================
# GENERATE WORKSHEET
# ==========================================================
from fastapi import BackgroundTasks

jobs = {}

@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    background_tasks: BackgroundTasks,
    class_name: str = Form(...),
    subject: str = Form(...),
    chapter: str = Form(...),
    header_text: str = Form(""),
    pdf_file: UploadFile = File(None),
    logo: UploadFile = File(None),
    use_default: str = Form("false"),
    default_pdf_name: str = Form(""),
    default_logo_name: str = Form("")
):
    user = get_current_user(request)
    BASE_DEFAULT = os.path.join(BASE_DIR, "default_assets")

    # ---------------- FILE HANDLING ----------------
    if use_default == "true":

        if not default_pdf_name:
            raise HTTPException(status_code=400, detail="Select default PDF")

        upload_path = os.path.join(BASE_DEFAULT, "pdfs", default_pdf_name)

        if not os.path.exists(upload_path):
            raise HTTPException(status_code=404, detail="Default PDF not found")

        unique_pdf = default_pdf_name

        logo_path = None
        if default_logo_name:
            logo_path = os.path.join(BASE_DEFAULT, "logos", default_logo_name)
            if not os.path.exists(logo_path):
                logo_path = None

    else:

        if not pdf_file:
            raise HTTPException(status_code=400, detail="PDF required")

        if not pdf_file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF allowed")

        filename = f"{uuid.uuid4().hex}_{pdf_file.filename}"
        upload_path = os.path.join("lesson_files", filename)

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)

        unique_pdf = filename

        logo_path = None
        if logo and logo.filename:
            logo_name = f"{uuid.uuid4().hex}_{logo.filename}"
            logo_path = os.path.join("uploads", logo_name)

            with open(logo_path, "wb") as buffer:
                shutil.copyfileobj(logo.file, buffer)

    # ---------------- CREATE JOB ----------------
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing"}

    # ---------------- BACKGROUND TASK ----------------
    def run_generation():

        try:
            # TEXT
            text, images = extract_text_and_images_from_pdf(upload_path)

            if len(text.split()) < 20:
                jobs[job_id] = {"status": "error", "error": "PDF too small"}
                return

            # ADAPTIVE
            student_level = get_adaptive_difficulty(user["username"])

            # GENERATE
            result = generate_worksheet(
                text=text,
                chapter=chapter
            )

            result["generation_mode"] = "adaptive"
            result["student_level"] = student_level
            result["chapter"] = chapter

            # FORMAT
            result["true_false"] = [
                (x.get("q",""), x.get("a",""))
                for x in result.get("true_false", [])
                if isinstance(x, dict)
            ]

            result["fill_blanks"] = [
                (x.get("q",""), x.get("a",""))
                for x in result.get("fill_blanks", [])
                if isinstance(x, dict)
            ]

            result["mcqs"] = [
                (x.get("q",""), x.get("options",[]), x.get("a",""))
                for x in result.get("mcqs", [])
                if isinstance(x, dict)
            ]

            result["header_logo"] = logo_path
            result["header_text"] = header_text or ""

            # FILES
            student_file = f"student_{uuid.uuid4().hex}.pdf"
            teacher_file = f"teacher_{uuid.uuid4().hex}.pdf"

            student_path = os.path.join(BASE_DIR, "static", "generated", student_file)
            teacher_path = os.path.join(BASE_DIR, "static", "generated", teacher_file)

            build_student_pdf(student_path, result)
            build_teacher_pdf(teacher_path, result)

            docx_file = f"worksheet_{uuid.uuid4().hex}.docx"
            docx_path = os.path.join("static/generated", docx_file)

            build_docx(docx_path, result)

            log_download(user["username"], student_file)
            log_download(user["username"], teacher_file)

            jobs[job_id] = {
                "status": "done",
                "student_pdf": student_file,
                "teacher_pdf": teacher_file,
                "docx_file": docx_file,
                "uploaded_pdf": unique_pdf,
                "text": text
            }

        except Exception as e:
            jobs[job_id] = {"status": "error", "error": str(e)}

    # run async in background
    background_tasks.add_task(run_generation)

    # ---------------- RETURN LOADING PAGE ----------------
    return templates.TemplateResponse(
        request,
        "loading.html",
        {
            "request": request,
            "job_id": job_id
        }
    )
@app.get("/job-status/{job_id}")
def job_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})

@app.get("/result/{job_id}")
def result_page(request: Request, job_id: str):
    job = jobs.get(job_id)

    if not job or job["status"] != "done":
        return HTMLResponse("Not ready")

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "request": request,
            "student_pdf": job["student_pdf"],
            "teacher_pdf": job["teacher_pdf"],
            "uploaded_pdf": job["uploaded_pdf"],
            "listen_text": job["text"],
            "docx_file": job["docx_file"]
        }
    )
@app.get("/default-assets")
def get_default_assets():

    BASE_DEFAULT = os.path.join(BASE_DIR, "default_assets")

    pdf_dir = os.path.join(BASE_DEFAULT, "pdfs")
    logo_dir = os.path.join(BASE_DEFAULT, "logos")

    pdfs = []
    logos = []

    if os.path.exists(pdf_dir):
        pdfs = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

    if os.path.exists(logo_dir):
        logos = [f for f in os.listdir(logo_dir)]

    return {
        "pdfs": pdfs,
        "logos": logos
    }
# ==========================================================
# LOGIN
# ==========================================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    return templates.TemplateResponse(
        request,
        "login.html",
        {"request": request}
    )

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):

    check_login_allowed(username)

    user = get_user(username)

    if not user or not verify_password(password, user["password"]):
        record_failed_login(username)
        raise HTTPException(status_code=401)

    token = create_token(user["username"], user["role"])

    response = RedirectResponse("/", status_code=302)
    response.set_cookie("auth_token", token, httponly=True)

    return response

@app.get("/logout")
def logout():

    response = RedirectResponse("/login", status_code=302)

    # 🔴 REMOVE AUTH COOKIE
    response.delete_cookie("auth_token")

    return response
# ==========================================================
# REGISTER
# ==========================================================

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):

    return templates.TemplateResponse(
        request,
        "register.html",
        {"request": request}
    )

@app.post("/register")
async def register(
    school_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):

    hashed = hash_password(password)

    try:
        create_user(school_name, username, email, hashed)
    except Exception as e:
        print("ERROR:", e)   # 🔴 ADD THIS
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse("/login", status_code=302)
# ==========================================================
# HISTORY
# ==========================================================

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):

    user = get_current_user(request)
    downloads = get_user_downloads(user["username"])

    return templates.TemplateResponse(
        request,
        "history.html",
        {"request": request, "downloads": downloads}
    )

# ==========================================================
# ADMIN ANALYTICS
# ==========================================================

@app.get("/api/admin/analytics")
async def admin_analytics(request: Request):

    user = get_current_user(request)

    if user["role"] != "admin":
        raise HTTPException(status_code=403)

    return {
        "downloads_user": downloads_per_user(),
        "downloads_day": downloads_per_day(),
        "top_files": top_files()
    }

# ==========================================================
# GET PDF LIST
# ==========================================================

@app.get("/get-pdfs")
def get_pdfs():

    files = os.listdir("lesson_files")
    pdfs = [f for f in files if f.endswith(".pdf")]

    return {"files": pdfs}

# ==========================================================
# DOWNLOAD
# ==========================================================

@app.get("/download/{file_name}")
async def download_file(request: Request, file_name: str):

    user = get_current_user(request)

    log_download(user["username"], file_name)

    path = os.path.join(BASE_DIR, "static", "generated", file_name)

    print("Download path:", path)  # debug

    if not os.path.exists(path):
        print("FILE NOT FOUND")
        raise HTTPException(status_code=404)

    return FileResponse(path, filename=file_name)

import ollama

@app.post("/api/chat")
async def chat(request: Request):

    data = await request.json()
    message = data.get("message", "")
    pdf_id = data.get("pdf_id")

    context = ""

    # ✅ CORRECT TRY STRUCTURE
    try:
        if pdf_id:

            from pdf_engine import extract_text_and_images_from_pdf

            result = extract_text_and_images_from_pdf(f"lesson_files/{pdf_id}")

            if isinstance(result, tuple):
                text = result[0]
            else:
                text = result
            index, chunks = build_index(text)

            context = search_index(index, chunks, message)

            # fallback to general chat
            if not context or len(context.strip()) < 20:
                context = ""

    except Exception as e:
        print("RAG ERROR:", e)
        context = ""

    # ✅ PROMPT (OUTSIDE TRY)
    prompt = f"""
You are a helpful AI tutor.

If the question is related to the lesson, use the context.
If the question is general, answer normally.

Context:
{context}

Question:
{message}

Answer clearly and simply.
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response["message"]["content"]

    return {"reply": reply}
@app.get("/get-user")
def get_user_name(request: Request):

    try:
        user = get_current_user(request)
        return {"username": user["username"]}
    except:
        return {"username": "User"}
    
@app.get("/preview")
def preview_pdf(pdf: str):

    try:
        from pdf_engine import extract_text_and_images_from_pdf

        text, _ = extract_text_and_images_from_pdf(f"lesson_files/{pdf}")

        return {
            "text": text[:2000]
        }

    except Exception as e:
        return {"detail": str(e)}
@app.get("/admin-report")
def admin_report():

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    import reportlab.lib.styles
    from database import get_connection

    path = os.path.join(BASE_DIR, "static", "generated", "admin_report.pdf")

    styles = reportlab.lib.styles.getSampleStyleSheet()
    doc = SimpleDocTemplate(path)

    content = []

    with get_connection() as conn:
        users = conn.execute("SELECT username, role FROM users").fetchall()
        downloads = conn.execute("SELECT username, file_name FROM downloads").fetchall()

    content.append(Paragraph("Users", styles["Heading1"]))
    content.append(Spacer(1, 10))

    for u in users:
        content.append(Paragraph(f"{u['username']} - {u['role']}", styles["Normal"]))

    content.append(Spacer(1, 20))
    content.append(Paragraph("Downloads", styles["Heading1"]))
    content.append(Spacer(1, 10))

    for d in downloads:
        content.append(Paragraph(f"{d['username']} - {d['file_name']}", styles["Normal"]))

    doc.build(content)

    return FileResponse(path, filename="admin_report.pdf")