import flet as ft

def main(page: ft.Page):
    page.title = "تطبيق البوت الخاص بي"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    page.add(
        ft.Row(
            [
                ft.Text("أهلاً بك في تطبيقي الأول", size=30, weight="bold"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(target=main)
