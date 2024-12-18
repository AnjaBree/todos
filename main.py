import flet as ft
import firebase_admin
from firebase_admin import auth, firestore, credentials

# Firebase inicijalizacija
cred = credentials.Certificate("todos.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def main(page: ft.Page):
    page.title = "TODOS"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 375
    page.window_height = 667
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # Pozadinska slika
    background_image = ft.Image(
        src="slika2.jpg",
        width=page.width,
        height=page.height,
        fit=ft.ImageFit.COVER
    )

    # Držanje stanja aplikacije
    authenticated = {"value": False}
    user_id = {"value": None}

    # Navigacija
    def navigate_to(route):
        page.views.clear()
        if route == "login":
            page.views.append(create_login_view())
        elif route == "register":
            page.views.append(create_register_view())
        elif route == "home" and authenticated["value"]:
            page.views.append(create_home_view())
        else:
            page.views.append(create_login_view())
        page.update()

    # Login handler
    def handle_login(e):
        try:
            user = auth.get_user_by_email(email_field.value)
            authenticated["value"] = True
            user_id["value"] = user.uid
            navigate_to("home")
        except Exception as ex:
            status_text.value = f"Login failed: {str(ex)}"
            status_text.color = ft.colors.RED
            status_text.update()

    # Register handler
    def handle_register(e):
        try:
            if reg_password_field.value != confirm_password_field.value:
                register_status.value = "Passwords do not match."
                register_status.color = ft.colors.RED
            else:
                user = auth.create_user(
                    email=reg_email_field.value, password=reg_password_field.value
                )
                register_status.value = "Registration successful! Please login."
                register_status.color = ft.colors.GREEN
        except Exception as ex:
            register_status.value = f"Registration failed: {str(ex)}"
            register_status.color = ft.colors.RED
        register_status.update()

    # Dodavanje zadatka handler
    def handle_add_task(e):
        try:
            if task_title.value == "" or task_description.value == "" or task_date.value == "":
                task_status.value = "All fields are required."
                task_status.color = ft.colors.RED
            else:
                db.collection("tasks").add({
                    "user_id": user_id["value"],
                    "title": task_title.value,
                    "description": task_description.value,
                    "date": task_date.value,
                })
                task_status.value = "Task added successfully!"
                task_status.color = ft.colors.GREEN
        except Exception as ex:
            task_status.value = f"Failed to add task: {str(ex)}"
            task_status.color = ft.colors.RED
        task_status.update()

    # Login forma
    def create_login_view():
        return ft.View(
            route="login",
            controls=[
                ft.Stack(
                    controls=[
                        background_image,
                        ft.Container(
                            expand=True,
                            border_radius=15,
                            bgcolor=ft.colors.with_opacity(0.8, ft.colors.WHITE),
                            padding=ft.padding.all(20),
                            margin=ft.margin.all(20),
                            content=ft.Column(
                                controls=[
                                    app_title,
                                    subtitle,
                                    ft.Container(height=20),
                                    email_field,
                                    password_field,
                                    ft.Container(height=10),
                                    login_button,
                                    ft.ElevatedButton("Register", on_click=lambda e: navigate_to("register"), width=300),
                                    ft.Container(height=10),
                                    status_text,
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        )
                    ]
                )
            ]
        )

    # Register forma
    def create_register_view():
        return ft.View(
            route="register",
            controls=[
                ft.Stack(
                    controls=[
                        background_image,
                        ft.Container(
                            expand=True,
                            border_radius=15,
                            bgcolor=ft.colors.with_opacity(0.8, ft.colors.WHITE),
                            padding=ft.padding.all(20),
                            margin=ft.margin.all(20),
                            content=ft.Column(
                                controls=[
                                    ft.Text("Register", size=24, weight=ft.FontWeight.BOLD),
                                    ft.Container(height=10),
                                    reg_email_field,
                                    reg_password_field,
                                    confirm_password_field,
                                    ft.Container(height=10),
                                    ft.ElevatedButton("Register", on_click=handle_register, width=300),
                                    ft.ElevatedButton("Back to Login", on_click=lambda e: navigate_to("login"), width=300),
                                    ft.Container(height=10),
                                    register_status,
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        )
                    ]
                )
            ]
        )

    # Home view
    def create_home_view():
        return ft.View(
            route="home",
            controls=[
                ft.Stack(
                    controls=[
                        background_image,
                        ft.Container(
                            expand=True,
                            border_radius=15,
                            bgcolor=ft.colors.with_opacity(0.8, ft.colors.WHITE),
                            padding=ft.padding.all(20),
                            margin=ft.margin.all(20),
                            content=ft.Column(
                                controls=[
                                    ft.Text("Welcome to TODOS!", size=24, weight=ft.FontWeight.BOLD),
                                    ft.Container(height=10),
                                    ft.TextField(label="Task Title", width=300, ref=lambda ref: setattr(globals(), "task_title", ref)),
                                    ft.TextField(label="Short Description", multiline=True, max_lines=3, width=300, ref=lambda ref: setattr(globals(), "task_description", ref)),
                                    ft.TextField(label="Date (YYYY-MM-DD)", width=300, ref=lambda ref: setattr(globals(), "task_date", ref)),
                                    ft.Container(height=10),
                                    ft.ElevatedButton("Add Task", on_click=handle_add_task, width=300),
                                    ft.Container(height=10),
                                    ft.Text(value="", size=14, weight=ft.FontWeight.BOLD, ref=lambda ref: setattr(globals(), "task_status", ref)),
                                    ft.Container(height=20),
                                    ft.ElevatedButton("Logout", on_click=lambda e: logout()),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        )
                    ]
                )
            ]
        )

    # Logout
    def logout():
        authenticated["value"] = False
        user_id["value"] = None
        navigate_to("login")

    # Komponente aplikacije
    app_title = ft.Text("TODOS", size=32, weight=ft.FontWeight.BOLD, color="#B6AB99")
    subtitle = ft.Text("Your tasks, organized.", size=16, color="#B6AB99")
    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Password", password=True, width=300)
    login_button = ft.ElevatedButton("Login", on_click=handle_login, width=300)
    status_text = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

    reg_email_field = ft.TextField(label="Email", width=300)
    reg_password_field = ft.TextField(label="Password", password=True, width=300)
    confirm_password_field = ft.TextField(label="Confirm Password", password=True, width=300)
    register_status = ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

    # Početni prikaz
    navigate_to("login")

# Pokretanje Flet aplikacije
ft.app(target=main)
