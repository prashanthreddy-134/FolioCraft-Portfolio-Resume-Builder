
# ============================================================
# FOLIOCRAFT - COMPLETE VIEWS
# ============================================================

from io import BytesIO
from xml.sax.saxutils import escape

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)

from .models import (
    Profile,
    Portfolio,
    PortfolioView,
    Skill,
    Project,
    Experience,
    Education,
    Certification,
    Testimonial,
)

from .forms import (
    RegisterForm,
    PortfolioForm,
    ProfileForm,
    SkillForm,
    ProjectForm,
    ExperienceForm,
    EducationForm,
    CertificationForm,
    TestimonialForm,
)


# ============================================================
# HOME
# ============================================================

def home(request):
    return render(request, "home.html")


# ============================================================
# REGISTRATION
# ============================================================

def register(request):
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()

        Profile.objects.create(
            user=user,
            full_name=user.username,
            email=user.email or ""
        )

        login(request, user)

        messages.success(request, "Account created successfully.")

        return redirect("dashboard")

    return render(
        request,
        "form.html",
        {
            "form": form,
            "heading": "Create your account"
        }
    )


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):
    portfolios = Portfolio.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "dashboard.html",
        {
            "portfolios": portfolios
        }
    )


# ============================================================
# CREATE PORTFOLIO
# ============================================================

@login_required
def create_portfolio(request):
    form = PortfolioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        portfolio = form.save(commit=False)
        portfolio.user = request.user
        portfolio.save()

        messages.success(request, "Portfolio created successfully.")

        return redirect("manage", portfolio.pk)

    return render(
        request,
        "form.html",
        {
            "form": form,
            "heading": "Create a portfolio"
        }
    )


# ============================================================
# PORTFOLIO OWNERSHIP
# ============================================================

@login_required
def owned(request, pk):
    return get_object_or_404(
        Portfolio,
        pk=pk,
        user=request.user
    )


# ============================================================
# MANAGE PORTFOLIO
# ============================================================

@login_required
def manage(request, pk):
    portfolio = owned(request, pk)

    profile = Profile.objects.filter(
        user=request.user
    ).first()

    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile
    )

    if request.method == "POST" and form.is_valid():
        profile_obj = form.save(commit=False)
        profile_obj.user = request.user
        profile_obj.save()

        messages.success(request, "Profile saved successfully.")

        return redirect("manage", pk)

    sections = [
        ("skill", "Skills", portfolio.skills.all()),
        ("project", "Projects", portfolio.projects.all()),
        ("experience", "Experience", portfolio.experiences.all()),
        ("education", "Education", portfolio.education.all()),
        ("certification", "Certifications", portfolio.certifications.all()),
        ("testimonial", "Testimonials", portfolio.testimonials.all()),
    ]

    return render(
        request,
        "manage.html",
        {
            "p": portfolio,
            "form": form,
            "sections": sections
        }
    )


# ============================================================
# ADD PORTFOLIO ITEMS
# ============================================================

@login_required
def add_item(request, pk, kind):
    portfolio = owned(request, pk)

    form_mapping = {
        "skill": SkillForm,
        "project": ProjectForm,
        "experience": ExperienceForm,
        "education": EducationForm,
        "certification": CertificationForm,
        "testimonial": TestimonialForm,
    }

    form_class = form_mapping.get(kind)

    if form_class is None:
        messages.error(request, "Invalid portfolio section.")
        return redirect("manage", pk)

    form = form_class(
        request.POST or None,
        request.FILES or None
    )

    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.portfolio = portfolio
        item.save()

        messages.success(
            request,
            f"{kind.title()} added successfully."
        )

        return redirect("manage", pk)

    return render(
        request,
        "form.html",
        {
            "form": form,
            "heading": "Add " + kind.title()
        }
    )


# ============================================================
# DELETE PORTFOLIO ITEMS
# ============================================================

@login_required
def delete_item(request, pk, kind, item):
    portfolio = owned(request, pk)

    model_mapping = {
        "skill": Skill,
        "project": Project,
        "experience": Experience,
        "education": Education,
        "certification": Certification,
        "testimonial": Testimonial,
    }

    model_class = model_mapping.get(kind)

    if model_class is None:
        messages.error(request, "Invalid section.")
        return redirect("manage", pk)

    if request.method == "POST":
        obj = get_object_or_404(
            model_class,
            pk=item,
            portfolio=portfolio
        )

        obj.delete()

        messages.success(
            request,
            f"{kind.title()} deleted successfully."
        )

    return redirect("manage", pk)


# ============================================================
# PORTFOLIO VISIBILITY
# ============================================================

@login_required
def visibility(request, pk):
    portfolio = owned(request, pk)

    if request.method == "POST":
        portfolio.is_public = not portfolio.is_public
        portfolio.save(update_fields=["is_public"])

        messages.success(
            request,
            "Portfolio visibility updated."
        )

    return redirect("manage", pk)


# ============================================================
# PUBLIC PORTFOLIO
# ============================================================

def public_portfolio(request, slug):
    portfolio = get_object_or_404(
        Portfolio,
        slug=slug,
        is_public=True
    )

    if (
        not request.user.is_authenticated
        or request.user != portfolio.user
    ):
        portfolio.views += 1
        portfolio.save(update_fields=["views"])

        PortfolioView.objects.create(
            portfolio=portfolio,
            ip_address=request.META.get("REMOTE_ADDR")
        )

    profile = Profile.objects.filter(
        user=portfolio.user
    ).first()

    return render(
        request,
        "public.html",
        {
            "p": portfolio,
            "profile": profile
        }
    )


# ============================================================
# PROFESSIONAL PDF RESUME GENERATOR
# ============================================================

@login_required
def resume(request, pk):

    portfolio = owned(request, pk)

    profile = Profile.objects.filter(
        user=request.user
    ).first()

    buffer = BytesIO()

    # --------------------------------------------------------
    # PDF DOCUMENT
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Professional Resume",
        author=(
            profile.full_name
            if profile and profile.full_name
            else request.user.username
        )
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "ResumeName",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17251f"),
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "ResumeSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#52645a"),
        spaceAfter=7
    )

    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontSize=8,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#444444"),
        spaceAfter=7
    )

    heading_style = ParagraphStyle(
        "ResumeHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#26734d"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#333333"),
        spaceAfter=5
    )

    item_style = ParagraphStyle(
        "ResumeItem",
        parent=body_style,
        fontName="Helvetica-Bold",
        spaceAfter=3,
        keepWithNext=True
    )

    small_style = ParagraphStyle(
        "ResumeSmall",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#555555")
    )

    story = []

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def safe(value):
        return escape(str(value or ""))

    def format_date(value):
        if not value:
            return ""

        return value.strftime("%b %Y")

    def add_text(value, style=body_style):
        if value is None or not str(value).strip():
            return

        story.append(
            Paragraph(
                safe(value).replace("\n", "<br/>"),
                style
            )
        )

    def add_section(title):
        story.append(
            Paragraph(
                safe(title.upper()),
                heading_style
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.7,
                color=colors.HexColor("#d5e2d9"),
                spaceAfter=7
            )
        )

    def add_link(label, url):
        if not url:
            return ""

        return (
            f'<link href="{safe(url)}" color="#26734d">'
            f'{safe(label)}</link>'
        )

    # --------------------------------------------------------
    # PERSONAL INFORMATION
    # --------------------------------------------------------

    full_name = (
        profile.full_name
        if profile and profile.full_name
        else request.user.username
    )

    story.append(
        Paragraph(
            safe(full_name),
            name_style
        )
    )

    if profile and profile.title:
        add_text(profile.title, subtitle_style)

    contact_details = []

    if profile:
        for value in [
            profile.email,
            profile.phone,
            profile.location
        ]:
            if value:
                contact_details.append(str(value))

    if contact_details:
        story.append(
            Paragraph(
                safe(" | ".join(contact_details)),
                contact_style
            )
        )

    social_links = []

    if profile:
        for label, url in [
            ("Website", profile.website),
            ("GitHub", profile.github),
            ("LinkedIn", profile.linkedin),
            ("Twitter", profile.twitter),
        ]:
            if url:
                social_links.append(
                    add_link(label, url)
                )

    if social_links:
        story.append(
            Paragraph(
                " | ".join(social_links),
                contact_style
            )
        )

    # --------------------------------------------------------
    # PROFESSIONAL SUMMARY
    # --------------------------------------------------------

    bio = profile.bio if profile and profile.bio else ""

    template = portfolio.template

    # Do not show template description as personal biography.
    if (
        template
        and bio.strip()
        and bio.strip() == (template.description or "").strip()
    ):
        bio = ""

    if bio:
        add_section("Professional Summary")
        add_text(bio)

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    skills = portfolio.skills.all()

    if skills.exists():
        add_section("Technical Skills")

        for skill in skills:
            content = f"<b>{safe(skill.name)}</b>"

            if skill.category:
                content += f" - {safe(skill.category)}"

            content += (
                f" ({skill.proficiency}% proficiency)"
            )

            story.append(
                Paragraph(content, body_style)
            )

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    projects = portfolio.projects.all()

    if projects.exists():
        add_section("Projects")

        for project in projects:
            story.append(
                Paragraph(
                    safe(project.title),
                    item_style
                )
            )

            if project.description:
                add_text(project.description)

            if project.tech_stack:
                story.append(
                    Paragraph(
                        f"<b>Technologies:</b> "
                        f"{safe(project.tech_stack)}",
                        small_style
                    )
                )

            links = []

            if project.github_url:
                links.append(
                    add_link(
                        "GitHub Repository",
                        project.github_url
                    )
                )

            if project.live_url:
                links.append(
                    add_link(
                        "Live Project",
                        project.live_url
                    )
                )

            if links:
                story.append(
                    Paragraph(
                        " | ".join(links),
                        small_style
                    )
                )

            story.append(Spacer(1, 6))

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    experiences = portfolio.experiences.all().order_by(
        "-start_date"
    )

    if experiences.exists():
        add_section("Work Experience")

        for experience in experiences:

            start = format_date(experience.start_date)

            if experience.current:
                end = "Present"
            else:
                end = format_date(experience.end_date) or "Not specified"

            story.append(
                Paragraph(
                    f"<b>{safe(experience.position)}</b>"
                    f" - {safe(experience.company)}",
                    item_style
                )
            )

            add_text(f"{start} - {end}", small_style)

            if experience.location:
                add_text(experience.location, small_style)

            if experience.description:
                add_text(experience.description)

            story.append(Spacer(1, 6))

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    education_records = portfolio.education.all().order_by(
        "-start_date"
    )

    if education_records.exists():
        add_section("Education")

        for education in education_records:

            start = format_date(education.start_date)
            end = format_date(education.end_date) or "Present"

            story.append(
                Paragraph(
                    safe(education.degree),
                    item_style
                )
            )

            add_text(education.institution)

            add_text(
                f"{start} - {end}",
                small_style
            )

            if education.field:
                add_text(
                    f"Field: {education.field}",
                    small_style
                )

            if education.description:
                add_text(education.description)

            story.append(Spacer(1, 6))

    # --------------------------------------------------------
    # CERTIFICATIONS
    # --------------------------------------------------------

    certifications = portfolio.certifications.all().order_by(
        "-issue_date"
    )

    if certifications.exists():
        add_section("Certifications")

        for certification in certifications:

            story.append(
                Paragraph(
                    safe(certification.name),
                    item_style
                )
            )

            add_text(
                f"Issued by: {certification.issuer}"
            )

            add_text(
                f"Issue date: {format_date(certification.issue_date)}",
                small_style
            )

            if certification.credential_url:
                story.append(
                    Paragraph(
                        add_link(
                            "View Credential",
                            certification.credential_url
                        ),
                        small_style
                    )
                )

            story.append(Spacer(1, 6))

    # --------------------------------------------------------
    # GENERATE PDF
    # --------------------------------------------------------

    document.build(story)

    pdf_content = buffer.getvalue()
    buffer.close()

    response = HttpResponse(
        pdf_content,
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{portfolio.slug}-resume.pdf"'
    )

    return response
